"""Runtime validation harness (JGRPP 0.73.4, Europe 1830 GRF set).

Isolation rules enforced here:
  * every run lives in its own directory under RUNS (outside the repository);
  * GRFs and basesets come from one test copy (runs/_shared), hard-linked into each run
    directory (never linked to production files); OpenTTD is started with
    -X (no global/personal search folders) and -x (never write the config);
  * the production openttd.cfg is only read (to inherit settings), never written;
  * no scenario or savegame is loaded: fixtures are generated from a heightmap;
  * SHA-256 of the executable, production config, Phase 7I scenario and every
    production GRF are checked before and after each suite; config and scenario
    before and after every run (guard()).

Python 3 standard library only (a stub replaces numpy for the repo's save decoders).
"""
import argparse, configparser, csv, hashlib, json, re, shutil, struct, subprocess, sys, time, types, zlib
from pathlib import Path

sys.modules.setdefault('numpy', types.ModuleType('numpy'))
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_vehicle_newgrfs import scenario            # noqa: E402
from prepare_vehicle_probe import ngrf                # noqa: E402
from vehicle_audit_tables import decode_table         # noqa: E402

EXE = Path(r'C:\Users\Kladd\Downloads\OpenTTD\openttd.exe')
PROD = Path(r'C:\Users\Kladd\Documents\OpenTTD')
SCN = PROD / 'scenario' / 'Europe 1830 Historical AXIS 0.6.0 - Phase 7I Transport-Driven Growth.scn'
RUNS = Path(r'C:\Users\Kladd\OTTD-runtime-validation\runs')
DATA = ROOT / 'docs/research/runtime_validation'
# Runtime IDs from docs/research/vehicle_roster.csv; names are logged at runtime to confirm.
# Planet, Coppernob, Norris, Grasshopper, NARS Single Hopper (101), Large Hopper (103),
# UKRS2 8F, NARS Mallet, Add-On Big Boy, Add-On Yellowstone
STD_ENGINES = [1534, 1531, 1585, 2038, 1686, 1688, 1500, 1599, 2018, 2030]
EVIDENCE = DATA / 'runs'      # phase scripts may point this elsewhere
AXIS231 = ('4A4B8808', '4a4b8808-AXIS_eXtreme_Industry_Set-2.3.1.tar')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest().upper()


# ---------------------------------------------------------------- environment
import functools


@functools.lru_cache(maxsize=None)
def environment():
    s = scenario(SCN)
    refs = ngrf(s)
    files = {}
    for r in refs:
        first = r['filename'].split('\\')[0]
        hits = [p for p in (PROD / 'newgrf').iterdir() if p.name.lower() == first.lower()]
        assert len(hits) == 1, first
        files[r['grfid']] = str(hits[0])
    axis231 = PROD / 'newgrf' / AXIS231[1]
    return dict(exe=str(EXE), exe_sha256=sha(EXE), version_file=(EXE.parent / 'jgrpp-changelog.md').read_text(encoding='utf8').split('### ')[1].split('\n')[0],
                scenario=str(SCN), scenario_sha256=sha(SCN), refs=refs, grf_files=files,
                axis231=str(axis231), date=decode_table(s['DATE'])[0], pats=decode_table(s['PATS'])[0],
                originals={str(EXE): sha(EXE), str(PROD / 'openttd.cfg'): sha(PROD / 'openttd.cfg'), str(SCN): sha(SCN),
                           str(axis231): sha(axis231), **{f: sha(f) for f in files.values()}})


def verify():
    DATA.mkdir(parents=True, exist_ok=True)
    env = environment()
    cfg = (PROD / 'openttd.cfg').read_text(encoding='utf8')
    sec = re.search(r'\[newgrf\]\n([\s\S]*?)\n\[', cfg).group(1).splitlines()
    prod = [(l.split('|')[0].upper(), l.split('|')[1].lower(), l.split('=')[1].split()) for l in sec if l.strip()]
    scen = [(r['grfid'], r['md5'], [str(x) for x in r['params']]) for r in env['refs']]
    env['production_cfg_matches_scenario'] = prod == scen
    env['calendar_minus_economy_days'] = env['date']['date'] - env['date']['economy_date']
    (DATA / 'environment.json').write_text(json.dumps({k: v for k, v in env.items() if k != 'pats'}, indent=2, default=str), encoding='utf8')
    print(json.dumps({k: env[k] for k in ['version_file', 'exe_sha256', 'scenario_sha256', 'production_cfg_matches_scenario', 'calendar_minus_economy_days']}, indent=1))
    return env


QUICK = {str(PROD / 'openttd.cfg'), str(SCN)}


def guard(originals, quick=False):
    bad = [p for p, h in originals.items() if (not quick or p in QUICK) and sha(p) != h]
    if bad:
        raise SystemExit('PRODUCTION FILE CHANGED: ' + ', '.join(bad))


# ---------------------------------------------------------------- fixture map
def png_gray(path, rows):
    h, w = len(rows), len(rows[0])
    raw = b''.join(b'\x00' + bytes(r) for r in rows)
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


HM_MAX = 64          # game_creation.heightmap_height


def level(h):        # brightness for tile height h (see analysis in README)
    return round(h * 255 / HM_MAX)


def heightmap(path, ramp=None, axis='col'):
    """256x256. Flat at height 2; with ramp=(c0, length) height rises 1 per tile along `axis`."""
    rows = []
    for r in range(256):
        row = []
        for c in range(256):
            # Measured: image row r -> map y = r; image column c -> map x = 255 - c (rotation 0).
            k = {'col': c, 'row': r, 'x': 255 - c}[axis]
            h = 2
            if ramp:
                c0, n = ramp[0], ramp[1]
                step = ramp[2] if len(ramp) > 2 else 1     # step 2 = alternate sloped/flat tiles (1.5% average)
                h = 2 + min(max(k - c0, 0), n) // step
            row.append(level(h))
        rows.append(row)
    png_gray(path, rows)


# ---------------------------------------------------------------- run preparation
def shared_copy(env):
    """One test copy of the GRFs/basesets; runs hard-link to it (never to production files)."""
    shared = RUNS / '_shared'
    if not (shared / 'complete').exists():
        (shared / 'newgrf').mkdir(parents=True, exist_ok=True)
        shutil.copytree(PROD / 'baseset', shared / 'baseset', dirs_exist_ok=True)
        for f in list(env['grf_files'].values()) + [env['axis231']]:
            shutil.copyfile(f, shared / 'newgrf' / Path(f).name)
        (shared / 'complete').write_text('ok')
    return shared


def link(src, dst):
    import os
    os.link(src, dst)


# ---------------------------------------------------------------- disk protection
import os as _os
MIN_FREE_GB = float(_os.environ.get('RV_MIN_FREE_GB', '40'))     # refuse to start / kill runs below this
RUN_BUDGET_GB = float(_os.environ.get('RV_RUN_BUDGET_GB', '8'))  # max size of all run dirs (excl. _shared)
KEEP_RUN_DIRS = _os.environ.get('RV_KEEP', '') == '1'
COMPACT = False   # phase scripts set True: drop monthly samples and debug noise from committed evidence
MARKER = '.rv_created'


def free_gb():
    return shutil.disk_usage(RUNS.anchor).free / 2**30


def runs_gb():
    total = 0
    for d in RUNS.iterdir() if RUNS.exists() else []:
        if d.name.startswith('_'):
            continue
        for f in d.rglob('*'):
            try:
                if f.is_file() and f.stat().st_nlink == 1:   # hard links to _shared cost nothing
                    total += f.stat().st_size
            except OSError:
                pass
    return total / 2**30


def check_disk(stage):
    f = free_gb()
    if f < MIN_FREE_GB:
        raise SystemExit(f'DISK GUARD ({stage}): only {f:.1f} GB free, minimum {MIN_FREE_GB} GB')


def check_budget():
    used = runs_gb()
    if used > RUN_BUDGET_GB:
        raise SystemExit(f'DISK GUARD: run directories use {used:.2f} GB, budget {RUN_BUDGET_GB} GB')
    return used


def verify_shared(env):
    """The shared store is treated as immutable: its files must still equal the production originals."""
    shared = RUNS / '_shared' / 'newgrf'
    for f in list(env['grf_files'].values()) + [env['axis231']]:
        if sha(shared / Path(f).name) != env['originals'][f]:
            raise SystemExit('SHARED STORE MODIFIED: ' + Path(f).name)


def cleanup(home):
    """Delete a run directory, but only one this harness created (marker file) under RUNS."""
    home = Path(home).resolve()
    if KEEP_RUN_DIRS or RUNS.resolve() not in home.parents or not (home / MARKER).exists() or home.name.startswith('_'):
        return False
    shutil.rmtree(home)
    return True



def prepare(tag, *, year, seed, mode, gs_config, axis='0.6.0', compat=None, extras=None, extra_settings=None, ramp=None, ramp_axis='x', load=None):
    extras = list(extras or [])
    if compat:
        extras.append(dict(compat, grfid='52560001'))
    env = environment()
    guard(env['originals'], quick=True)
    check_disk('prepare')
    home = RUNS / tag
    if home.exists():
        raise SystemExit('Refusing to overwrite ' + str(home))
    (home / 'newgrf').mkdir(parents=True)
    (home / MARKER).write_text('created by rv.py; safe to delete')
    shared = shared_copy(env)
    (home / 'baseset').mkdir()
    for f in (shared / 'baseset').iterdir():
        link(f, home / 'baseset' / f.name)
    refs = [dict(r) for r in env['refs']]
    for r in refs:
        name = Path(env['grf_files'][r['grfid']]).name
        link(shared / 'newgrf' / name, home / 'newgrf' / name)
    if axis == '2.3.1':
        i = next(i for i, r in enumerate(refs) if r['grfid'] == '4B484531')
        link(shared / 'newgrf' / AXIS231[1], home / 'newgrf' / AXIS231[1])
        refs[i] = dict(grfid=AXIS231[0], md5='b580ae20d12247f3a7edd28fadc6f2e5', filename=AXIS231[1].lower() + '\\axis_extreme_industry_set-2.3.1\\axis_2.3.1.grf',
                       params=[0, 0, 0, 0, 0, 0, 16, 150, 80, 300])   # vector of the committed AXIS 2.3.1 baseline (newest_autosave_economy.json)
    cfg = configparser.RawConfigParser(strict=False, interpolation=None)
    cfg.optionxform = str
    cfg.read(PROD / 'openttd.cfg', encoding='utf8')
    pats = env['pats']

    def setv(sec, key, val):
        if not cfg.has_section(sec):
            cfg.add_section(sec)
        cfg.set(sec, key, str(val))
    # Inherit every scalar scenario setting that the config knows (economy, vehicles, difficulty ...).
    for full, value in pats.items():
        if not isinstance(value, int) or '.' not in full or '[' in full:
            continue
        sec, key = full.split('.', 1)
        if cfg.has_section(sec) and cfg.has_option(sec, key) and sec != 'locale':
            old = cfg.get(sec, key)
            setv(sec, key, ('true' if value else 'false') if old in ('true', 'false') else value)
    fixture = [('game_creation', 'starting_year', year), ('game_creation', 'generation_seed', seed),
               ('game_creation', 'map_x', 8), ('game_creation', 'map_y', 8), ('game_creation', 'heightmap_height', HM_MAX),
               ('game_creation', 'heightmap_rotation', 0), ('construction', 'map_height_limit', 0),
               ('game_creation', 'tree_placer', 0), ('game_creation', 'amount_of_rivers', 0), ('difficulty', 'quantity_sea_lakes', 0), ('difficulty', 'industry_density', 0),
               ('difficulty', 'number_towns', 0), ('difficulty', 'max_no_competitors', 0),
               ('gui', 'autosave_interval', 0), ('gui', 'autosave_on_exit', 'false'), ('locale', 'currency', 'GBP'),
               ('company', 'engine_renew', 'false')]
    for sec, key, val in fixture + [(*k.split('.', 1), v) for k, v in (extra_settings or {}).items()]:
        setv(sec, key, val)
    cfg.remove_section('newgrf')
    cfg.add_section('newgrf')
    lines = []
    for r in refs:
        m = r['md5'].upper() if r['md5'] else md5(home / 'newgrf' / AXIS231[1])
        lines.append((f"{r['grfid']}|{m}|{r['filename']}", ' '.join(map(str, r['params']))))
        for x in extras:
            if r['grfid'] == x['after']:
                lines.append((f"{x['grfid']}|{md5(x['path'])}|{Path(x['path']).name}", ''))
    for x in extras:   # experimental GRFs are small and mutable: copied, never hard-linked
        shutil.copyfile(x['path'], home / 'newgrf' / Path(x['path']).name)
    for k, v in lines:
        cfg.set('newgrf', k, v)
    cfg.remove_section('newgrf-static')
    cfg.add_section('newgrf-static')
    cfg.remove_section('game_scripts')
    cfg.add_section('game_scripts')
    cfg.set('game_scripts', 'RVProbe', '')
    cfg.remove_section('ai_players')
    cfg.add_section('ai_players')
    gs = home / 'game' / 'rvprobe'
    gs.mkdir(parents=True)
    (gs / 'info.nut').write_text('class RVInfo extends GSInfo {function GetAuthor(){return "runtime validation";} function GetName(){return "RVProbe";} '
                                 'function GetDescription(){return "Measurements on disposable fixtures only";} function GetVersion(){return 1;} '
                                 'function GetDate(){return "2026-11-12";} function CreateInstance(){return "RVProbe";} function GetShortName(){return "RVPR";} '
                                 'function GetAPIVersion(){return "15";}} RegisterGS(RVInfo());', encoding='utf8')
    conf = dict(gs_config, mode=mode)
    conf.setdefault('engines', STD_ENGINES)
    (gs / 'main.nut').write_text('CONFIG <- ' + squirrel(conf) + ';\n' + (HERE / 'rv_probe.nut').read_text(encoding='utf8'), encoding='utf8')
    (home / 'ai' / 'bootstrap').mkdir(parents=True)
    (home / 'ai/bootstrap/info.nut').write_text('class BootstrapInfo extends AIInfo {function GetAuthor(){return "rv";} function GetName(){return "EconomyBootstrap";} '
                                               'function GetDescription(){return "Empty test company";} function GetVersion(){return 1;} function GetDate(){return "2026-11-12";} '
                                               'function CreateInstance(){return "Bootstrap";} function GetShortName(){return "RVBS";} function GetAPIVersion(){return "15";}} RegisterAI(BootstrapInfo());')
    (home / 'ai/bootstrap/main.nut').write_text('class Bootstrap extends AIController {function Start(){while(true) Sleep(10000);}}')
    (home / 'scripts').mkdir()
    (home / 'scripts/game_start.scr').write_text('start_ai EconomyBootstrap\n')
    heightmap(home / 'map.png', ramp, ramp_axis)
    if load:      # a cloned save (never a production path) is copied in and deleted with the run dir
        assert 'OTTD-runtime-validation' in str(load), 'only cloned saves may be loaded'
        shutil.copyfile(load, home / 'game.sav')
    with (home / 'test.cfg').open('w', encoding='utf8') as f:
        cfg.write(f, space_around_delimiters=True)
    manifest = dict(tag=tag, year=year, seed=seed, mode=mode, axis=axis, compat=bool(compat),
                    extras=[dict(grfid=x['grfid'], after=x['after'], file=Path(x['path']).name, sha256=sha(x['path'])) for x in extras], ramp=ramp, ramp_axis=ramp_axis,
                    gs_config=conf, extra_settings=extra_settings or {}, load=str(load) if load else None, load_sha256=sha(load) if load else None, newgrf=[k + ' = ' + v for k, v in lines],
                    config_sha256=sha(home / 'test.cfg'), script_sha256=sha(gs / 'main.nut'), exe_sha256=env['exe_sha256'])
    (home / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
    return home


def squirrel(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, (list, tuple)):
        return '[' + ','.join(squirrel(x) for x in v) + ']'
    return '{' + ','.join(k + '=' + squirrel(x) for k, x in v.items()) + '}'


def run(home, wall=1800, debug='script=4,grf=3'):
    home = Path(home)
    m = json.loads((home / 'manifest.json').read_text())
    env_orig = environment()['originals']
    guard(env_orig, quick=True)
    cmd = [str(EXE), '-X', '-x', '-c', str(home / 'test.cfg'), '-v', 'null:ticks=40000000', '-s', 'null', '-m', 'null',
           '-d', debug, '-G', str(m['seed']), '-g', str(home / ('game.sav' if (home / 'game.sav').exists() else 'map.png'))]
    log = home / 'game.log'
    start = time.monotonic()
    reason = 'exited'
    with log.open('wb') as f:
        p = subprocess.Popen(cmd, cwd=home, stdout=f, stderr=f, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        while p.poll() is None:
            time.sleep(1)
            raw = log.read_text(errors='replace')
            if 'RV_DONE|' in raw:
                reason = 'completed' if 'RV_DONE|blocked' not in raw else 'blocked'
                time.sleep(0.5); p.terminate(); p.wait(); break
            if any(s in raw for s in ['Your script made an error', 'Failed to compile', 'The script died unexpectedly']):
                reason = 'script failure'; p.terminate(); p.wait(); break
            if time.monotonic() - start > wall:
                reason = 'wall timeout'; p.kill(); p.wait(); break
            if int(time.monotonic() - start) % 15 == 0 and free_gb() < MIN_FREE_GB:
                reason = 'disk guard'; p.kill(); p.wait(); break
    guard(env_orig, quick=True)
    raw = log.read_text(errors='replace')
    if COMPACT:
        keep = [l for l in raw.splitlines() if ('RV_' in l and 'RV_MONTH|' not in l and 'RV_INDTYPE|' not in l and 'RV_LEDGER_START|' not in l)
                or 'price base multiplier' in l or 'made an error' in l or 'died' in l]
        keep = [l.replace('dbg: [script:4] [18] [I] ', '') for l in keep]
    else:
        keep = [l for l in raw.splitlines() if 'RV_' in l or 'price base multiplier' in l or 'error' in l.lower() or 'warning' in l.lower()]
    out = EVIDENCE / home.name
    out.mkdir(parents=True, exist_ok=True)
    (out / 'evidence.log').write_text('\n'.join(keep) + '\n', encoding='utf8')
    shutil.copyfile(home / 'manifest.json', out / 'manifest.json')
    receipt = dict(tag=home.name, command=cmd, reason=reason, returncode=p.returncode, seconds=round(time.monotonic() - start, 1),
                   full_log_sha256=sha(log), full_log_bytes=log.stat().st_size, production_files_unchanged=True,
                   free_gb_after=round(free_gb(), 1))
    receipt['run_dir_deleted'] = cleanup(home)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf8')
    print(json.dumps({k: receipt[k] for k in ['tag', 'reason', 'seconds']}), flush=True)
    return receipt


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['verify'])
    a = ap.parse_args()
    verify()
