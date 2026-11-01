"""A separately engine-saved scenario; unchanged AXIS, new GS v7/schema6 profile."""
import argparse,json,shutil,subprocess
from pathlib import Path
from transformation_phase7h import *
from transformation_phase7h import setup
from coastal_phase6_preservation import parts,maps
from historical_scenario_migration import inspect
NAME='Europe 1830 Historical AXIS 0.6.0 - Phase 7H Industrial Transformation.scn'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--stage-editor',action='store_true');a=ap.parse_args();guards()
 if a.stage_editor:
  h=prepare('phase7h-editor');setup(h);(h/'scenario').mkdir();source=h/'scenario/Phase7H source copy.scn';shutil.copyfile(SOURCE,source)
  cmd=[str(ENGINE),'-X','-x','-c',str(h/'test.cfg'),'-e','-g',str(source),'-r','1280x800','-s','null','-m','null']
  proc=subprocess.Popen(cmd,cwd=h,creationflags=subprocess.CREATE_NO_WINDOW);record=dict(case=str(h),pid=proc.pid,source=str(source),command=cmd)
  (BASE/'editor.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));return
 h=Path(json.loads((BASE/'editor.json').read_text())['case']);saved=h/'scenario/UNNAMED.scn';assert saved.exists()
 target=h/'scenario'/NAME
 if target.exists():assert sha(target)==sha(saved),'Prior candidate differs; stage a new profile'
 else:
  with target.open('xb') as f:f.write(saved.read_bytes())
 before,after=parts(SOURCE),parts(target)
 for tag in ['CITY','INDY','PATS','PSAC']:assert before[tag]==after[tag],tag
 assert maps(before)==maps(after)
 assert inspect(SOURCE)['newgrfs']==inspect(target)['newgrfs']
 normal=Path.home()/'Documents/OpenTTD/scenario'/NAME
 if normal.exists():assert sha(normal)==sha(target),'Refusing to overwrite any prior scenario'
 else:
  with normal.open('xb') as f:f.write(target.read_bytes())
 (h/'game/lifecycle/main.nut').write_text(bundle(),encoding='utf-8-sig');(h/'game/lifecycle/info.nut').write_text((DIR/'transformation_info.nut').read_text(encoding='utf-8-sig'));setup(h);m=dict(candidate=str(normal),candidate_sha256=sha(normal),profile_candidate=str(target),profile=str(h),configuration=str(h/'test.cfg'),source=str(SOURCE),source_sha256=sha(SOURCE),
  engine=str(ENGINE),engine_sha256=sha(ENGINE),grf=str(GRF),grf_sha256=sha(GRF),script=str(h/'game/lifecycle/main.nut'),script_sha256=sha(h/'game/lifecycle/main.nut'),
  gs_version=7,gs_schema=6,axis_version='0.6.0 unchanged',test_dates=False,towns=617,initial_industries=542,newgrfs=inspect(target)['newgrfs'],
  preserved_chunks=['CITY','INDY','PATS','PSAC'],all_map_planes_unchanged=True,
  script_files=[dict(path=str(p),sha256=sha(p)) for p in sorted((h/'game/lifecycle').glob('*.nut'))],
  asset_files=[dict(path=str(p),sha256=sha(p)) for folder in ['baseset','newgrf'] for p in sorted((h/folder).rglob('*')) if p.is_file()])
 (BASE/'candidate.json').write_text(json.dumps(m,indent=2));(ROOT/'docs/research/phase7h_candidate_delivery.json').write_text(json.dumps(m,indent=2));print(json.dumps(m,indent=2)[:1800])
if __name__=='__main__':main()
