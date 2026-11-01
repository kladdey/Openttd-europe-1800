"""Reconcile immutable raw receipts; never infer payment from pickup alone."""
import csv,datetime,hashlib,json,re,shutil
from pathlib import Path
from lifecycle_phase7c_runtime import *
from coastal_phase6_preservation import parts,maps
from historical_scenario_migration import inspect
from industrial_phase6b_plan import write_csv
DATA=ROOT/'docs/research'
def date(n):return (datetime.date.fromordinal(int(n)-365)).isoformat()
def main():
 guards();delivery=json.loads((BASE/'candidate-delivery.json').read_text());profile=Path(delivery['profile']);candidate=Path(delivery['candidate'])
 before,after=parts(SOURCE),parts(candidate)
 for tag in ['CITY','INDY','PATS','PSAC']:assert before[tag]==after[tag],tag
 assert maps(before)==maps(after)
 original,new=inspect(SOURCE),inspect(candidate)
 assert len(new['newgrfs'])==15
 for a,b in zip(original['newgrfs'],new['newgrfs']):
  assert a['grfid']==b['grfid'] and a['params']==b['params']
  if a['grfid']!='4B484531':assert a==b
 target=Path.home()/'Documents/OpenTTD/scenario'/candidate.name
 if target.exists():assert sha(target)==sha(candidate),'Refusing to overwrite a prior scenario'
 else:
  with target.open('xb') as f:f.write(candidate.read_bytes())
 delivery.update(candidate=str(target),profile_candidate=str(candidate),candidate_sha256=sha(target),info_sha256=sha(profile/'game/lifecycle/info.nut'),expansion_policy_sha256=sha(profile/'game/lifecycle/expansion_policy.nut'),
  required_asset_files=[dict(path=str(p),sha256=sha(p)) for folder in ['newgrf','baseset'] for p in sorted((profile/folder).rglob('*')) if p.is_file()],
  newgrfs=new['newgrfs'],source=str(SOURCE),source_sha256=sha(SOURCE),baseline_commit='6c6f8dd7519bb0e8878bc362e3b0c793ca47cc1c',test_dates=False)
 (DATA/'phase7c_candidate_delivery.json').write_text(json.dumps(delivery,indent=2))
 (DATA/'phase7c_preservation_diff.json').write_text(json.dumps(dict(source=str(SOURCE),candidate=str(target),source_sha256=sha(SOURCE),candidate_sha256=sha(target),unchanged=['CITY','INDY','PATS','PSAC','ALL 16777216 MAP TILES/ALL PLANES'],towns=617,industries=542,newgrfs=15,train_limit=7,calendar_start=1830,economy_start=1800,newgrf_parameters_unchanged=True,original_files_unchanged=True),indent=2))
 logdir=DATA/'phase7c_logs';logdir.mkdir(exist_ok=True);(logdir/'.gitattributes').write_text('*.log -text -whitespace\n')
 receipts=[];events=[];paid=[];capacity=[]
 for scope in ['controls','europe','waves-europe','waves-mini','capacity','regression-7b','safety-blocked','safety-native','safety-replay','safety-dedicated','safety-assets','safety-off','candidate-roundtrip']:
  path=BASE/(scope+'.json');assert path.exists(),f'Missing required evidence: {scope}'
  data=json.loads(path.read_text());runs=data if isinstance(data,list) else data.get('runs',[data.get('run',data)])
  for index,r in enumerate(runs):
   src=Path(r['log']);assert sha(src)==r['log_sha256'];archive=logdir/f'{scope}-{index}.log';shutil.copyfile(src,archive)
   assert sha(archive)==r['log_sha256'];inputs=json.loads((Path(r['case'])/'inputs.json').read_text())
   assert inputs['grf_sha256']==sha(GRF),'Superseded prototype receipt: '+scope
   row=dict(r,scope=scope,archived_log=archive.relative_to(ROOT).as_posix(),grf_sha256=inputs['grf_sha256']);receipts.append(row)
   for line in src.read_text(encoding='utf8').splitlines():
    if 'P7 EVENT|' in line:
     name,event_id,details=line.split('P7 EVENT|',1)[1].split('|',2);m=re.search(r'(?:calendar|born)=(\d+)',details)
     events.append(dict(scope=scope,run=index,event=name,event_id=event_id,calendar_date=date(m[1]) if m else '',details=details))
    if 'I6 CONTROL_PAID|' in line:
     tag,vehicle,sampled_net,distance,tile=line.split('I6 CONTROL_PAID|')[1].split('|')
     paid.append(dict(scope=scope,route=tag,vehicle_id=vehicle,positive_sampled_net_gbp=sampled_net,distance_to_destination=distance,tile=tile,evidence='VERIFIED IN GAME: prior loaded observation and positive vehicle-profit delta near destination; not gross revenue'))
    m=re.search(r'C_CAPACITY\|elapsed=(\d+)\|level=(\d+)\|grain_stock=(\d+)\|food_produced=(\d+)',line)
    if m:capacity.append(dict(zip(['elapsed_economy_days','level','grain_stock','last_month_food'],map(int,m.groups()))))
 (DATA/'phase7c_engine_receipts.json').write_text(json.dumps(receipts,indent=2));write_csv(DATA/'phase7c_engine_events.csv',events);write_csv(DATA/'phase7c_paid_deliveries.csv',paid);write_csv(DATA/'phase7c_capacity_observations.csv',capacity)
 build=json.loads((ROOT/'newgrfs/axis-historical-expansion/dist/build-result.json').read_text());(DATA/'phase7c_grf_build.json').write_text(json.dumps(build,indent=2))
 print('Receipts',len(receipts),'paid observations',len(paid),'candidate',target,sha(target))
if __name__=='__main__':main()
