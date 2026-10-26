#!/usr/bin/env python3
"""Trace the current exported candidate backwards; do not call placement generators."""
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
import unicodedata

import numpy as np
from PIL import Image
from scenario_geography import read_terrain

ROOT = Path(__file__).resolve().parents[1]
V11 = ROOT/'maps/calibration/geography_v11'
MASTER_HASH = '6e4d9ebc4f489c7a83742e63f0599f94158f889c435e02b96110769503339410'


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def independent_target(x, y, size=4096):
    """Independent scalar IEEE-754 implementation of CCW importer arithmetic."""
    if any(type(v) not in (int,float) or not math.isfinite(v) or not 0 < v < 1 for v in (x,y)):
        raise ValueError('Coordinates must be finite, numeric and strictly interior')
    x, y = f32(x), f32(y)
    if not (0 < x < 1 and 0 < y < 1):
        raise ValueError('Coordinate rounds to importer boundary')
    return int(f32(f32(1-y)*(size-1))), int(f32(x*(size-1)))


def rows(path):
    with path.open(encoding='utf-8',newline='') as stream:
        return list(csv.DictReader(stream))


def identity(name):
    return ' '.join(unicodedata.normalize('NFKC',name).casefold().split())


def audit_candidate(master, candidate, decisions, raw, terrains, spacing, claim, size=4096):
    """Independent output checks; return explicit errors instead of silently repairing data."""
    errors, records = [], []
    master_by_name = {t['name']:t for t in master}
    decisions_by_name = {r['name']:r for r in decisions}
    if len(decisions_by_name)!=len(decisions) or set(decisions_by_name)!=set(master_by_name):
        errors.append('All-source decision rows are duplicate, missing or extraneous')
    candidate_names = [t.get('name') for t in candidate]
    if any(not isinstance(n,str) or not n.strip() for n in candidate_names):
        raise ValueError('Candidate has missing or invalid names')
    if len({identity(n) for n in candidate_names})!=len(candidate_names):
        errors.append('Candidate has duplicate normalized names')
    states = Counter(r['state'] for r in decisions)
    allowed = {'RETAINED_CLEAR_TARGET_CANDIDATE','DEFERRED_TERRAIN','DEFERRED_SPACING','DEFERRED_OUTSIDE_MAP','DEFERRED_IDENTITY'}
    if set(states)-allowed:errors.append('Unknown decision state')
    retained = {r['name'] for r in decisions if r['state']=='RETAINED_CLEAR_TARGET_CANDIDATE'}
    if set(candidate_names)!=retained:errors.append('Export membership disagrees with retained decisions')
    for r in decisions:
        original=master_by_name.get(r['name'])
        if original and any(str(original[k])!=r.get(k) for k in ('population','city')):
            errors.append('Decision metadata changed: '+r['name'])
        if r['state'].startswith('DEFERRED') and not r.get('reason','').strip():
            errors.append('Deferral has no reason: '+r['name'])
    for town in candidate:
        name=town['name']; original=master_by_name.get(name); decision=decisions_by_name.get(name)
        if original is None:
            errors.append('Export has unknown source town: '+name);continue
        if any(type(town.get(k))!=type(original[k]) or town.get(k)!=original[k] for k in ('name','population','city')):
            errors.append('Source metadata changed: '+name)
        try:tx,ty=independent_target(town['x'],town['y'],size)
        except (ValueError,KeyError,OverflowError) as exc:
            errors.append('Invalid export coordinate: '+name+' '+str(exc));continue
        col,row=size-1-tx,ty
        types=[int(a[ty,tx]) for a,_ in terrains]
        elevation=int(raw[row,col]);clear=elevation>0 and all(v==0 for v in types)
        flat=all(np.ptp(height[ty:ty+2,tx:tx+2])==0 for _,height in terrains)
        if not clear:errors.append('Export target is not source land and clear in both scenarios: '+name)
        recomputed=dict(source_column=col,source_row=row,tile_x=tx,tile_y=ty,raw_elevation=elevation,
                        v1_tile_type=types[0],industries_tile_type=types[1],direct_clear_land=clear,both_saved_flat_corners=flat)
        if decision:
            for k,v in recomputed.items():
                if str(v)!=decision.get(k):errors.append('Stale decision '+k+': '+name)
            for k in ('x','y'):
                if float(decision[k])!=town[k]:errors.append('Decision/export coordinate mismatch '+k+': '+name)
        records.append(dict(name=name,x=town['x'],y=town['y'],**recomputed))
    reviewed={frozenset((r['town_a'],r['town_b'])) for r in spacing if r.get('reason','').strip()}
    close, minimum_actual, minimum_normalized = [], math.inf, math.inf
    nearest={r['name']:(math.inf,'') for r in records}
    for i,a in enumerate(records):
        for b in records[i+1:]:
            actual=math.hypot(a['tile_x']-b['tile_x'],a['tile_y']-b['tile_y'])
            normalized=(size-1)*math.hypot(a['x']-b['x'],a['y']-b['y'])
            minimum_actual=min(minimum_actual,actual);minimum_normalized=min(minimum_normalized,normalized)
            for one,other in ((a,b),(b,a)):
                if actual<nearest[one['name']][0]:nearest[one['name']]=(actual,other['name'])
            if min(actual,normalized)<=30:
                documented=frozenset((a['name'],b['name'])) in reviewed
                close.append(dict(town_a=a['name'],town_b=b['name'],actual_target_distance=round(actual,6),
                                  normalized_distance=round(normalized,6),documented_review=documented))
                if not documented:errors.append('Unreviewed close pair: '+a['name']+' / '+b['name'])
                if min(actual,normalized)<15:errors.append('Sub-15 retained pair needs explicit exception: '+a['name']+' / '+b['name'])
    for r in records:
        d,n=nearest[r['name']];r.update(nearest_actual_town=n,nearest_actual_tiles=round(d,6))
    measured=dict(catalogue_entries=len(master),clear_target_candidate=len(candidate),total_deferred=sum(v for k,v in states.items() if k.startswith('DEFERRED')),
                  clear_candidate_nonflat_targets=sum(not r['both_saved_flat_corners'] for r in records),minimum_spacing_tiles=round(minimum_normalized*size/(size-1),6))
    for k,v in measured.items():
        if claim.get(k)!=v:errors.append('Summary claim mismatch: '+k)
    categories={k:v for k,v in states.items() if k.startswith('DEFERRED')}
    if claim.get('deferred_categories')!=categories:errors.append('Summary deferral categories mismatch')
    return dict(errors=errors,candidate_towns_checked=len(records),master_records=len(master),
                minimum_normalized_4095_distance=round(minimum_normalized,6),minimum_legacy_normalized_4096_distance=round(minimum_normalized*size/(size-1),6),minimum_actual_target_distance=round(minimum_actual,6),
                candidate_close_pairs=len(close),nonflat_targets=measured['clear_candidate_nonflat_targets'],
                deferred_categories=categories),records,close



def audit_comparison(master, exported, decisions, excluded_states):
    errors=[]
    original={t['name']:t for t in master}
    by_name={r['name']:r for r in decisions}
    expected={r['name'] for r in decisions if r['state'] not in excluded_states}
    names=[t['name'] for t in exported]
    if set(names)!=expected or len(names)!=len(set(names)):
        errors.append('Comparison membership mismatch')
    for town in exported:
        name=town['name']
        if name not in original or name not in by_name:continue
        if any(type(town.get(k))!=type(original[name][k]) or town.get(k)!=original[name][k] for k in ('population','city')):
            errors.append('Comparison metadata changed: '+name)
        try:
            independent_target(town['x'],town['y'])
            if any(town[k]!=float(by_name[name][k]) for k in ('x','y')):
                errors.append('Comparison coordinate mismatch: '+name)
        except (ValueError,KeyError,OverflowError):errors.append('Comparison invalid coordinate: '+name)
    return errors


def write_csv(path, records):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)


def run(out):
    from calibrate_heightmap import HASHES
    master_path=ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json'
    if hashlib.sha256(master_path.read_bytes()).hexdigest()!=MASTER_HASH:raise ValueError('Master source hash changed')
    for name,expected in HASHES.items():
        if hashlib.sha256((ROOT/'source_assets'/name).read_bytes()).hexdigest()!=expected:raise ValueError('Original asset hash changed: '+name)
    master=json.loads(master_path.read_bytes());candidate=json.loads((V11/'Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json').read_bytes())
    claim=json.loads((V11/'summary.json').read_bytes())
    with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as image:raw=np.array(image)[:,:,0]
    terrain=[read_terrain(ROOT/'source_assets/scenarios'/n) for n in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]
    report,records,close=audit_candidate(master,candidate,rows(V11/'all_600_decisions.csv'),raw,terrain,rows(V11/'spacing_audit.csv'),claim)
    for path,expected in claim['input_sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:report['errors'].append('V11 input hash mismatch: '+path)
    for label,filename in [('retained_comparison','Europe_1800_V11_RETAINED_COMPARISON_TEST.json'),('all_in_bounds_comparison','Europe_1800_V11_ALL_IN_BOUNDS_COMPARISON_TEST.json')]:
        exported=json.loads((V11/filename).read_bytes())
        if len(exported)!=claim[label]:report['errors'].append('Comparison count mismatch: '+label)
        excluded={'DEFERRED_OUTSIDE_MAP'}
        if label=='retained_comparison':excluded.update({'DEFERRED_SPACING','DEFERRED_IDENTITY'})
        report['errors'].extend(label+': '+message for message in audit_comparison(master,exported,rows(V11/'all_600_decisions.csv'),excluded))
    report.update(scope='Reverse audit of V11 export membership, metadata, importer arithmetic, terrain, flatness, spacing and recorded counts; uses independent scalar importer arithmetic and shares the read-only scenario decoder and preserved-asset hash manifest.',
                  geographic_accuracy_certified=False,in_game_tests=0)
    out.mkdir(parents=True,exist_ok=False)
    (out/'candidate_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    write_csv(out/'candidate_reverse_audit.csv',records);write_csv(out/'candidate_close_pairs.csv',close)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    result=run(parser.parse_args().out);print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
