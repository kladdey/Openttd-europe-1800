"""Actual checkpoint replay, schema migration and post-closure reload checks."""
import argparse,json,shutil
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,prepare,execute,sha
from lifecycle_phase7a_schedule import fixture,compile_schedule
from lifecycle_phase7a_fixture import code

def significant(lines):
    kinds=['opened','closing','closed','final','decline','longevity']
    return [s.split('P7 EVENT|',1)[1] for s in lines if any('EVENT|'+k+'|' in s for k in kinds)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['replay','migration']);a=ap.parse_args()
    if a.case=='replay':
        original=Path((BASE/'vertical-slice-case.txt').read_text());checkpoint=original/'checkpoint.sav';results=[]
        for n in range(2):
            home=prepare('checkpoint-replay',code(2));compile_schedule(fixture(),home/'game/lifecycle/schedule.nut')
            results.append(execute(home,150000,source=checkpoint))
        assert significant(results[0]['observations'])==significant(results[1]['observations']),'Replay diverged'
        home=Path(results[-1]['case']);saved=home/'save/autosave/exit.sav';shutil.copyfile(saved,home/'post-closure.sav')
        post=execute(home,3000,source=home/'post-closure.sav',tag='post-closure-reload')
        assert not any('EVENT|opened|' in s for s in post['observations']),'Unexpected reopening on terminal reload'
        (BASE/'checkpoint-replay.json').write_text(json.dumps(dict(checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),runs=results,significant_transitions_identical=True,post_closure_reload=post),indent=2))
    else:
        legacy_save='''function Save(){local output=clone state;output.schema=0;output.events={};foreach(id,r in state.events){local row=clone r;if("batches" in row)delete row.batches;if("last_observation_month" in row)delete row.last_observation_month;output.events[id]<-row;}return output;}'''
        text=code(2).replace('function Save(){return state!=null?state:loaded;}',legacy_save)
        text=text.replace('Initialize(now);','Initialize(now);GSGame.Pause();Log("legacy_checkpoint","fixture","supported Save emits schema 0");while(true)Sleep(365);')
        home=prepare('schema-migration',text);compile_schedule(fixture(),home/'game/lifecycle/schedule.nut')
        original=Path((BASE/'vertical-slice-case.txt').read_text())/'checkpoint.sav'
        initial=execute(home,3500,source=original,tag='legacy');assert any('EVENT|legacy_checkpoint|' in s for s in initial['observations'])
        checkpoint=home/'legacy.sav';shutil.copyfile(home/'save/autosave/exit.sav',checkpoint)
        (home/'game/lifecycle/main.nut').write_text(code(2),encoding='utf-8-sig')
        info=home/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('function GetVersion(){return 1;}','function GetVersion(){return 2;}function MinVersionToLoad(){return 1;}'))
        result=execute(home,150000,source=checkpoint,tag='upgraded')
        assert any('EVENT|migrated|scheduler|schema=0->1' in s for s in result['observations'])
        assert any('EVENT|closed|' in s for s in result['observations'])
        assert not any('EVENT|opened|gb_south_hetton_1833|' in s for s in result['observations'])
        (BASE/'schema-migration.json').write_text(json.dumps(dict(case=str(home),old_schema=0,new_schema=1,old_script_version=1,test_script_version=2,result=result),indent=2))

if __name__=='__main__':main()
