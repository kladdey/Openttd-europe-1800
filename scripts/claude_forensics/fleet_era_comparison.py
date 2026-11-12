"""Era x traction x set comparison of running cost per hp and per kN, evaluated IN SERVICE.

For each powered engine (hp>50), take the observation from the first Phase 2 snapshot year
that is >= its introduction year and <= intro+25 (so UKRS2's calendar surcharge is included
as a player would actually pay it). Medians over de-duplicated economic profiles.
Usage: python3 -I scripts/claude_forensics/fleet_era_comparison.py <repo_root>
"""
import csv, sys, os, collections, statistics as st
root = sys.argv[1] if len(sys.argv) > 1 else '.'
R = os.path.join(root, 'docs', 'research')
rows = [r for r in csv.DictReader(open(os.path.join(R, 'vehicle_economy_normalized.csv'), encoding='utf-8-sig')) if r['kind'] == 'powered']
YEARS = [1830, 1849, 1879, 1913, 1945, 1970, 1990, 2025]
by = collections.defaultdict(dict)
for r in rows:
    by[(r['source_grfid'], r['local_vehicle_id'])][int(r['snapshot_year'])] = r
ERAS = [(1830, 1879), (1880, 1913), (1914, 1945), (1946, 1970), (1971, 1990), (1991, 2025)]
cells = collections.defaultdict(list); seen = set()
for k, d in by.items():
    any_r = next(iter(d.values()))
    intro = int(any_r['introduction_year']); hp = int(any_r['power_hp'] or 0)
    if hp <= 50: continue
    ys = [y for y in YEARS if intro <= y <= intro + 25 and y in d]
    if not ys: continue
    r = d[ys[0]]
    prof = (r['set_name'], r['vehicle_name'].split('(')[0].strip(), r['display_running_gbp_year'], r['power_hp'])
    if prof in seen: continue
    seen.add(prof)
    era = next((e for e in ERAS if e[0] <= intro <= e[1]), None)
    if not era: continue
    run = int(r['display_running_gbp_year']); te = float(r['tractive_effort_kn'] or 0)
    role = r['role']
    cells[(r['traction'], era, r['set_name'])].append((run / hp, run / te if te > 0 else None, int(r['purchase_gbp']) / hp, role, r['multiple_unit'] if 'multiple_unit' in r else ''))
sets = ['UKRS2', 'NARS 2.52', 'NARS Add-On 2cc', 'GETS', 'Polish Train Set', 'Polish Rolling Stock Pack']
out = []
hdr = 'traction | era | ' + ' | '.join(f'{s} run/hp (n)' for s in sets)
out.append(hdr)
for tr in ['Steam', 'Diesel', 'Electric']:
    for era in ERAS:
        vals = []
        for s in sets:
            v = cells.get((tr, era, s), [])
            vals.append(f'{st.median(x[0] for x in v):.2f} ({len(v)})' if v else '-')
        if any(x != '-' for x in vals):
            out.append(f'{tr} | {era[0]}-{era[1]} | ' + ' | '.join(vals))
out.append('\npurchase GBP per hp, same cells')
for tr in ['Steam', 'Diesel', 'Electric']:
    for era in ERAS:
        vals = []
        for s in sets:
            v = cells.get((tr, era, s), [])
            vals.append(f'{st.median(x[2] for x in v):.1f}' if v else '-')
        if any(x != '-' for x in vals):
            out.append(f'{tr} | {era[0]}-{era[1]} | ' + ' | '.join(vals))
out.append('\nCounterfactual: NARS 2.52 running exponent +4 -> +3 (all NARS 2.52 running costs x0.5), run/hp medians')
out.append('traction | era | NARS 2.52 now | NARS 2.52 x0.5 | median of the other sets present')
for tr in ['Steam', 'Diesel', 'Electric']:
    for era in ERAS:
        v = cells.get((tr, era, 'NARS 2.52'), [])
        others = [st.median(x[0] for x in cells[(tr, era, s)]) for s in sets if s != 'NARS 2.52' and cells.get((tr, era, s))]
        if v and others:
            m = st.median(x[0] for x in v)
            out.append(f'{tr} | {era[0]}-{era[1]} | {m:.2f} | {m/2:.2f} | {st.median(others):.2f} (of {len(others)} sets)')
txt = '\n'.join(out); print(txt)
od = os.path.join(R, 'claude_forensics'); os.makedirs(od, exist_ok=True)
open(os.path.join(od, 'fleet_era_comparison.txt'), 'w').write(txt + '\n')
