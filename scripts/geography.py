#!/usr/bin/env python3
"""Read-only geography diagnostics. No inferred transform or automatic town deletion."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / 'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json'
INVENTORY = ROOT / 'data/towns/europe_1800_towns_600_DRAFT.csv'
V4 = ROOT / 'maps/calibration/baseline_v2/Europe_1800_40_city_V4_REGIONAL_TEST.json'
V2 = ROOT / 'maps/calibration/baseline_v2/Europe_1800_5_city_CONTROL_V2_TEST.json'
SIZE = 4096


def key(name):
    return ' '.join(unicodedata.normalize('NFKC', name).casefold().split())


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(towns):
    if not isinstance(towns, list) or not towns:
        raise ValueError('Expected a nonempty town array')
    seen = set()
    for t in towns:
        if not isinstance(t.get('name'), str) or not t['name'].strip():
            raise ValueError('Missing town name')
        name = key(t['name'])
        if name in seen:
            raise ValueError('Duplicate normalized name: ' + t['name'])
        seen.add(name)
        for axis in ('x', 'y'):
            v = t.get(axis)
            if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1:
                raise ValueError(f'{t["name"]}: invalid {axis}')
        if type(t.get('population')) is not int or t['population'] <= 0:
            raise ValueError('Invalid population: ' + t['name'])
        if type(t.get('city')) is not bool:
            raise ValueError('Invalid city flag: ' + t['name'])


def distance(a, b):
    # Continuous normalized-space diagnostic; not quantized founding-tile distance.
    return SIZE * math.hypot(a['x'] - b['x'], a['y'] - b['y'])


def band(d):
    return 'under_15_review_importance' if d < 15 else (
        '15_to_30_individual_review' if d <= 30 else 'over_30_generally_coexist')


def spacing(towns):
    rows = []
    for i, t in enumerate(towns):
        others = [(distance(t, u), u['name']) for j, u in enumerate(towns) if i != j]
        d, name = min(others) if others else (math.inf, '')
        rows.append(dict(name=t['name'], x=t['x'], y=t['y'], nearest_town=name,
                         distance_tiles=round(d, 6) if others else '',
                         spacing_band=band(d), coordinate_status='UNVERIFIED'))
    return rows


def write_csv(path, rows, fields):
    with path.open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def inventory():
    with INVENTORY.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    result = {key(r['name']): r for r in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate inventory names')
    return result


def audit(out):
    master, v4, v2 = [read_json(p) for p in (MASTER, V4, V2)]
    for towns in (master, v4, v2):
        validate(towns)
    inv = inventory()
    source = {key(t['name']): t for t in master}
    metadata_deltas = []
    for t in v4:
        old = source[key(t['name'])]
        if (t['population'], t['city']) != (old['population'], old['city']):
            metadata_deltas.append(dict(name=t['name'], master_population=old['population'],
                                        v4_population=t['population'], master_city=old['city'],
                                        v4_city=t['city'], action='Existing discrepancy documented; neither input modified'))
    for t in v2:
        if t != next(u for u in v4 if key(u['name']) == key(t['name'])):
            raise ValueError('V2 anchor changed in V4: ' + t['name'])
    missing_inventory = sorted(set(source) - set(inv))
    inventory_only = sorted(set(inv) - set(source))
    out.mkdir(parents=True, exist_ok=False)
    write_csv(out / 'existing_metadata_deltas.csv', metadata_deltas,
              ['name', 'master_population', 'v4_population', 'master_city', 'v4_city', 'action'])
    for label, towns in [('master', master), ('v4', v4)]:
        rows = spacing(towns)
        write_csv(out / f'{label}_nearest_neighbours.csv', rows, list(rows[0]))
        pairs = []
        for a, b in itertools.combinations(towns, 2):
            d = distance(a, b)
            if d <= 30:
                pairs.append(dict(town_a=a['name'], town_b=b['name'],
                                  distance_tiles=round(d, 6), spacing_band=band(d),
                                  decision='NONE: correct geography before spacing decisions'))
        write_csv(out / f'{label}_close_pairs.csv', pairs,
                  ['town_a', 'town_b', 'distance_tiles', 'spacing_band', 'decision'])
    baseline = {key(t['name']) for t in v4}
    anchors = {key(t['name']) for t in v2}
    rows = []
    for t in master:
        r = inv.get(key(t['name']), {})
        issue = ''
        if not r:
            issue = 'No matching row in draft inventory; geographic identity and coordinates require sourcing'
        elif t['name'] == 'BRANDENBURG':
            issue = 'Source 52.5N 13.5E is near Berlin; verify identity and coordinates for Brandenburg an der Havel before fitting'
        elif t['name'] == 'BOULOGNE':
            issue = 'Source 48.83333N 2.25E indicates Paris suburb; historical identity versus Boulogne-sur-Mer unresolved'
        elif t['name'] in ('GREENWICH', 'VERSAILLES'):
            issue = 'Previously deferred for spacing; recalculate after geographic correction'
        rows.append(dict(id=r.get('id', ''), name=t['name'], region=r.get('region', ''),
                         latitude=r.get('latitude', ''), longitude=r.get('longitude', ''),
                         in_v4=key(t['name']) in baseline,
                         prior_evidence='V2 provisional visual acceptance' if key(t['name']) in anchors else 'unverified',
                         land_status='UNKNOWN: original heightmap missing',
                         release_status='WITHHELD_PENDING_GEOGRAPHY',
                         spacing_decision='NOT_MADE', issue=issue))
    write_csv(out / 'catalogue_review.csv', rows, list(rows[0]))
    summary = dict(status='BLOCKED_MISSING_RASTER_AND_IMPORT_MAPPING',
                   master_towns=len(master), v4_towns=len(v4),
                   geographically_validated=0, coordinates_corrected=0,
                   existing_v4_metadata_discrepancies=len(metadata_deltas),
                   master_names_missing_from_inventory=missing_inventory,
                   inventory_names_absent_from_master=inventory_only,
                   withheld_from_new_release=len(master), new_spacing_deferrals=0,
                   v4_minimum_spacing_tiles=min(r['distance_tiles'] for r in spacing(v4)),
                   inputs={str(p.relative_to(ROOT)): digest(p) for p in (MASTER, INVENTORY, V4, V2)},
                   missing=['original heightmap raster and provenance',
                            'target-version importer mapping, heightmap rotation and generation settings',
                            'independently identified fit and holdout landmarks'],
                   note='No new import emitted; original catalogue and V2/V3/V4 remain unchanged. Withheld is not a spacing deletion.')
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    return summary


def fit_controls(path, max_error):
    """Diagnostic affine lon/lat -> source pixels, with independent holdouts.

    Does not claim the raster has an affine geographical projection.
    Controls CSV: name,longitude,latitude,column,row,role,evidence.
    """
    import numpy as np
    if not math.isfinite(max_error) or max_error <= 0:
        raise ValueError('max-error must be finite and positive')
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    names = set()
    for r in rows:
        if key(r['name']) in names or not r['evidence'].strip() or r['role'] not in ('fit', 'holdout'):
            raise ValueError('Controls require unique names, evidence and fit/holdout role')
        names.add(key(r['name']))
        for k in ('longitude', 'latitude', 'column', 'row'):
            r[k] = float(r[k])
            if not math.isfinite(r[k]):
                raise ValueError('Nonfinite control')
        if not -180 <= r['longitude'] <= 180 or not -90 <= r['latitude'] <= 90:
            raise ValueError('Invalid geographic control')
    training = [r for r in rows if r['role'] == 'fit']
    holdouts = [r for r in rows if r['role'] == 'holdout']
    if len(training) < 3 or len(holdouts) < 3:
        raise ValueError('Need >=3 fit and >=3 independent holdout controls; use 20+ holdouts for release review')
    fit_locations = {(r['longitude'], r['latitude']) for r in training}
    if any((r['longitude'], r['latitude']) in fit_locations for r in holdouts):
        raise ValueError('Holdout location reused in fit set')
    a = np.array([[r['longitude'], r['latitude'], 1] for r in training])
    b = np.array([[r['column'], r['row']] for r in training])
    coefficients, _, rank, singular = np.linalg.lstsq(a, b, rcond=None)
    if rank != 3:
        raise ValueError('Degenerate affine controls')
    errors = []
    for r in rows:
        prediction = np.array([r['longitude'], r['latitude'], 1]) @ coefficients
        errors.append(dict(name=r['name'], role=r['role'],
                           error_pixels=float(np.linalg.norm(prediction - [r['column'], r['row']]))))
    held = [r['error_pixels'] for r in errors if r['role'] == 'holdout']
    return dict(model='diagnostic_affine_lon_lat_to_source_pixels',
                coefficients=coefficients.tolist(), controls_sha256=digest(path),
                holdout_count=len(held), holdout_median_pixels=float(np.median(held)),
                holdout_max_pixels=max(held), requested_max_error_pixels=max_error,
                holdout_threshold_passed=max(held) <= max_error,
                release_validated=False, residuals=errors,
                note='Threshold pass is diagnostic only. Confirm projection, independent evidence, regional coverage and importer mapping before use.')


def game_to_pixel(x, y, width, height, matrix):
    """Explicit externally verified affine normalized-game -> normalized-raster mapping.

    No default axis swap, flip, scaling or pixel convention is inferred.
    Matrix operates on [x,y,1]; output normalized raster endpoints map to [0,W-1].
    """
    if len(matrix) != 2 or any(len(row) != 3 for row in matrix):
        raise ValueError('Mapping must be 2x3')
    if any(type(v) not in (int, float) or not math.isfinite(v) for row in matrix for v in row):
        raise ValueError('Invalid mapping coefficients')
    a, b = matrix
    if abs(a[0]*b[1] - a[1]*b[0]) < 1e-12:
        raise ValueError('Singular mapping')
    u, v = [row[0]*x + row[1]*y + row[2] for row in matrix]
    if not 0 <= u <= 1 or not 0 <= v <= 1:
        raise ValueError('Mapped point outside raster')
    return round(u*(width-1)), round(v*(height-1))


def terrain(towns_path, raster_path, manifest_path, out):
    from PIL import Image
    towns = read_json(towns_path)
    validate(towns)
    m = read_json(manifest_path)
    if not m.get('mapping_evidence', '').strip():
        raise ValueError('Mapping evidence required')
    if m['raster_sha256'] != digest(raster_path):
        raise ValueError('Raster hash mismatch')
    if m['pixel_convention'] != 'normalized_endpoints_nearest':
        raise ValueError('Unsupported pixel convention; verify importer before using')
    threshold = m['zero_elevation_threshold']
    if type(threshold) is not int or not 0 <= threshold <= 65535:
        raise ValueError('Invalid zero-elevation threshold')
    with Image.open(raster_path) as im:
        im.load()
        if list(im.size) != m['raster_dimensions']:
            raise ValueError('Raster dimensions mismatch')
        if im.mode not in ('L', 'I;16', 'I', 'RGB', 'RGBA'):
            raise ValueError('Unsupported elevation mode; do not silently convert')
        rows = []
        for t in towns:
            col, row = game_to_pixel(t['x'], t['y'], *im.size, m['game_to_raster_matrix'])
            value = im.getpixel((col, row))
            if isinstance(value, tuple):
                if len(set(value[:3])) != 1 or (len(value) == 4 and value[3] != 255):
                    raise ValueError('Town pixel is not opaque grayscale')
                value = value[0]
            rows.append(dict(name=t['name'], column=col, row=row, raw_elevation=value,
                             raster_status='ZERO_OR_LOW_REVIEW' if value <= threshold else 'NONZERO_REVIEW',
                             land_status='UNVERIFIED_IN_GAME'))
    # Elevation is not a sea mask; no automatic land claim or relocation.
    write_csv(Path(out), rows, list(rows[0]))
    return dict(sampled=len(rows), land_validated=0)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('audit')
    a.add_argument('--out', type=Path, required=True)
    a = sub.add_parser('fit')
    a.add_argument('--controls', required=True)
    a.add_argument('--max-error-pixels', type=float, required=True)
    a.add_argument('--out', type=Path, required=True)
    a = sub.add_parser('terrain')
    a.add_argument('--towns', required=True)
    a.add_argument('--raster', required=True)
    a.add_argument('--manifest', required=True)
    a.add_argument('--out', required=True)
    args = p.parse_args()
    try:
        if args.command == 'audit':
            result = audit(args.out)
        elif args.command == 'fit':
            result = fit_controls(args.controls, args.max_error_pixels)
            with args.out.open('x', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                f.write('\n')
        else:
            result = terrain(args.towns, args.raster, args.manifest, args.out)
    except (ValueError, KeyError, OSError) as e:
        p.exit(2, str(e) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
