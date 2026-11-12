"""Re-derive the Phase-3 runtime findings from the committed evidence (no game needed).

Fails (exit 1) if any finding quoted in the Phase 4 brief is not supported by
docs/research/runtime_validation/. Standard library only.
"""
import csv, json, sys
from pathlib import Path
D = Path(__file__).resolve().parents[2] / 'docs/research/runtime_validation'
fails = []
def check(name, got, want):
    ok = got == want if not isinstance(want, tuple) else want[0] <= got <= want[1]
    print(('PASS ' if ok else 'FAIL ') + f'{name}: got {got!r}, expected {want!r}')
    if not ok: fails.append(name)

def eng(tag, eid):
    for l in (D / 'runs' / tag / 'evidence.log').read_text(encoding='utf8').splitlines():
        i = l.find('RV_ENGINE|start|')
        if i >= 0:
            f = l[i:].split('|')
            if int(f[2]) == eid: return int(f[4]), int(f[5])
cat = 't1-planet-4-l16-s734'
check('Planet catalogue', eng(cat, 1534)[1], 525)
check('Grasshopper catalogue', eng(cat, 2038)[1], 3150)
check('Coppernob catalogue', eng(cat, 1531)[1], 1181)
check('Norris catalogue', eng(cat, 1585)[1], 6300)

ages = list(csv.DictReader(open(D / 't2_state_by_age.csv')))
def first(loco, col):
    r = next(r for r in ages if r['loco'] == loco and r['seed'] == '734' and r.get('year'))
    return float(r[col])
H = 4 * 38   # four NARS hoppers, flat 38 each (verified in t1 4/6/12 consist steps)
check('Planet stationary/catalogue', round((first('planet', 'rate_depot') - H) / 525, 3), 0.25)
check('Coppernob stationary/catalogue', round((first('coppernob', 'rate_depot') - H) / 1181, 3), (0.33, 0.34))
check('Norris stationary/catalogue', round((first('norris', 'rate_depot') - H) / 6300, 3), 0.25)
check('Grasshopper stationary = moving', first('grasshopper', 'rate_depot'), first('grasshopper', 'rate_moving_loaded'))
check('Planet moving/catalogue', round((first('planet', 'rate_moving_loaded') - H) / 525, 3), 0.75)
check('Coppernob moving/catalogue', round((first('coppernob', 'rate_moving_loaded') - H) / 1181, 3), (0.66, 0.67))
check('Planet loaded == empty', first('planet', 'rate_moving_loaded'), first('planet', 'rate_moving_empty'))

def steps(loco):
    rs = [r for r in ages if r['loco'] == loco and r['seed'] == '734' and r.get('year')]
    out, prev = [], None
    for r in rs:
        v = r['twin_in_depot_max']
        if prev is not None and v != prev: out.append(round(float(r['twin_age_years_DERIVED'])))
        prev = v
    return out
check('Planet ageing steps (years)', steps('planet'), [12, 24])
check('Coppernob ageing steps (years)', steps('coppernob'), [9, 21])
check('Norris no ageing step', steps('norris'), [])
check('Grasshopper no ageing step', steps('grasshopper'), [])

t4 = {(r['terrain'], r['loco'], r['wagons']): r for r in csv.DictReader(open(D / 't4_early_summary.csv'))}
climbs = lambda l, n: float(t4[('ramp', l, str(n))]['ramp_mean_speed_mean']) > 10
check('Coppernob climbs with 2', climbs('coppernob', 2), True)
check('Coppernob fails with 4', climbs('coppernob', 4), False)
check('Norris climbs with 1', climbs('norris', 1), True)
check('Norris fails with 2', climbs('norris', 2), False)
check('Planet fails with 1', climbs('planet', 1), False)
check('Grasshopper fails with 1', climbs('grasshopper', 1), False)
hv = {(r['terrain'], r['loco']): r for r in csv.DictReader(open(D / 't4_heavy_nosub_summary.csv'))}
check('8F stalls on ramp', float(hv[('ramp', 'ukrs2-8f')]['ramp_mean_speed_mean']) < 5, True)
for l in ('mallet', 'bigboy', 'yellowstone'):
    check(f'{l} climbs', float(hv[('ramp', l)]['ramp_mean_speed_mean']) > 30, True)

comp = list(csv.DictReader(open(D / 't3_compat_catalogue.csv')))
roster = {int(r['runtime_engine_id']): r['source_grfid'] for r in csv.DictReader(open(D.parents[0] / 'vehicle_roster.csv', encoding='utf-8-sig'))}
halved = [r for r in comp if r['year'] == '1850' and r['running_ratio_DERIVED'] in ('0.5', '0.4999')]
check('compat halves 71 entries', len(halved), 71)
check('all halved are NARS 2.52', {roster[int(r['engine'])] for r in halved}, {'44440302'})
check('compat changes no purchase price', sum(r['price_base'] != r['price_compat'] for r in comp), 0)
check('Norris compat catalogue', next(int(r['running_compat']) for r in comp if r['engine'] == '1585' and r['year'] == '1850'), 3150)
svc = {r['variant']: r for r in csv.DictReader(open(D / 't3_service_summary.csv'))}
check('Norris service base', round(float(svc['base']['train_running_mean'])), 6281)
check('Norris service compat', round(float(svc['compat']['train_running_mean'])), 3276)
print('\n%d failures' % len(fails))
sys.exit(1 if fails else 0)
