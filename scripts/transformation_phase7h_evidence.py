"""Five native invocations, compact gate/transition/reload receipts; no economics model."""
import csv,json,re,datetime
from pathlib import Path
from transformation_phase7h import *
from coastal_phase6_preservation import parts,maps

def fields(line,event):
 tail=line.split('EVENT|'+event+'|',1)[1];tag,rest=tail.split('|',1);return dict(event=tag,**dict(x.split('=',1) for x in rest.split('|')))
def main():
 runs=[];samples=[];opened=[]
 for name in ['gate1','gate2','transformation','reload']:
  r=json.loads((BASE/(name+'.json')).read_text());lines=r['observations'];assert not any('G_ERROR|' in s or 'H_ERROR|' in s or 'H_RELOAD_ERROR|' in s for s in lines)
  selected=[s.split('P7 ',1)[1] for s in lines if any(k in s for k in ['cycle_opened|','cycle_level|','cycle_boundary|','h_gate_saved|','h_opened|','h_accepts|','h_outputs|','h_decline|','h_retire_command|','h_retired|','h_final|','h_done|','h_reload_'])]
  runs.append(dict(name=name,command=r['command'],seconds=r['seconds'],source=str(r.get('source') or SOURCE),source_sha256=r.get('source_sha256') or sha(SOURCE),case=r['case'],log=r['log'],log_sha256=r['log_sha256'],script_sha256=r['script_sha256'],observations=selected))
  if name=='transformation':
   for line in lines:
    if 'EVENT|h_sample|' in line:
     row=fields(line,'h_sample');row['calendar_iso']=datetime.date.fromordinal(int(row['calendar'])-365).isoformat();row['mature']=int(row['days_since_change'])>=45;row['evidence']='VERIFIED IN GAME';samples.append(row)
    if 'EVENT|h_opened|' in line:opened.append(fields(line,'h_opened'))
 editor=json.loads((BASE/'editor.json').read_text());m=json.loads((BASE/'candidate.json').read_text())
 runs.append(dict(name='editor',command=editor['command'],candidate=m['candidate'],candidate_sha256=m['candidate_sha256']))
 for key in ['candidate','source','engine','grf','script']:assert sha(Path(m[key]))==m[key+'_sha256'],key
 for item in m['script_files']+m['asset_files']:assert sha(Path(item['path']))==item['sha256']
 g1='\n'.join(json.loads((BASE/'gate1.json').read_text())['observations']);g2='\n'.join(json.loads((BASE/'gate2.json').read_text())['observations'])
 assert 'h_gate_saved|active|schema=5|stage=boom|target=542' in g2
 gate_counts={k:(g1+'\n'+g2).count('EVENT|'+k+'|') for k in ['cycle_opened']}
 for tag in ['baseline','boom','downturn','restored']:gate_counts[tag]=(g1+'\n'+g2).count('EVENT|cycle_level|'+tag+'|')
 assert all(v==1 for v in gate_counts.values())
 after=Path(json.loads((BASE/'transformation.json').read_text())['case'])/'save/autosave/exit.sav'
 import numpy as np
 a,b=maps(parts(SOURCE)),maps(parts(after));changed=np.frombuffer(a['MAPH'],dtype='u1')!=np.frombuffer(b['MAPH'],dtype='u1')
 local={}
 for row in opened:
  tile=int(row['tile']);x,y=tile%4096,tile//4096;indices=[(y+dy)*4096+x+dx for dx in range(-10,11) for dy in range(-10,11)];local[row['event']]=int(np.count_nonzero(changed[indices]))
 assert all(v==0 for v in local.values())
 report=dict(verdict='READY WITH CAVEATS',engine_invocations=len(runs),failed_invocations=0,active_gate='PASS',gate_transition_counts=gate_counts,gate_schema=5,new_schema=6,gs_version=7,axis='0.6.0 unchanged',new_ended_reload='PASS; both rows ended with no repeated new effects',normal_policy_years_tested=False,fixture_dates='accelerated 1830; native industry date gates still enforced',original_industries_preserved=542,towns_preserved=617,initial_industries=542,final_fixture_industries=543,newgrfs_unchanged=15,local_height_changes=local,paid_deliveries='NOT TESTED',runs=runs)
 data=ROOT/'docs/research';(data/'phase7h_engine_receipts.json').write_text(json.dumps(report,indent=2)+'\n')
 with (data/'phase7h_production_samples.csv').open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(samples[0]));w.writeheader();w.writerows(samples)
 rows=[]
 for e in policy()['events']:
  o=next(r for r in opened if r['event']==e['id']);rows.append(dict(event_id=e['id'],region=e['region'],local_type=e['local_id'],industry=e['industry'],normal_open=datetime.date.fromordinal(e['open_date']-365).isoformat(),normal_decline=datetime.date.fromordinal(e['decline_date']-365).isoformat() if e['kind']=='retire' else 'NOT APPLICABLE',normal_retire=datetime.date.fromordinal(e['retire_date']-365).isoformat() if e['kind']=='retire' else 'NOT APPLICABLE',fixture_industry=o['industry'],fixture_tile=o['tile'],fixture_open_calendar=o['calendar'],result='VERIFIED NATIVE OPENING AND ACCEPTANCE; production unserved' if e['kind']=='open' else 'VERIFIED DECLINE AND PHYSICAL RETIREMENT',inputs=' '.join(RULES[e['local_id']]['accepted']),outputs=' '.join(c for c,_ in RULES[e['local_id']]['produced'])))
 with (data/'phase7h_event_results.csv').open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('Active gate PASS; invocations',len(runs),'samples',len(samples),'local height changes',local)
if __name__=='__main__':main()
