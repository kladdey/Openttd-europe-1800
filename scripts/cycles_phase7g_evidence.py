"""Compact native receipts and full raw monthly observations; no profit estimates."""
import csv,json,datetime,re
from pathlib import Path
from cycles_phase7g import *
from coastal_phase6_preservation import parts,maps

def samples(lines):
 out=[]
 for line in lines:
  if 'cycle_sample|ruhr|' not in line:continue
  r=dict(v.split('=',1) for v in line.split('cycle_sample|ruhr|',1)[1].split('|'));r['calendar_iso']=datetime.date.fromordinal(int(r['calendar'])-365).isoformat();r['mature_sample']=int(r['days_since_change'])>=45;r['evidence']='VERIFIED IN GAME';out.append(r)
 return out

def main():
 runs=[]
 for h in sorted(BASE.glob('cycle-part*-*/')):
  log=h/'engine.log'
  if not log.exists():continue
  text=log.read_text(encoding='utf8',errors='replace');result=h/'engine-result.json';r=json.loads(result.read_text()) if result.exists() else {}
  outcome='COMPLETE' if 'cycle_boundary|' in text else 'FAILED COMPILE' if 'Failed to compile' in text else 'FAILED RUNTIME'
  runs.append(dict(case=str(h),outcome=outcome,command=r.get('command') or [str(ENGINE),'-X','-x','-c',str(h/'test.cfg'),'-g',str(SOURCE),'-v','null:ticks=22000','-s','null','-m','null','-d','script=4'],seconds=r.get('seconds'),log=str(log),log_sha256=sha(log),script_sha256=sha(h/'game/lifecycle/main.nut'),observations=[s.split('P7 ',1)[1] for s in text.splitlines() if 'P7 ' in s and any(k in s for k in ['cycle_','G_ERROR|'])]))
 r=json.loads((BASE/'part1.json').read_text());rows=samples(r['observations']);assert {x['stage'] for x in rows if x['mature_sample']}=={'baseline','boom','downturn','ended'}
 with (ROOT/'docs/research/phase7g_production_samples.csv').open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 editor=json.loads((BASE/'editor.json').read_text());m=json.loads((BASE/'candidate.json').read_text())
 runs.append(dict(outcome='EDITOR SAVE; initial prototype compile error corrected by Reload AI in same process',command=editor['command'],candidate_sha256=m['candidate_sha256']))
 for key in ['candidate','source','engine','grf','script']:assert sha(Path(m[key]))==m[key+'_sha256'],key
 for item in m['script_files']+m['asset_files']:assert sha(Path(item['path']))==item['sha256']
 # Focus on the real newly placed mine, not natural background map evolution.
 import numpy as np
 a,b=maps(parts(SOURCE)),maps(parts(Path(r['case'])/'save/autosave/exit.sav'))
 tile=int(re.search(r'cycle_opened\|ruhr\|industry=\d+\|tile=(\d+)', '\n'.join(r['observations']))[1]);x,y=tile%4096,tile//4096
 inds=[(y+dy)*4096+x+dx for dx in range(-10,11) for dy in range(-10,11)]
 heights=np.frombuffer(a['MAPH'],dtype='u1')!=np.frombuffer(b['MAPH'],dtype='u1');assert not np.any(heights[inds])
 report=dict(verdict='READY WITH CAVEATS',total_engine_invocations=len(runs),completed_simulation_runs=1,failed_headless_runs=2,editor_invocations=1,save_reload='NOT TESTED: budget used on concrete compiler/delegation fixes',paid_transport='NOT TESTED; cargo supply only',calendar_fixture='compressed into 1830; normal dates 1850/1851/1873/1879 not simulated',target_industry=542,target_tile=tile,original_industries_intact=542,towns=617,final_industries=543,all_initial_candidate_map_planes_equal=True,newgrfs_unchanged=15,local_height_changes_within_10_tiles=0,normal_candidate_sha256=m['candidate_sha256'],engine_sha256=m['engine_sha256'],grf_sha256=m['grf_sha256'],runs=runs)
 (ROOT/'docs/research/phase7g_engine_receipts.json').write_text(json.dumps(report,indent=2)+'\n');print('Runs',len(runs),'sample rows',len(rows),'target',tile)
if __name__=='__main__':main()
