#!/usr/bin/env python3
"""Implement the coverage research queue conservatively using frozen V6 calibration."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from build_coverage_additions import ROOT, audit, write_csv
from build_full_import import BASELINE as OLD_BASELINE, ADDITIONS as OLD_ADDITIONS, combine, check_spacing, read_rows
from calibrate_heightmap import HASHES
from scenario_geography import read_terrain
from validate_inland_features import MODEL, load_frozen_model

CONFIG=ROOT/'data/geography/gap_additions_v1.json'
BASELINE=ROOT/'maps/calibration/geography_v12/Europe_1800_V12_568_TOWN_FULL_IMPORT_TEST.json'
ADDITIONS='Europe_1800_V13_ADDITIONS_ONLY_TEST.json'
FULL='Europe_1800_V13_FULL_IMPORT_TEST.json'

def run(out):
    baseline=json.loads(BASELINE.read_bytes())
    if hashlib.sha256(BASELINE.read_bytes()).hexdigest()!='753868a44669ff923e2fe74f5a904bd662a5aff69420961a044c92ebd8868f95':raise ValueError('V12 changed')
    for name,sha in HASHES.items():
        if hashlib.sha256((ROOT/'source_assets'/name).read_bytes()).hexdigest()!=sha:raise ValueError('Original asset changed: '+name)
    master_path=ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json'
    if hashlib.sha256(master_path.read_bytes()).hexdigest()!='6e4d9ebc4f489c7a83742e63f0599f94158f889c435e02b96110769503339410':raise ValueError('Master changed')
    cfg=json.loads(CONFIG.read_bytes());coeffs,_=load_frozen_model(MODEL)
    with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as image:raw=np.array(image)[:,:,0]
    terrains=[read_terrain(ROOT/'source_assets/scenarios'/name) for name in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]
    results,probes,pairs=audit(cfg,baseline,json.loads(master_path.read_bytes()),[],raw,terrains,coeffs)
    retained=[r for r in results if r['status']=='RETAIN_ADDITION_TEST']
    deferred=[r for r in results if r['status']!='RETAIN_ADDITION_TEST']
    additions=[dict(name=r['export_name'],population=r['population'],city=r['city'],x=r['x'],y=r['y']) for r in retained]
    full=combine(baseline,additions)
    review_paths=[ROOT/'maps/calibration/geography_v11/spacing_audit.csv',ROOT/'maps/calibration/coverage_additions_v1/spacing_review.csv']
    spacing=check_spacing(full,[r for p in review_paths for r in read_rows(p)]+pairs)
    out.mkdir(parents=True,exist_ok=False)
    for name,items in ((ADDITIONS,additions),(FULL,full)):(out/name).write_text(json.dumps(items,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for name,items in [('all_candidate_decisions.csv',results),('deferred_towns.csv',deferred),('nearest_neighbours.csv',retained),('sensitivity_probes.csv',probes),('new_spacing_review.csv',pairs),('combined_spacing_audit.csv',spacing)]:write_csv(out/name,items)
    summary=dict(version='V13',baseline_towns=len(baseline),research_candidates=len(results),additions=len(additions),full_import_towns=len(full),deferred=len(deferred),retained_by_region=dict(Counter(r['region'] for r in retained)),deferred_by_reason=dict(Counter(r['status'] for r in deferred)),baseline_records_unchanged=full[:len(baseline)]==baseline,nonflat_addition_targets=sum(not r['both_saved_flat_corners'] for r in retained),config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),output_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in (ADDITIONS,FULL)},limitations='Offline candidate only. Published city points are approximate. Nine half-pixel probes do not bound registration uncertainty. Two supplied source scenarios are not the user saved 568-town map. Actual founding, historic bank/coast placement, realized population and growth need in-game checks. Six earlier held centres remain held; no restoration or relocation is attempted.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True,type=Path)
    print(json.dumps(run(parser.parse_args().out),indent=2,ensure_ascii=False))
