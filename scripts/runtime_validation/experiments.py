"""Experiment suites for the runtime validation (tests 1-6 of RECOMMENDATIONS section 6).

  python -B experiments.py --suite t1|t2|t3|t4|t5|t6|all [--jobs 8]

Every run gets a fresh tag; existing runs are never overwritten (re-running a suite skips
tags whose receipt already exists). A full SHA-256 guard of all production files runs
before and after each suite.
"""
import argparse, csv, json, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import rv
import make_compat_grf

SEEDS = [734, 735, 736, 737]
LOCOS = {'planet': 1534, 'grasshopper': 2038, 'norris': 1585, 'coppernob': 1531}
HEAVY = {'mallet': 1599, 'bigboy': 2018, 'yellowstone': 2030, 'ukrs2-8f': 1500}
HOPPER_EARLY = 1686      # NARS Single Hopper (local 101), as Codex
HOPPER_1940S = 1688      # NARS Large Hopper (local 103, 1930)
RAMP = (50, 20)          # heightmap column 50, +1 height per tile for 20 tiles (sustained 3%)


def roster_ids(grfids):
    rows = list(csv.DictReader(open(rv.ROOT / 'docs/research/vehicle_roster.csv', encoding='utf-8-sig')))
    return sorted({int(r['runtime_engine_id']) for r in rows if r['source_grfid'] in grfids})


def job(tag, **kw):
    if (rv.DATA / 'runs' / tag / 'receipt.json').exists():
        return json.loads((rv.DATA / 'runs' / tag / 'receipt.json').read_text())
    wall = kw.pop('wall', 900)
    home = rv.prepare(tag, **kw)
    return rv.run(home, wall=wall)


def route(engine, wagons, *, years=5, level=16, distance=32, twin=False, ramp=None):
    c = dict(engine=engine, wagon=HOPPER_EARLY, wagons=wagons, distance=distance, years=years, x0=40, y0=20,
             production_level=level, twin=twin)
    if ramp:
        c.update(ramp_x0=ramp[0], ramp_x1=ramp[0] + ramp[1])
    return c


def suite(name):
    jobs = []
    if name in ('t1', 'all'):
        for label, e in LOCOS.items():
            for n in (4, 6, 12):
                for level, lname in ((16, 'l16'), (128, 'l128')):
                    for s in SEEDS:
                        jobs.append((f't1-{label}-{n}-{lname}-s{s}', dict(year=1850, seed=s, mode='route', gs_config=route(e, n, level=level))))
                # Control: subsidies off (duration 0). Subsidies are offered for high-output
                # industries and multiply revenue (seen in l128 years), so this is the clean variant.
                for s in SEEDS:
                    jobs.append((f't1-{label}-{n}-l128nosub-s{s}', dict(year=1850, seed=s, mode='route', extra_settings={'difficulty.subsidy_duration': 0},
                                                                         gs_config=route(e, n, level=128))))
    if name in ('t2', 'all'):
        for label, e in LOCOS.items():
            for s in SEEDS[:2]:
                jobs.append((f't2b-age-{label}-s{s}', dict(year=1845, seed=s, mode='route', wall=1800,
                                                         gs_config=route(e, 4, years=31, twin=True))))
    if name in ('t3', 'all'):
        out = rv.RUNS / '_compat' / 'rv_nars_compat.grf'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(make_compat_grf.build())
        ids = roster_ids({'44440302', '4E4D0518', '44441000', '53410808'})
        for year in (1850, 2000):
            for compat in (False, True):
                jobs.append((f't3-catalogue-{year}-{"compat" if compat else "base"}',
                             dict(year=year, seed=734, mode='catalogue', gs_config=dict(engines=ids),
                                  compat=dict(path=str(out), after='4E4D0518') if compat else None)))
        # Billed-cost proof: Norris + 4 hoppers in service with and without the compat GRF.
        for compat in (False, True):
            for s in SEEDS[:2]:
                jobs.append((f't3-norris-service-{"compat" if compat else "base"}-s{s}',
                             dict(year=1850, seed=s, mode='route', gs_config=route(1585, 4, years=2),
                                  compat=dict(path=str(out), after='4E4D0518') if compat else None)))
    if name in ('t4', 'all'):
        for label, e in LOCOS.items():
            for n in (1, 2, 4):
                for s in SEEDS[:2]:
                    for terrain in ('ramp', 'flat'):
                        jobs.append((f't4-{terrain}-{label}-{n}-s{s}', dict(year=1850, seed=s, mode='route', ramp=RAMP if terrain == 'ramp' else None,
                                                                             gs_config=route(e, n, years=2, level=128, ramp=RAMP if terrain == 'ramp' else None))))
        for label, e in HEAVY.items():
            for s in SEEDS:
                for terrain in ('ramp', 'flat'):
                    g = route(e, -1, years=3, level=128, ramp=RAMP if terrain == 'ramp' else None)
                    g['wagon'] = HOPPER_1940S
                    jobs.append((f't4-heavy-{terrain}-{label}-s{s}', dict(year=1943, seed=s, mode='route', ramp=RAMP if terrain == 'ramp' else None, gs_config=g)))
                    jobs.append((f't4-heavynosub-{terrain}-{label}-s{s}', dict(year=1943, seed=s, mode='route', ramp=RAMP if terrain == 'ramp' else None,
                                                                              extra_settings={'difficulty.subsidy_duration': 0}, gs_config=g)))
    if name in ('t5', 'all'):
        eng = [1534, 1531, 1500, 1585, 2038]
        # Calendar-mode controls: calendar == economy.
        for year in (1900, 1913, 1930, 1940, 1941, 1945, 1950, 1955, 1960, 1970):
            jobs.append((f't5-control-{year}', dict(year=year, seed=734, mode='catalogue', gs_config=dict(engines=eng))))
        # Wallclock mode, calendar 12x faster than economy (1 vs 12 minutes per year).
        jobs.append(('t5b-wallclock-1900', dict(year=1900, seed=734, mode='catalogue', wall=1800,
                                               extra_settings={'economy.timekeeping_units': 1, 'economy.minutes_per_calendar_year': 1},
                                               gs_config=dict(engines=eng + [1599, 2018, 2030, 1688], watch_months=72))))
        # Reverse: calendar frozen (0 = frozen) while the economy runs from 1945.
        jobs.append(('t5b-wallclock-frozen-1945', dict(year=1945, seed=734, mode='catalogue', wall=1800,
                                                       extra_settings={'economy.timekeeping_units': 1, 'economy.minutes_per_calendar_year': 0},
                                                       gs_config=dict(engines=eng + [2018], watch_months=72))))
    if name in ('t6', 'all'):
        # Full routes on AXIS 2.3.1 are impossible on the fixture: its industry-availability
        # callback refuses every coal producer/consumer (RV_BLOCKED, see t6-probe). Compare the
        # cargo payment schedule instead, at the same date and settings.
        for axis in ('0.6.0', '2.3.1'):
            for year in (1850, 1900):
                jobs.append((f't6-income-{axis}-{year}', dict(year=year, seed=734, mode='catalogue', axis=axis, gs_config=dict(engines=[1534], income=True))))
    return jobs


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--suite', required=True)
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    env = rv.environment()
    rv.guard(env['originals'])
    rv.shared_copy(env)          # create once, before worker threads hard-link to it
    jobs = suite(a.suite)
    print(len(jobs), 'runs', flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda j: job(j[0], **j[1]), jobs))
    rv.guard(env['originals'])
    bad = [r for r in results if r['reason'] != 'completed']
    print('completed', len(results) - len(bad), 'not completed', [(r['tag'], r['reason']) for r in bad])
    print('Full production-file guard passed before and after the suite.')
