# SPDX-License-Identifier: GPL-2.0-only
"""Fresh-world historical policy tests with the campaign's other 14 GRFs.

Only writes beneath .work and dist. Never substitutes GRFs in an existing save.
Run with the fork venv Python. Runtime outcomes are captured, not inferred.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
M = json.loads((ROOT / 'historical_manifest.json').read_text())
YEARS = [1830, 1850, 1870, 1900, 1925, 1950, 1975, 2000, 2025]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_matrix():
    source = json.loads((REPO / 'docs/research/axis-2.3.1-extreme-classic.json').read_text())
    originals = {i['id']: i for i in source['industries']}
    snapshot_path = ROOT / '.work/historical-model.json'
    models = json.loads(snapshot_path.read_text())['BASIC_TEMPERATE']['industries'] if snapshot_path.exists() else {}
    rows = []
    for name, r in M['industries'].items():
        original = originals.get(name, {'inputs': ['IRON', 'COKE'], 'outputs': [['STEL', 3], ['SLAG', 1]]})
        properties = models.get(name, {}).get('properties', {})
        random_probability = properties.get('prob_in_game', original.get('prob_in_game', 'UNVERIFIED'))
        map_probability = properties.get('prob_map_gen', 'UNVERIFIED')
        rows.append(dict(industry=name, local_id=r['local_id'], earliest_year=r['earliest_year'],
                         exists_1830=r['earliest_year'] <= 1830 and r['allow_map_generation'],
                         natural_and_deity=r['allow_natural_and_gs'], funding=r['allow_player_funding_and_prospecting'],
                         map_generation=r['allow_map_generation'], final_construction_year=r['final_construction_year'],
                         upstream_random_probability_property=random_probability,
                         upstream_map_probability_property=map_probability,
                         natural_opening_after_date=('Policy allows, original probability is zero' if str(random_probability)=='0' and r['allow_natural_and_gs']
                                                    else 'Policy permits; original probability/site/density/spawning controls apply' if r['allow_natural_and_gs'] else 'Policy excludes'),
                         existing_survival='Unchanged AXIS production/closure; no date-triggered demolition',
                         accepted_labels=' '.join(original['inputs']),
                         produced_labels=' '.join(c for c, _ in original['outputs']),
                         date_status=r['date_status'], source=r.get('historical_evidence') or 'docs/AXIS_INDUSTRY_MATRIX.md (draft policy)',
                         prerequisites=r.get('prerequisites', 'Requires both IRON and COKE for production')))
    target = REPO / 'docs/research/axis_historical_availability.csv'
    with target.open('w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def squirrel_targets():
    return '[' + ','.join('{id=%d,year=%d,allow=%s}' % (
        r['local_id'], r['earliest_year'], str(r['allow_natural_and_gs']).lower())
        for r in M['industries'].values()) + ']'


def setup():
    engine = ROOT / '.work/runtime/engine/openttd-jgrpp-0.73.4-windows-win64/openttd.exe'
    assert engine.exists()
    reference = json.loads((REPO / 'docs/research/scenario_vehicle_references.json').read_text())
    original = Path(reference['scenario'])
    assert sha(original) == reference['sha256']
    base = ROOT / '.work/integration'
    base.mkdir(exist_ok=True)
    if not (base / 'newgrf').exists():
        shutil.copytree(REPO / '.vehicle-audit-runtime/phase2/newgrf', base / 'newgrf')
    shutil.copytree(engine.parent / 'baseset', base / 'baseset', dirs_exist_ok=True)
    artifact = ROOT / f'dist/axis-historical-europe-{M["version"]}.grf'
    installed = base / 'newgrf' / artifact.name
    if installed.exists():
        assert sha(installed) == sha(artifact), 'Use a new integration directory for a changed artifact; old case hardlinks must remain immutable'
    else:
        shutil.copyfile(artifact, installed)
    cfg = (REPO / '.vehicle-audit-runtime/phase2/phase2-verified-1830.cfg').read_text()
    import re
    lines = re.search(r'(?m)^\[newgrf\]\n(.*?)(?=\n\[)', cfg, re.S)[1].strip().splitlines()
    assert len(lines) == 15
    assert sum(line.startswith('4A4B8808|') for line in lines) == 1
    lines = [line if not line.startswith('4A4B8808|') else
             f'{artifact.name} = 0 0 4 0 0 0 16 150 80 300 1' for line in lines]
    return engine, base, lines, artifact, original, reference


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--year', type=int, choices=YEARS)
    args = ap.parse_args()
    write_matrix()
    engine, base, grfs, artifact, original, ref = setup()
    results = []
    for year in ([args.year] if args.year else YEARS):
        case = base / (str(year) + '-' + str(time.time_ns()))
        case.mkdir(exist_ok=False)  # Never overwrite observations.
        for folder in ['baseset', 'newgrf']:
            shutil.copytree(base / folder, case / folder, copy_function=os.link)
        game = case / 'game/historical-steel-runtime-test'
        game.mkdir(parents=True)
        shutil.copyfile(ROOT / 'tests/game/info.nut', game / 'info.nut')
        (game / 'main.nut').write_text('TARGETS <- ' + squirrel_targets() + ';\n' +
                                      (ROOT / 'tests/integration/main.nut').read_text())
        ai = case / 'ai/historical-funding-company'; ai.mkdir(parents=True)
        for name in ['info.nut', 'main.nut']:
            shutil.copyfile(ROOT / 'tests/ai' / name, ai / name)
        scripts = case / 'scripts'; scripts.mkdir()
        (scripts / 'game_start.scr').write_text('start_ai "Historical Funding Test Company"\n')
        cfg = f'''[game_creation]
map_x = 8
map_y = 8
generation_seed = 734
land_generator = 0
starting_year = {year}
[difficulty]
industry_density = 4
terrain_type = 0
quantity_sea_lakes = 0
number_towns = 2
[construction]
raw_industry_construction = 1
[economy]
timekeeping_units = 0
inflation = false
infrastructure_maintenance = true
[vehicle]
max_train_length = 7
[gui]
autosave_interval = 0
[newgrf]
''' + '\n'.join(grfs) + '\n[game_scripts]\n"Historical Steel Runtime Test" = historical=1,spawning=1\n'
        (case / 'test.cfg').write_text(cfg)
        log = case / 'engine.log'
        command = [str(engine), '-X', '-x', '-c', str(case / 'test.cfg'), '-g', '-v',
                   'null:ticks=12000', '-s', 'null', '-m', 'null', '-d', 'script=4,grf=1']
        start = time.monotonic()
        with log.open('w') as f:
            process = subprocess.Popen(command, cwd=case, stdout=f, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                while process.poll() is None and time.monotonic() - start < 110:
                    if 'AHE5 DONE' in log.read_text(errors='replace'): break
                    time.sleep(.25)
            finally:
                if process.poll() is None: process.terminate()
                process.wait(timeout=10)
        lines = [s for s in log.read_text(errors='replace').splitlines() if 'AHE5 ' in s]
        result = dict(year=year, evidence='VERIFIED BY ENGINE TEST',
                      passed=any('AHE5 DONE failures=0' in s for s in lines), lines=lines,
                      log_sha256=sha(log), command=command, seconds=round(time.monotonic()-start, 2))
        results.append(result)
        print(json.dumps({k: v for k, v in result.items() if k != 'lines'}), flush=True)
    assert sha(original) == ref['sha256']
    report = dict(grfid=M['grfid'], version=M['version'], engine_sha256=sha(engine),
                  grf_sha256=sha(artifact), original_scenario_sha256=sha(original),
                  configuration_differences=['Fresh 256x256 worlds; original scenario not loaded',
                                            'AXIS spawning enabled (parameter 2=4) to test RANDOM path',
                                            'Raw industry construction enabled to exercise company funding'],
                  results=results)
    output = ROOT / ('integration-result.json' if not args.year else f'integration-{args.year}.json')
    output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__': main()
