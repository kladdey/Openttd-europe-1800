#!/usr/bin/env python3
"""Frozen-model inland shape diagnostics. Never fits a model or exports town coordinates."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, label, distance_transform_edt

from calibrate_heightmap import project

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'data/geography/inland_observations_v1.json'
VECTOR = ROOT / 'data/geography/ne_10m_inland_lakes_subset.geojson'
MODEL = ROOT / 'maps/calibration/geography_v6/coastline_models.json'
SOURCE = ROOT / 'source_assets/heightmaps/Europe_heightmap_original.png'
SOURCE_HASH = 'beb1760c157e72f90b87713cc7a88b7455d47e235f91fe54a11de663c541d744'
FROZEN_MODEL_HASH = '263b814b4ce30e93f9034c8d328217f2e70681ccb362fa619bc5d5d0116e1e50'


def load_frozen_model(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != FROZEN_MODEL_HASH:
        raise ValueError('Frozen V6 model hash mismatch')
    return json.loads(data)['axis_affine']['coefficients'], data


STATES = {'APPROXIMATE_BASIN', 'FRAGMENTED_BASIN', 'PARTIAL_BASIN', 'CLIPPED_REFERENCE', 'UNRESOLVED_IDENTIFICATION'}


def observed_mask(raw, feature):
    """Union explicitly identified constant-elevation components; no nearest-point logic."""
    if feature['identification'] not in STATES:
        raise ValueError('Unknown identification state')
    left, top, right, bottom = feature['box']
    if not (0 <= left < right <= raw.shape[1] and 0 <= top < bottom <= raw.shape[0]):
        raise ValueError('Observation box outside image')
    crop = raw[top:bottom, left:right]
    mask = np.zeros(crop.shape, dtype=bool)
    if feature['identification'] == 'UNRESOLVED_IDENTIFICATION':
        if feature['seeds'] or feature['elevation'] is not None:
            raise ValueError('Unresolved feature must not claim component seeds')
        return mask
    elevation = feature['elevation']
    if not isinstance(elevation, int) or isinstance(elevation, bool) or not 0 <= elevation <= 255:
        raise ValueError('Invalid component elevation')
    labels, _ = label(crop == elevation)  # Four-connected; touching corners do not merge basins.
    selected = set()
    if not feature['seeds']:
        raise ValueError('Identified feature needs explicit seeds')
    for col, row in feature['seeds']:
        if not (left <= col < right and top <= row < bottom):
            raise ValueError('Seed outside observation box')
        component = int(labels[row-top, col-left])
        if component == 0:
            raise ValueError('Seed does not have declared elevation')
        if component in selected:
            raise ValueError('Duplicate component seed')
        selected.add(component)
        mask |= labels == component
    if np.any(mask[0]) or np.any(mask[-1]) or np.any(mask[:, 0]) or np.any(mask[:, -1]):
        raise ValueError('Observed component touches window edge; identification must be reviewed')
    return mask


def projected_mask(geometry, coefficients, box, image_shape):
    """Rasterize all polygon exteriors and holes in the fixed observation window."""
    polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    if geometry['type'] not in ('Polygon', 'MultiPolygon'):
        raise ValueError('Expected lake polygon geometry')
    left, top, right, bottom = box
    result = np.zeros((bottom-top, right-left), dtype=bool)
    clipped = False
    for polygon in polygons:
        canvas = Image.new('1', (right-left, bottom-top))
        draw = ImageDraw.Draw(canvas)
        for i, ring in enumerate(polygon):
            points = project(ring, coefficients)
            clipped |= bool(np.any((points[:, 0] < 0) | (points[:, 0] >= image_shape[1]) |
                                   (points[:, 1] < 0) | (points[:, 1] >= image_shape[0])))
            # Also disallow comparison when the chosen window cuts the projected lake.
            clipped |= bool(np.any((points[:, 0] < left) | (points[:, 0] >= right) |
                                   (points[:, 1] < top) | (points[:, 1] >= bottom)))
            draw.polygon([tuple(p) for p in points - [left, top]], fill=1 if i == 0 else 0)
        result |= np.array(canvas, dtype=bool)
    return result, clipped


def shape_metrics(observed, predicted):
    if observed.shape != predicted.shape or not observed.any() or not predicted.any():
        raise ValueError('Nonempty same-shape masks required')
    oy, ox = np.nonzero(observed)
    py, px = np.nonzero(predicted)
    dx, dy = float(ox.mean()-px.mean()), float(oy.mean()-py.mean())
    a = observed & ~binary_erosion(observed)
    b = predicted & ~binary_erosion(predicted)
    distances = np.r_[distance_transform_edt(~a)[b], distance_transform_edt(~b)[a]]
    return dict(observed_minus_predicted_column=round(dx, 3),
                observed_minus_predicted_row=round(dy, 3),
                centroid_difference_pixels=round(float(np.hypot(dx, dy)), 3),
                boundary_distance_median_pixels=round(float(np.median(distances)), 3),
                boundary_distance_p90_pixels=round(float(np.percentile(distances, 90)), 3),
                intersection_over_union=round(float(np.count_nonzero(observed & predicted) / np.count_nonzero(observed | predicted)), 4),
                observed_to_predicted_area_ratio=round(float(observed.sum()/predicted.sum()), 4))


def audit(raw, features, vectors, coefficients):
    results, masks = [], []
    names, ids = set(), set()
    for feature in features:
        name, feature_id = feature['name'], feature['ne_id']
        if not name or name in names or feature_id in ids:
            raise ValueError('Missing or duplicate feature identity')
        names.add(name); ids.add(feature_id)
        if feature_id not in vectors:
            raise ValueError('Missing vector feature')
        observed = observed_mask(raw, feature)
        predicted, clipped = projected_mask(vectors[feature_id]['geometry'], coefficients, feature['box'], raw.shape)
        state = feature['identification']
        comparable = state in {'APPROXIMATE_BASIN', 'FRAGMENTED_BASIN'} and not clipped
        if comparable and not predicted.any():
            raise ValueError('Reference polygon absent from observation window')
        values = shape_metrics(observed, predicted) if comparable else {}
        result = dict(name=name, ne_id=feature_id, identification=state,
                      scalar_elevation=feature['elevation'], components=len(feature['seeds']),
                      observed_pixels=int(observed.sum()), projected_pixels=int(predicted.sum()),
                      clipped_reference=clipped, diagnostic_comparison=comparable,
                      eligible_for_automatic_town_correction=False, **values,
                      note=feature['note'])
        results.append(result); masks.append((feature, observed, predicted))
    return results, masks


def contact_sheet(raw, masks, out):
    width, height = 900, 260 * ((len(masks)+2)//3)
    sheet = Image.new('RGB', (width, height), 'white')
    pen = ImageDraw.Draw(sheet)
    for i, (feature, observed, predicted) in enumerate(masks):
        left, top, right, bottom = feature['box']
        crop = raw[top:bottom, left:right]
        grey = np.clip(crop.astype(float)*1.6, 35, 230).astype('uint8')
        rgb = np.repeat(grey[:, :, None], 3, axis=2)
        # Edges only, no optimized alignment: cyan reference; yellow observed plateau.
        rgb[predicted & ~binary_erosion(predicted)] = [0, 220, 255]
        rgb[observed & ~binary_erosion(observed)] = [255, 210, 0]
        tile = Image.fromarray(rgb)
        scale = min(280/tile.width, 195/tile.height)
        tile = tile.resize((round(tile.width*scale), round(tile.height*scale)), Image.Resampling.NEAREST)
        x, y = i%3*300, i//3*260
        sheet.paste(tile, (x, y+45))
        pen.text((x, y), feature['name'], fill='black')
        pen.text((x, y+15), feature['identification'], fill='black')
        pen.text((x, y+29), f'Source window {left},{top} to {right},{bottom}', fill='black')
    sheet.save(out)


def run(out):
    config = json.loads(CONFIG.read_text())
    vector_bytes = VECTOR.read_bytes()
    source_bytes = SOURCE.read_bytes()
    if config['schema_version'] != 1:
        raise ValueError('Unsupported observation schema')
    if hashlib.sha256(vector_bytes).hexdigest() != config['subset_sha256']:
        raise ValueError('Vector hash mismatch')
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_HASH:
        raise ValueError('Original heightmap hash mismatch')
    coefficients, model_bytes = load_frozen_model(MODEL)
    with Image.open(SOURCE) as image:
        raw = np.array(image)[:, :, 0]
    vectors = {f['properties']['ne_id']: f for f in json.loads(vector_bytes)['features']}
    results, masks = audit(raw, config['features'], vectors, coefficients)
    out.mkdir(parents=True, exist_ok=False)
    fields = list(dict.fromkeys(k for row in results for k in row))
    with (out/'inland_shape_audit.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(results)
    from river_bank_diagnostics import run as bank_review
    bank_summary = bank_review(raw, coefficients, out)
    summary = dict(river_bank_review=bank_summary, schema_version=1, heightmap_sha256=SOURCE_HASH,
                   vector_sha256=config['subset_sha256'], model_sha256=hashlib.sha256(model_bytes).hexdigest(),
                   frozen_model='V6 axis_affine', model_coefficients=coefficients,
                   features_reviewed=len(results), diagnostic_comparisons=sum(r['diagnostic_comparison'] for r in results),
                   withheld_features=[r['name'] for r in results if not r['diagnostic_comparison']],
                   town_coordinate_changes=0, model_fitted=False,
                   limitation='Generalized modern lake shapes are not surveyed inland controls or proof of historic river-bank registration.')
    (out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    contact_sheet(raw, masks, out/'inland_contact_sheet.png')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    print(json.dumps(run(parser.parse_args().out), indent=2))
