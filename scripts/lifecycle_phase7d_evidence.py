"""Compact receipts and coverage. Large native logs stay in the local profiles."""
import csv,datetime,json,re
from pathlib import Path
from lifecycle_phase7d_runtime import *
from lifecycle_phase7d_policy import production,RULES,DATA
from coastal_phase6_preservation import parts,maps,differences
def main():
 guards();receipts=[];coverage={};p=production()
 for scope in ['modern-smoke','europe','timeline','guard','legacy','startup']:
  data=json.loads((BASE/(scope+'.json')).read_text());runs=data.get('runs',[data.get('run',data)])
  for index,r in enumerate(runs):
   log=Path(r['log']);assert sha(log)==r['log_sha256'];observations=r['observations']
   markers={'modern-smoke':'D_SMOKE_DONE|constructed=4','europe':'d_europe_done|fixture|baseline_intact=542|towns=617','timeline':'d_boundary|timeline|','guard':'D_GUARD|optin_off_available=false|unplanned=0','legacy':'BPROBE_DONE','startup':'d_autosave|candidate|temporary_parent_view=3|serialized_root=4'}
   assert any(markers[scope] in line for line in observations),scope+' did not reach its claimed outcome'
   selected=[s.split('P7 ',1)[1] for s in observations if any(t in s for t in ['D_BUILT|','D_SITE_COUNTS|','D_COLLECTION_PRODUCTION|','D_SMOKE_DONE|','D_GUARD|','BPROBE_DONE','BCLOSE|','d_event_final|','d_boundary|','d_startup|','d_autosave|','d_europe_done|','expansion_opened|','d_fixture_house|'])]
   receipts.append(dict(scope=scope,part=index,command=r['command'],engine_sha256=sha(ENGINE),grf_sha256=sha(GRF),script_sha256=r['script_sha256'],seconds=r['seconds'],raw_log=r['log'],raw_log_sha256=r['log_sha256'],outcome='OBSERVED; see scope limitations',observations=selected))
   for s in observations:
    m=re.search(r'EVENT\|d_event_final\|([^|]+)\|state=([^|]+)\|attempts=(\d+)',s)
    if m:coverage[(scope,m[1])]=(m[2],m[3])
 # Count failed compile attempts too; do not disguise them as completed tests.
 failures=[]
 for log in BASE.glob('*/part0.log'):
  text=log.read_text(encoding='utf8',errors='replace')
  if 'Failed to compile' in text:failures.append(dict(log=str(log),sha256=sha(log),outcome='SCRIPT SYNTAX FAILURE; corrected before successful timeline'))
 for log in BASE.glob('off-natural-control-*/engine.log'):
  if 'Failed to compile' in log.read_text(errors='replace'):failures.append(dict(log=str(log),sha256=sha(log),outcome='FIXTURE SYNTAX FAILURE; corrected before successful guard'))
 report=dict(successful_engine_invocations=len(receipts),failed_compile_invocations=failures,total_invocations=len(receipts)+len(failures),engine_version='stock JGRPP 0.73.4',scope_note='Construction/registration and limited production; no new paid modern cargo chain or multiplayer certification',receipts=receipts)
 (DATA/'phase7d_test_receipts.json').write_text(json.dumps(report,indent=2))
 rows=[]
 for e in p['events']:
  a=coverage.get(('europe',e['event_id']));b=coverage.get(('timeline',e['event_id']))
  rows.append(dict(event_id=e['event_id'],region=e['region'],local_id=e['local_id'],action=e['action'],policy_year=datetime.date.fromordinal(e['open_date']-365).year,
   europe_fixture=a[0] if a else 'NOT TESTED',timeline_fixture=b[0] if b else 'NOT IN EARLIER 28-EVENT FIXTURE',
   evidence='VERIFIED CONSTRUCTION at fixture dates only' if (a and a[0]=='built') or (b and b[0]=='built') else 'UNVERIFIED OR CONDITIONAL',
   inputs=' '.join(e['inputs']),outputs=' '.join(label for label,_ in e['outputs'])))
 with (DATA/'phase7d_event_coverage.csv').open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 native=[dict(local_id=i,industry=RULES[i]['industry'],earliest_year=RULES[i]['earliest_year'],inputs=RULES[i]['accepted'],outputs=RULES[i]['produced'],layouts=RULES[i]['layouts'],tile_checks=RULES[i]['tile_location_checks'],industry_checks=RULES[i]['industry_location_checks']) for i in [24,25,23,18,56,79]]
 (DATA/'phase7d_native_rules.json').write_text(json.dumps(dict(grf_sha256=sha(GRF),unchanged_cargo_slots=64,rules=native),indent=2))
 delivery=json.loads((BASE/'candidate.json').read_text());before,after=parts(SOURCE),parts(Path(delivery['candidate']))
 for tag in ['CITY','INDY','PATS','PSAC']:assert before[tag]==after[tag],tag
 assert maps(before)==maps(after)
 m=json.loads((BASE/'europe.json').read_text());fixture=Path(m['run']['command'][m['run']['command'].index('-g')+1]);saved=Path(m['run']['case'])/'save/autosave/exit.sav'
 a,b,changed,diff=differences(fixture,saved)
 import numpy as np
 at=np.frombuffer(a['MAPT'],dtype='u1')>>4;bt=np.frombuffer(b['MAPT'],dtype='u1')>>4
 infra=np.isin(at,[1,2,5,9]);removed=int(np.count_nonzero(infra & (at!=bt)))
 opened=[int(re.search(r'tile=(\d+)',s)[1]) for s in m['run']['observations'] if 'expansion_opened|' in s]
 heights=np.flatnonzero(np.frombuffer(a['MAPH'],dtype='u1')!=np.frombuffer(b['MAPH'],dtype='u1'))
 waters=np.flatnonzero((at==6)!=(bt==6))
 distance=lambda t:min(abs(int(t)%4096-i%4096)+abs(int(t)//4096-i//4096) for i in opened)
 nearby_height=sum(distance(t)<=16 for t in heights);nearby_water=sum(distance(t)<=16 for t in waters)
 assert nearby_height==0 and nearby_water==0 and removed==0,(diff,removed)
 (DATA/'phase7d_preservation.json').write_text(json.dumps(dict(initial_towns=617,initial_industries=542,initial_map_all_planes_identical=True,initial_CITY_INDY_PATS_PSAC_identical=True,newgrf_references_identical_to_7c=True,train_limit=7,calendar_start=1830,economy_start=1800,
  europe_runtime=diff,europe_height_changes_within_16_tiles_of_openings=nearby_height,europe_water_changes_within_16_tiles_of_openings=nearby_water,
  minimum_height_change_distance_from_openings=min(map(distance,heights),default=None),
  runtime_note='Simulation updated remote map tiles. Not a claim of a globally frozen runtime map. No terrain/water commands in GS, no height/water changes near placements.',
  europe_removed_existing_rail_road_station_bridge_tiles=removed,source_sha256=sha(SOURCE),candidate_sha256=delivery['candidate_sha256']),indent=2))
 print('Completed engine invocations',len(receipts),'compile failures',len(failures),'runtime preservation',diff)
if __name__=='__main__':main()
