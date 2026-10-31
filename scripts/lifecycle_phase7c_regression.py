"""Run the unchanged Phase 7B served comparison under the 0.6 binary.

Only the pinned required GRF version and the separate package entry point change.
Policy, company cash, routes, deadlines and observation periods are unchanged.
"""
import json,shutil
from lifecycle_phase7c_runtime import *
from lifecycle_phase7b_compare import code
from lifecycle_phase7b_policy import fixture,compile_policy
from lifecycle_phase7a_schedule import historical,compile_schedule
def main():
    h=prepare('regression-7b-served',code(True,0).replace('GetVersion(0x4B484531)!=5','GetVersion(0x4B484531)!=6'))
    shutil.copyfile(ROOT/'gamescripts/historical_industry_lifecycle/legacy_info.nut',h/'game/lifecycle/info.nut')
    compile_policy(fixture(),h/'game/lifecycle/legacy_policy.nut');compile_schedule(historical(),h/'game/lifecycle/schedule.nut')
    (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n');source=SOURCE;results=[]
    for stage in range(4):
        (h/'game/lifecycle/main.nut').write_text(code(True,stage).replace('GetVersion(0x4B484531)!=5','GetVersion(0x4B484531)!=6'),encoding='utf-8-sig')
        r=execute(h,150000,source=source,tag=f'stage{stage}',timeout=900);assert any('comparison_checkpoint|fixture|stage='+str(stage) in s for s in r['observations'])
        source=h/f'checkpoint-{stage}.sav';shutil.copyfile(h/'save/autosave/exit.sav',source);results.append(r)
    assert sum('legacy_extended|legacy_1|' in s for r in results for s in r['observations'])==1
    assert sum('legacy_closed|' in s for r in results for s in r['observations'])==4
    (BASE/'regression-7b.json').write_text(json.dumps(dict(runs=results,policy=fixture(),case=str(h)),indent=2))
if __name__=='__main__':main()
