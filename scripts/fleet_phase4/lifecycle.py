"""20-year measured lifecycle (autorenew off) and autoreplace results (RUNTIME; cash flows DERIVED)."""
import csv, json, statistics as st
from collections import defaultdict
import p4lib as P

rows, summ = [], defaultdict(list)
for d in sorted(P.A.RUNS.iterdir()):
    if not d.name.startswith('life-'):
        continue
    label = d.name.split('-')[1]
    r = P.A.parse_route(d.name)
    b = r['build']
    cum = -b['purchase']
    for i, y in enumerate(r['years']):
        profit = y['revenue'] - y['train_running'] - y['property']
        cum += profit
        rows.append(dict(run=d.name, label=label, year=y['year'], age_years_DERIVED=round(y['age_days'] / 365.25, 2), delivered=y['unloaded'],
                         revenue=y['revenue'], running=y['train_running'], operating_profit_DERIVED=profit, cumulative_cash_DERIVED=cum,
                         twin_depot_rate=y['twin_max'], reliability=y['reliability']))
    ys = r['years']
    prof = [y['revenue'] - y['train_running'] - y['property'] for y in ys]
    summ[label].append(dict(purchase=b['purchase'], cash10=-b['purchase'] + sum(prof[:10]), cash20=-b['purchase'] + sum(prof[:20]),
                            run_y1_5=st.mean(y['train_running'] for y in ys[1:6]), run_y16_20=st.mean(y['train_running'] for y in ys[16:21]),
                            depot_first=ys[0]['twin_max'], depot_last=ys[-1]['twin_max'], payback=next((i + 1 for i in range(len(prof)) if sum(prof[:i + 1]) >= b['purchase']), None)))
with open(P.OUT / 'lifecycle_years.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
out = {}
for label, xs in summ.items():
    out[label] = {k: round(st.mean(x[k] for x in xs if x[k] is not None), 1) if any(x[k] is not None for x in xs) else None for k in xs[0]}
    out[label]['seeds'] = len(xs)
ar = {}
for d in sorted(P.A.RUNS.iterdir()):
    if d.name.startswith('arep-'):
        lines = P.A.lines(d.name)
        rep = [f for f in lines if f[0] == 'REPLACED']
        sets = [f for f in lines if f[0] == 'AUTOREPLACE_SET']
        build = next((f for f in lines if f[0] == 'BUILD'), None)
        ar[d.name] = dict(rule=sets[0][1:] if sets else None, replaced=[dict(date=f[1], old=f[2], new=f[3], engine=f[4], name=f[5], parts=f[6], capacity=f[7], running=f[8]) for f in rep],
                          original_parts=build[6] if build else None, original_capacity=build[4] if build else None)
(P.OUT / 'lifecycle_summary.json').write_text(json.dumps(dict(lifecycle=out, autoreplace=ar), indent=2))
for k, v in sorted(out.items()): print(k, v)
for k, v in ar.items(): print(k, v['rule'], v['replaced'][:1], 'orig parts', v['original_parts'], 'cap', v['original_capacity'])
