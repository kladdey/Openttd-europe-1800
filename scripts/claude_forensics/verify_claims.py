"""Assertion checks for the headline numerical claims in the Claude reinvestigation reports.
Fails loudly if committed evidence no longer supports a claim.
Usage: python3 -I scripts/claude_forensics/verify_claims.py <repo_root>
"""
import csv, os, re, sys
root = sys.argv[1] if len(sys.argv) > 1 else '.'
R = os.path.join(root, 'docs', 'research'); D = os.path.join(R, 'claude_forensics')
ok = 0
def check(cond, msg):
    global ok
    if not cond: raise SystemExit('FAILED: ' + msg)
    ok += 1; print('PASS', msg)

price = lambda base: base * 6 >> 3
cost = lambda base, f, e: (price(base) * f << (e - 8)) if e >= 8 else (price(base) * f) >> (8 - e)
# 1. Formula reproduces catalogue values (src/engine.cpp, src/economy.cpp, table/pricebase.h)
check(cost(5600, 4, 3) == 525, 'Planet = 4200*4*2^3/256 = 525')
check(cost(5600, 24, 3) == 3150, 'Grasshopper = 4200*24*2^3/256 = 3150')
check(cost(5600, 24, 4) == 6300, 'Norris = 4200*24*2^4/256 = 6300')
check(cost(5600, 9, 3) == 1181, 'Coppernob = floor(4200*9*2^3/256) = 1181')
check(abs(6300 / 1181 - 2 * 24 / 9) < 0.01, 'Norris/Coppernob 5.33 = exponent 2 x factor 2.67')
# 2. JGRPP debug log exponents
log = open(os.path.join(R, 'vehicle_runtime_mapping.log'), encoding='utf-8', errors='replace').read()
check(re.search(r"newnars\.grf' sets local price base multiplier 42 to 4", log) is not None, 'NARS 2.52 steam running exponent +4 (engine debug)')
check(re.search(r"proj1000\.grf' sets local price base multiplier 42 to 3", log) is not None, 'UKRS2 steam running exponent +3 (engine debug)')
check(re.search(r"nars_add_on_set\.grf' sets local price base multiplier 42 to 3", log) is not None, 'Add-on steam running exponent +3 (engine debug)')
# 3. Base class inference: all NARS 2.52 and UKRS2 locos price on the steam base
inf = list(csv.DictReader(open(os.path.join(D, 'running_cost_factor_inference.csv'))))
for s in ('UKRS2', 'NARS 2.52'):
    sel = [r for r in inf if r['set'] == s and r['snapshot_year'] == '1830']
    check(sel and all(r['matched_classes'] == 'steam' for r in sel), f'all {len(sel)} {s} powered entries reproduce exactly only on the steam base')
# 4. Calendar dependence: only UKRS2 varies across Phase 1 snapshots
snap = list(csv.DictReader(open(os.path.join(R, 'vehicle_economy_snapshots.csv'), encoding='utf-8-sig')))
var = {}
for r in snap:
    if r['wagon'] == 'true': continue
    var.setdefault((r['source_grfid'], r['local_vehicle_id']), set()).add(r['annual_running_cost_gbp'])
varying = {k[0] for k, v in var.items() if len(v) > 1}
check(varying == {'44441000'}, 'only UKRS2 engines have calendar-dependent running cost')
pc = {r['snapshot_year']: int(r['annual_running_cost_gbp']) for r in snap if r['source_grfid'] == '44441000' and r['local_vehicle_id'] == '124'}
cn = {r['snapshot_year']: int(r['annual_running_cost_gbp']) for r in snap if r['source_grfid'] == '44441000' and r['local_vehicle_id'] == '113'}
check(all(cn[y] - cn['1830'] == pc[y] - pc['1830'] for y in pc), 'UKRS2 surcharge is an identical additive step for Planet and Coppernob in every snapshot')
# 5. Ledger: Planet billing rises with age, Grasshopper flat
rr = list(csv.DictReader(open(os.path.join(R, 'transport_route_results.csv'), encoding='utf-8-sig')))
pl = [int(r['actual_vehicle_running_expense_gbp']) for r in rr if r['tag'] == 'rail-coal-ledger']
gr = [int(r['actual_vehicle_running_expense_gbp']) for r in rr if r['tag'] == 'rail-grasshopper']
check(pl[0] == 666 and pl[-1] == 1288 and len(pl) == 20, 'Planet coal billed 666 (yr1) -> 1288 (yr20)')
check(max(gr) - min(gr) <= 150 and abs(sum(gr) / len(gr) - 3251) < 1, 'Grasshopper billed flat ~3251')
check(4.9 < (sum(gr) / 5) / (sum(pl[:5]) / 5) < 5.3, 'billed ratio years 1-5 about 5.1x (catalogue 6.0x)')
# 6. State-dependent built-train rates
tt = {r['snapshot_year'] + r['test_id']: r for r in csv.DictReader(open(os.path.join(R, 'representative_train_tests.csv'), encoding='utf-8-sig'))}
n = tt['1849norris_coal_4_uk']; g = tt['1849grasshopper_coal_4_uk']; p = tt['1849planet_coal_4_uk']
check(int(n['built_depot_running_rate_gbp_year']) < 0.3 * int(n['moving_empty_rate_peak_gbp_year']), 'NARS Norris depot rate < 30% of moving rate (callback)')
check(g['built_depot_running_rate_gbp_year'] == g['moving_empty_rate_peak_gbp_year'], 'Add-on Grasshopper flat rate in depot and moving')
check(int(p['moving_empty_rate_peak_gbp_year']) < int(p['display_rate_sum_gbp_year']), 'UKRS2 Planet moving-empty rate below catalogue sum')
# 7. Saved campaign: engine-level stopped/depot divisors are 1 (no engine discount)
import json
pats = json.load(open(os.path.join(R, 'transport_economic_settings.json')))['embedded_scenario']['PATS'][0]
check(pats['difficulty.vehicle_costs_in_depot'] == 1 and pats['difficulty.vehicle_costs_when_stopped'] == 1, 'JGRPP depot/stopped running-cost divisors = 1 in campaign')
print(f'\n{ok} checks passed')
