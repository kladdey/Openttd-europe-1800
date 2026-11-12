"""Automated validation of the Phase 4 claims against committed evidence (no game run needed).

  python -B test_phase4.py        -> exit 1 on any failure
"""
import csv, hashlib, json, subprocess, sys
from collections import defaultdict
from pathlib import Path
import p4lib as P

OUT = P.OUT
fails = []


def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (f'  [{detail}]' if detail else ''))
    if not ok:
        fails.append(name)


# 1. Phase-3 findings still re-derive from their evidence
r = subprocess.run([sys.executable, '-B', str(Path(__file__).parent / 'verify_prior_evidence.py')], capture_output=True, text=True)
check('phase-3 findings re-derived (31 checks)', r.returncode == 0 and '0 failures' in r.stdout)

# 2. Mechanism feasibility (in-service consist rates incl. 4 NARS hoppers = 152)
def svc(tag):
    d = P.A.parse_route(tag); y = d['years'][-1]['year']; s = d['states'][y]
    return round(s['moving_loaded']['cost'] / s['moving_loaded']['n']), round(s['depot']['cost'] / s['depot']['n'])
check('NARS static factor 0x0D is ignored in service (trap)', svc('feas-f1-nars-factor-service') == svc('feas-base-norris-service') == (6452, 1727))
check('NARS class switch works in service, 1/4 standstill kept', svc('feas-f2-nars-class44-service') == (5552, 1502))
check('Add-On static factor works in service', svc('feas-f3-addon-factor-service') == (1727, 1727))
check('UKRS2 static factor has no effect', svc('feas-f4-ukrs2-factor-service') == svc('feas-base-planet-service'))
check('UKRS2 class switch works in service', svc('feas-f9-ukrs2-class44-service') == (1502, 602))
cat = lambda t: P.catalogue(f'feas-{t}-catalogue')
check('NARS class 44 unused by any NARS vehicle', P.cat_diff('feas-base-catalogue', 'feas-f5-nars-mult44-catalogue') == [])
check('NARS class 43 carries 42 NARS wagons (avoid)', len(P.cat_diff('feas-base-catalogue', 'feas-f6-nars-mult43-catalogue')) == 42)
check('UKRS2 class 44 unused', P.cat_diff('feas-base-catalogue', 'feas-f11-ukrs2-mult44-catalogue') == [])

# 3. Catalogue integrity of the three variants
ci = json.loads((OUT / 'catalogue_integrity.json').read_text())
check('variants change exactly the intended engines, at 3 dates',
      all(not v['unexpected_running_changes'] and not v['expected_but_unchanged'] for v in ci.values()))
check('variants change no price/power/TE/weight/speed/date/capacity', all(not v['other_field_changes'] for v in ci.values()))
check('Variant B changes only the 21 NARS steam engines', ci['B_steam-1850']['running_changed'] == 21 and ci['B_steam-1850']['by_set']['NARS'] == 21)
check('Variant C changes 71 NARS + 2 Add-On', ci['C_cross-1850']['by_set']['NARS'] == 71 and ci['C_cross-1850']['by_set']['Add-On'] == 2)

# 4. Determinism: unaffected control engines reproduce the original runs exactly
R = list(csv.DictReader(open(OUT / 'runs_table.csv', encoding='utf8')))
base = {(r['year'], r['engine'], r['terrain'], r['supply_level'], r['cargo'], r['seed']): r for r in R if r['suite'] == 'era' and r['label'] == 'base' and r['status'] == 'completed'}
ctl = [r for r in R if r['suite'] == 'era' and r['label'] != 'base' and r['engine'] in ('1509', '3167') and r['status'] == 'completed']
mism = [r['tag'] for r in ctl if (r['delivered'], r['revenue'], r['running']) != tuple(base[(r['year'], r['engine'], r['terrain'], r['supply_level'], r['cargo'], r['seed'])][k] for k in ('delivered', 'revenue', 'running'))]
check('determinism controls identical under all variant GRFs', len(ctl) >= 150 and not mism, f'{len(ctl)} runs')

# 5. Callback state ratios preserved
ratios = json.loads((OUT / 'callback_state_ratios.json').read_text())
check('standstill/moving ratio unchanged for every modified engine',
      all(abs(v[k] - v['base']) <= 0.01 for v in ratios.values() for k in v if k != 'base'))

# 6. Cloned-save tests
for v in ('B_steam', 'C_cross'):
    p = OUT / f'savecompare_{v}.json'
    if p.exists():
        s = json.loads(p.read_text())
        check(f'save {v}: identity kept, rollback restores, prices unchanged',
              s['identity_original_vs_balanced'] and s['identity_balanced_end_vs_rollback'] and s['rollback_restores_all_costs'] and not s['engines_price_changed'] and s['train_cost_changed_only_for_changed_engines'])
    t = json.loads((OUT / f'savetest_{v}.json').read_text())
    check(f'save {v}: production save folder and source untouched', t['production_save_dir_unchanged'] and t['source_unchanged'])

# 6b. Windowed multiplayer client: sync checks performed, no desync
g = OUT / 'mptest_C_cross_gui.json'
if g.exists():
    m = json.loads(g.read_text())
    check('GUI client: 2 joins, 0 missed sync frames, no desync',
          sum(' joined as ' in l for l in m['server_connect_lines']) == 2 and all(c['missed'] == 0 and not c['desync'] for c in m['client_full']) and not m['server_desync_lines'])

# 7. Built GRFs are byte-identical to the GRFs used in the runs
man = json.loads((OUT / 'grf_build' / 'MANIFEST.json').read_text())
same = []
for v, files in man.items():
    for f in files:
        tag = v.split('_')[0]
        used = OUT / 'grf' / f"rv_{f['grfid'].lower()}_{tag}.grf"
        same.append(used.exists() and hashlib.sha256(used.read_bytes()).hexdigest() == f['sha256'])
check('build script reproduces the tested GRFs byte-for-byte', all(same) and len(same) == 5)

# 8. Economic claims (aggregated RUNTIME results, profit DERIVED)
A = list(csv.DictReader(open(OUT / 'fleet_phase4_results.csv', encoding='utf8')))
def prof(label, terrain='flat', dist='32', wagons=None, lvl=None, cargo='COAL'):
    for r in A:
        if r['suite'] == 'p1850' and r['label'] == label and r['terrain'] == terrain and r['distance'] == dist and r['cargo'] == cargo \
           and (wagons is None or r['wagons_requested'] == str(wagons)) and (lvl is None or r['supply_level'] == str(lvl)):
            return float(r['operating_profit_DERIVED'])
check('Norris 2700 beats Planet on heavy 12-hopper duty', prof('norris2700', wagons=12, lvl=128) > 1.4 * prof('planet', wagons=12, lvl=128))
check('Norris 2700 within +-10% of Planet on light 6-hopper duty', abs(prof('norris2700', wagons=6, lvl=16) / prof('planet', wagons=6, lvl=16) - 1) < 0.10)
check('Norris never beats Coppernob, even at 675', all(prof(f'norris{v}', wagons=w, lvl=l) < prof('coppernob', wagons=w, lvl=l) for v in (675, 1350, 2700) for w in (6, 12) for l in (16, 128)))
check('Grasshopper stays below Planet even at Planet cost', all(prof(f'grass{v}', wagons=6, lvl=16) < prof('planet', wagons=6, lvl=16) for v in (525, 787, 1050, 1575, 3150)))
era = defaultdict(dict)
for r in A:
    if r['suite'] == 'era' and r.get('operating_profit_DERIVED'):
        era[(r['year'], r['terrain'], r['supply_level'], r['cargo'])].setdefault(r['engine'], {})[r['label']] = (float(r['operating_profit_DERIVED']), r['set'])
worst = 0
for k, engs in era.items():
    for e, d in engs.items():
        if 'C_cross' in d and d['C_cross'][1] == 'NARS':
            others = [x.get('C_cross', x['base'])[0] for e2, x in engs.items() if e2 != e]
            if others and max(others) > 0 and d['C_cross'][0] > 0:
                worst = max(worst, d['C_cross'][0] / max(others))
check('Variant C creates no NARS outlier (<= 1.10 x best other engine in any era/duty)', worst <= 1.10, f'max {worst:.3f}')

# 9. Judah in its passenger role (1866)
J = {(r['label'], r['engine'], r['distance']): float(r['operating_profit_DERIVED']) for r in A if r['suite'] == 'judah' and r.get('operating_profit_DERIVED')}
rivals = [J[('original', e, '48')] for e in ('1533', '1532', '1531')]
check('Judah C improves on short passenger duty but stays below Lady, Crampton, Coppernob',
      J[('original', '2044', '48')] < J[('C_cross', '2044', '48')] < min(rivals))
check('American C not overpowered in 1866 passenger (<= 1.05 x Lady)',
      J[('C_cross', '1586', '96')] <= 1.05 * J[('original', '1533', '96')] and J[('C_cross', '1586', '48')] <= 1.05 * J[('original', '1533', '48')])

print(f'\n{len(fails)} failures')
sys.exit(1 if fails else 0)
