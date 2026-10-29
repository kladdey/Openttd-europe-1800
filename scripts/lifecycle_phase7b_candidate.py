"""Stage a separate GUI editor profile; finalize only an engine-created save."""
import argparse,json,shutil,subprocess
from pathlib import Path
from lifecycle_phase7b_runtime import ROOT,BASE,ENGINE,GRF,prepare,execute,source7a,bundle,guards,sha
from lifecycle_phase7b_policy import production,compile_policy
from lifecycle_phase7a_schedule import historical,compile_schedule
from coastal_phase6_preservation import parts,maps

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage-editor',action='store_true');a=ap.parse_args();guards()
    if a.stage_editor:
        home=prepare('legacy-editor',bundle());compile_policy(production(),home/'game/lifecycle/legacy_policy.nut');compile_schedule(historical(),home/'game/lifecycle/schedule.nut')
        (home/'scenario').mkdir();source=home/'scenario/Phase7B baseline copy.scn';shutil.copyfile(source7a(),source)
        cmd=[str(ENGINE),'-X','-x','-c',str(home/'test.cfg'),'-e','-g',str(source),'-r','1280x800','-s','null','-m','null']
        process=subprocess.Popen(cmd,cwd=home,creationflags=subprocess.CREATE_NO_WINDOW)
        record=dict(case=str(home),pid=process.pid,source=str(source),source_sha256=sha(source),command=cmd)
        (BASE/'editor.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));return
    editor=json.loads((BASE/'editor.json').read_text());home=Path(editor['case']);saved=home/'scenario/UNNAMED.scn'
    assert saved.exists(),'Missing real editor save; use UI, do not fabricate a scenario'
    target=home/'scenario/Europe 1830 Historical AXIS 0.5.0 - Legacy Mine Lifecycle.scn'
    if target.exists():assert sha(target)==sha(saved),'Refusing to overwrite different candidate'
    else:
        with target.open('xb') as f:f.write(saved.read_bytes())
    (home/'game/lifecycle/main.nut').write_text(bundle(),encoding='utf-8-sig')
    shutil.copyfile(ROOT/'gamescripts/historical_industry_lifecycle/legacy_info.nut',home/'game/lifecycle/info.nut')
    compile_policy(production(),home/'game/lifecycle/legacy_policy.nut');compile_schedule(historical(),home/'game/lifecycle/schedule.nut')
    before,after=parts(source7a()),parts(target)
    for tag in ['CITY','INDY','PATS','PSAC']:assert before[tag]==after[tag],tag
    assert maps(before)==maps(after)
    record=dict(candidate=str(target),candidate_sha256=sha(target),profile=str(home),configuration=str(home/'test.cfg'),engine=str(ENGINE),engine_sha256=sha(ENGINE),
        grf=str(GRF),grf_sha256=sha(GRF),script=str(home/'game/lifecycle/main.nut'),script_sha256=sha(home/'game/lifecycle/main.nut'),
        policy_sha256=sha(home/'game/lifecycle/legacy_policy.nut'),schedule_sha256=sha(home/'game/lifecycle/schedule.nut'),
        baseline_towns=617,baseline_industries=542,all_map_bytes_unchanged=True,unchanged_chunks=['CITY','INDY','PATS','PSAC'],test_dates=False)
    (BASE/'candidate-delivery.json').write_text(json.dumps(record,indent=2));guards();print(json.dumps(record,indent=2))

if __name__=='__main__':main()
