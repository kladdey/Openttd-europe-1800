"""Phase 4 experiment driver. Reuses scripts/runtime_validation (rv.py, rv_probe.nut).

  python -B phase4.py --suite feas|... [--jobs 8]

Evidence: docs/research/fleet_phase4/runs/<tag>/ (filtered log, manifest, receipt).
Experimental GRFs: docs/research/fleet_phase4/grf/ (tiny, mutable; copied into runs).
"""
import argparse, csv, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'runtime_validation'))
import rv                                   # noqa: E402
import balance_grf as bg                    # noqa: E402

OUT = rv.ROOT / 'docs/research/fleet_phase4'
rv.EVIDENCE = OUT / 'runs'
rv.COMPACT = True
GRF = OUT / 'grf'
NARS, ADDON, UKRS2 = '44440302', '4E4D0518', '44441000'
OWN = {NARS: '52560010', ADDON: '52560011', UKRS2: '52560012'}
ROSTER = list(csv.DictReader(open(rv.ROOT / 'docs/research/vehicle_roster.csv', encoding='utf-8-sig')))
RID = {(r['source_grfid'], int(r['local_vehicle_id'])): int(r['runtime_engine_id']) for r in ROSTER}
ALL_RAIL = sorted({int(r['runtime_engine_id']) for r in ROSTER if r['source_grfid'] in (NARS, ADDON, UKRS2, '53410808', '4D560103', '4D560105')})


def grf(target, tag, prices=None, engines=None):
    spec = dict(grfid=OWN[target], target=target, tag=tag, name=f'RV P4 {tag}', prices=prices or {}, engines=engines or [])
    path, meta = bg.write(spec, GRF)
    return dict(path=str(path), after=target, grfid=OWN[target])


def job(tag, **kw):
    if (rv.EVIDENCE / tag / 'receipt.json').exists():
        return json.loads((rv.EVIDENCE / tag / 'receipt.json').read_text())
    wall = kw.pop('wall', 900)
    home = rv.prepare(tag, **kw)
    return rv.run(home, wall=wall)


def route(engine, wagons, *, wagon=1686, years=5, level=16, distance=32, twin=False, ramp=None):
    c = dict(engine=engine, wagon=wagon, wagons=wagons, distance=distance, years=years, x0=40, y0=20, production_level=level, twin=twin)
    if ramp:
        c.update(ramp_x0=ramp[0], ramp_x1=ramp[0] + ramp[1])
    return c


NOSUB = {'difficulty.subsidy_duration': 0}
FIX = dict(NOSUB, **{'vehicle.never_expire_vehicles': 'true'})   # same wagons available in every era; affects availability only
SEEDS = [734, 735, 736, 737, 738]
SUSTAINED = (50, 20)        # +1 height per tile for 20 tiles: 3% on every tile
MODERATE = (50, 20, 2)      # +1 height every 2nd tile: alternating 3% and flat, 1.5% average, +10 overall
NARS_STEAM = list(range(0, 20)) + [70]   # NARS 2.52 steam locomotives (local IDs), from the catalogue
LOCO = dict(planet=1534, coppernob=1531, norris=1585, grasshopper=2038, crampton=1532)

# ---- candidate settings for the two sweeps (all measured; nothing here is assumed to work)
def norris_extras(v):
    if v == 6300: return []
    if v == 3150: return [grf(NARS, 'g42p3', prices={42: 3})]                       # global NARS halving (reference)
    e = {5400: 4, 2700: 3, 1350: 2, 675: 1}[v]
    return [grf(NARS, f'norris44e{e}', prices={44: e}, engines=[dict(id=0, cls='electric')])]

def grass_extras(v):
    if v == 3150: return []
    f = {1575: 12, 1050: 8, 787: 6, 525: 4}[v]
    return [grf(ADDON, f'grassf{f}', engines=[dict(id=116, factor=f)])]


def duties_1850(engine, extras, label):
    out = []
    for s in SEEDS:
        for n, lv in ((6, 16), (12, 16), (6, 128), (12, 128)):
            out.append((f'p1850-{label}-flat32-w{n}-l{lv}-s{s}', dict(year=1850, seed=s, mode='route', extras=extras, extra_settings=FIX, gs_config=route(engine, n, level=lv))))
        for n in (6, 12):
            out.append((f'p1850-{label}-flat96-w{n}-l128-s{s}', dict(year=1850, seed=s, mode='route', extras=extras, extra_settings=FIX, gs_config=route(engine, n, level=128, distance=96))))
        out.append((f'p1850-{label}-mod32-w4-l128-s{s}', dict(year=1850, seed=s, mode='route', ramp=MODERATE, extras=extras, extra_settings=FIX, gs_config=route(engine, 4, level=128, ramp=SUSTAINED))))
        for n in (1, 2):
            out.append((f'p1850-{label}-sus32-w{n}-l128-s{s}', dict(year=1850, seed=s, mode='route', ramp=SUSTAINED, extras=extras, extra_settings=FIX, gs_config=route(engine, n, level=128, ramp=SUSTAINED))))
        out.append((f'p1850-{label}-pass48-w4-s{s}', dict(year=1850, seed=s, mode='route', extras=extras, extra_settings=FIX, gs_config=dict(route(engine, 4, wagon=1462, distance=48), cargo='PASS'))))
    return out


ERAS = {   # year: (wagon, [engines]) - representative freight locomotives of each set
    1832: (1686, [1534, 2038]),
    1860: (1686, [1586, 1535, 2040, 1531]),
    1878: (1686, [1587, 1588, 1496, 2044]),
    1903: (1686, [1589, 1591, 1497, 2046, 3605]),
    1925: (1687, [1594, 1596, 1529, 2042, 3583]),
    1945: (1688, [1599, 1596, 2018, 2030, 1500, 3621]),
    1955: (1688, [1609, 1623, 2003, 1500, 3200]),
    1977: (1688, [1614, 1615, 1961, 1508, 3188]),
    2000: (1688, [1618, 1629, 1957, 1509, 1512, 3167]),
    2025: (1688, [1631, 1618, 1958, 1509, 3167]),
}
PASS_ERAS = {1850: (48, [1534, 1531, 1585, 2038, 1532]), 1890: (96, [1590, 1495, 2045]), 1940: (96, [1601, 1603, 1502, 2049, 1501]), 1980: (96, [1616, 1508, 3209, 1932])}


def era_jobs(variant, extras, engines_filter=None):
    out = []
    for year, (wagon, engines) in ERAS.items():
        for e in engines:
            if engines_filter is not None and e not in engines_filter: continue
            for s in SEEDS:
                for terrain, ramp, lv in (('flat', None, 128), ('flat', None, 16), ('sus', SUSTAINED, 128)):
                    g = route(e, -1, wagon=wagon, years=4, level=lv, ramp=ramp)
                    out.append((f'era-{variant}-{year}-{e}-{terrain}-l{lv}-s{s}', dict(year=year, seed=s, mode='route', ramp=ramp, extras=extras, extra_settings=FIX, gs_config=g)))
    for year, (dist, engines) in PASS_ERAS.items():
        for e in engines:
            if engines_filter is not None and e not in engines_filter: continue
            for s in SEEDS:
                g = dict(route(e, -1, wagon=1462, years=4, distance=dist), cargo='PASS')
                out.append((f'era-{variant}-{year}-{e}-pass{dist}-s{s}', dict(year=year, seed=s, mode='route', extras=extras, extra_settings=FIX, gs_config=g)))
    return out


def suite(name):
    jobs = []
    if name == 'feas':
        tests = {
            # does a static factor override reach a callback-driven NARS engine?
            'f1-nars-factor': [grf(NARS, 'f1', engines=[dict(id=0, factor=12)])],
            # running-cost class switch on one NARS engine (+ local multiplier for that class)
            'f2-nars-class44': [grf(NARS, 'f2', prices={44: 4}, engines=[dict(id=0, cls='electric')])],
            # which NARS vehicles use classes 43 / 44 (multiplier change only)?
            'f5-nars-mult44': [grf(NARS, 'f5', prices={44: 6})],
            'f6-nars-mult43': [grf(NARS, 'f6', prices={43: 0})],
            # Add-On: static factor on Grasshopper (flat-rate set)
            'f3-addon-factor': [grf(ADDON, 'f3', engines=[dict(id=116, factor=12)])],
            'f7-addon-mult44': [grf(ADDON, 'f7', prices={44: 6})],
            'f8-addon-mult43': [grf(ADDON, 'f8', prices={43: 6})],
            # UKRS2: factor and class on Planet; multipliers
            'f4-ukrs2-factor': [grf(UKRS2, 'f4', engines=[dict(id=124, factor=8)])],
            'f9-ukrs2-class44': [grf(UKRS2, 'f9', engines=[dict(id=124, cls='electric')])],
            'f10-ukrs2-mult43': [grf(UKRS2, 'f10', prices={43: 0})],
            'f11-ukrs2-mult44': [grf(UKRS2, 'f11', prices={44: 0})],
        }
        jobs.append(('feas-base-catalogue', dict(year=1850, seed=734, mode='catalogue', gs_config=dict(engines=ALL_RAIL))))
        for t, extras in tests.items():
            jobs.append((f'feas-{t}-catalogue', dict(year=1850, seed=734, mode='catalogue', extras=extras, gs_config=dict(engines=ALL_RAIL))))
        # in-service state probes for the per-engine mechanisms
        for t, eng in (('f1-nars-factor', 1585), ('f2-nars-class44', 1585), ('f3-addon-factor', 2038), ('f4-ukrs2-factor', 1534), ('f9-ukrs2-class44', 1534)):
            jobs.append((f'feas-{t}-service', dict(year=1850, seed=734, mode='route', extras=tests[t], extra_settings=NOSUB,
                                                    gs_config=route(eng, 4, years=1, twin=True))))
        for eng, l in ((1585, 'norris'), (2038, 'grasshopper'), (1534, 'planet')):
            jobs.append((f'feas-base-{l}-service', dict(year=1850, seed=734, mode='route', extra_settings=NOSUB, gs_config=route(eng, 4, years=1, twin=True))))
    if name == 'sweep':
        for v in (6300, 5400, 3150, 2700, 1350, 675):
            jobs += duties_1850(LOCO['norris'], norris_extras(v), f'norris{v}')
        for v in (3150, 1575, 1050, 787, 525):
            jobs += duties_1850(LOCO['grasshopper'], grass_extras(v), f'grass{v}')
        for l in ('planet', 'coppernob'):
            jobs += duties_1850(LOCO[l], [], l)
    if name == 'erabase':
        jobs += era_jobs('base', [])
    if name == 'lifecycle':      # 20 years, autorenew off, stopped twin in depot for the depot rate
        for label, e, n, ex in (('norris6300', 1585, 12, norris_extras(6300)), ('norris2700', 1585, 12, norris_extras(2700)), ('norris1350', 1585, 12, norris_extras(1350)),
                                ('grass3150', 2038, 6, grass_extras(3150)), ('grass1575', 2038, 6, grass_extras(1575)), ('grass787', 2038, 6, grass_extras(787)), ('grass525', 2038, 6, grass_extras(525)),
                                ('planet6', 1534, 6, []), ('planet12', 1534, 12, []), ('coppernob12', 1531, 12, [])):
            for s in SEEDS[:3]:
                jobs.append((f'life-{label}-s{s}', dict(year=1850, seed=s, mode='route', wall=2400, extras=ex, extra_settings=FIX, gs_config=route(e, n, years=20, twin=True))))
    if name == 'autoreplace':    # replacement onto/away from modified engines keeps consist and picks up the new engine's rate
        import variants as V
        ex = V.extras('A_targeted')
        for label, e, to in (('norris-to-coppernob', 1585, 1531), ('coppernob-to-norris', 1531, 1585), ('grass-to-planet', 2038, 1534), ('planet-to-grass', 1534, 2038)):
            for vname, xx in (('original', []), ('A_targeted', ex)):
                g = route(e, 4, years=3)
                g['autoreplace_to'] = to
                jobs.append((f'arep-{vname}-{label}-s734', dict(year=1850, seed=734, mode='route', extras=xx, extra_settings=FIX, gs_config=g)))
    if name == 'catalogue':
        import variants as V
        for v in ['original'] + V.VARIANTS:
            for year in (1850, 1925, 2000):
                jobs.append((f'cat-{v}-{year}', dict(year=year, seed=734, mode='catalogue', extras=V.extras(v), extra_settings=FIX, gs_config=dict(engines=ALL_RAIL))))
    if name.startswith('era-'):  # era-<variant>: only engines whose cost the variant changes (+ determinism controls)
        import variants as V
        v = name[4:]
        ex = V.extras(v)
        changed = V.changed_engines(v)
        controls = {1509, 3167}  # unaffected UKRS2 Class 66 and GETS BR 266: must reproduce the base runs exactly
        jobs += era_jobs(v, ex, engines_filter=changed | controls)
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--suite', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    env = rv.environment()
    rv.guard(env['originals'])
    rv.check_disk('suite start')
    rv.shared_copy(env)
    rv.verify_shared(env)
    jobs = suite(a.suite)
    print(len(jobs), 'runs; run dirs use %.2f GB; %.1f GB free' % (rv.check_budget(), rv.free_gb()), flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda j: job(j[0], **j[1]), jobs))
    rv.guard(env['originals'])
    rv.verify_shared(env)
    bad = [(r['tag'], r['reason']) for r in results if r['reason'] != 'completed']
    print('completed', len(results) - len(bad), 'not completed', bad)
    print('Production files and shared store verified unchanged; %.1f GB free' % rv.free_gb())


if __name__ == '__main__':
    main()
