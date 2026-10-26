#!/usr/bin/env python3
"""Reproducible V8 desk review; no game launch, scenario write or automatic snapping.

Pair recommendations and source-coordinate corrections are explicit reviewed inputs,
not decisions inferred from a population sort or a hard-coded desired town count.
"""
import argparse
import collections
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_propagation

import geography as g
from calibrate_heightmap import HASHES, project, save_json
from scenario_geography import import_target, source_pixel, read_terrain

V7 = g.ROOT/'maps/calibration/geography_v7'
EVIDENCE = g.ROOT/'data/geography'
CHECKS = EVIDENCE/'coordinate_checks_v8.csv'
CORRECTIONS = EVIDENCE/'coordinate_overrides_v8.csv'
POLICY = EVIDENCE/'spacing_decisions_v8.csv'
DEFERRALS = EVIDENCE/'town_deferrals_v8.csv'
SOURCES = EVIDENCE/'review_sources_v8.csv'
MODEL = g.ROOT/'maps/calibration/geography_v6/coastline_models.json'
FULL_FILE = 'Europe_1800_V8_CORRECTED_ALL_IN_BOUNDS_TEST.json'
CORE_FILE = 'Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json'


def rows(path):
    with Path(path).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def pair_key(a, b):
    return tuple(sorted((a, b)))


def km_distance(lat, lon, lat2, lon2):
    lat, lon, lat2, lon2 = map(math.radians, (lat, lon, lat2, lon2))
    a = math.sin((lat-lat2)/2)**2 + math.cos(lat)*math.cos(lat2)*math.sin((lon-lon2)/2)**2
    return 6371.0088*2*math.asin(min(1, math.sqrt(a)))


def close_pairs(towns):
    return {pair_key(a['name'], b['name']): g.distance(a, b)
            for a, b in itertools.combinations(towns, 2) if g.distance(a, b) <= 30}


def checked_policy(original, corrected):
    sources = {r['id']: r for r in rows(SOURCES)}
    policies = {}
    deferred = {}
    for r in rows(POLICY):
        k = pair_key(r['town_a'], r['town_b'])
        if k in policies:
            raise ValueError('Duplicate pair decision')
        if not r['reason'].strip() or any(s not in sources for s in r['evidence_ids'].split(';')):
            raise ValueError('Missing reason or unknown evidence')
        if r['recommendation'] not in ('RETAIN_BOTH', 'DEFER_A', 'DEFER_B', 'DEFER_BOTH', 'NO_LONGER_CLOSE'):
            raise ValueError('Unknown recommendation')
        policies[k] = r
        names = []
        if r['recommendation'] in ('DEFER_A', 'DEFER_BOTH'):
            names.append(r['town_a'])
        if r['recommendation'] in ('DEFER_B', 'DEFER_BOTH'):
            names.append(r['town_b'])
        for name in names:
            deferred.setdefault(name, []).append(r['reason'])
    old, new = close_pairs(original), close_pairs(corrected)
    if set(policies) != set(old) | set(new):
        raise ValueError(f'Every old/new close pair needs explicit review; missing={(set(old)|set(new))-set(policies)}')
    for k, policy in policies.items():
        a, b = policy['town_a'], policy['town_b']
        if policy['recommendation'] == 'RETAIN_BOTH' and (a in deferred or b in deferred):
            raise ValueError('Contradictory pair recommendations: ' + str(k))
        if policy['recommendation'] == 'NO_LONGER_CLOSE' and k in new:
            raise ValueError('Claimed resolved pair is still close')
    return policies, deferred, old, new


def terrain_patch(tx, ty, types, height, industry_types, industry_height):
    x0, x1 = max(1, tx-16), min(4093, tx+16)
    y0, y1 = max(1, ty-16), min(4093, ty+16)
    clear = ((types[y0:y1+1, x0:x1+1] == 0) &
             (industry_types[y0:y1+1, x0:x1+1] == 0))
    flat = np.ones_like(clear)
    for heights in (height, industry_height):
        h = heights[y0:y1+1, x0:x1+1]
        flat &= ((h == heights[y0+1:y1+2, x0:x1+1]) &
                 (h == heights[y0:y1+1, x0+1:x1+2]) &
                 (h == heights[y0+1:y1+2, x0+1:x1+2]))
    yy, xx = np.nonzero(clear & flat)
    nearest = min(np.hypot(xx+x0-tx, yy+y0-ty), default=None)
    return len(xx), None if nearest is None else float(nearest)


def generate(assets, out):
    if out.exists():
        raise FileExistsError('Use a new output directory')
    for path, sha in HASHES.items():
        if g.digest(assets/path) != sha:
            raise ValueError('Original source asset mismatch: ' + path)
    original = g.read_json(V7/'Europe_1800_V7_ALL_IN_BOUNDS_TEST.json')
    master = g.read_json(g.MASTER)
    master_by_name = {t['name']: t for t in master}
    for t in original:
        source = master_by_name[t['name']]
        if (t['population'], t['city']) != (source['population'], source['city']):
            raise ValueError('Input metadata differs from preserved master: ' + t['name'])
    audit = {r['name']: r for r in rows(V7/'all_600_placement_audit.csv')}
    corrected = [dict(t) for t in original]
    by_name = {t['name']: t for t in corrected}
    coefficients = g.read_json(MODEL)['axis_affine']['coefficients']
    correction_rows = []
    for r in rows(CORRECTIONS):
        t = by_name[r['name']]
        lat, lon = float(r['latitude']), float(r['longitude'])
        col, row = project([[lon, lat]], coefficients)[0]
        x, y = round(float(row/4095), 9), round(float(col/4095), 9)
        correction_rows.append(dict(name=t['name'], old_latitude=audit[t['name']]['latitude'],
                                    old_longitude=audit[t['name']]['longitude'], new_latitude=lat,
                                    new_longitude=lon, old_x=t['x'], old_y=t['y'], new_x=x, new_y=y,
                                    shift_tiles=round(g.SIZE*math.hypot(t['x']-x, t['y']-y), 6),
                                    source=r['source'], reason=r['reason']))
        t.update(x=x, y=y)
    g.validate(corrected)
    policies, spaced_out, old_pairs, new_pairs = checked_policy(original, corrected)
    extra = {r['name']: r for r in rows(DEFERRALS)}
    if set(extra) - set(by_name):
        raise ValueError('Unknown town-level deferral')
    deferred_names = set(spaced_out) | set(extra)
    retained = [t for t in corrected if t['name'] not in deferred_names]
    if any(g.distance(a, b) < 15 for a, b in itertools.combinations(retained, 2)):
        raise ValueError('Unresolved sub-15 pair in the desk candidate')
    g.validate(retained)
    correction_geo = {r['name']: (r['new_latitude'], r['new_longitude']) for r in correction_rows}
    reference_checks = []
    for r in rows(CHECKS):
        name = r['name']; old_geo = audit[name]
        lat, lon = float(old_geo['latitude']), float(old_geo['longitude'])
        lat2, lon2 = float(r['latitude']), float(r['longitude'])
        after_lat, after_lon = correction_geo.get(name, (lat, lon))
        before = km_distance(lat, lon, lat2, lon2)
        after = km_distance(after_lat, after_lon, lat2, lon2)
        reference_checks.append(dict(r, prior_difference_km=round(before, 4),
                                      current_difference_km=round(after, 4),
                                      status='AMBIGUOUS_LABEL_ALTERNATIVES' if name in extra else
                                      'SOURCE_CORRECTED' if name in correction_geo else
                                      'WITHIN_3KM_REFERENCE' if after <= 3 else 'SOURCE_REVIEW_REQUIRED'))
    pair_report = []
    for k, r in policies.items():
        a, b = by_name[r['town_a']], by_name[r['town_b']]
        d = g.distance(a, b)
        alat, alon = correction_geo.get(a['name'], (float(audit[a['name']]['latitude']), float(audit[a['name']]['longitude'])))
        blat, blon = correction_geo.get(b['name'], (float(audit[b['name']]['latitude']), float(audit[b['name']]['longitude'])))
        ax, ay = import_target(a['x'], a['y']); bx, by = import_target(b['x'], b['y'])
        pair_report.append(dict(r, v7_distance_tiles=round(old_pairs[k], 6) if k in old_pairs else '',
                                corrected_distance_tiles=round(d, 6), corrected_band=g.band(d),
                                approx_source_distance_km=round(km_distance(alat, alon, blat, blon), 4),
                                near_policy_boundary=min(abs(d-15), abs(d-30)) <= 2,
                                actual_target_distance_tiles=round(math.hypot(ax-bx, ay-by), 6),
                                new_pair_after_correction=k not in old_pairs,
                                both_in_candidate=a['name'] not in deferred_names and b['name'] not in deferred_names,
                                judgement_status='DESK_RECOMMENDATION; not user-approved final layout'))
    with Image.open(assets/'heightmaps/Europe_heightmap_original.png') as im:
        raw = np.array(im)[:, :, 0]
    water = raw == 0
    seed = np.zeros_like(water)
    seed[0, :], seed[-1, :], seed[:, 0], seed[:, -1] = water[0, :], water[-1, :], water[:, 0], water[:, -1]
    ocean = binary_propagation(seed, mask=water)
    types, heights = read_terrain(assets/'scenarios/Europe_1800_V1.scn')
    itypes, iheights = read_terrain(assets/'scenarios/Europe_1800_Industries_Original.scn')
    sampled = {}
    for t in corrected:
        tx, ty = import_target(t['x'], t['y']); col, row = source_pixel(t['x'], t['y'])
        sampled[t['name']] = dict(raw_elevation=int(raw[row, col]),
                                  v1_tile_type=int(types[ty, tx]), industries_tile_type=int(itypes[ty, tx]),
                                  direct_clear_land=bool(raw[row, col] > 0 and types[ty, tx] == 0 and itypes[ty, tx] == 0))
    review_names = {r['name'] for r in rows(V7/'terrain_review.csv')}
    review_names |= {name for name, sample in sampled.items() if not sample['direct_clear_land']}
    terrain = []
    for t in corrected:
        if t['name'] not in review_names:
            continue
        tx, ty = import_target(t['x'], t['y']); col, row = source_pixel(t['x'], t['y'])
        a, b, elevation = int(types[ty, tx]), int(itypes[ty, tx]), int(raw[row, col])
        if a == 2 or b == 2:
            category = 'SAVED_ROAD_OCCUPANCY'
            interpretation = 'Source raster is nonzero; saved road/tram occupancy is not a coast error. A fresh empty map may differ.'
        elif elevation == 0 and ocean[row, col] and (a == 6 or b == 6):
            category = 'SOURCE_ZERO_OCEAN_CONNECTED'
            interpretation = 'Zero source pixel connected to the raster edge and saved water: inspect coastline or harbour before moving any target.'
        elif elevation > 0 and (a == 6 or b == 6):
            category = 'SAVED_WATER_OVER_NONZERO_SOURCE'
            interpretation = 'Saved water over a nonzero source pixel; compatible with an inland/generated channel but channel identity is not independently confirmed.'
        else:
            category = 'OTHER_REVIEW'
            interpretation = 'Water/terrain interpretation needs manual verification.'
        count, distance = terrain_patch(tx, ty, types, heights, itypes, iheights)
        terrain.append(dict(name=t['name'], category=category, source_column=col, source_row=row,
                            raw_elevation=elevation, v1_tile_type=a, industries_tile_type=b,
                            source_ocean_connected=bool(ocean[row, col]),
                            common_clear_flat_pixels_in_33_square=count,
                            nearest_clear_flat_distance_tiles='' if distance is None else round(distance, 6),
                            in_candidate=t['name'] not in deferred_names,
                            interpretation=interpretation,
                            next_action='Resolve combined Modica/Pozzallo identity first' if t['name'] in extra else
                            'Historical exception retained in documentation; optional later reinstatement' if t['name'] in spaced_out else
                            'Inspect historically appropriate location; do not auto-snap. Founding is not established.'))
    # Complete 600-row accounting includes original map-boundary deferrals.
    all_rows = []
    for town in master:
        name = town['name']; prior = audit[name]
        if name not in by_name:
            state, reason = 'DEFERRED_OUTSIDE_MAP', prior['reason']
        elif name in extra:
            state, reason = 'DEFERRED_IDENTITY', extra[name]['reason']
        elif name in spaced_out:
            state, reason = 'DEFERRED_SPACING', ' | '.join(dict.fromkeys(spaced_out[name]))
        else:
            state, reason = 'RETAINED_DESK_CANDIDATE', 'No sub-15 conflict; all corrected 15-30 pairs have explicit recommendations. Terrain/centre verification may remain open.'
        t = by_name.get(name)
        all_rows.append(dict(name=name, region=prior['region'], population=town['population'], city=town['city'],
                             state=state, reason=reason, x='' if not t else t['x'], y='' if not t else t['y'],
                             terrain_review_open=any(r['name'] == name for r in terrain),
                             boundary_review_open=prior['boundary_review'] == 'True',
                             input_coordinate_corrected=name in correction_geo,
                             **sampled.get(name, dict(raw_elevation='', v1_tile_type='', industries_tile_type='', direct_clear_land=''))))
    out.mkdir(parents=True)
    save_json(out/FULL_FILE, corrected)
    save_json(out/CORE_FILE, retained)
    outputs = [('coordinate_reference_audit.csv', reference_checks),
               ('coordinate_changes.csv', correction_rows), ('spacing_review.csv', pair_report),
               ('terrain_review_refined.csv', terrain), ('all_600_decisions.csv', all_rows),
               ('deferred_towns.csv', [r for r in all_rows if r['state'] != 'RETAINED_DESK_CANDIDATE']),
               ('historical_exceptions.csv', [r for r in pair_report if r['evidence_ids'] not in ('CATALOGUE', 'COORDINATES')])]
    for name, records in outputs:
        g.write_csv(out/name, records, list(records[0]))
    nearest = g.spacing(retained)
    for r in nearest:
        r['coordinate_status'] = 'DESK_REVIEWED_CANDIDATE; founding and exact centre not verified'
    g.write_csv(out/'candidate_nearest_neighbours.csv', nearest, list(nearest[0]))
    balance = []
    for region in sorted({r['region'] for r in all_rows}):
        group = [r for r in all_rows if r['region'] == region]
        balance.append(dict(region=region, master_entries=len(group),
                            retained=sum(r['state'] == 'RETAINED_DESK_CANDIDATE' for r in group),
                            spacing_deferred=sum(r['state'] == 'DEFERRED_SPACING' for r in group),
                            identity_deferred=sum(r['state'] == 'DEFERRED_IDENTITY' for r in group),
                            outside_map=sum(r['state'] == 'DEFERRED_OUTSIDE_MAP' for r in group)))
    g.write_csv(out/'regional_balance.csv', balance, list(balance[0]))
    summary = dict(status='DESK REVIEW ONLY; no game launched and no founding success claimed',
                   catalogue_entries=len(master), corrected_full_import=len(corrected),
                   candidate_towns=len(retained), spacing_deferred=len(spaced_out),
                   identity_deferred=len(extra), outside_map=sum(r['state'] == 'DEFERRED_OUTSIDE_MAP' for r in all_rows),
                   coordinate_inputs_corrected=len(correction_rows),
                   reference_comparisons=len(reference_checks), distinct_reference_towns=len({r['name'] for r in reference_checks}),
                   reference_checks_are_raster_holdouts=False,
                   original_close_pairs=len(old_pairs), corrected_close_pairs=len(new_pairs),
                   pair_decisions=len(pair_report), retained_close_pairs=len(close_pairs(retained)),
                   candidate_pairs_under_15=sum(d < 15 for d in close_pairs(retained).values()),
                   minimum_candidate_spacing_tiles=min(r['distance_tiles'] for r in nearest),
                   refined_terrain_categories=dict(collections.Counter(r['category'] for r in terrain)),
                   unresolved_terrain_in_candidate=sum(r['in_candidate'] for r in terrain),
                   in_game_tests=0, population_changes=0,
                   input_sha256={str(p.relative_to(g.ROOT)): g.digest(p) for p in
                                 [g.MASTER, MODEL, CHECKS, CORRECTIONS, POLICY, DEFERRALS, SOURCES,
                                  V7/'Europe_1800_V7_ALL_IN_BOUNDS_TEST.json', V7/'all_600_placement_audit.csv']},
                   original_assets_sha256=HASHES,
                   limitations='Modern gazetteer concordance is not survey-grade historic-centre or raster calibration proof. Clear-flat pixels are diagnostics only; no snapping or scenario edits occurred.')
    save_json(out/'summary.json', summary)
    # A compact contact sheet keeps each unresolved target inspectable without a game launch.
    sheet = Image.new('RGB', (8*180, math.ceil(len(terrain)/8)*198), '#0b1523')
    draw = ImageDraw.Draw(sheet)
    for i, r in enumerate(terrain):
        col, row = r['source_column'], r['source_row']
        crop = raw[row-40:row+40, col-40:col+40]
        if crop.shape != (80, 80):
            raise ValueError('Terrain review crop reaches image boundary')
        # Game Y stays image row; counter-clockwise game X is reflected image column.
        tile_crop = types[row-40:row+40, 4096-(col+40):4096-(col-40)][:, ::-1]
        level = np.clip(35+crop.astype(float)*2, 35, 205).astype('uint8')
        rgb = np.repeat(level[:, :, None], 3, axis=2)
        rgb[crop == 0] = [10, 22, 40]
        rgb[tile_crop == 6] = [32, 115, 180]
        rgb[tile_crop == 2] = [190, 130, 65]
        left, top = (i%8)*180, (i//8)*198
        sheet.paste(Image.fromarray(rgb).resize((160, 160), Image.Resampling.NEAREST), (left+10, top+22))
        draw.text((left+8, top+5), r['name'], fill='#e5edf3')
        draw.line((left+82, top+102, left+98, top+102), fill='#ff647f', width=2)
        draw.line((left+90, top+94, left+90, top+110), fill='#ff647f', width=2)
        draw.text((left+8, top+184), 'Retained; review open' if r['in_candidate'] else 'Deferred; documented', fill='#ffbd69')
    sheet.save(out/'terrain_review_contact_sheet.png')
    for path, sha in HASHES.items():
        if g.digest(assets/path) != sha:
            raise ValueError('Source asset changed')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, default=g.ROOT/'source_assets')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.assets, args.out), indent=2))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, str(error)+'\n')
