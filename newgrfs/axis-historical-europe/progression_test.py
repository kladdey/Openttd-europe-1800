# SPDX-License-Identifier: GPL-2.0-only
"""Advance an actual fresh 1830 world to 2025, saving/reloading near 1870."""
import json
import os
import shutil
import subprocess
import time
from integration_test import ROOT, setup, squirrel_targets, sha


def main():
    engine, base, grfs, artifact, original, ref = setup()
    case = base / ('progression-' + str(time.time_ns())); case.mkdir()
    for folder in ['baseset', 'newgrf']:
        shutil.copytree(base / folder, case / folder, copy_function=os.link)
    game=case/'game/progression';game.mkdir(parents=True)
    shutil.copyfile(ROOT/'tests/game/info.nut',game/'info.nut')
    (game/'main.nut').write_text('TARGETS <- '+squirrel_targets()+';\n'+(ROOT/'tests/integration/progression.nut').read_text())
    (case/'test.cfg').write_text('''[gui]
autosave_on_exit = true
autosave_interval = 0
[game_creation]
map_x = 8
map_y = 8
generation_seed = 734
land_generator = 0
starting_year = 1830
[difficulty]
industry_density = 4
terrain_type = 0
quantity_sea_lakes = 0
number_towns = 2
[economy]
timekeeping_units = 0
inflation = false
infrastructure_maintenance = true
[newgrf]
'''+'\n'.join(grfs)+'\n[game_scripts]\n"Historical Steel Runtime Test" =\n')
    results=[]
    for phase,ticks in [('initial',1150000),('reloaded',4500000)]:
        load=[]
        if phase=='reloaded':
            checkpoint=case/'save/autosave/exit.sav'
            if not checkpoint.exists():break
            shutil.copyfile(checkpoint,case/'checkpoint.sav');load=[str(case/'checkpoint.sav')]
        command=[str(engine),'-X','-x','-c',str(case/'test.cfg'),'-g']+load+['-v',f'null:ticks={ticks}','-s','null','-m','null','-d','script=4']
        log=case/(phase+'.log');start=time.monotonic()
        with log.open('w') as f:
            subprocess.run(command,cwd=case,stdout=f,stderr=subprocess.STDOUT,timeout=600,
                           creationflags=subprocess.CREATE_NO_WINDOW,check=True)
        text=log.read_text(errors='replace')
        results.append(dict(phase=phase,seconds=round(time.monotonic()-start,2),log_sha256=sha(log),
                            lines=[s for s in text.splitlines() if 'AHE5P' in s],
                            log=str(log.relative_to(ROOT))))
        print(phase,results[-1]['seconds'],results[-1]['lines'],flush=True)
    lines=[s for r in results for s in r['lines']]
    report=dict(evidence='VERIFIED BY ENGINE TEST',engine_sha256=sha(engine),grf_sha256=sha(artifact),
                results=results,passed=any('AHE5P DONE' in s for s in lines) and
                all('failures=' not in s or 'failures=0' in s for s in lines),
                limitations='Unserved industries may close through original AXIS behavior; ID/type matches are not unique lifetime identities. No human companies or freight in this soak.')
    if (case/'checkpoint.sav').exists():report['checkpoint_sha256']=sha(case/'checkpoint.sav')
    (ROOT/'progression-result.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
