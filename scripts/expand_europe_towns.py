#!/usr/bin/env python3
"""Project every master settlement; never clamp an out-of-map town or snap to land.

ALL_IN_BOUNDS is the complete requested test batch, not a spacing-approved release.
TERRAIN_SCREENED is a separately labelled direct-target land subset.
"""
import argparse
import collections
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

import geography as g
from calibrate_heightmap import HASHES, project, save_json
from scenario_geography import import_target, read_terrain, source_pixel

MODEL = g.ROOT/'maps/calibration/geography_v6/coastline_models.json'
OVERRIDES = g.ROOT/'data/geography/europe_coordinate_overrides_v7.csv'
ALL_FILE = 'Europe_1800_V7_ALL_IN_BOUNDS_TEST.json'
LAND_FILE = 'Europe_1800_V7_TERRAIN_SCREENED_TEST.json'
# Broad geographic sanity boxes, not borders or independent location validation.
# These expose obvious homonym joins while tolerating historical region coverage.
REGION_BOUNDS = {
    'France': (41, 51.6, -5.5, 10), 'Germany': (47, 55.5, 5, 23),
    'Spain': (35, 44.5, -10, 5), 'Portugal': (36.8, 42.3, -10, -6),
    'England and Wales': (49.8, 55.9, -6, 2), 'Scotland': (54.5, 61, -9, 0),
    'Ireland': (51, 56, -11, -5), 'The Netherlands': (50.7, 54, 3, 8),
    'Belgium': (49.4, 51.6, 2, 7), 'Scandinavia': (54, 72, 4, 33),
    'Northern Italy': (43, 47, 6, 15), 'Southern Italy': (35, 43, 8, 19),
    'Central Italy': (41, 45, 8, 15), 'Switzerland': (45.7, 47.9, 5.8, 10.6),
}


def check_region(region, lat, lon):
    if region in REGION_BOUNDS:
        south, north, west, east = REGION_BOUNDS[region]
        if not (south <= lat <= north and west <= lon <= east):
            raise ValueError(f'Geographic source outside broad region bounds: {region}: {lat}, {lon}')


def export(assets, out):
    if out.exists():
        raise FileExistsError('Use a new output directory')
    for path, sha in HASHES.items():
        if g.digest(assets/path) != sha:
            raise ValueError('Original asset hash mismatch: ' + path)
    master = g.read_json(g.MASTER)
    g.validate(master)
    inv = g.inventory()
    with OVERRIDES.open(encoding='utf-8', newline='') as f:
        overrides = {g.key(r['name']): r for r in csv.DictReader(f)}
    models = g.read_json(MODEL)
    coefficients = models['axis_affine']['coefficients']
    with Image.open(assets/'heightmaps/Europe_heightmap_original.png') as im:
        if im.size != (4096, 4096) or im.mode != 'RGBA':
            raise ValueError('Unexpected source raster')
        raw = np.array(im)[:, :, 0]
    types, _ = read_terrain(assets/'scenarios/Europe_1800_V1.scn')
    industry_types, _ = read_terrain(assets/'scenarios/Europe_1800_Industries_Original.scn')
    all_towns, land_towns, rows = [], [], []
    for town in master:
        name = g.key(town['name'])
        geo = overrides.get(name, inv.get(name))
        if geo is None:
            raise ValueError('Unsourced geographic coordinate: ' + town['name'])
        lat, lon = float(geo['latitude']), float(geo['longitude'])
        if not math.isfinite(lat+lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError('Invalid geographic source: ' + town['name'])
        check_region(geo['region'], lat, lon)
        col, row = project([[lon, lat]], coefficients)[0]
        r = dict(name=town['name'], region=geo['region'], latitude=lat, longitude=lon,
                 geographic_source=geo.get('source', 'draft inventory; individually unverified'),
                 override_reason=geo.get('reason', ''), projected_column=float(col), projected_row=float(row),
                 x='', y='', tile_x='', tile_y='', sampled_column='', sampled_row='',
                 raw_elevation='', v1_tile_type='', industries_tile_type='',
                 direct_clear_land=False, nearby_clear_land_distance_tiles='',
                 terrain_status='NOT_SAMPLED', coverage_status='DEFERRED_OUTSIDE_MAP',
                 boundary_review=False, spacing_status='PENDING_PAIR_REVIEW', reason='')
        # Reject rather than clamp or fall back to the old unreliable positions.
        if not (0 < col/4095 < 1 and 0 < row/4095 < 1):
            r['reason'] = 'Outside calibrated raster footprint; map-edge uncertainty does not justify inventing an interior location'
        else:
            candidate = dict(town, x=round(float(row/4095), 9), y=round(float(col/4095), 9))
            g.validate([candidate])
            tx, ty = import_target(candidate['x'], candidate['y'])
            pc, pr = source_pixel(candidate['x'], candidate['y'])
            clear = bool(raw[pr, pc] > 0 and types[ty, tx] == 0 and industry_types[ty, tx] == 0)
            # Merely a terrain diagnostic: this is not an emulation of town founding,
            # its search order, slope rules, or spacing from other founded towns.
            x0, x1, y0, y1 = max(1, tx-16), min(4094, tx+16), max(1, ty-16), min(4094, ty+16)
            nearby = (types[y0:y1+1, x0:x1+1] == 0) & (industry_types[y0:y1+1, x0:x1+1] == 0)
            yy, xx = np.nonzero(nearby)
            nearest = float(np.min(np.hypot(xx+x0-tx, yy+y0-ty))) if len(xx) else ''
            r.update(x=candidate['x'], y=candidate['y'], tile_x=tx, tile_y=ty,
                     sampled_column=pc, sampled_row=pr, raw_elevation=int(raw[pr, pc]),
                     v1_tile_type=int(types[ty, tx]), industries_tile_type=int(industry_types[ty, tx]),
                     direct_clear_land=clear, nearby_clear_land_distance_tiles=nearest,
                     terrain_status='DIRECT_CLEAR_LAND' if clear else 'TARGET_REQUIRES_TERRAIN_REVIEW',
                     coverage_status='IN_ALL_IN_BOUNDS_TEST',
                     boundary_review=bool(min(col, row, 4095-col, 4095-row) < 90),
                     reason='All-town request: preserve target and flag issues; no position snapped and no spacing deletion')
            all_towns.append(candidate)
            if clear:
                land_towns.append(candidate)
        rows.append(r)
    g.validate(all_towns)
    g.validate(land_towns)
    nearest_rows = g.spacing(all_towns)
    near_by_name = {r['name']: r for r in nearest_rows}
    for r in rows:
        if r['name'] in near_by_name:
            r['spacing_status'] = near_by_name[r['name']]['spacing_band']
    pairs = []
    for a, b in itertools.combinations(all_towns, 2):
        distance = g.distance(a, b)
        if distance <= 30:
            ax, ay = import_target(a['x'], a['y'])
            bx, by = import_target(b['x'], b['y'])
            pairs.append(dict(town_a=a['name'], town_b=b['name'], distance_tiles=round(distance, 6),
                              actual_target_distance_tiles=round(math.hypot(ax-bx, ay-by), 6),
                              policy=g.band(distance),
                              decision='BOTH INCLUDED FOR REQUESTED ALL-TOWN TEST; importance/transport exception review pending'))
    out.mkdir(parents=True)
    save_json(out/ALL_FILE, all_towns)
    save_json(out/LAND_FILE, land_towns)
    g.write_csv(out/'all_600_placement_audit.csv', rows, list(rows[0]))
    deferred = [r for r in rows if r['coverage_status'] == 'DEFERRED_OUTSIDE_MAP']
    g.write_csv(out/'outside_map_deferred.csv', deferred, list(rows[0]))
    terrain_review = [r for r in rows if r['coverage_status'] != 'DEFERRED_OUTSIDE_MAP' and not r['direct_clear_land']]
    g.write_csv(out/'terrain_review.csv', terrain_review, list(rows[0]))
    g.write_csv(out/'all_town_nearest_neighbours.csv', nearest_rows, list(nearest_rows[0]))
    g.write_csv(out/'close_pairs_review.csv', pairs,
                ['town_a', 'town_b', 'distance_tiles', 'actual_target_distance_tiles', 'policy', 'decision'])
    summary = dict(status='ALL-TOWN EXPERIMENTAL IMPORT; not spacing-approved or in-game validated',
                   catalogue_towns=len(master), all_in_bounds_towns=len(all_towns),
                   direct_clear_land_towns=len(land_towns), terrain_review_towns=len(terrain_review),
                   outside_map_deferred=len(deferred), unmatched_catalogue_rows=0,
                   individually_verified_all_town_positions=False,
                   pairs_under_15=sum(p['distance_tiles'] < 15 for p in pairs),
                   pairs_15_through_30=sum(15 <= p['distance_tiles'] <= 30 for p in pairs),
                   towns_by_region=dict(sorted(collections.Counter(r['region'] for r in rows if r['x'] != '').items())),
                   in_game_founding_successes=None, source_assets_sha256=HASHES,
                   input_sha256={str(p.relative_to(g.ROOT)): g.digest(p) for p in [g.MASTER, g.INVENTORY, MODEL, OVERRIDES]},
                   note='Out-of-map records remain documented; close towns and water targets stay in the requested full test, with explicit reviews. Model uncertainty is unchanged from V6; Boulogne identity correction is provisional.')
    save_json(out/'summary.json', summary)
    for path, sha in HASHES.items():
        if g.digest(assets/path) != sha:
            raise ValueError('Source asset mutated: ' + path)
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assets', type=Path, default=g.ROOT/'source_assets')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    try:
        print(json.dumps(export(args.assets, args.out), indent=2))
    except (ValueError, KeyError, OSError) as error:
        p.exit(2, str(error)+'\n')
