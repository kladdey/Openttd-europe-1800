#!/usr/bin/env python3
"""Offline historic-bank evidence and exact-importer sensitivity; never changes towns."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from calibrate_heightmap import HASHES
from reverse_audit import independent_target
from river_bank_diagnostics import PINNED_INPUTS, read_rows, source_oriented_crop, unique_index, verify_held_target
from scenario_geography import read_terrain
from validate_inland_features import load_frozen_model, MODEL

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'data/geography/historic_river_bank_research_v1.json'
DECISIONS = 'maps/calibration/geography_v11/all_600_decisions.csv'
DECISIONS_HASH = 'bce9343ee233a879ff763a4e87ba683167dc1fb4e2b96123b1aadae4f8f834a9'


def timeline_context(record, year):
    kind = record['kind']
    if kind == 'CROSSING_INTERRUPTION':
        begin, end = record['interruption_start'], record['interruption_end']
        if begin >= end:
            raise ValueError('Invalid crossing interruption')
        if begin < year < end:
            return 'ABSENT_DURING_RECORDED_INTERRUPTION'
        if year in (begin, end):
            return 'TRANSITION_YEAR_REQUIRES_EXACT_DATE'
        return 'OUTSIDE_DOCUMENTED_GAP_CONTINUITY_UNKNOWN'
    date = record['not_before']
    if kind == 'LATER_CONFIGURATION':
        return 'LATER_CONFIGURATION_NOT_1800' if year < date else 'CONFIGURATION_DATE_PASSED_CONTINUITY_UNKNOWN'
    if kind == 'LATER_NAME_OR_FABRIC':
        if not record.get('pre_1800_building_site'):
            raise ValueError('Later name/fabric must distinguish the older building site')
        return 'OLDER_SITE_LATER_NAME_OR_FABRIC' if year < date else 'LATER_NAME_OR_FABRIC_DATE_PASSED'
    if kind == 'DATED_OPENING':
        return 'OPENED_BEFORE_START_CONTINUITY_NOT_PROVEN' if year > date else ('OPENING_YEAR_REQUIRES_EXACT_DATE' if year == date else 'NOT_OPENED_YET')
    raise ValueError('Unknown timeline interpretation')


def validate_research(data):
    if data['schema_version'] != 1 or data['scenario_start_year'] != 1800:
        raise ValueError('Unsupported river-bank research schema or checkpoint')
    sources = unique_index(data['sources'], 'id')
    unique_index(data['cases'], 'name')
    for source in sources.values():
        if not source['url'].startswith('https://') or not source['summary'].strip():
            raise ValueError('Missing source URL or evidence summary')
    for case in data['cases']:
        if case['historic_bank'] not in ('RIGHT_DOWNSTREAM', 'LEFT_DOWNSTREAM'):
            raise ValueError('Banks must be defined looking downstream, not by compass direction')
        if (case['georeferenced_historic_bank_available'] is not False or
            case['saved_named_channel_identified'] is not False or
            case['registration_error_bound_pixels'] is not None or
            case['site_to_bank_margin_pixels'] is not None):
            raise ValueError('This research snapshot has no measured geographic registration evidence')
        for key in ('bank_source_ids', 'site_source_ids'):
            if not case[key] or any(i not in sources or sources[i]['access'].startswith('LOCATOR_ONLY') for i in case[key]):
                raise ValueError('A locator-only or missing source cannot support a bank/site claim')
    for record in data['timeline']:
        if any(i not in sources or sources[i]['access'].startswith('LOCATOR_ONLY') for i in record['source_ids']):
            raise ValueError('Timeline needs usable source evidence')
        if timeline_context(record, 1800) != record['start_1800_context']:
            raise ValueError('Chronology disagrees with recorded 1800 context')


def sensitivity(reference, raw, terrain):
    results = []
    for dy in (-0.5, 0.0, 0.5):
        for dx in (-0.5, 0.0, 0.5):
            tx, ty = independent_target(float(reference['x']) + dy/4095, float(reference['y']) + dx/4095)
            col, row = 4095-tx, ty
            a, b = (int(array[ty, tx]) for array in terrain)
            elevation = int(raw[row, col])
            results.append(dict(reference_id=reference['reference_id'],offset_column_pixels=dx,offset_row_pixels=dy,
                                source_column=col,source_row=row,tile_x=tx,tile_y=ty,raw_elevation=elevation,
                                v1_tile_type=a,industries_tile_type=b,direct_clear_land=elevation>0 and a==b==0))
    return results


def write_csv(path, records):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)


def local_sheet(cases, audited, terrain, out):
    sheet=Image.new('RGB',(720,720),'white');draw=ImageDraw.Draw(sheet)
    draw.text((5,5),'Local saved terrain. H = held target; source columns increase right; rows increase down.',fill='black')
    draw.text((5,20),'Blue: water; green: clear; grey: road; red: house. Water is not identified as a named river.',fill='black')
    for i,case in enumerate(cases):
        a=audited[case['reference_id']];col,row=int(a['source_column']),int(a['source_row'])
        for j,array in enumerate(terrain):
            x0,y0=j*360,45+i*330
            draw.text((x0+5,y0),case['name']+' - '+('V1' if j==0 else 'Industries'),fill='black')
            draw.text((x0+5,y0+15),f'Columns {col-3}..{col+3}; rows {row-3}..{row+3}',fill='black')
            crop=source_oriented_crop(array,[col-3,row-3,col+4,row+4])
            for yy in range(7):
                for xx in range(7):
                    kind=int(crop[yy,xx]);color={0:'#468241',2:'#999999',3:'#d24141',6:'#143c82'}.get(kind,'#222222')
                    x,y=x0+30+xx*36,y0+40+yy*36
                    draw.rectangle((x,y,x+35,y+35),fill=color,outline='white')
                    draw.text((x+13,y+12),'H' if (xx,yy)==(3,3) else str(kind),fill='yellow' if (xx,yy)==(3,3) else 'white')
            draw.text((x0+5,y0+300),'No inferred bank polygon; no coordinate correction.',fill='black')
    sheet.save(out)


def run(out):
    data=json.loads(MANIFEST.read_bytes());validate_research(data)
    inputs=dict(PINNED_INPUTS)
    inputs[DECISIONS]=DECISIONS_HASH
    inputs.update({'source_assets/'+name:sha for name,sha in HASHES.items()})
    for filename,expected in inputs.items():
        if hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()!=expected:
            raise ValueError('Input hash mismatch: '+filename)
    coefficients,model_bytes=load_frozen_model(MODEL)
    refs=unique_index(read_rows(ROOT/'data/geography/historic_centre_references_v11.csv'),'reference_id')
    audited=unique_index(read_rows(ROOT/'maps/calibration/geography_v11/historic_reference_audit.csv'),'reference_id')
    with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as image:raw=np.array(image)[:,:,0]
    terrain=[read_terrain(ROOT/'source_assets/scenarios'/name)[0] for name in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]
    results=[];samples=[]
    for case in data['cases']:
        ref=refs[case['reference_id']];a=audited[case['reference_id']]
        verify_held_target(case,ref,a,coefficients,raw,terrain)
        probe=sensitivity(a,raw,terrain);samples.extend(probe)
        results.append(dict(name=case['name'],reference_id=case['reference_id'],historic_bank_context=case['historic_bank'],
                            bank_scope=case['bank_scope'],prior_hold='HOLD_BANK_ALIGNMENT',outcome='HOLD_BANK_ALIGNMENT',
                            source_column=int(a['source_column']),source_row=int(a['source_row']),
                            probes=len(probe),unique_import_targets=len({(r['tile_x'],r['tile_y']) for r in probe}),
                            probes_hitting_saved_water=sum(r['v1_tile_type']==6 or r['industries_tile_type']==6 for r in probe),
                            historic_bank_georeferenced=case['georeferenced_historic_bank_available'],
                            saved_named_channel_identified=case['saved_named_channel_identified'],
                            reason='Historical bank context strengthened; no georeferenced bank or bounded registration to named saved channel. Half-pixel perturbations reach water. Retain the hold; do not select a neighbouring clear pixel.'))
    timeline=[dict(id=r['id'],name=r['name'],feature=r['feature'],kind=r['kind'],context_at_1800=timeline_context(r,1800),source_ids=';'.join(r['source_ids'])) for r in data['timeline']]
    out.mkdir(parents=True,exist_ok=False)
    write_csv(out/'bank_case_review.csv',results);write_csv(out/'half_pixel_sensitivity.csv',samples);write_csv(out/'historical_context_1800.csv',timeline)
    write_csv(out/'source_access.csv',[dict(source_id=r['id'],url=r['url'],access=r['access'],locator=r['locator'],geometry_inspected=r['geometry_inspected']) for r in data['sources']])
    local_sheet(data['cases'],audited,terrain,out/'held_target_neighbourhoods.png')
    summary=dict(schema_version=1,research_manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                 model_sha256=hashlib.sha256(model_bytes).hexdigest(),input_sha256=inputs,cases_reviewed=len(results),
                 holds_lifted=0,source_records=len(data['sources']),historic_maps_georeferenced=0,town_coordinate_changes=0,
                 candidate_towns=sum(r['state']=='RETAINED_CLEAR_TARGET_CANDIDATE' for r in read_rows(ROOT/DECISIONS)),
                 terrain_cases_unresolved=sum(r['state']=='DEFERRED_TERRAIN' for r in read_rows(ROOT/DECISIONS)),in_game_tests=0,
                 probe_interpretation='Deterministic sensitivity examples, not registration error bounds, independent samples, likelihoods or candidate alternatives.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(run(parser.parse_args().out),indent=2))
