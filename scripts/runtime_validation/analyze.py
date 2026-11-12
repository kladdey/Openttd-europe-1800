"""Turn runtime evidence logs into CSV tables (all values RUNTIME unless a column says DERIVED).

Reads docs/research/runtime_validation/runs/*/evidence.log, writes
docs/research/runtime_validation/*.csv and summary.json. Standard library only.
"""
import csv, json, re, statistics as st
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / 'docs/research/runtime_validation'
RUNS = DATA / 'runs'
TRAIN_RUN, PROPERTY, TRAIN_REVENUE, OTHER = 2, 6, 7, 12   # logged as RV_EXPENSE_IDS (revenue index = ExpensesType order)


def lines(tag):
    out = []
    for l in (RUNS / tag / 'evidence.log').read_text(encoding='utf8').splitlines():
        i = l.find('RV_')
        if i >= 0:
            out.append(l[i + 3:].split('|'))
    return out


def receipt(tag):
    return json.loads((RUNS / tag / 'receipt.json').read_text())


def parse_route(tag):
    d = dict(tag=tag, years=[], states=defaultdict(dict), build=None, blocked=None, catalogue={}, months=[])
    for f in lines(tag):
        k = f[0]
        if k == 'BUILD':
            d['build'] = dict(vehicle=int(f[1]), purchase=int(f[2]), infrastructure=int(f[3]), capacity=int(f[4]), length16=int(f[5]),
                              parts=int(f[6]), twin=int(f[9]), cost_at_build=int(f[10]))
        elif k == 'BLOCKED':
            d['blocked'] = f[1]
        elif k == 'ENGINE' and f[1] == 'start' and len(f) > 4:
            d['catalogue'][int(f[2])] = dict(name=f[3], price=int(f[4]), running=int(f[5]))
        elif k == 'YEAR':
            led = [int(x) for x in f[6].split(',') if x != '']
            d['years'].append(dict(year=int(f[1]), delivered_quarterly=int(f[2]), unloaded=int(f[3]), arrivals=int(f[4]),
                                   vehicle_profit=int(f[5]), train_running=led[TRAIN_RUN], property=led[PROPERTY],
                                   revenue=-led[TRAIN_REVENUE], other=led[OTHER], age_days=int(f[7]), reliability=int(f[8]),
                                   ramp_samples=int(f[9]), ramp_speed_sum=int(f[10]), ramp_min_speed=int(f[11]),
                                   twin_min=int(f[12]), twin_max=int(f[13]), twin_age=int(f[14])))
        elif k == 'STATE':
            d['states'][int(f[1])][f[2]] = dict(n=int(f[3]), cost=int(f[4]), cmin=int(f[5]), cmax=int(f[6]), speed=int(f[7]), load=int(f[8]))
        elif k == 'MONTH':
            d['months'].append(f[1:])
    return d


def speed_stats(states):
    mv = [states.get(c) for c in ('moving_loaded', 'moving_empty') if states.get(c)]
    n = sum(s['n'] for s in mv)
    allc = sum(s['n'] for s in states.values())
    ml = states.get('moving_loaded')
    return dict(mean_speed_moving=round(sum(s['speed'] for s in mv) / n, 2) if n else None,
                mean_speed_all_samples=round(sum(s['speed'] for s in states.values()) / allc, 2) if allc else None,
                mean_speed_loaded_moving=round(ml['speed'] / ml['n'], 2) if ml and ml['n'] else None,
                moving_share=round(n / allc, 4) if allc else None)


def rate(states, cls):
    s = states.get(cls)
    if not s or not s['n']:
        return None
    return round(s['cost'] / s['n'], 1)


STATE_CLASSES = ['moving_loaded', 'moving_empty', 'platform_loading_part', 'platform_loading_empty', 'platform_unloading', 'other_stopped', 'depot']


def write(name, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with (DATA / name).open('w', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(rows)


def tags(prefix):
    return sorted(p.name for p in RUNS.iterdir() if p.name.startswith(prefix) and (p / 'evidence.log').exists())


def route_tables(prefix, tag_re, outname):
    rows, summary = [], defaultdict(list)
    for t in tags(prefix):
        m = re.match(tag_re, t)
        if not m:
            continue
        meta = m.groupdict()
        d = parse_route(t)
        rec = receipt(t)
        if d['blocked'] or rec['reason'] != 'completed':
            rows.append(dict(tag=t, **meta, status=rec['reason'] + (':' + d['blocked'] if d['blocked'] else '')))
            continue
        first = d['years'][0]['year'] if d['years'] else None
        for y in d['years']:
            s = d['states'][y['year']]
            r = dict(tag=t, **meta, status='completed', year=y['year'], commissioning_year=y['year'] == first,
                     purchase=d['build']['purchase'], capacity=d['build']['capacity'], length16=d['build']['length16'],
                     delivered_quarterly=y['delivered_quarterly'], delivered_unloaded=y['unloaded'], arrivals=y['arrivals'],
                     revenue=y['revenue'], train_running=y['train_running'], property=y['property'],
                     operating_net_DERIVED=y['revenue'] - y['train_running'] - y['property'] - (y['other'] if y['year'] != first else 0),
                     vehicle_profit=y['vehicle_profit'], reliability=y['reliability'], age_days=y['age_days'], **speed_stats(s))
            for c in STATE_CLASSES:
                r['rate_' + c] = rate(s, c)
            if y['ramp_samples']:
                r['ramp_mean_speed'] = round(y['ramp_speed_sum'] / y['ramp_samples'], 2)
                r['ramp_min_speed'] = y['ramp_min_speed']
            rows.append(r)
            if y['year'] != first:
                summary[tuple(meta[k] for k in meta if k != 'seed')].append(r)
    write(outname + '_years.csv', rows)
    out = []
    for key, rs in sorted(summary.items()):
        seeds = sorted({r['seed'] for r in rs})
        def agg(f):
            v = [r[f] for r in rs if r.get(f) is not None]
            return (round(st.mean(v), 1), min(v), max(v)) if v else (None, None, None)
        row = dict(zip([k for k in re.compile(tag_re).groupindex if k != 'seed'], key))
        row.update(seeds=len(seeds), seed_years=len(rs))
        for f in ['delivered_unloaded', 'delivered_quarterly', 'arrivals', 'revenue', 'train_running', 'operating_net_DERIVED',
                  'mean_speed_moving', 'mean_speed_loaded_moving', 'moving_share', 'rate_moving_loaded', 'rate_moving_empty',
                  'rate_platform_loading_part', 'rate_platform_loading_empty', 'rate_depot', 'ramp_mean_speed', 'ramp_min_speed']:
            m_, lo, hi = agg(f)
            if m_ is not None:
                row[f + '_mean'] = m_
                row[f + '_min'] = lo
                row[f + '_max'] = hi
        row['purchase'] = rs[0]['purchase']
        row['capacity'] = rs[0]['capacity']
        out.append(row)
    write(outname + '_summary.csv', out)
    return rows, out


def age_table():
    rows = []
    for t in tags('t2b-age-'):
        d = parse_route(t)
        loco, seed = re.match(r't2b-age-(.+)-s(\d+)', t).groups()
        if d['blocked']:
            rows.append(dict(tag=t, loco=loco, seed=seed, status=d['blocked']))
            continue
        for y in d['years']:
            s = d['states'][y['year']]
            r = dict(tag=t, loco=loco, seed=seed, year=y['year'], age_years_DERIVED=round(y['age_days'] / 365.25, 2),
                     train_running_billed=y['train_running'], twin_in_depot_min=y['twin_min'], twin_in_depot_max=y['twin_max'],
                     twin_age_years_DERIVED=round(y['twin_age'] / 365.25, 2), reliability=y['reliability'])
            for c in STATE_CLASSES:
                r['rate_' + c] = rate(s, c)
                if s.get(c):
                    r['min_' + c] = s[c]['cmin']
                    r['max_' + c] = s[c]['cmax']
            rows.append(r)
    write('t2_state_by_age.csv', rows)
    return rows


def catalogue(tag):
    out = {}
    for f in lines(tag):
        if f[0] == 'ENGINE' and len(f) > 4:
            out.setdefault(f[1], {})[int(f[2])] = dict(name=f[3], price=int(f[4]), running=int(f[5]), buildable=f[13] if len(f) > 13 else None)
    return out


def compat_table():
    rows = []
    for year in (1850, 2000):
        b = catalogue(f't3-catalogue-{year}-base').get('start', {})
        c = catalogue(f't3-catalogue-{year}-compat').get('start', {})
        for i in sorted(b):
            if i in c:
                rows.append(dict(year=year, engine=i, name=b[i]['name'], price_base=b[i]['price'], price_compat=c[i]['price'],
                                 running_base=b[i]['running'], running_compat=c[i]['running'],
                                 running_ratio_DERIVED=round(c[i]['running'] / b[i]['running'], 4) if b[i]['running'] else None))
    write('t3_compat_catalogue.csv', rows)
    return rows


def date_table():
    rows = []
    for t in tags('t5-control-'):
        y = int(t.rsplit('-', 1)[1])
        for i, e in catalogue(t).get('start', {}).items():
            rows.append(dict(run=t, timekeeping='calendar', economy_year=y, calendar_year_DERIVED=y, engine=i, name=e['name'], running=e['running']))
    for t in tags('t5b-wallclock-'):
        months, start_day, start_cat = {}, None, None
        for f in lines(t):
            if f[0] == 'DATE':
                months['m%d' % (len(months) + 1)] = (int(f[1]), int(f[2]))
            if f[0] == 'BEGIN':
                start_day = int(f[1])
        cat = catalogue(t)
        months['start'] = (start_day, None)
        for tag, (day, year) in months.items():
            for i, e in cat.get(tag, {}).items():
                rows.append(dict(run=t, timekeeping='wallclock', sample=tag, economy_day=day, economy_year_GSDate=year,
                                 engine=i, name=e['name'], running=e['running'], buildable=e.get('buildable')))
    write('t5_date_basis.csv', rows)
    return rows


if __name__ == '__main__':
    res = {}
    res['t1'] = route_tables('t1-', r't1-(?P<loco>[a-z]+)-(?P<wagons>\d+)-(?P<supply>l\d+(?:nosub)?)-s(?P<seed>\d+)$', 't1')[1]
    res['t2'] = len(age_table())
    res['t3'] = len(compat_table())
    route_tables('t3-norris-service-', r't3-norris-service-(?P<variant>[a-z]+)-s(?P<seed>\d+)$', 't3_service')
    route_tables('t4-', r't4-(?P<terrain>ramp|flat)-(?P<loco>[a-z0-9]+)-(?P<wagons>\d+)-s(?P<seed>\d+)$', 't4_early')
    route_tables('t4-heavy-', r't4-heavy-(?P<terrain>ramp|flat)-(?P<loco>[a-z0-9-]+)-s(?P<seed>\d+)$', 't4_heavy')
    route_tables('t4-heavynosub-', r't4-heavynosub-(?P<terrain>ramp|flat)-(?P<loco>[a-z0-9-]+)-s(?P<seed>\d+)$', 't4_heavy_nosub')
    res['t5'] = len(date_table())

    print(json.dumps({k: (v if isinstance(v, int) else len(v)) for k, v in res.items()}))
