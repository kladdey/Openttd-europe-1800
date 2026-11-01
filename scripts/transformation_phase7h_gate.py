"""Mandatory two-invocation active-cycle gate; reuses Phase 7G's exact fixture."""
import argparse,json
from pathlib import Path
import cycles_phase7g as g
from cycles_phase7g_validate import PROBE
BASE=g.BASE.parent/'phase7h';BASE.mkdir(exist_ok=True)

def run(part):
 end='1830-06-15' if part==1 else '1830-12-15'
 probe=PROBE.replace('Initialize(Calendar());local last=-1;', '''if(loaded!=null)Log("h_gate_saved","active","schema="+loaded.schema+"|stage="+loaded.cycles.stage+"|target="+loaded.cycles.signature.id+"|last_change="+loaded.cycles.last_change);
 Initialize(Calendar());local last=-1;''')
 probe=probe.replace('"|originals="+intact);','"|originals="+intact+"|level="+GSIndustry.GetProductionLevel(r.signature.id)+"|flags="+GSIndustry.GetControlFlags(r.signature.id)+"|last_change="+r.last_change);')
 old=g.BASE
 try:g.BASE=BASE;h=g.prepare('active-gate-'+str(part),g.bundle()+probe.replace('BOUNDARY',str(g.absolute_date(end))),g.policy(True))
 finally:g.BASE=old
 info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"CyclesController"','"CycleProbe"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 source=g.SOURCE if part==1 else Path(json.loads((BASE/'gate1.json').read_text())['case'])/'save/autosave/exit.sav'
 before=g.sha(source);r=g.execute(h,23000,source=source);assert g.sha(source)==before
 r.update(source=str(source),source_sha256=before);(BASE/('gate'+str(part)+'.json')).write_text(json.dumps(r,indent=2))
 obs='\n'.join(r['observations']);assert 'G_ERROR|' not in obs and 'cycle_boundary|' in obs,r['log']
 assert ('stage=boom' if part==1 else 'stage=ended') in obs
 if part==2:
  assert 'h_gate_saved|active|schema=5|stage=boom|target=542' in obs
  assert 'cycle_level|boom|' not in obs and 'cycle_opened|ruhr|' not in obs
  assert obs.count('cycle_level|downturn|')==1 and obs.count('cycle_level|restored|')==1
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('part',type=int,choices=[1,2]);run(ap.parse_args().part)
