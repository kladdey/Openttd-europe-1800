#!/usr/bin/env python3
"""Bounded regional coast registration. Fits coastlines only; never inspects town land."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares

import geography as g
from calibrate_heightmap import COAST, HASHES, coast_distance_field, project

CONFIG = g.ROOT/'data/geography/coastal_regions_v10.json'
MODEL = g.ROOT/'maps/calibration/geography_v6/coastline_models.json'


def coastline_points(coefficients):
    # Densify existing line segments to <=3 source pixels; do not invent finer
    # geographic detail than the 1:50m reference. Preserve source ordering.
    dense = []
    for feature in g.read_json(COAST)['features']:
        line = project(feature['geometry']['coordinates'], coefficients)
        for start, end in zip(line[:-1], line[1:]):
            steps = max(1, int(np.ceil(np.linalg.norm(end-start)/3)))
            dense.extend(start+(end-start)*np.arange(steps)[:, None]/steps)
    points = np.array(dense)
    _, indices = np.unique(np.round(points/3).astype(int), axis=0, return_index=True)
    return points[np.sort(indices)]


def fit_translation(points, field, config):
    points = np.asarray(points, dtype=float)
    # Spatial blocks prevent randomly interleaved neighbouring samples being
    # advertised as independent holdouts. Interpolated source segments can
    # still cross blocks: report coast-normal checks, not 2D survey validation.
    blocks = np.floor(points/24).astype(int)
    holdout = (blocks[:, 0]+2*blocks[:, 1]) % 5 == 0
    train = ~holdout
    report = dict(samples=len(points), train_samples=int(sum(train)), holdout_samples=int(sum(holdout)), accepted=False)
    if sum(train) < config['minimum_train_samples'] or sum(holdout) < config['minimum_holdout_samples']:
        return dict(report, rejection_reasons=['INSUFFICIENT_SPATIALLY_SPLIT_COAST_SAMPLES'])

    def residual(shift, selected):
        p = points[selected]+shift
        return map_coordinates(field, [p[:, 1], p[:, 0]], order=1, mode='constant', cval=100)

    bound = config['max_shift_pixels']
    def optimize(selected):
        candidates = [least_squares(lambda shift: residual(shift, selected), start,
                        bounds=(-bound, bound), diff_step=.01, loss='soft_l1', f_scale=2, max_nfev=300)
                      for start in ([0, 0], [-6, 6], [6, -6])]
        valid = [r for r in candidates if r.success]
        if not valid:
            raise ValueError('All regional optimizer starts failed')
        return min(valid, key=lambda r:r.cost)

    result = optimize(train)
    before = residual([0, 0], holdout)
    after = residual(result.x, holdout)
    eigen = np.linalg.eigvalsh(result.jac.T@result.jac)
    ratio = float(eigen[0]/eigen[-1]) if eigen[-1] > 0 else 0
    jackknife = []
    groups = (blocks[:, 0]+3*blocks[:, 1]) % 4
    for group in range(4):
        selected = train & (groups != group)
        if sum(selected) < config['minimum_train_samples']:
            return dict(report, rejection_reasons=['INSUFFICIENT_JACKKNIFE_SAMPLES'])
        jackknife.append(optimize(selected).x)
    spread = float(max(np.linalg.norm(np.array(jackknife)-result.x, axis=1)))
    median0, p900 = np.percentile(before, [50, 90])
    median, p90 = np.percentile(after, [50, 90])
    failed = []
    if max(abs(result.x)) >= bound-.1: failed.append('TRANSLATION_AT_BOUND')
    if p90 > config['maximum_holdout_p90_pixels']: failed.append('HOLDOUT_P90_TOO_LARGE')
    if median0-median < config['minimum_holdout_median_improvement']: failed.append('MEDIAN_IMPROVEMENT_TOO_SMALL')
    if p90 > p900: failed.append('HOLDOUT_P90_WORSENED')
    if spread > config['maximum_jackknife_shift_pixels']: failed.append('SPATIALLY_UNSTABLE_TRANSLATION')
    if ratio < config['minimum_jacobian_eigenvalue_ratio']: failed.append('POORLY_CONSTRAINED_DIRECTION')
    return dict(report, accepted=not failed, rejection_reasons=failed,
        shift_column=float(result.x[0]), shift_row=float(result.x[1]),
        before_holdout_median_pixels=float(median0), before_holdout_p90_pixels=float(p900),
        holdout_median_pixels=float(median), holdout_p90_pixels=float(p90),
        jacobian_eigenvalue_ratio=ratio, maximum_jackknife_difference_pixels=spread,
        jackknife_shifts=[s.tolist() for s in jackknife])


def calibrate(assets):
    if g.digest(assets/'heightmaps/Europe_heightmap_original.png') != HASHES['heightmaps/Europe_heightmap_original.png']:
        raise ValueError('Original heightmap hash mismatch')
    with Image.open(assets/'heightmaps/Europe_heightmap_original.png') as im:
        raw = np.array(im)[:, :, 0]
    field = coast_distance_field(raw)
    coefficients = g.read_json(MODEL)['axis_affine']['coefficients']
    config = g.read_json(CONFIG)
    points = coastline_points(coefficients)
    regions = []
    for r in config['regions']:
        west, east, south, north = r['bounds_west_east_south_north']
        corner = project([[west, north], [east, south]], coefficients)
        left, top = corner[0]; right, bottom = corner[1]
        selected = points[(points[:, 0] >= left) & (points[:, 0] <= right) &
                          (points[:, 1] >= top) & (points[:, 1] <= bottom)]
        result = fit_translation(selected, field, config)
        regions.append(dict(r, **result))
    return dict(method='V6 affine plus regional translation; coastline fit only, no town land used',
        input_sha256={str(p.relative_to(g.ROOT)):g.digest(p) for p in (CONFIG, MODEL, COAST)},
        heightmap_sha256=HASHES['heightmaps/Europe_heightmap_original.png'],
        gates={k:v for k,v in config.items() if k != 'regions'}, regions=regions,
        limitations='Modern generalized coastline, coast-normal holdouts and spatial jackknife are diagnostics, not true point errors or historic-shoreline surveys. No named landmark was used to fit or select these regional shifts. Rejected fits must not be applied.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, default=g.ROOT/'source_assets')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists(): raise FileExistsError('Use a new output file')
    data = calibrate(args.assets)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({r['id']:dict(accepted=r['accepted'],reasons=r['rejection_reasons']) for r in data['regions']},indent=2))
