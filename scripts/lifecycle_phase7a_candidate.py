"""Name and test the editor-generated scenario with the exact production GS.

No save/scenario bytes are modified. Experimental assets stay in this profile.
"""
import json,shutil
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,SOURCE,GRF,ENGINE,prepare,execute,sha,guards
from lifecycle_phase7a_schedule import historical,compile_schedule
from coastal_phase6_preservation import parts,maps

def main():
    editor=json.loads((BASE/'europe-editor.json').read_text());original=Path(editor['candidate']);home=Path(editor['case'])
    target=home/'scenario/Europe 1830 Historical AXIS 0.4.0 - Lifecycle Foundation.scn'
    if target.exists():assert sha(target)==sha(original),'Refusing to overwrite different candidate'
    else:
        with target.open('xb') as f:f.write(original.read_bytes())
    text=(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text()
    for p in [home/'game/lifecycle/main.nut']:p.write_text(text,encoding='utf-8-sig')
    shutil.copyfile(ROOT/'gamescripts/historical_industry_lifecycle/info.nut',home/'game/lifecycle/info.nut')
    compile_schedule(historical(),home/'game/lifecycle/schedule.nut')
    probe=prepare('production-candidate-roundtrip',text);compile_schedule(historical(),probe/'game/lifecycle/schedule.nut')
    first=execute(probe,1400,source=target,tag='production-start');checkpoint=probe/'production-start.sav';shutil.copyfile(probe/'save/autosave/exit.sav',checkpoint)
    second=execute(probe,1400,source=checkpoint,tag='production-reload')
    assert any('EVENT|initialized|scheduler|baseline=542|calendar=668394|economy=657437' in s for s in first['observations'])
    assert any('EVENT|loaded|scheduler|schema=1|events=3' in s for s in second['observations'])
    assert not any('FATAL|' in s or 'EVENT|opened|' in s for r in [first,second] for s in r['observations'])
    source=parts(SOURCE);candidate=parts(target)
    for p in [target,checkpoint,probe/'save/autosave/exit.sav']:
        after=parts(p)
        for tag in ['CITY','INDY','PATS']:assert source[tag]==after[tag],(tag,p)
        assert maps(source)==maps(after)
    report=dict(verdict='Experimental playable foundation; not a complete historical campaign schedule',candidate=str(target),candidate_sha256=sha(target),
        profile=str(home),configuration=str(home/'test.cfg'),engine=str(ENGINE),engine_sha256=sha(ENGINE),grf=str(GRF),grf_sha256=sha(GRF),
        script_version=1,script=str(home/'game/lifecycle/main.nut'),script_sha256=sha(home/'game/lifecycle/main.nut'),schedule_sha256=sha(home/'game/lifecycle/schedule.nut'),
        original_scenario_sha256=sha(SOURCE),baseline_towns=617,baseline_industries=542,other_14_grfs_preserved=True,all_map_bytes_and_initial_industry_town_records_preserved=True,
        actual_production_script_gameplay_save_reload=[first,second],experimental_files_not_installed_over_originals=True)
    (BASE/'candidate-delivery.json').write_text(json.dumps(report,indent=2));guards();print(json.dumps(report,indent=2))

if __name__=='__main__':main()
