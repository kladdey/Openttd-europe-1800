#!/usr/bin/env python3
"""V11 follow-up to the 28 V10 terrain deferrals, without launching OpenTTD."""
import argparse
import collections
import json
from pathlib import Path

import geography as g
import resolve_terrain_flags as r
from review_europe_placements import rows

PROFILE=g.ROOT/'data/geography/placement_profile_v11.json'
RESEARCH=g.ROOT/'data/geography/remaining_case_research_v11.csv'
EXCLUSIONS=g.ROOT/'data/geography/source_exclusions_v11.csv'
V10=g.ROOT/'maps/calibration/geography_v10'


def generate(assets,out):
    if out.exists():raise FileExistsError('Use a new output directory')
    prior=rows(V10/'terrain_resolution.csv')
    pending={a['name'] for a in prior if a['decision']=='TEMPORARILY_DEFER_TERRAIN'}
    research=rows(RESEARCH)
    if len(research)!=len(pending) or {a['name'] for a in research}!=pending:
        raise ValueError('Every V10 terrain deferral needs an explicit follow-up')
    summary=r.generate(assets,out,PROFILE)
    settings=r.load_profile(PROFILE)
    before={t['name']:t for t in g.read_json(V10/r.FULL)}
    after={t['name']:t for t in g.read_json(out/settings['full'])}
    old_core={t['name'] for t in g.read_json(V10/r.CORE)}
    core={t['name'] for t in g.read_json(out/settings['core'])}
    changed={name for name in before if before[name]!=after[name]}
    restored=core-old_core
    if set(before)!=set(after) or not old_core<=core or changed!=restored or not restored<=pending:
        raise ValueError('Follow-up unexpectedly changes the existing candidate or comparison coverage')
    refs=rows(out/'historic_reference_audit.csv')
    oldrefs=rows(V10/'historic_reference_audit.csv')
    oldids={a['reference_id'] for a in oldrefs}
    by_id={a['reference_id']:a for a in refs}
    records=[]
    for note in research:
        name=note['name'];new=[a for a in refs if a['name']==name and a['reference_id'] not in oldids]
        oldpixels={(a['tile_x'],a['tile_y']) for a in oldrefs if a['name']==name}
        newpixels={(a['tile_x'],a['tile_y']) for a in new}
        status=('REINSTATED_CLEAR_HISTORIC_SITE' if name in restored else
                'CLEAR_REFERENCE_HELD_FOR_REVIEW' if any(a['direct_clear_land']=='True' and a['eligible']=='False' for a in new) else
                'NO_CONFIRMED_NEW_POINT' if not new else 'RESEARCHED_POINTS_STILL_UNSUITABLE')
        records.append(dict(note,outcome=status,new_references=len(new),distinct_new_import_pixels=len(newpixels-oldpixels),
            clear_new_references=sum(a['direct_clear_land']=='True' for a in new),
            held_clear_references=sum(a['direct_clear_land']=='True' and a['eligible']=='False' for a in new),
            remains_deferred=name not in restored))
    deltas=[]
    for name in sorted(changed):
        ref=by_id[next(a['reference_id'] for a in rows(out/'terrain_resolution.csv') if a['name']==name)]
        deltas.append(dict(name=name,old_x=before[name]['x'],old_y=before[name]['y'],new_x=after[name]['x'],new_y=after[name]['y'],
            shift_tiles=round(g.distance(before[name],after[name]),6),feature=ref['feature'],reference_id=ref['reference_id'],
            coordinate_source=ref['coordinate_source'],history_source=ref['history_source'],placement_review=ref['placement_review'],
            founding='UNTESTED'))
    r.write_csv(out/'v10_to_v11_changes.csv',deltas)
    r.write_csv(out/'remaining_case_review.csv',records)
    exclusions=rows(EXCLUSIONS);r.write_csv(out/'source_exclusions.csv',exclusions)
    all_decisions=rows(out/'all_600_decisions.csv')
    balance=[]
    for region in sorted({a['region'] for a in all_decisions}):
        group=[a for a in all_decisions if a['region']==region]
        balance.append(dict(region=region,master_records=len(group),retained=sum(a['name'] in core for a in group),
            deferred=sum(a['name'] not in core for a in group),added_since_v10=sum(a['name'] in restored for a in group)))
    r.write_csv(out/'regional_balance.csv',balance)
    summary.update(previous_version='V10',v10_pending_cases_reviewed=len(pending),new_historic_references=sum(a['reference_id'] not in oldids for a in refs),
        reinstated_since_v10=len(restored),remaining_terrain_cases=len(pending-restored),clear_references_held=sum(a['held_clear_references'] for a in records),
        excluded_source_attempts=len(exclusions),existing_v10_candidate_preserved=True,
        follow_up_outcomes=dict(collections.Counter(a['outcome'] for a in records)))
    for p in (RESEARCH,EXCLUSIONS):summary['input_sha256'][str(p.relative_to(g.ROOT))]=g.digest(p)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assets',type=Path,default=g.ROOT/'source_assets')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(generate(a.assets,a.out),indent=2))
