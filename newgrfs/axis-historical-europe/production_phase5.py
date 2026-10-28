# SPDX-License-Identifier: GPL-2.0-only
"""Repeat actual steel deliveries/save-load on the current artifact, accelerated.

Uses the stockpile fixture with an eligible 1860 sheet/pipe mill customer instead
of the now 1880-gated metal workshop. Default trucks are diagnostic concessions.
This proves cargo processing and save persistence, not campaign profitability.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from PIL import Image
from integration_test import ROOT, M, sha


def main():
    engine = ROOT / '.work/runtime/engine/openttd-jgrpp-0.73.4-windows-win64/openttd.exe'
    case = ROOT / '.work' / ('production-phase5-' + str(time.time_ns()))
    case.mkdir()
    shutil.copytree(engine.parent / 'baseset', case / 'baseset', copy_function=os.link)
    (case / 'newgrf').mkdir()
    artifact = ROOT / f'dist/axis-historical-europe-{M["version"]}.grf'
    shutil.copyfile(artifact, case / 'newgrf' / artifact.name)
    for folder, source in [('game/production', 'tests/production'), ('ai/company', 'tests/ai')]:
        shutil.copytree(ROOT / source, case / folder)
    gs = case / 'game/production/main.nut'
    original = gs.read_text()
    assert original.count('this.Industry(9, x + 45, y + 65)') == 1
    gs.write_text(original.replace('this.Industry(9, x + 45, y + 65)', 'this.Industry(103, x + 45, y + 65)'))
    (case / 'scripts').mkdir()
    (case / 'scripts/game_start.scr').write_text('start_ai "Historical Funding Test Company"\n')
    image = case / 'flat.png'; Image.new('L', (256, 256), 255).save(image)
    cfg = '''[gui]
autosave_interval = 0
autosave_on_exit = true
[game_creation]
map_x = 8
map_y = 8
generation_seed = 734
heightmap_height = 16
starting_year = 1860
custom_town_number = 1
[difficulty]
industry_density = 0
number_towns = 4
vehicle_breakdowns = 0
disasters = false
[economy]
timekeeping_units = 0
[construction]
raw_industry_construction = 1
[newgrf]
''' + artifact.name + ' = 0 0 4 0 0 0 16 150 80 300 1\n[game_scripts]\n"Historical Steel Production Test" =\n'
    (case / 'test.cfg').write_text(cfg)
    results = []
    checkpoint = case / 'save/autosave/exit.sav'
    for phase in ['initial', 'reloaded']:
        if phase == 'reloaded':
            if not checkpoint.exists(): break
            shutil.copyfile(checkpoint, case / 'checkpoint.sav')
            (case / 'scripts/game_start.scr').write_text('')
        log = case / (phase + '.log')
        command = [str(engine), '-X', '-x', '-c', str(case / 'test.cfg'), '-g',
                   str(image if phase == 'initial' else case / 'checkpoint.sav'),
                   '-v', 'null:ticks=35000', '-s', 'null', '-m', 'null', '-d', 'script=4']
        with log.open('w') as f:
            subprocess.run(command, cwd=case, stdout=f, stderr=subprocess.STDOUT, timeout=120,
                           creationflags=subprocess.CREATE_NO_WINDOW, check=True)
        text = log.read_text(errors='replace')
        passed = ('PRODTEST CHECKPOINT' in text if phase == 'initial' else 'failures=0' in text) and 'PRODTEST FAILED' not in text
        results.append(dict(phase=phase, passed=passed, log=str(log.relative_to(ROOT)),
                            log_sha256=sha(log), lines=[s for s in text.splitlines() if 'PRODTEST' in s]))
        print(phase, passed, flush=True)
        if not passed: break
    report = dict(evidence='VERIFIED BY ENGINE TEST', grf_sha256=sha(artifact), engine_sha256=sha(engine),
                  fixture='Actual transported coal/ore/pig iron/coke/steel; sheet-and-pipe customer ID103',
                  limitations='Diagnostic default trucks force-enabled; grants and no breakdowns. Not an economic test.',
                  passed=len(results) == 2 and all(r['passed'] for r in results), results=results)
    if (case / 'checkpoint.sav').exists(): report['checkpoint_sha256'] = sha(case / 'checkpoint.sav')
    (ROOT / 'production-phase5-result.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__': main()
