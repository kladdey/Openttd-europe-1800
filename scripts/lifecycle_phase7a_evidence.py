"""Portable source receipts and real-engine observations, with explicit scopes."""
import csv,datetime,difflib,json,re,shutil
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,ENGINE,GRF,SOURCE,sha,guards
from industrial_phase6b_plan import write_csv

def load(name):return json.loads((BASE/name).read_text(encoding='utf8'))

def main():
    guards();runs=[];engine_digest=sha(ENGINE)
    def add(result,scope,label):
        log=Path(result['log']);assert sha(log)==result['log_sha256']
        inputs=Path(result['case'])/'inputs.json'
        runs.append(result|dict(scope=scope,label=label,inputs=json.loads(inputs.read_text()) if inputs.exists() else {},
            extra_measurements=[s for s in log.read_text(encoding='utf8').splitlines() if any(k in s for k in ['I6 CONTROL_PAID|','P7 ','I6 PERIOD_ENGINE|','P4_COMMISSION|'])]))
    for i,r in enumerate(load('probes.json')):add(r,'SMALL MAP ENGINE PROBE',['original 0.3 policy','0.4 default off','0.4 opt-in construction and closure'][i])
    small=Path((BASE/'vertical-slice-case.txt').read_text())
    for stage in ['initial','reloaded']:add(json.loads((small/(stage+'-result.json')).read_text()),'SMALL MAP ENGINE: ACCELERATED TEST DATES','vertical slice '+stage)
    for i,r in enumerate(load('natural-controls.json')):add(r,'SMALL MAP ENGINE: FIVE-YEAR NATURAL CONTROL','0.3 control' if i==0 else '0.4 selective policy')
    add(load('historical-soak.json'),'SMALL MAP ENGINE: ORDINARY OPENING DATES','1830 to 1861')
    add(load('ten-year-warnings.json')['result'],'SMALL MAP ENGINE: REAL TEN-YEAR WARNING','30-year test lifetimes; actual decade notice')
    add(load('europe-smoke.json')['result'],'FULL EUROPE ENGINE: SNAPSHOT','617 towns / 542 industries / clock / acceptance')
    europe=Path(load('europe-slice.json')['case'])
    for stage in ['initial','reloaded']:add(json.loads((europe/(stage+'-result.json')).read_text()),'FULL EUROPE ENGINE: ACCELERATED REGIONAL TEST','Europe vertical slice '+stage)
    replay=load('checkpoint-replay.json')
    for i,r in enumerate(replay['runs']):add(r,'SMALL MAP ENGINE: SAME-CHECKPOINT REPLAY','Replay '+str(i+1))
    add(replay['post_closure_reload'],'SMALL MAP ENGINE: POST-CLOSURE RELOAD','No resurrected industry/event')
    migration=load('schema-migration.json');home=Path(migration['case'])
    for stage in ['legacy','upgraded']:add(json.loads((home/(stage+'-result.json')).read_text()),'SMALL MAP ENGINE: SUPPORTED SAVE MIGRATION',stage)
    add(load('dedicated-smoke.json'),'LOOPBACK DEDICATED SERVER SMOKE','Actual dedicated driver and multiplayer=true; no human clients')
    delivery=load('candidate-delivery.json')
    from coastal_phase6_preservation import parts,maps
    from audit_vehicle_newgrfs import scenario
    from vehicle_audit_tables import decode_table
    from historical_scenario_migration import inspect
    source_parts,candidate_parts=parts(SOURCE),parts(Path(delivery['candidate']))
    source_date=decode_table(scenario(SOURCE)['DATE'])[0];candidate_date=decode_table(scenario(Path(delivery['candidate']))['DATE'])[0]
    preservation=dict(changed_chunks=sorted(k for k in set(source_parts)|set(candidate_parts) if source_parts.get(k)!=candidate_parts.get(k)),
        date_changed_fields=[k for k in source_date if source_date[k]!=candidate_date[k]],source_date=source_date,candidate_date=candidate_date,
        unchanged_record_chunks=[k for k in ['CITY','INDY','PATS','PSAC'] if source_parts[k]==candidate_parts[k]],
        all_map_bytes_unchanged=maps(source_parts)==maps(candidate_parts),embedded_newgrfs=inspect(Path(delivery['candidate']))['newgrfs'])
    assert preservation['date_changed_fields']==['id'] and preservation['all_map_bytes_unchanged']
    for i,r in enumerate(delivery['actual_production_script_gameplay_save_reload']):add(r,'FULL EUROPE ENGINE: EXACT PRODUCTION SCRIPT','Production bundle round trip '+str(i+1))
    for row in load('boundary-tests.json'):add(row['result'],row['scope'],row['name'])
    add(load('schedule-contract-rejection.json'),'FULL EUROPE ENGINE: EXPECTED SAFE REJECTION','One-day schedule edit rejected without reset')
    records=[];paid=[]
    for run in runs:
        case_id=Path(run['case']).name+'/'+Path(run['log']).stem
        for line in run['observations']:
            payload=line.split('P7 ',1)[1]
            if payload.startswith('EVENT|'):
                _,event,event_id,detail=payload.split('|',3)
                if event in ['status','production','construction_context']:continue
            else:event,event_id,detail=payload.split('|',1)[0],'',payload
            def number(name):
                match=re.search(r'(?:^|\|)'+name+r'=(\d+)',detail);return int(match.group(1)) if match else ''
            calendar=number('calendar') or (number('warn') if event=='decline' else '')
            tile=number('tile');width=4096 if 'EUROPE' in run['scope'] else 256
            records.append(dict(case_id=case_id,scope=run['scope'],event=event,event_id=event_id,calendar_date=str(datetime.date.fromordinal(calendar-365)) if calendar else '',
                calendar_engine_date=calendar,economy_engine_date=number('economy'),industry_id=number('industry') if number('industry')!='' else number('old_industry'),
                tile=tile,x=tile%width if tile!='' else '',y=tile//width if tile!='' else '',details=detail,
                engine_log=run['log'],engine_log_sha256=run['log_sha256'],script_sha256=run['script_sha256'],grf_sha256=run['inputs'].get('grf_sha256',''),engine_sha256=engine_digest,scheduler_seed=7341830))
        for line in run['extra_measurements']:
            if 'I6 CONTROL_PAID|' not in line:continue
            route,vehicle,increase,distance,tile=line.split('I6 CONTROL_PAID|',1)[1].split('|')
            paid.append(dict(case_id=case_id,scope=run['scope'],route=route,vehicle_id=int(vehicle),sampled_net_vehicle_profit_increase=int(increase),distance_to_accepting_stop=int(distance),vehicle_tile=int(tile),
                evidence='VERIFIED IN GAME: loaded cargo followed by positive sampled vehicle profit near destination; not gross shipment invoice',engine_log=run['log']))
    data=ROOT/'docs/research'
    write_csv(data/'phase7a_engine_events.csv',records);write_csv(data/'phase7a_paid_deliveries.csv',paid)
    (data/'phase7a_engine_run_evidence.json').write_text(json.dumps(runs,indent=2),encoding='utf8')
    persistence=dict(small_vertical_slice=load('vertical-slice.json'),europe_vertical_slice=load('europe-slice.json'),checkpoint_replay=replay,schema_migration=migration,
        safe_rejection_and_boundaries=load('boundary-tests.json'),schedule_edit_rejection=load('schedule-contract-rejection.json'),production_roundtrips=delivery['actual_production_script_gameplay_save_reload'])
    (data/'phase7a_save_reload_results.json').write_text(json.dumps(persistence,indent=2))
    for source,target in [('candidate-delivery.json','phase7a_candidate_delivery.json'),('visible-warning.json','phase7a_warning_visibility.json'),('europe-test-schedule.json','phase7a_europe_test_schedule.json'),('natural-controls.json','phase7a_natural_spawning_controls.json'),('ten-year-warnings.json','phase7a_ten_year_warnings.json'),('dedicated-smoke.json','phase7a_dedicated_smoke.json')]:
        shutil.copyfile(BASE/source,data/target)
    (data/'phase7a_candidate_delivery.json').write_text(json.dumps(delivery|dict(initial_preservation=preservation),indent=2))
    build=json.loads((ROOT/'newgrfs/axis-historical-lifecycle/dist/build-result.json').read_text());build['reproduction']=load('build-reproduction.json')
    (data/'phase7a_grf_build.json').write_text(json.dumps(build,indent=2))
    old=ROOT/'newgrfs/axis-historical-copper-salt/.work/source';new=ROOT/'newgrfs/axis-historical-lifecycle/.work/source';patch=[]
    for rel in ['src/templates/header.pynml','src/templates/availability.pynml','src/templates/historical_location.pynml','src/templates/industry_primary.pynml','src/lang_templates/english.pylng']:
        patch.extend(difflib.unified_diff((old/rel).read_text(encoding='utf8').splitlines(True),(new/rel).read_text(encoding='utf8').splitlines(True),fromfile='a/'+rel,tofile='b/'+rel,n=0))
    (ROOT/'newgrfs/axis-historical-lifecycle/source-changes.patch').write_text(''.join(patch),encoding='utf8')
    source_root=ROOT.parent/'openttd-europe-1830-2025-historical-industry/.research/jgr734/src'
    names=['company_type.h','newgrf_callbacks.h','newgrf_industries.cpp','industry_cmd.cpp','script/api/script_industrytype.cpp','script/api/script_industry.hpp','script/api/script_industry.cpp','script/api/script_date.cpp','script/api/script_story_page.hpp','story.cpp','script/api/script_news.hpp','game/game_core.cpp','video/dedicated_v.cpp']
    (data/'phase7a_engine_source_receipts.json').write_text(json.dumps(dict(source_root=str(source_root),engine_sha256=sha(ENGINE),files={name:sha(source_root/name) for name in names}),indent=2))
    print('Retained engine runs:',len(runs),'event records:',len(records),'paid observations:',len(paid))

if __name__=='__main__':main()
