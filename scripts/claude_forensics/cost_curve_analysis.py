"""Fit running-cost-factor curves per set and build size/era-matched locomotive pairs.

Input: docs/research/claude_forensics/running_cost_factor_inference.csv (from infer_cost_factors.py).
Uses the 1913 snapshot: before UKRS2's calendar surcharge begins (zero surcharge in
1830/1849/1879/1913 snapshots, verified), so base factors are compared like-for-like.
Usage: python3 -I scripts/claude_forensics/cost_curve_analysis.py <repo_root>
"""
import csv, sys, os, collections
root = sys.argv[1] if len(sys.argv) > 1 else '.'
D = os.path.join(root, 'docs', 'research', 'claude_forensics')
rows = [r for r in csv.DictReader(open(os.path.join(D, 'running_cost_factor_inference.csv')))]

def ols(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxx = sum((x-mx)**2 for x in xs); sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    b = sxy/sxx; a = my - b*mx
    ss = sum((y-a-b*x)**2 for x, y in zip(xs, ys)); st = sum((y-my)**2 for y in ys)
    return a, b, 1-ss/st, n

def uniq(sel):
    seen = {}; 
    for r in sel: seen.setdefault((r['name'], r['running_gbp'], r['power_hp']), r)
    return list(seen.values())

snap = [r for r in rows if r['snapshot_year'] == '1913']
out_lines = []
def p(s=''): print(s); out_lines.append(s)

p('## Fitted factor = a + b*hp, steam locomotives introduced <=1950, 1913 snapshot (base factors)')
p('set | n | a (fixed factor) | b (factor per 1000 hp) | R^2 | exponent | fixed GBP/yr | GBP/yr per hp')
fits = {}
for s in ['UKRS2', 'NARS 2.52', 'NARS Add-On 2cc', 'Polish Train Set', 'Polish Rolling Stock Pack']:
    sel = uniq([r for r in snap if r['set'] == s and r['traction_label'] == 'Steam' and r['best_class'] == 'steam'
                and int(r['intro']) <= 1950 and int(r['power_hp']) > 1])
    if len(sel) < 4: continue
    xs = [int(r['power_hp']) for r in sel]; ys = [int(r['factor']) for r in sel]
    a, b, r2, n = ols(xs, ys); e = int(sel[0]['exponent'])
    unit = 4200 * 2**e / 256
    fits[s] = (a, b, e)
    p(f'{s} | {n} | {a:.1f} | {b*1000:.1f} | {r2:.3f} | +{e} | {a*unit:,.0f} | {b*unit:.2f}')

p('\n## Predicted catalogue running cost (GBP/yr) from fitted curves, same hp, 1830-1913 base (no UKRS2 surcharge)')
p('hp | ' + ' | '.join(fits))
for hp in (63, 120, 200, 250, 450, 800, 1500, 2000, 3000, 5000):
    vals = []
    for s, (a, b, e) in fits.items():
        vals.append(f'{max(1,(a+b*hp))*4200*2**e/256:,.0f}')
    p(f'{hp} | ' + ' | '.join(vals))

# matched pairs: each NARS / add-on steam engine vs UKRS2 steam within +-35% hp and +-20 yrs intro
uk = uniq([r for r in snap if r['set'] == 'UKRS2' and r['traction_label'] == 'Steam' and int(r['intro']) <= 1950])
pairs = []
for s in ['NARS 2.52', 'NARS Add-On 2cc']:
    for r in uniq([r for r in snap if r['set'] == s and r['traction_label'] == 'Steam' and int(r['intro']) <= 1950]):
        hp = int(r['power_hp']); yr = int(r['intro'])
        cands = [u for u in uk if abs(int(u['intro'])-yr) <= 20 and 0.65 <= int(u['power_hp'])/hp <= 1.35]
        if not cands: continue
        u = min(cands, key=lambda u: abs(int(u['power_hp'])-hp)/hp + abs(int(u['intro'])-yr)/40)
        pairs.append(dict(set=s, engine=r['name'], intro=yr, hp=hp, te_kn=r['te_kn'], speed=r['speed'], weight_t=r['weight_t'],
                          buy=int(r['purchase_gbp']), run=int(r['running_gbp']), factor=r['factor'], exp=r['exponent'],
                          ukrs2=u['name'], uk_intro=u['intro'], uk_hp=u['power_hp'], uk_te_kn=u['te_kn'], uk_speed=u['speed'],
                          uk_weight_t=u['weight_t'], uk_buy=int(u['purchase_gbp']), uk_run=int(u['running_gbp']), uk_factor=u['factor'],
                          run_ratio=round(int(r['running_gbp'])/int(u['running_gbp']), 2),
                          run_per_hp_ratio=round((int(r['running_gbp'])/hp)/(int(u['running_gbp'])/int(u['power_hp'])), 2),
                          buy_ratio=round(int(r['purchase_gbp'])/int(u['purchase_gbp']), 2),
                          factor_ratio=round(int(r['factor'])/int(u['factor']), 2),
                          exponent_ratio=2**(int(r['exponent'])-int(u['exponent']))))
with open(os.path.join(D, 'steam_matched_pairs.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(pairs[0])); w.writeheader(); w.writerows(pairs)
p('\n## Size/era-matched steam pairs (UKRS2 counterpart within +-35% hp, +-20 yrs); 1913 base values')
p('set | engine | intro | hp | run | UKRS2 match | intro | hp | run | run ratio | /hp ratio | = factor ratio x exponent ratio | buy ratio')
for q in pairs:
    p(f"{q['set']} | {q['engine'][:28]} | {q['intro']} | {q['hp']} | {q['run']:,} | {q['ukrs2'][:22]} | {q['uk_intro']} | {q['uk_hp']} | {q['uk_run']:,} | {q['run_ratio']} | {q['run_per_hp_ratio']} | {q['factor_ratio']} x {q['exponent_ratio']} | {q['buy_ratio']}")
open(os.path.join(D, 'cost_curve_analysis.txt'), 'w').write('\n'.join(out_lines) + '\n')
