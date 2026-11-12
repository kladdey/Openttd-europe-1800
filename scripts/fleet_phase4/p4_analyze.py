"""Phase 4 analysis: evidence logs -> per-run rows -> aggregated results.

Labels in column names: no suffix = RUNTIME (measured in JGRPP), _DERIVED = arithmetic on
RUNTIME values. Writes docs/research/fleet_phase4/runs_table.csv and fleet_phase4_results.csv.
"""
import csv, json, statistics as st
from collections import defaultdict
from pathlib import Path
import p4lib as P

A = P.A
OUT = P.OUT
ROSTER = {int(r['runtime_engine_id']): r for r in csv.DictReader(open(OUT.parents[0] / 'vehicle_roster.csv', encoding='utf-8-sig'))}
SET = {'44440302': 'NARS', '4E4D0518': 'NARS Add-On', '44441000': 'UKRS2', '53410808': 'GETS', '4D560103': 'PTS', '4D560105': 'PRSP'}


def terrain_of(m):
    r = m.get('ramp')
    if not r:
        return 'flat'
    return 'moderate1.5' if len(r) > 2 and r[2] == 2 else 'sustained3'


def run_rows():
    rows = []
    for d in sorted(A.RUNS.iterdir()):
        if not (d / 'receipt.json').exists():
            continue
        rec = json.loads((d / 'receipt.json').read_text())
        m = json.loads((d / 'manifest.json').read_text())
        if m.get('mode') != 'route':
            continue
        g = m['gs_config']
        base = dict(tag=d.name, suite=d.name.split('-')[0], label=d.name.split('-')[1], year=m['year'], seed=m['seed'],
                    engine=g['engine'], set=SET.get(ROSTER.get(g['engine'], {}).get('source_grfid'), '?'),
                    name=ROSTER.get(g['engine'], {}).get('vehicle_name', '?'), cargo=g.get('cargo', 'COAL'), distance=g['distance'],
                    terrain=terrain_of(m), wagons_requested=g['wagons'], wagon=g['wagon'], supply_level=g.get('production_level'),
                    grfs='+'.join(x['file'] for x in m.get('extras', [])) or 'original', status=rec['reason'])
        if rec['reason'] != 'completed':
            r = A.parse_route(d.name)
            base['status'] = rec['reason'] + (':' + r['blocked'] if r['blocked'] else '')
            rows.append(base)
            continue
        r = A.parse_route(d.name)
        ys = r['years'][1:]   # drop commissioning year
        if not ys:
            base['status'] = 'no stable year'
            rows.append(base)
            continue
        f = lambda k: st.mean(y[k] for y in ys)
        states = defaultdict(lambda: dict(n=0, cost=0, speed=0))
        for y in ys:
            for c, v in r['states'][y['year']].items():
                states[c]['n'] += v['n']; states[c]['cost'] += v['cost']; states[c]['speed'] += v['speed']
        moving = [states[c] for c in ('moving_loaded', 'moving_empty') if states[c]['n']]
        mv_n = sum(s['n'] for s in moving)
        all_n = sum(s['n'] for s in states.values())
        delivered, revenue, running, prop = f('unloaded'), f('revenue'), f('train_running'), f('property')
        profit = revenue - running - prop
        b = r['build']
        row = dict(base, years_measured=len(ys), purchase=b['purchase'], infrastructure=b['infrastructure'], capacity=b['capacity'],
                   length16=b['length16'], parts=b['parts'], catalogue_engine_running=r['catalogue'].get(g['engine'], {}).get('running'),
                   delivered=round(delivered, 1), revenue=round(revenue, 1), running=round(running, 1), property=round(prop, 1),
                   operating_profit_DERIVED=round(profit, 1),
                   mean_speed_moving=round(sum(s['speed'] for s in moving) / mv_n, 2) if mv_n else None,
                   moving_share=round(mv_n / all_n, 4) if all_n else None,
                   rate_moving=round(sum(s['cost'] for s in moving) / mv_n, 1) if mv_n else None,
                   rate_platform=round(states['platform_loading_part']['cost'] / states['platform_loading_part']['n'], 1) if states['platform_loading_part']['n'] else None,
                   rate_depot=round(states['depot']['cost'] / states['depot']['n'], 1) if states['depot']['n'] else None,
                   ramp_mean_speed=round(sum(y['ramp_speed_sum'] for y in ys) / max(1, sum(y['ramp_samples'] for y in ys)), 2) if any(y['ramp_samples'] for y in ys) else None,
                   ramp_min_speed=min((y['ramp_min_speed'] for y in ys if y['ramp_min_speed'] >= 0), default=None),
                   reliability=round(f('reliability'), 1))
        tt = delivered * g['distance']
        row['running_per_unit_tile_DERIVED'] = round(running / tt, 5) if tt else None
        row['payback_vehicle_years_DERIVED'] = round(b['purchase'] / profit, 2) if profit > 0 else None
        row['payback_with_line_years_DERIVED'] = round((b['purchase'] + b['infrastructure']) / profit, 2) if profit > 0 else None
        row['cash10_DERIVED'] = round(-b['purchase'] + 10 * profit)
        row['cash20_DERIVED'] = round(-b['purchase'] + 20 * profit)
        rows.append(row)
    return rows


NUM = ['delivered', 'revenue', 'running', 'operating_profit_DERIVED', 'mean_speed_moving', 'moving_share', 'rate_moving', 'rate_platform',
       'rate_depot', 'ramp_mean_speed', 'ramp_min_speed', 'running_per_unit_tile_DERIVED', 'payback_vehicle_years_DERIVED',
       'payback_with_line_years_DERIVED', 'cash10_DERIVED', 'cash20_DERIVED', 'reliability']
KEY = ['suite', 'label', 'year', 'engine', 'set', 'name', 'cargo', 'distance', 'terrain', 'wagons_requested', 'supply_level', 'grfs']


def aggregate(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in KEY)].append(r)
    out = []
    for k, rs in sorted(groups.items(), key=lambda kv: [str(x) for x in kv[0]]):
        ok = [r for r in rs if r['status'] == 'completed']
        row = dict(zip(KEY, k), seeds_attempted=len(rs), seeds_completed=len(ok),
                   failures=';'.join(sorted({r['status'] for r in rs if r['status'] != 'completed'})))
        if ok:
            row.update(purchase=ok[0]['purchase'], capacity=ok[0]['capacity'], length16=ok[0]['length16'],
                       catalogue_engine_running=ok[0]['catalogue_engine_running'])
            for f in NUM:
                v = [r[f] for r in ok if r.get(f) is not None]
                if v:
                    row[f] = round(st.mean(v), 2)
                    if f in ('delivered', 'operating_profit_DERIVED', 'running'):
                        row[f + '_sd'] = round(st.pstdev(v), 1)
                        row[f + '_min'] = min(v)
                        row[f + '_max'] = max(v)
        out.append(row)
    return out


def write(path, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, 'w', newline='', encoding='utf8') as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    rows = run_rows()
    write(OUT / 'runs_table.csv', rows)
    agg = aggregate(rows)
    write(OUT / 'fleet_phase4_results.csv', agg)
    print(len(rows), 'runs,', sum(r['status'] == 'completed' for r in rows), 'completed;', len(agg), 'configurations')
