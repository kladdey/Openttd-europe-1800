#!/usr/bin/env python3
"""Combine the V11 baseline and audited coverage additions without changing records."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from geography import validate
from build_coverage_additions import key
from reverse_audit import independent_target

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'maps/calibration/geography_v11/Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json'
ADDITIONS=ROOT/'maps/calibration/coverage_additions_v1/Europe_1800_ALL_COVERAGE_ADDITIONS_V1_TEST.json'
OUTPUT='Europe_1800_V12_568_TOWN_FULL_IMPORT_TEST.json'


def combine(baseline,additions):
    validate(baseline);validate(additions)
    result=baseline+additions
    validate(result)
    names=[key(t['name']) for t in result]
    if len(names)!=len(set(names)):raise ValueError('Duplicate town identity across imports')
    for t in result:independent_target(t['x'],t['y'])
    return result


def read_rows(path):
    with path.open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))


def check_spacing(towns,reviews):
    documented={frozenset((r['town_a'],r['town_b'])) for r in reviews if r.get('reason','').strip()}
    coords=[independent_target(t['x'],t['y']) for t in towns]
    result=[]
    for i,a in enumerate(towns):
        for j in range(i+1,len(towns)):
            b=towns[j];actual=math.dist(coords[i],coords[j]);normalized=4095*math.hypot(a['x']-b['x'],a['y']-b['y'])
            if min(actual,normalized)>30:continue
            if min(actual,normalized)<15:raise ValueError('Sub-15 pair needs explicit review: '+a['name']+' / '+b['name'])
            if frozenset((a['name'],b['name'])) not in documented:raise ValueError('Close pair lacks review: '+a['name']+' / '+b['name'])
            result.append(dict(town_a=a['name'],town_b=b['name'],actual_target_distance=round(actual,6),normalized_4095_distance=round(normalized,6),documented_review=True))
    return result


def run(out):
    baseline=json.loads(BASELINE.read_bytes());additions=json.loads(ADDITIONS.read_bytes())
    full=combine(baseline,additions)
    review_paths=[ROOT/'maps/calibration/geography_v11/spacing_audit.csv',ROOT/'maps/calibration/coverage_additions_v1/spacing_review.csv']
    pairs=check_spacing(full,[r for p in review_paths for r in read_rows(p)])
    out.mkdir(parents=True,exist_ok=False)
    encoded=json.dumps(full,indent=2,ensure_ascii=False)+'\n'
    (out/OUTPUT).write_text(encoded,encoding='utf-8')
    with (out/'combined_spacing_audit.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(pairs[0]));writer.writeheader();writer.writerows(pairs)
    summary=dict(version='V12',baseline_towns=len(baseline),additions=len(additions),full_import_towns=len(full),
                 baseline_records_unchanged=full[:len(baseline)]==baseline,addition_records_unchanged=full[len(baseline):]==additions,
                 reviewed_close_pairs=len(pairs),minimum_actual_target_spacing=round(min(r['actual_target_distance'] for r in pairs),6),
                 intended_use='One import into a fresh empty 4096x4096 map; do not load into an already populated checkpoint.',
                 input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASELINE,ADDITIONS,*review_paths]},
                 output_sha256=hashlib.sha256(encoded.encode('utf-8')).hexdigest(),new_coordinate_changes=0,
                 validation='Exact composition of previously tested components. User confirmed completion after the 568-town count/save prompt; no save file supplied and no fresh-map V12 full-import test independently observed.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(run(parser.parse_args().out),indent=2))
