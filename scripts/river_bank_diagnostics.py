"""Read-only named-river overlays; generalized centerlines cannot approve town banks."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from calibrate_heightmap import HASHES, project
from scenario_geography import read_terrain

ROOT = Path(__file__).resolve().parents[1]


def source_oriented_crop(game_array, box):
    left, top, right, bottom = box
    if game_array.ndim != 2 or game_array.shape[0] != game_array.shape[1]:
        raise ValueError('Expected square game array')
    size = game_array.shape[1]
    if not (0 <= left < right <= size and 0 <= top < bottom <= size):
        raise ValueError('Crop outside game array')
    return game_array[top:bottom, size-right:size-left][:, ::-1]


def read_rows(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def run(raw, coefficients, out):
    config_path = ROOT/'data/geography/river_bank_observations_v1.json'
    config = json.loads(config_path.read_text())
    if config['schema_version'] != 1:
        raise ValueError('Unsupported river observation schema')
    vector_bytes = (ROOT/'data/geography/ne_10m_bank_review_rivers.geojson').read_bytes()
    if hashlib.sha256(vector_bytes).hexdigest() != config['subset_sha256']:
        raise ValueError('River vector hash mismatch')
    rivers = {f['properties']['name']: f for f in json.loads(vector_bytes)['features']}
    references = {r['reference_id']: r for r in read_rows(ROOT/'data/geography/historic_centre_references_v11.csv')}
    audited = {r['reference_id']: r for r in read_rows(ROOT/'maps/calibration/geography_v11/historic_reference_audit.csv')}
    terrain = []
    for filename in ['Europe_1800_V1.scn', 'Europe_1800_Industries_Original.scn']:
        path = ROOT/'source_assets/scenarios'/filename
        if hashlib.sha256(path.read_bytes()).hexdigest() != HASHES['scenarios/'+filename]:
            raise ValueError('Scenario hash mismatch')
        terrain.append(read_terrain(path)[0])
    sheet = Image.new('RGB', (1200, 460*len(config['cases'])+45), 'white')
    draw = ImageDraw.Draw(sheet)
    draw.text((5, 5), 'Cyan: generalized river centerline; yellow: held historic-site target. No line was fitted.', fill='black')
    draw.text((5, 20), 'Saved types: blue water; green clear; grey roads; red houses; black other. Source: grayscale elevation.', fill='black')
    records = []
    for index, case in enumerate(config['cases']):
        ref = references[case['reference_id']]
        a = audited[case['reference_id']]
        if ref['placement_review'] != 'HOLD_BANK_ALIGNMENT' or a['eligible'] != 'False':
            raise ValueError('Expected an explicitly held bank reference')
        left, top, right, bottom = case['box']
        river = rivers[case['river']]['geometry']
        if river['type'] not in ('LineString', 'MultiLineString'):
            raise ValueError('Expected river centerline')
        lines = [river['coordinates']] if river['type'] == 'LineString' else river['coordinates']
        line_canvas = Image.new('1', (right-left, bottom-top))
        line_draw = ImageDraw.Draw(line_canvas)
        for line in lines:
            coords = project(line, coefficients)-[left, top]
            line_draw.line([tuple(p) for p in coords], fill=1, width=1)
        line_mask = np.array(line_canvas, dtype=bool)
        if not line_mask.any():
            raise ValueError('Named river absent from case window')
        col, row = int(a['source_column']), int(a['source_row'])
        if not (left <= col < right and top <= row < bottom):
            raise ValueError('Held site outside case window')
        item = dict(name=case['name'], reference_id=case['reference_id'], river=case['river'],
                    prior_review=ref['placement_review'], outcome='HOLD_BANK_ALIGNMENT',
                    approved=False, generalized_line_pixels=int(line_mask.sum()),
                    source_zero_fraction_on_line=round(float((raw[top:bottom,left:right][line_mask] == 0).mean()), 4),
                    next_evidence='Historic bank polygons or a confidently identified source channel; the generalized centerline alone cannot resolve this hold.')
        for j, title in enumerate(['Original source', 'V1 saved terrain', 'Industries saved terrain']):
            if j == 0:
                crop = raw[top:bottom, left:right]
                rgb = np.repeat(np.clip(crop.astype(float)*2, 30, 235).astype('uint8')[:, :, None], 3, 2)
            else:
                types = source_oriented_crop(terrain[j-1], case['box'])
                rgb = np.zeros((*types.shape, 3), dtype='uint8')
                for kind, color in [(0,[70,130,65]),(2,[145,145,145]),(3,[210,65,65]),(6,[20,60,130])]:
                    rgb[types == kind] = color
                item['v1_water_fraction_on_line' if j == 1 else 'industries_water_fraction_on_line'] = round(float((types[line_mask] == 6).mean()), 4)
            rgb[line_mask] = [0,220,255]
            tile = Image.fromarray(rgb).resize((400,400), Image.Resampling.NEAREST)
            mark = ImageDraw.Draw(tile)
            x, y = (col-left)*5, (row-top)*5
            mark.ellipse((x-5,y-5,x+5,y+5), outline='yellow', width=2)
            dest_x, dest_y = j*400, 45+index*460
            sheet.paste(tile, (dest_x,dest_y+40))
            draw.text((dest_x,dest_y), case['name']+' - '+title, fill='black')
            draw.text((dest_x,dest_y+17), 'HOLD: no demonstrated historic-bank registration', fill='black')
        records.append(item)
    with (out/'river_bank_review.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    sheet.save(out/'river_bank_overlays.png')
    return dict(cases_reviewed=len(records), cases_resolved=0, vector_sha256=config['subset_sha256'],
                limitation='Line-over-water fractions are descriptive overlap with any water, not named-river identification or proof of historic-bank alignment.')
