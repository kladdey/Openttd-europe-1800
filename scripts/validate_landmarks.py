#!/usr/bin/env python3
"""Frozen-model V9 landmark observations and terrain diagnostics; never moves towns."""
import argparse
import collections
import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

import geography as g
from calibrate_heightmap import HASHES, project
from scenario_geography import import_target, read_terrain, source_pixel
from review_europe_placements import rows

V8 = g.ROOT/'maps/calibration/geography_v8'
OBSERVATIONS = g.ROOT/'data/geography/landmark_observations_v9.csv'
MODEL = g.ROOT/'maps/calibration/geography_v6/coastline_models.json'
CANDIDATE = V8/'Europe_1800_V8_DESK_REVIEWED_CANDIDATE_TEST.json'


def observe_extremum(raw, r):
    """Land extremum in an explicit manually identified feature box; no model input."""
    left, right, top, bottom = (int(r[k]) for k in ('box_left', 'box_right', 'box_top', 'box_bottom'))
    if not (0 <= left < right < 4096 and 0 <= top < bottom < 4096):
        raise ValueError('Invalid observation box')
    rule = r['observation_rule']
    if rule not in ('MIN_ROW', 'MAX_ROW', 'MIN_COLUMN', 'MAX_COLUMN'):
        raise ValueError('Unknown observation rule')
    yy, xx = np.nonzero(raw[top:bottom+1, left:right+1] > 0)
    if not len(xx):
        raise ValueError('No land in feature box')
    xx, yy = xx+left, yy+top
    values = xx if 'COLUMN' in rule else yy
    extreme = values.min() if rule.startswith('MIN') else values.max()
    indices = np.flatnonzero(values == extreme)
    i = indices[len(indices)//2]
    col, row = int(xx[i]), int(yy[i])
    if col in (left, right) or row in (top, bottom):
        raise ValueError('Observation touches box edge; inspect identification: '+r['name'])
    return col, row


def landmark_audit(observations, coefficients):
    """Compare fixed observations to frozen projection; never fit or select nearest coast."""
    names = set()
    result = []
    for r in observations:
        name = r['name']
        if not name or name in names:
            raise ValueError('Missing or duplicate landmark name')
        names.add(name)
        lat, lon = float(r['latitude']), float(r['longitude'])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('Invalid geographic coordinate')
        uncertainty = float(r['feature_uncertainty_pixels'])
        if not math.isfinite(uncertainty) or uncertainty <= 0:
            raise ValueError('Invalid feature uncertainty')
        col, row = project(np.array([[lon, lat]]), coefficients)[0]
        out = dict(r, projected_column=round(float(col), 3), projected_row=round(float(row), 3))
        # Same cell split as V6; newly named observations do not make training cells independent.
        outside = not (-11 < lon < 25 and 35.5 < lat < 58.5)
        out['coast_fit_spatial_relation'] = ('OUTSIDE_FIT_SAMPLE_EXTENT' if outside else
            'HELD_OUT_CELL' if (math.floor(lon/2)+2*math.floor(lat/2)) % 4 == 0 else 'TRAINING_CELL')
        if r['identification_status'] == 'AMBIGUOUS':
            if r['observed_column'] or r['observed_row']:
                raise ValueError('Ambiguous landmark must not have a claimed observation')
            out.update(delta_column='', delta_row='', vector_difference_pixels='', review_status='UNRESOLVED_IDENTIFICATION')
        elif r['identification_status'] == 'APPROXIMATE_MORPHOLOGICAL_MATCH':
            x, y = float(r['observed_column']), float(r['observed_row'])
            if not (math.isfinite(x) and math.isfinite(y) and 0 <= x < 4096 and 0 <= y < 4096):
                raise ValueError('Observed landmark outside raster')
            dx, dy = float(col)-x, float(row)-y
            difference = math.hypot(dx, dy)
            out.update(delta_column=round(dx, 3), delta_row=round(dy, 3),
                vector_difference_pixels=round(difference, 3),
                review_status='EXCEEDS_FEATURE_ESTIMATE' if difference > uncertainty else 'WITHIN_FEATURE_ESTIMATE')
        else:
            raise ValueError('Unknown identification status')
        result.append(out)
    return result


def write_csv(path, records):
    if not records:
        raise ValueError('Empty report')
    g.write_csv(path, records, list(records[0]))


def landmark_sheet(raw, audits, out):
    rgb = np.stack([raw*.55+65]*3, axis=-1).clip(0, 255).astype('uint8')
    rgb[raw == 0] = [15, 35, 60]
    base = Image.fromarray(rgb)
    sheet = Image.new('RGB', (1200, math.ceil(len(audits)/4)*310), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, r in enumerate(audits):
        left, top = int(r['crop_left']), int(r['crop_top'])
        x, y = i%4*300, i//4*310
        sheet.paste(base.crop((left, top, left+120, top+120)).resize((240, 240), Image.Resampling.NEAREST), (x, y+30))
        draw.text((x, y), r['name'], fill='black')
        draw.text((x, y+14), f'Source origin {left},{top}; 120px square', fill='black')
        px, py = x+2*(r['projected_column']-left), y+30+2*(r['projected_row']-top)
        draw.line((px-6, py, px+6, py), fill='cyan', width=2)
        draw.line((px, py-6, px, py+6), fill='cyan', width=2)
        if r['observed_column']:
            ox, oy = x+2*(float(r['observed_column'])-left), y+30+2*(float(r['observed_row'])-top)
            draw.ellipse((ox-5, oy-5, ox+5, oy+5), outline='yellow', width=2)
            draw.line((px, py, ox, oy), fill='red', width=1)
        draw.text((x, y+275), f"Difference: {r['vector_difference_pixels']} px; feature +/-{r['feature_uncertainty_pixels']}", fill='black')
        draw.text((x, y+290), r['review_status'], fill='black')
    sheet.save(out/'landmark_contact_sheet.png')


def generate(assets, out):
    if out.exists():
        raise FileExistsError('Use a new output directory')
    for relative, expected in HASHES.items():
        if g.digest(assets/relative) != expected:
            raise ValueError('Original asset hash mismatch: '+relative)
    with Image.open(assets/'heightmaps/Europe_heightmap_original.png') as im:
        raw = np.array(im)[:, :, 0]
    coeff = g.read_json(MODEL)['axis_affine']['coefficients']
    landmarks = landmark_audit(rows(OBSERVATIONS), coeff)
    for r in landmarks:
        if r['identification_status'] != 'AMBIGUOUS':
            actual = observe_extremum(raw, r)
            if actual != (int(r['observed_column']), int(r['observed_row'])):
                raise ValueError('Recorded observation disagrees with raster feature: '+r['name'])
    towns = g.read_json(CANDIDATE)
    g.validate(towns)
    types, _ = read_terrain(assets/'scenarios/Europe_1800_V1.scn')
    industry, _ = read_terrain(assets/'scenarios/Europe_1800_Industries_Original.scn')
    saved_clear = (types == 0) & (industry == 0)
    land_distance = distance_transform_edt(raw > 0)
    source_clear = saved_clear[:, ::-1]
    review = []
    old_terrain = {r['name']: r for r in rows(V8/'terrain_review_refined.csv') if r['in_candidate'] == 'True'}
    for town in towns:
        name = town['name']
        if name not in old_terrain:
            continue
        old = old_terrain[name]
        tx, ty = import_target(town['x'], town['y'])
        col, row = source_pixel(town['x'], town['y'], 'counter_clockwise')
        item = dict(name=name, category=old['category'], source_column=col, source_row=row,
                    source_nonzero_distance_to_zero_pixels=round(float(land_distance[row, col]), 3),
                    raw_elevation=int(raw[row, col]), v1_tile_type=int(types[ty, tx]), industries_tile_type=int(industry[ty, tx]))
        for radius in (5, 10, 16):
            ys, xs = np.ogrid[-radius:radius+1, -radius:radius+1]
            disk = xs*xs+ys*ys <= radius*radius
            region = np.s_[row-radius:row+radius+1, col-radius:col+radius+1]
            item[f'r{radius}_source_land_fraction'] = round(float(np.mean((raw[region] > 0)[disk])), 6)
            item[f'r{radius}_both_saved_clear_fraction'] = round(float(np.mean(source_clear[region][disk])), 6)
        item['priority'] = 'COAST_OR_HARBOUR_REVIEW' if old['category'] == 'SOURCE_ZERO_OCEAN_CONNECTED' else 'ROAD_OCCUPANCY_REVIEW' if old['category'] == 'SAVED_ROAD_OCCUPANCY' else 'INLAND_CHANNEL_OR_CENTRE_REVIEW'
        item['decision'] = 'KEEP_FLAGGED_UNMOVED'
        item['limitation'] = 'Disk radii are sensitivity probes, not error bounds. Clear pixels do not establish historic centre, named channel, flatness or founding.'
        review.append(item)
    if set(old_terrain) != {r['name'] for r in review}:
        raise ValueError('Retained terrain queue not completely accounted for')
    decisions = rows(V8/'all_600_decisions.csv')
    terrain_names = set(old_terrain)
    confidence = []
    for r in decisions:
        status = ('DEFERRED' if r['state'] != 'RETAINED_DESK_CANDIDATE' else
                  'TERRAIN_REVIEW_OPEN' if r['name'] in terrain_names else
                  'BOUNDARY_REVIEW_OPEN' if r['boundary_review_open'] == 'True' else 'CONDITIONAL_CLEAR_TARGET')
        confidence.append(dict(name=r['name'], evidence_status=status, decision=r['state'],
            x=r['x'], y=r['y'], population=r['population'], reason=r['reason'],
            terrain_review_open=r['terrain_review_open'], boundary_review_open=r['boundary_review_open'],
            geographic_accuracy='EMPIRICAL_TRANSFORM_UNCERTAIN', founding='UNTESTED'))
    measured = [float(r['vector_difference_pixels']) for r in landmarks if r['vector_difference_pixels'] != '']
    summary = dict(status='DESK EVIDENCE ONLY; frozen transform; no town movement',
        landmarks_attempted=len(landmarks), approximate_morphological_matches=len(measured),
        ambiguous_landmarks=len(landmarks)-len(measured),
        landmark_spatial_relations=dict(collections.Counter(r['coast_fit_spatial_relation'] for r in landmarks)),
        landmark_vector_median_pixels=round(float(np.median(measured)), 3),
        landmark_vector_p90_pixels=round(float(np.percentile(measured, 90)), 3),
        landmark_vector_max_pixels=max(measured),
        landmark_feature_estimate_exceeded=sum(r['review_status']=='EXCEEDS_FEATURE_ESTIMATE' for r in landmarks),
        terrain_targets_investigated=len(review), terrain_targets_resolved=0,
        terrain_priorities=dict(collections.Counter(r['priority'] for r in review)),
        catalogue_entries=len(confidence), candidate_towns=len(towns), deferred_towns=600-len(towns),
        coordinates_changed=0, population_changes=0, scenario_changes=0, in_game_tests=0,
        input_sha256={str(p.relative_to(g.ROOT)):g.digest(p) for p in (OBSERVATIONS, MODEL, CANDIDATE, V8/'all_600_decisions.csv', V8/'terrain_review_refined.csv')},
        original_assets_sha256=HASHES,
        limitations='Observations were identified in model-selected crops; approximate shoreline/lighthouse matches are not blinded or survey controls. No refit. New feature points in training cells share coastline information with fitting. No town is survey validated by this report.')
    out.mkdir(parents=True)
    write_csv(out/'landmark_vector_audit.csv', landmarks)
    write_csv(out/'retained_terrain_diagnostics.csv', review)
    write_csv(out/'all_600_evidence_status.csv', confidence)
    (out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    landmark_sheet(raw, landmarks, out)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, default=g.ROOT/'source_assets')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.assets, args.out), indent=2))
