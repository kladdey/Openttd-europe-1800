"""Cloned campaign save: load with original vs balance GRFs, identity/cost comparison, game-written
autosave, rollback (balance GRFs removed again), all in the test area.

  python -B savetest.py --variant <name>     (GRF set from variants.py)

Production saves are only read (SHA-256 checked before/after; the production save folder listing
is compared before/after to prove no autosave landed there).
"""
import argparse, hashlib, json, shutil, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
import phase4 as P4
import rv
import save_tools as S
import variants as V

PROD_SAVE_DIR = Path(r'C:\Users\Kladd\Documents\OpenTTD\save')
SRC = max(PROD_SAVE_DIR.glob('*.sav'), key=lambda p: p.stat().st_mtime)   # newest campaign save, read only
SAVES = rv.RUNS / '_saves'


def listing():
    return sorted((p.relative_to(PROD_SAVE_DIR).as_posix(), p.stat().st_size, p.stat().st_mtime) for p in PROD_SAVE_DIR.rglob('*') if p.is_file())


def ngrf_rec(extra):
    meta = json.loads(Path(extra['path']).with_suffix('.json').read_text())
    return (extra['after'], S.ngrf_record(meta['file'], meta['grfid'], meta['md5'], 0, [], 0, meta['name']))


def observe(tag, save, months=3, extras=(), autosave=False, wall=1500):
    rv.KEEP_RUN_DIRS = True
    settings = {'gui.autosave_interval': 1, 'misc.savegame_format': 'lzma'} if autosave else {}
    home = rv.prepare(tag, year=1893, seed=734, mode='observe', extras=list(extras), extra_settings=settings,
                      gs_config=dict(watch_months=months, engines=[]), load=save)
    rec = rv.run(home, wall=wall)
    autosaves = sorted(home.rglob('*.sav'))
    kept = []
    for a in autosaves:
        if a.name == 'game.sav':
            continue
        dst = SAVES / f'{tag}__{a.name}'
        shutil.copyfile(a, dst)
        kept.append(str(dst))
    rec['autosaves_in_run_dir'] = [str(a.relative_to(home)) for a in autosaves if a.name != 'game.sav']
    rv.KEEP_RUN_DIRS = False
    rv.cleanup(home)
    return rec, kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', required=True)
    a = ap.parse_args()
    extras = V.extras(a.variant)
    h_src = hashlib.sha256(SRC.read_bytes()).hexdigest()
    before = listing()
    SAVES.mkdir(parents=True, exist_ok=True)
    clone = SAVES / 'campaign_1893_clone.sav'
    if not clone.exists():
        shutil.copyfile(SRC, clone)
    report = dict(source='<newest campaign save, ' + SRC.name[-14:] + '>', source_sha256=h_src, variant=a.variant, steps=[])
    s0 = SAVES / 'clone_original_gs.sav'
    s1 = SAVES / f'clone_{a.variant}_gs.sav'
    if not s0.exists():
        report['steps'].append(S.rewrite(clone, s0, gs_name='RVProbe'))
    report['steps'].append(S.rewrite(clone, s1, gs_name='RVProbe', insert=[ngrf_rec(x) for x in extras]))
    r0, _ = observe(f'save-{a.variant}-original', s0)
    r1, autos = observe(f'save-{a.variant}-balanced', s1, extras=extras, autosave=True, months=40)
    report.update(original=r0, balanced=r1, autosaves=autos)
    if autos:
        # Rollback: the game-written save (with balance GRFs) loaded with the balance GRFs removed.
        rb = SAVES / f'clone_{a.variant}_rollback.sav'
        report['steps'].append(S.rewrite(Path(autos[-1]), rb, remove={x['grfid'] for x in extras}))
        r2, _ = observe(f'save-{a.variant}-rollback', rb)
        report['rollback'] = r2
    report['production_save_dir_unchanged'] = listing() == before
    report['source_unchanged'] = hashlib.sha256(SRC.read_bytes()).hexdigest() == h_src
    out = P4.OUT / f'savetest_{a.variant}.json'
    out.write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps({k: report[k] for k in ('production_save_dir_unchanged', 'source_unchanged', 'autosaves')}, indent=1))


if __name__ == '__main__':
    main()
