"""Build and verify the Europe 1830 Balance v1 deployment package (Variant C).

  python -B build_package.py

Writes C:\\Users\\Kladd\\OTTD-runtime-validation\\deploy\\europe1830-balance-v1\\ (outside the
repository and outside every production folder). Production files are only read.
Verification (all native JGRPP, recorded in verification.json):
  1. production-named GRFs give a catalogue identical to the tested Variant C GRFs (3 dates)
  2. balanced save copy: identities kept, costs changed only for Variant C engines and equal
     to the tested values (observer copy with the measurement GameScript)
  3. the package save itself loads and runs with the campaign's own GameScript
  4. rollback output is content-identical to the original campaign save
"""
import hashlib, json, shutil, subprocess, sys, time, zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import phase4 as P4          # noqa: E402
import rv                    # noqa: E402
import balance_grf as bg     # noqa: E402
import save_tools as S       # noqa: E402
import variants as V         # noqa: E402
import savetest as ST        # noqa: E402

PKG = rv.RUNS.parent / 'deploy' / 'europe1830-balance-v1'
GS_DIR = Path(r'C:\Users\Kladd\Documents\OpenTTD\game')
NAMES = {P4.NARS: ('europe1830_balance_v1_nars.grf', 'Europe 1830 Balance v1 - NARS 2.52',
                   'Running costs only: all NARS 2.52 locomotives x1/2; Norris and 4-4-0 American x0.43. Load directly after NARS 2.52.'),
         P4.ADDON: ('europe1830_balance_v1_nars_addon.grf', 'Europe 1830 Balance v1 - NARS Add-On',
                    'Running costs only: Grasshopper 787 and T.D. Judah 1575 GBP/yr. Load directly after the NARS Add-On Set 2cc.')}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build_grfs():
    out = []
    for s in V.spec('C_cross'):
        fn, name, desc = NAMES[s['target']]
        spec = dict(grfid=P4.OWN[s['target']], target=s['target'], name=name, desc=desc, prices=s.get('prices', {}), engines=s.get('engines', []))
        data = bg.build(spec)
        assert data == bg.build(spec)
        (PKG / 'newgrf').mkdir(parents=True, exist_ok=True)
        (PKG / 'newgrf' / fn).write_bytes(data)
        out.append(dict(filename=fn, grfid=spec['grfid'], md5=hashlib.md5(data).hexdigest().upper(), sha256=hashlib.sha256(data).hexdigest(),
                        bytes=len(data), name=name, after=s['target'], prices={str(k): v for k, v in spec['prices'].items()}, engines=spec['engines']))
    return out


def extras(grfs):
    return [dict(path=str(PKG / 'newgrf' / g['filename']), after=g['after'], grfid=g['grfid']) for g in grfs]


def catalogue_equivalence(grfs):
    res = {}
    for year in (1850, 1925, 2000):
        tag = f'deploy-cat-{year}'
        P4.job(tag, year=year, seed=734, mode='catalogue', extras=extras(grfs), extra_settings=P4.FIX, gs_config=dict(engines=P4.ALL_RAIL))
        import p4lib as PL
        a, b = PL.catalogue(f'cat-C_cross-{year}'), PL.catalogue(tag)
        diff = [i for i in a if a[i]['price'] != b[i]['price'] or a[i]['running'] != b[i]['running']]
        res[year] = dict(engines=len(a), differences=diff)
    return res


def main():
    PKG.mkdir(parents=True, exist_ok=True)
    rv.check_disk('package')
    grfs = build_grfs()
    (HERE / 'balance_grfs.json').write_text(json.dumps([{k: g[k] for k in ('filename', 'grfid', 'md5', 'name', 'after')} for g in grfs], indent=2))
    shutil.copyfile(HERE / 'balance_grfs.json', PKG / 'balance_grfs.json')
    shutil.copyfile(HERE / 'apply_balance.py', PKG / 'apply_balance.py')
    ver = dict(grfs=grfs)

    ver['catalogue_equivalence_to_tested_variant_C'] = catalogue_equivalence(grfs)

    src = ST.SRC
    src_sha = sha(src)
    date = src.name[-14:-4]
    save = PKG / f'campaign_{date}_balance-v1.sav'
    tmp = rv.RUNS / '_saves'
    clone = tmp / f'deploy_source_{date}.sav'
    shutil.copyfile(src, clone)
    if save.exists():
        save.unlink()
    r = subprocess.run([sys.executable, '-B', str(PKG / 'apply_balance.py'), 'apply', str(clone), str(save)], capture_output=True, text=True)
    ver['apply'] = r.stdout.strip().splitlines()
    assert r.returncode == 0, r.stderr

    # 2. observer copy (measurement GameScript attached only in the copy)
    obs = tmp / f'deploy_observer_{date}.sav'
    S.rewrite(save, obs, gs_name='RVProbe')
    if (P4.OUT / 'runs' / 'deploy-observe').exists():
        shutil.rmtree(P4.OUT / 'runs' / 'deploy-observe')
    rec, _ = ST.observe('deploy-observe', obs, months=3, extras=extras(grfs))
    import savecompare as SC
    o, oe = SC.obs('save-C_cross-original')
    d, de = SC.obs('deploy-observe')
    b, be = SC.obs('save-C_cross-balanced')
    ident = lambda v: {k: (x['owner'], x['unit'], x['engine'], x['wagons'], x['length']) for k, x in v.items()}
    ver['observer'] = dict(reason=rec['reason'], trains=len(d[0]), identity_equal_to_original=ident(d[0]) == ident(o[0]),
                           engine_costs_equal_to_tested_C={e: de[0][e]['running'] == be[0][e]['running'] for e in de[0]},
                           engine_prices_equal_to_original=all(de[0][e]['price'] == oe[0][e]['price'] for e in de[0]))

    # 3. the package save as it is, with the campaign's own GameScript
    rv.KEEP_RUN_DIRS = True
    tag = 'deploy-campaign-gs'
    if (rv.RUNS / tag).exists():
        rv.KEEP_RUN_DIRS = False
        shutil.rmtree(rv.RUNS / tag)
        rv.KEEP_RUN_DIRS = True
    home = rv.prepare(tag, year=1893, seed=734, mode='observe', extras=extras(grfs), gs_config=dict(watch_months=1, engines=[]), load=save)
    for sub in GS_DIR.iterdir():
        if sub.is_dir():
            shutil.copytree(sub, home / 'game' / sub.name)
    rec = rv.run(home, wall=240)
    log = (home / 'game.log').read_text(errors='replace')
    ver['campaign_gamescript_run'] = dict(reason=rec['reason'], seconds=rec['seconds'],
                                          gs_lines=sum('[script' in l and 'RV_' not in l for l in log.splitlines()),
                                          script_errors=[l for l in log.splitlines() if 'made an error' in l or 'died' in l][:5],
                                          grf_not_found=[l for l in log.splitlines() if 'not found' in l.lower() and 'grf' in l.lower()][:5],
                                          first_gs_lines=[l for l in log.splitlines() if '[script' in l][:8])
    rv.KEEP_RUN_DIRS = False
    rv.cleanup(home)

    # 4. rollback
    rb = tmp / f'deploy_rollback_{date}.sav'
    r = subprocess.run([sys.executable, '-B', str(PKG / 'apply_balance.py'), 'rollback', str(save), str(rb)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    ver['rollback_content_identical_to_original'] = S.load(rb)[1] == S.load(clone)[1]
    ver['source'] = dict(name='<newest campaign save, ' + src.name[-14:] + '>', sha256=src_sha, unchanged=sha(src) == src_sha)
    ver['package_save'] = dict(file=save.name, sha256=sha(save), bytes=save.stat().st_size)
    for f in (obs, rb, clone):
        f.unlink()

    sums = [f"{sha(p)}  {p.relative_to(PKG).as_posix()}" for p in sorted(PKG.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS.txt']
    (PKG / 'verification.json').write_text(json.dumps(ver, indent=2, default=str))
    sums = [f"{sha(p)}  {p.relative_to(PKG).as_posix()}" for p in sorted(PKG.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS.txt']
    (PKG / 'SHA256SUMS.txt').write_text('\n'.join(sums) + '\n')
    print(json.dumps({k: v for k, v in ver.items() if k != 'grfs'}, indent=1, default=str)[:4000])


if __name__ == '__main__':
    main()
