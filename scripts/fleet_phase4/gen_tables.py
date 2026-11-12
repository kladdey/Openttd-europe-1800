"""Markdown tables for the Phase 4 documents, generated from fleet_phase4_results.csv."""
import csv, sys
from collections import defaultdict
import p4lib as P
A = [r for r in csv.DictReader(open(P.OUT / 'fleet_phase4_results.csv', encoding='utf8')) if r['suite'] == 'era' and r.get('operating_profit_DERIVED')]
DUTY = {('flat', '128', 'COAL'): 'flat, saturated', ('flat', '16', 'COAL'): 'flat, supply-limited', ('sustained3', '128', 'COAL'): '3% sustained', ('flat', '', 'PASS'): 'passenger'}
T = defaultdict(dict)
for r in A:
    d = DUTY.get((r['terrain'], r['supply_level'] if r['cargo'] == 'COAL' else '', r['cargo']))
    T[(int(r['year']), d)].setdefault(r['engine'], dict(name=r['name'], set=r['set']))[r['label']] = float(r['operating_profit_DERIVED'])
V = ['base', 'A_targeted', 'B_steam', 'C_cross']
lines = ['| Era | Duty | Set | Locomotive | Original £/yr | A | B | C |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
for (y, d), engs in sorted(T.items()):
    best = {v: max(x.get(v, x['base']) for x in engs.values()) for v in V}
    for e, x in sorted(engs.items(), key=lambda kv: -kv[1]['base']):
        cells = []
        for v in V:
            val = x.get(v, x['base'])
            share = val / best[v] if best[v] > 0 else float('nan')
            changed = v != 'base' and v in x and abs(x[v] - x['base']) > 1
            sh = f'{share:.2f}' if share == share else 'all <0'
            cells.append(f"{'**' if changed else ''}{val/1000:.1f}k ({sh}){'**' if changed else ''}")
        lines.append(f"| {y} | {d} | {x['set']} | {x['name']} | " + ' | '.join(cells) + ' |')
out = P.OUT / 'era_comparison_table.md'
out.write_text('\n'.join(lines) + '\n', encoding='utf8')
print(out, len(lines))
