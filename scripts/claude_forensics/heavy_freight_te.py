"""Top tractive-effort locomotives introduced <=1945 per set (1945 snapshot), with the
maximum total train mass a TE can lift on a sustained 3% grade: TE / (300 slope + 10 axle + 15 rolling N/t).
Usage: python3 -I scripts/claude_forensics/heavy_freight_te.py <repo_root>
"""
import csv, os, sys
root = sys.argv[1] if len(sys.argv) > 1 else '.'
D = os.path.join(root, 'docs', 'research', 'claude_forensics')
rows = [r for r in csv.DictReader(open(os.path.join(D, 'running_cost_factor_inference.csv'))) if r['snapshot_year'] == '1945']
out = ['set | engine | intro | hp | kN | t | speed | buy | run/yr | run per kN | max train t on sustained 3%']
for s in ['UKRS2', 'NARS 2.52', 'NARS Add-On 2cc']:
    sel = {}
    for r in rows:
        if r['set'] == s and int(r['intro']) <= 1945 and float(r['te_kn'] or 0) > 0: sel[(r['name'], r['te_kn'])] = r
    for r in sorted(sel.values(), key=lambda r: -float(r['te_kn']))[:6]:
        te = float(r['te_kn']); rc = int(r['running_gbp'])
        out.append(f"{s} | {r['name'][:30]} | {r['intro']} | {r['power_hp']} | {te:.0f} | {r['weight_t']} | {r['speed']} | {int(r['purchase_gbp']):,} | {rc:,} | {rc/te:.1f} | {te*1000/325:,.0f}")
open(os.path.join(D, 'heavy_freight_te.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
