#!/usr/bin/env python3
"""Reproduce V6 coastline calibration and conservative regional candidate.

Uses read-only source assets. Emits a new directory; does not alter originals.
Coast distances are normal residuals, not true town positional accuracy.
"""
import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import scipy
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, binary_propagation, distance_transform_edt, map_coordinates, label
from scipy.optimize import least_squares

import geography as g
from scenario_geography import import_target, read_terrain, source_pixel

COAST = g.ROOT / 'data/geography/ne_50m_europe_coastline.geojson'
OVERRIDES = g.ROOT / 'data/geography/regional_coordinate_overrides.csv'
HASHES = {
    'heightmaps/Europe_heightmap_original.png': 'beb1760c157e72f90b87713cc7a88b7455d47e235f91fe54a11de663c541d744',
    'scenarios/Europe_1800_Industries_Original.scn': 'b49bda4d118dc7037441e9e0661543f1d1ea06e13349b7d1517f7ca39c9044db',
    'scenarios/Europe_1800_V1.scn': '904097ebfda8db35b6f58f27e07aad1bf0595805ea6c8196245b7f9b68f29f3e',
}


def save_json(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def coastline_samples():
    lines = [np.array(f['geometry']['coordinates']) for f in g.read_json(COAST)['features']]
    pts = np.concatenate(lines)
    # Keep the first vertex in each 0.05-degree longitude / 1/30-degree latitude bin.
    # This prevents dense fjords dominating the fit. Preserve source ordering.
    _, index = np.unique(np.round(pts * [20, 30]).astype(int), axis=0, return_index=True)
    pts = pts[np.sort(index)]
    mask = (pts[:, 0] > -11) & (pts[:, 0] < 25) & (pts[:, 1] > 35.5) & (pts[:, 1] < 58.5)
    pts = pts[mask]
    # Entire 2-degree geographic cells are withheld, not random neighbouring vertices.
    holdout = (np.floor(pts[:, 0]/2).astype(int) + 2*np.floor(pts[:, 1]/2).astype(int)) % 4 == 0
    return pts, holdout


def coast_distance_field(raw):
    water = raw == 0
    seed = np.zeros_like(water)
    seed[0, :] = water[0, :]
    seed[-1, :] = water[-1, :]
    seed[:, 0] = water[:, 0]
    seed[:, -1] = water[:, -1]
    ocean = binary_propagation(seed, mask=water)
    coast = ocean & ~binary_erosion(ocean)
    coast[:10, :] = coast[-10:, :] = False
    coast[:, :10] = coast[:, -10:] = False
    return distance_transform_edt(~coast)


def project(pts, coefficients, model='axis_affine'):
    geo = np.array(pts, dtype=float, copy=True)
    if model == 'mercator':
        geo[:, 1] = np.rad2deg(np.log(np.tan(np.pi/4 + np.deg2rad(geo[:, 1])/2)))
    if model == 'affine':
        return np.c_[geo, np.ones(len(geo))] @ np.array(coefficients).reshape(2, 3).T
    a, b, c, d = coefficients
    return np.c_[a*geo[:, 0]+b, c*geo[:, 1]+d]


def fit_coast(raw):
    pts, holdout = coastline_samples()
    dt = coast_distance_field(raw)
    models = {}
    for model, initial in [('axis_affine', [104, 1400, -167, 9920]),
                           ('affine', [104, 0, 1400, 0, -167, 9920]),
                           ('mercator', [104, 1400, -110, 8600])]:
        def residual(parameters):
            predicted = project(pts, parameters, model)
            return map_coordinates(dt, [predicted[:, 1], predicted[:, 0]],
                                   order=1, mode='constant', cval=200)
        result = least_squares(lambda p: residual(p)[~holdout], initial,
                               diff_step=1e-4, loss='soft_l1', f_scale=4, max_nfev=1000)
        if not result.success:
            raise ValueError(f'{model} optimizer failed: {result.message}')
        errors = residual(result.x)
        held = errors[holdout]
        models[model] = dict(coefficients=result.x.tolist(),
                             fit_samples=int(sum(~holdout)), holdout_samples=int(sum(holdout)),
                             holdout_median_coast_distance_pixels=float(np.median(held)),
                             holdout_p90_coast_distance_pixels=float(np.percentile(held, 90)),
                             holdout_max_coast_distance_pixels=float(max(held)))
    # Use the simplest well-performing model; do not fit towns or V2 anchors.
    chosen = models['axis_affine']
    if chosen['holdout_p90_coast_distance_pixels'] > 12 or chosen['holdout_median_coast_distance_pixels'] > 4:
        raise ValueError('Coastline diagnostics deteriorated; do not generate candidate')
    predicted = project(pts, chosen['coefficients'])
    errors = map_coordinates(dt, [predicted[:, 1], predicted[:, 0]], order=1, mode='constant', cval=200)
    controls = [dict(longitude=float(pt[0]), latitude=float(pt[1]),
                     role='holdout' if held else 'fit', predicted_column=float(pp[0]),
                     predicted_row=float(pp[1]), coast_normal_distance_pixels=float(error))
                for pt, held, pp, error in zip(pts, holdout, predicted, errors)]
    return models, controls


def orientation(raw, tile_types, heights):
    results = []
    # Compare all eight square symmetries. Rows of save arrays are game Y.
    for transpose in (False, True):
        for flip_rows in (False, True):
            for flip_columns in (False, True):
                a = raw.T if transpose else raw
                if flip_rows:
                    a = a[::-1, :]
                if flip_columns:
                    a = a[:, ::-1]
                s = np.s_[4:-4:8, 4:-4:8]
                results.append(dict(transpose=transpose, flip_rows=flip_rows, flip_columns=flip_columns,
                                    sampled_height_correlation=float(np.corrcoef(a[s].ravel(), heights[s].ravel())[0, 1]),
                                    sampled_zero_water_agreement=float(np.mean((a[s] == 0) == (tile_types[s] == 6)))))
    best = max(results, key=lambda r: r['sampled_height_correlation'])
    if (best['transpose'], best['flip_rows'], best['flip_columns']) != (False, False, True) or best['sampled_height_correlation'] < .98:
        raise ValueError('Scenario orientation no longer matches proven counter-clockwise layout')
    return results


def run(assets, out):
    if out.exists():
        raise FileExistsError('Output directory already exists: ' + str(out))
    # Validate every required input before creating output.
    for path, expected in HASHES.items():
        if g.digest(assets/path) != expected:
            raise ValueError('Source asset hash mismatch: ' + path)
    with Image.open(assets/'heightmaps/Europe_heightmap_original.png') as image:
        if image.size != (4096, 4096) or image.mode != 'RGBA':
            raise ValueError('Unexpected original raster dimensions or mode')
        rgba = np.array(image)
    # Target JGR code uses channel 0 for four-channel PNGs, NOT luminance conversion.
    raw = rgba[:, :, 0]
    components, _ = label(raw > 0)
    # Raster-only landmass seeds, visually checked on the uploaded coastline;
    # not geodetic controls and not used in fitting.
    landmasses = {int(components[970, 725]): 'Ireland',
                  int(components[1117, 1181]): 'Great Britain',
                  int(components[1712, 1625]): 'continental Europe'}
    models, controls = fit_coast(raw)
    types, heights = read_terrain(assets/'scenarios/Europe_1800_V1.scn')
    industry_types, industry_heights = read_terrain(assets/'scenarios/Europe_1800_Industries_Original.scn')
    orientations = dict(v1=orientation(raw, types, heights),
                        industries_original=orientation(raw, industry_types, industry_heights))
    coefficients = models['axis_affine']['coefficients']
    master = g.read_json(g.MASTER)
    v4 = g.read_json(g.V4)
    g.validate(master)
    inv = g.inventory()
    with OVERRIDES.open(encoding='utf-8', newline='') as f:
        overrides = {g.key(r['name']): r for r in csv.DictReader(f)}
    regional = {g.key(t['name']) for t in v4} | {g.key(n) for n in ['GREENWICH', 'VERSAILLES', 'BOULOGNE']}
    rows, retained, old_audit = [], [], []
    for town in v4:
        tx, ty = import_target(town['x'], town['y'])
        col, row = source_pixel(town['x'], town['y'])
        old_audit.append(dict(name=town['name'], source_column=col, source_row=row,
                              raw_elevation=int(raw[row, col]), v1_tile_type=int(types[ty, tx]),
                              original_industries_tile_type=int(industry_types[ty, tx]),
                              approximate_longitude_from_coast_model=float((col-coefficients[1])/coefficients[0]),
                              approximate_latitude_from_coast_model=float((row-coefficients[3])/coefficients[2]),
                              landmass=landmasses.get(int(components[row, col]), 'other island or zero elevation'),
                              geography_status='Land alone does not validate geographic location'))
    for t in master:
        name = g.key(t['name'])
        geo = overrides.get(name, inv.get(name))
        r = dict(name=t['name'], regional=name in regional, latitude='', longitude='',
                 coordinate_source='draft inventory; not individually verified',
                 projected_column='', projected_row='', x='', y='', target_tile_x='', target_tile_y='',
                 raw_elevation='', v1_tile_type='', original_industries_tile_type='', landmass='',
                 v4_shift_tiles='', decision='DEFERRED', reason='')
        if not geo:
            r['reason'] = 'Missing geographic companion row; do not join by row number'
        else:
            lat, lon = float(geo['latitude']), float(geo['longitude'])
            if not math.isfinite(lat+lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                raise ValueError('Invalid geographic coordinate: ' + t['name'])
            r.update(latitude=lat, longitude=lon)
            if name in overrides:
                r['coordinate_source'] = overrides[name]['source']
            col, row = project([[lon, lat]], coefficients)[0]
            r.update(projected_column=float(col), projected_row=float(row))
            if not (1 < col < 4094 and 1 < row < 4094):
                r['reason'] = 'Outside fitted raster bounds; near-boundary uncertainty requires review; never clamp'
            else:
                candidate = dict(t, x=round(float(row/4095), 9), y=round(float(col/4095), 9))
                tx, ty = import_target(candidate['x'], candidate['y'])
                pc, pr = source_pixel(candidate['x'], candidate['y'])
                r.update(x=candidate['x'], y=candidate['y'], target_tile_x=tx, target_tile_y=ty,
                         raw_elevation=int(raw[pr, pc]), v1_tile_type=int(types[ty, tx]),
                         original_industries_tile_type=int(industry_types[ty, tx]),
                         landmass=landmasses.get(int(components[pr, pc]), 'other island or zero elevation'))
                region = inv.get(name, {}).get('region', '')
                expected_landmass = ('Great Britain' if region == 'England and Wales' else
                                     'Ireland' if region == 'Ireland' else
                                     'continental Europe' if region in ('France', 'Germany') else '')
                old = next((u for u in v4 if g.key(u['name']) == name), None)
                if old:
                    r['v4_shift_tiles'] = round(g.distance(candidate, old), 3)
                if name == g.key('BOULOGNE'):
                    r['reason'] = 'Historical evidence favours Boulogne-sur-Mer; draft coordinates are Paris suburb; identity join unresolved'
                elif name == g.key('GREENWICH'):
                    r['reason'] = 'Prior spacing deferral; source town-centre coordinate also needs correction; preserve separate historical review'
                elif name == g.key('VERSAILLES'):
                    r['reason'] = 'Prior spacing deferral near Paris; historical court merits individual spacing review after in-game test'
                elif name not in regional:
                    r['reason'] = 'Europe-wide projection diagnostic only; outside current regional review scope'
                elif min(col, row, 4095-col, 4095-row) < 90:
                    r['reason'] = 'Near raster boundary within worst coastal residual; manual geographic review'
                elif expected_landmass and r['landmass'] != expected_landmass:
                    r['reason'] = 'Expected landmass mismatch; review geographic identity and coastline'
                elif raw[pr, pc] == 0:
                    r['reason'] = 'Zero original elevation at target; inspect coast or lowland; no automatic snapping'
                elif types[ty, tx] in (6, 7) or industry_types[ty, tx] in (6, 7):
                    r['reason'] = 'Water or void in a saved scenario at corrected target; inspect river/harbour bank and founding search'
                elif types[ty, tx] != 0 or industry_types[ty, tx] != 0:
                    r['reason'] = 'Occupied saved-scenario tile; inspect in a fresh empty test map'
                else:
                    r.update(decision='RETAINED_TEST_ONLY', reason='Corrected regional model target; nonzero raster and clear land in both saved scenarios; in-game test pending')
                    retained.append(candidate)
        rows.append(r)
    # Current regional targets all clear the spacing guideline. If future outputs
    # do not, stop instead of choosing importance or deleting historical towns.
    if any(g.distance(a, b) <= 30 for i, a in enumerate(retained) for b in retained[i+1:]):
        raise ValueError('Corrected regional spacing needs individual review before emitting import')
    g.validate(retained)
    out.mkdir(parents=True, exist_ok=False)
    save_json(out/'Europe_1800_V6_REGIONAL_GEOGRAPHIC_TEST.json', retained)
    save_json(out/'coastline_models.json', models)
    save_json(out/'scenario_orientation.json', orientations)
    g.write_csv(out/'coastline_fit_holdouts.csv', controls, list(controls[0]))
    g.write_csv(out/'catalogue_projection_review.csv', rows, list(rows[0]))
    regional_rows = [r for r in rows if r['regional']]
    g.write_csv(out/'regional_validation.csv', regional_rows, list(rows[0]))
    deferred = [r for r in regional_rows if r['decision'] == 'DEFERRED']
    g.write_csv(out/'regional_deferred.csv', deferred, list(rows[0]))
    g.write_csv(out/'v4_actual_terrain.csv', old_audit, list(old_audit[0]))
    nearest = g.spacing(retained)
    for r in nearest:
        r['coordinate_status'] = 'COASTLINE_MODEL_TEST_ONLY; target terrain checked; founding not tested'
    g.write_csv(out/'regional_spacing.csv', nearest, list(nearest[0]))
    # Full regional comparison, including existing omissions, with no silent disappearance.
    projected = [dict(name=r['name'], x=r['x'], y=r['y']) for r in regional_rows if r['x'] != '']
    projected_nearest = g.spacing(projected)
    g.write_csv(out/'regional_all_projected_spacing.csv', projected_nearest, list(projected_nearest[0]))
    summary = dict(status='EXPERIMENTAL_REGIONAL_CANDIDATE; not an in-game validated release',
                   original_assets_sha256=HASHES, master_sha256=g.digest(g.MASTER),
                   inventory_sha256=g.digest(g.INVENTORY), coastline_sha256=g.digest(COAST),
                   overrides_sha256=g.digest(OVERRIDES), regional_reviewed=len(regional_rows),
                   retained_and_corrected=len(retained), regional_deferred=len(deferred),
                   catalogue_projection_rows=len(rows), in_game_validated=0,
                   independently_surveyed_town_positions=0,
                   minimum_retained_spacing_tiles=min(r['distance_tiles'] for r in nearest),
                   libraries=dict(numpy=np.__version__, scipy=scipy.__version__),
                   approximate_bounds=dict(west=-coefficients[1]/coefficients[0],
                                           east=(4095-coefficients[1])/coefficients[0],
                                           north=-coefficients[3]/coefficients[2],
                                           south=(4095-coefficients[3])/coefficients[2]),
                   warning='Coastal normal residual is not 2D town accuracy. Coastline source generalized; town coordinates still need local review. No full Europe import emitted.')
    save_json(out/'summary.json', summary)
    # Geographic overlay is a review artifact, not an edited source heightmap.
    preview = Image.fromarray(raw).resize((1024, 1024)).convert('RGB')
    draw = ImageDraw.Draw(preview)
    for c in controls:
        u, v = c['predicted_column']/4, c['predicted_row']/4
        draw.point((u, v), fill='cyan' if c['role'] == 'holdout' else 'red')
    for r in regional_rows:
        if r['x'] != '':
            u, v = r['projected_column']/4, r['projected_row']/4
            color = 'lime' if r['decision'] == 'RETAINED_TEST_ONLY' else 'orange'
            draw.ellipse((u-2, v-2, u+2, v+2), outline=color)
            draw.text((u+3, v), r['name'], fill=color)
    preview.save(out/'regional_coastline_overlay.png')
    # Confirm all supplied originals still have their initial hashes after analysis.
    for path, expected in HASHES.items():
        if g.digest(assets/path) != expected:
            raise ValueError('Unexpected source mutation: ' + path)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, required=True, help='Extracted original source archive')
    parser.add_argument('--out', type=Path, required=True, help='New output directory only')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.assets, args.out), indent=2))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, str(error) + '\n')
