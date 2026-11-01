"""Reconcile real-engine receipts; preserve raw logs and scoped observations."""
import collections,csv,datetime,difflib,json,re,shutil
from pathlib import Path
from lifecycle_phase7b_runtime import ROOT,BASE,SOURCE,GRF,ENGINE,source7a,guards,sha
from industrial_phase6b_plan import write_csv
from coastal_phase6_preservation import parts,maps
from historical_scenario_migration import inspect
from audit_vehicle_newgrfs import scenario
from vehicle_audit_tables import decode_table

def load(name):return json.loads((BASE/name).read_text())
def date(n):return datetime.date.fromordinal(int(n)-365).isoformat()
def main():
    guards();data=ROOT/'docs/research';raw=data/'phase7b_logs';raw.mkdir(exist_ok=True);runs=[]
    def add(r,scope):
        path=Path(r['log']);assert sha(path)==r['log_sha256'];name=Path(r['case']).name+'-'+path.name;shutil.copyfile(path,raw/name)
        inputs=Path(r['case'])/'inputs.json';runs.append(r|dict(scope=scope,committed_log='docs/research/phase7b_logs/'+name,inputs=json.loads(inputs.read_text()) if inputs.exists() else {}))
        if Path(r['case']).name.startswith('missing-gamescript-'):
            save=Path(r['case'])/'save/autosave/exit.sav';saved=parts(save);clock=decode_table(scenario(save)['DATE'])[0]
            observation=dict(calendar_date=clock['date'],elapsed_calendar_days=clock['date']-668394,industry_count=len(saved['INDY'][1])-1,registered_info_file_absent=not (Path(r['case'])/'game/lifecycle/info.nut').exists(),save_sha256=sha(save))
            assert observation['elapsed_calendar_days']>=120 and observation['industry_count']==542 and observation['registered_info_file_absent']
            runs[-1]['saved_engine_observation']=observation
    add(load('registration.json')['result'],'FULL EUROPE ENGINE: 0.4 baseline type registration')
    add(load('handshake-probe.json'),'FULL EUROPE ENGINE: original neutral mine, unarmed versus one-shot closure')
    add(load('postcheck.json'),'FULL EUROPE ENGINE: post-closure markets and unchanged unmanaged production/control flags')
    comparisons={mode:load('comparison-'+mode+'.json') for mode in ['control','served']}
    for mode,p in comparisons.items():
        for i,r in enumerate(p['runs']):add(r,'FULL EUROPE ENGINE: '+mode+' comparison checkpoint '+str(i))
    for r in load('safety-results.json'):add(r['result'],r['scope']+'; '+r['name'])
    for name in ['roundtrip','migration','controls','soak','dedicated','replay']:
        for r in load('validation-'+name+'.json')['runs']:add(r,'ENGINE VALIDATION: '+name+'; '+Path(r['case']).name)
    # Preserve earlier accepted receipts copied by previous evidence passes.
    # They are archives, not extra passes of the final validation matrix.
    active={Path(r['committed_log']).name for r in runs};available={}
    for case in BASE.iterdir():
        if not case.is_dir():continue
        for receipt in case.glob('*-result.json'):
            r=json.loads(receipt.read_text());available[case.name+'-'+Path(r['log']).name]=r
    archived=[]
    for log in raw.glob('*.log'):
        if log.name in active:continue
        r=available.get(log.name)
        assert r and sha(log)==r['log_sha256'],'Unindexed archived engine log: '+log.name
        archived.append(r|dict(scope='Earlier accepted Phase 7B source version; superseded validation invocation',committed_log='docs/research/phase7b_logs/'+log.name))
    events=[];samples=[];paid=[]
    for run in runs:
        for line in run['observations']:
            if 'P7 EVENT|' not in line:continue
            kind,site,detail=line.split('P7 EVENT|',1)[1].split('|',2)
            values={k:v for k,v in re.findall(r'(?:^|\|)([a-z_]+)=([^|]+)',detail)}
            r=dict(scope=run['scope'],case=Path(run['case']).name,kind=kind,site_id=site,calendar_date=date(values['calendar']) if 'calendar' in values else '',**values,detail=detail,log=run['committed_log'])
            events.append(r)
            if kind=='legacy_sample':samples.append(r)
        for line in Path(run['log']).read_text(encoding='utf8').splitlines():
            if 'I6 CONTROL_PAID|' in line:
                route,vehicle,income,distance,tile=line.split('I6 CONTROL_PAID|')[1].split('|')
                paid.append(dict(scope=run['scope'],route=route,vehicle_id=vehicle,sampled_net_vehicle_income_increase=int(income),distance=int(distance),tile=int(tile),evidence='VERIFIED IN GAME: actual prior loading and positive sampled vehicle income at accepting destination; not gross invoice or annual profitability',log=run['committed_log']))
    write_csv(data/'phase7b_production_service_ledger.csv',samples)
    write_csv(data/'phase7b_warnings.csv',[r for r in events if r['kind'] in ['legacy_warning','legacy_extended','news']])
    write_csv(data/'phase7b_closure_authorization_audit.csv',[r for r in events if r['kind'] in ['legacy_enrolled','legacy_authorization','legacy_closed','legacy_identity_lost','safety_pass']])
    write_csv(data/'phase7b_engine_events.csv',events);write_csv(data/'phase7b_paid_deliveries.csv',paid)
    annual=collections.defaultdict(lambda:dict(production=0,transported=0,samples=0))
    for r in samples:
        if ' comparison checkpoint ' not in r['scope']:continue
        mode=r['scope'].split(': ')[1].split(' comparison')[0];key=(mode,r['site_id'],r['calendar_date'][:4]);row=annual[key]
        row['production']+=int(r['production']);row['transported']+=int(r['transported']);row['samples']+=1
    write_csv(data/'phase7b_annual_observations.csv',[dict(mode=m,site_id=s,observation_year=y,**r,scope='Actual last-month counters grouped by observation calendar year; period lags sample, not invoice-year accounting') for (m,s,y),r in sorted(annual.items())])
    outcomes=[]
    for mode,p in comparisons.items():
        joined=[e for e in events if e['scope'].startswith('FULL EUROPE ENGINE: '+mode+' comparison')]
        for s in p['policy']['sites']:
            subset=[r for r in joined if r['site_id']==s['site_id']]
            warning=next(r for r in subset if r['kind']=='legacy_warning');closed=next(r for r in subset if r['kind']=='legacy_closed')
            extended=[r for r in subset if r['kind']=='legacy_extended']
            outcomes.append(dict(mode=mode,site_id=s['site_id'],industry_id=s['industry_id'],warning_date=warning['calendar_date'],physical_closure_date=closed['calendar_date'],
                actual_warning_days=int(closed['calendar'])-int(warning['calendar']),extended=bool(extended),forecast_after_extension=date(extended[0]['forecast']) if extended else '',
                rolling_transport_at_extension=int(extended[0]['rolling_transported']) if extended else 0,service_percent_at_extension=int(extended[0]['service_percent']) if extended else 0))
    write_csv(data/'phase7b_survival_comparison.csv',outcomes)
    manifest=load('candidate-delivery.json');candidate=Path(manifest['candidate']);before,after=parts(source7a()),parts(candidate)
    a=decode_table(scenario(source7a())['DATE'])[0];b=decode_table(scenario(candidate)['DATE'])[0]
    preserve=dict(source=str(source7a()),source_sha256=sha(source7a()),candidate=str(candidate),candidate_sha256=sha(candidate),towns=617,industries=542,
        unchanged_chunks=[t for t in ['CITY','INDY','PATS','PSAC'] if before[t]==after[t]],all_map_bytes_unchanged=maps(before)==maps(after),
        changed_chunks=sorted(t for t in set(before)|set(after) if before.get(t)!=after.get(t)),date_changed_fields=[k for k in a if a[k]!=b[k]],source_date=a,candidate_date=b)
    oldrefs=inspect(source7a())['newgrfs'];newrefs=inspect(candidate)['newgrfs'];assert len(newrefs)==15
    assert [r for r in oldrefs if r['grfid']!='4B484531']==[r for r in newrefs if r['grfid']!='4B484531']
    assert preserve['all_map_bytes_unchanged'] and preserve['unchanged_chunks']==['CITY','INDY','PATS','PSAC'] and preserve['date_changed_fields']==['id']
    ids={r['grfid'].upper() for r in newrefs};filenames={r['filename'].replace('\\','/').split('/')[-1] for r in newrefs};assets=[];inactive=[]
    for p in (Path(manifest['profile'])/'newgrf').rglob('*'):
        if not p.is_file():continue
        item=dict(path=str(p),sha256=sha(p),format='archive' if p.suffix=='.tar' else 'loose GRF')
        (assets if p.name in filenames or p.name[:8].upper() in ids else inactive).append(item)
    assert len(assets)==15,'Every active GRF must have its actual loose/archive asset hashed'
    manifest.update(embedded_newgrfs=newrefs,required_asset_files=assets,inactive_library_files=inactive,
        info_sha256=sha(Path(manifest['script']).with_name('info.nut')))
    (data/'phase7b_candidate_delivery.json').write_text(json.dumps(manifest,indent=2));(data/'phase7b_preservation_diff.json').write_text(json.dumps(preserve,indent=2))
    state_sizes=[]
    for mode,p in comparisons.items():
        for i in range(4):
            path=Path(p['case'])/f'checkpoint-{i}.sav'
            state_sizes.append(dict(mode=mode,stage=i,path=str(path),sha256=sha(path),file_bytes=path.stat().st_size,gs_state_bytes=sum(len(r) for r in parts(path)['GSDT'][1]),scope='Read-only saved GSDT payload, including full baseline ledger and fixture route state, not only legacy observations'))
    (data/'phase7b_engine_receipts.json').write_text(json.dumps(dict(engine_sha256=sha(ENGINE),grf_sha256=sha(GRF),script_version=2,schema=2,seed=7341830,runs=runs,archived_runs=archived,comparisons=comparisons,state_sizes=state_sizes,
        safety=load('safety-results.json'),validations={name:load('validation-'+name+'.json') for name in ['roundtrip','migration','controls','soak','dedicated','replay']}),indent=2))
    old=json.loads((ROOT/'newgrfs/axis-historical-lifecycle/.work/runtime/candidate-models.json').read_text());new=json.loads((ROOT/'newgrfs/axis-historical-legacy/.work/models.json').read_text());assert old==new
    build=json.loads((ROOT/'newgrfs/axis-historical-legacy/dist/build-result.json').read_text());build.update(models_equal_in_all_six_economies=True,economies={k:dict(industries=len(v['industries']),cargos=len(v['cargo_ids'])) for k,v in new.items()})
    (data/'phase7b_grf_build.json').write_text(json.dumps(build,indent=2))
    patch=[]
    for rel in ['src/templates/header.pynml','src/templates/industry_primary.pynml','src/lang_templates/english.pylng']:
        first=ROOT/'newgrfs/axis-historical-lifecycle/.work/source'/rel;second=ROOT/'newgrfs/axis-historical-legacy/.work/source'/rel
        patch.extend(difflib.unified_diff(first.read_text().splitlines(True),second.read_text().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel,n=0))
    (ROOT/'newgrfs/axis-historical-legacy/source-changes.patch').write_text(''.join(patch))
    print('engine runs',len(runs),'archived',len(archived),'samples',len(samples),'events',len(events),'paid',len(paid));print(json.dumps(outcomes,indent=2))
    guards()
if __name__=='__main__':main()
