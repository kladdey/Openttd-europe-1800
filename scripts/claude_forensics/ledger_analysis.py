"""Billed (annual finance ledger) running expense versus catalogue, from Phase 3 in-game runs.

Input: docs/research/transport_route_results.csv (VERIFIED IN GAME ledger rows, Phase 3).
Catalogue sums: Planet 525 + 4 x UKRS2 Open Wagon 7 = 553; Grasshopper 3150 + 4 x 7 = 3178
(docs/research/representative_train_tests.csv, planet_coal_4_uk / grasshopper_coal_4_uk).
Usage: python3 -I scripts/claude_forensics/ledger_analysis.py <repo_root>
"""
import csv, sys, os, statistics as st
root = sys.argv[1] if len(sys.argv) > 1 else '.'
R = os.path.join(root, 'docs', 'research')
rows = list(csv.DictReader(open(os.path.join(R, 'transport_route_results.csv'), encoding='utf-8-sig')))
CAT = {'2-2-0 Planet (Steam)': 553, '0-4-0 Grasshopper (Steam)': 3178}
out = []
def p(s=''): print(s); out.append(s)
def series(tag): return [r for r in rows if r['tag'] == tag]
p('tag | yr | age d | billed running | billed/catalogue | revenue | delivered | reliability')
for tag in ['rail-coal-ledger', 'rail-grasshopper', 'rail-wood-final', 'rail-wood-grasshopper', 'rail-lodi']:
    for r in series(tag):
        c = CAT.get(r['vehicle_name']); b = int(r['actual_vehicle_running_expense_gbp'])
        ratio = f'{b/c:.2f}' if c and r['configured_wagons'] == '4' and 'lodi' not in tag else 'n/a'
        p(f"{tag} | {r['economy_year']} | {r['vehicle_age_days']} | {b} | {ratio} | {r['revenue_gbp']} | {r['delivered_cargo_units']} | {r['lead_reliability_percent']}")
pl = series('rail-coal-ledger'); gr = series('rail-grasshopper')
b = [int(r['actual_vehicle_running_expense_gbp']) for r in pl]
ages = [int(r['vehicle_age_days'])/365 for r in pl]
mx = st.mean(ages); my = st.mean(b)
slope = sum((a-mx)*(y-my) for a, y in zip(ages, b)) / sum((a-mx)**2 for a in ages)
p(f'\nPlanet coal (same route, same consist, 1830-1849 calendar; no calendar surcharge before 1913):')
p(f'  billed year1 {b[0]}, year20 {b[-1]}; OLS slope {slope:.1f} GBP/yr per year of age; 20-yr mean {st.mean(b):.0f}')
g = [int(r['actual_vehicle_running_expense_gbp']) for r in gr]
p(f'Grasshopper coal (same route/consist, 5 yrs): mean {st.mean(g):.0f}, range {min(g)}-{max(g)} (flat)')
p(f'Catalogue engine ratio Grasshopper/Planet: {3150/525:.2f}; consist catalogue ratio {3178/553:.2f}')
p(f'Billed ratio, years 1-5 (same years): {st.mean(g)/st.mean(b[:5]):.2f}')
p(f'Billed ratio vs Planet 20-yr lifecycle mean (Grasshopper assumed flat, as observed): {st.mean(g)/st.mean(b):.2f}')
rp = [int(r['revenue_gbp']) for r in pl[:5]]; rg = [int(r['revenue_gbp']) for r in gr]
dp = [int(r['delivered_cargo_units']) for r in pl[:5]]; dg = [int(r['delivered_cargo_units']) for r in gr]
p(f'Years 1-5 mean: Planet revenue {st.mean(rp):.0f}, delivered {st.mean(dp):.0f}; Grasshopper revenue {st.mean(rg):.0f}, delivered {st.mean(dg):.0f}')
p(f'Years 1-5 mean (revenue - billed running - 132 property): Planet {st.mean(rp)-st.mean(b[:5])-132:.0f}; Grasshopper {st.mean(rg)-st.mean(g)-132:.0f}')
od = os.path.join(R, 'claude_forensics'); os.makedirs(od, exist_ok=True)
open(os.path.join(od, 'ledger_analysis.txt'), 'w').write('\n'.join(out) + '\n')
