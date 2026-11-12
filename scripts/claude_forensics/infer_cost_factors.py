"""Infer running-cost base class and integer cost factor for every powered engine.

Independent re-derivation (Claude reinvestigation). Uses only committed runtime
observations (docs/research/vehicle_economy_normalized.csv) plus the JGRPP 0.73.4
formula, verified from source:

  _price[class]  = start_price * 6 >> 3            (low running-cost difficulty, no inflation)
  catalogue cost = _price[class] * factor << (local_exponent - 8)    (Engine::GetRunningCost)

start_price: steam 5600, diesel 5200, electric 4800 (src/table/pricebase.h).
Local exponents come from JGRPP's own debug lines in docs/research/vehicle_runtime_mapping.log.
A (class, factor) is accepted only if floor(price*factor*2^e/256) reproduces the
observed cost exactly for an integer factor 1..255 (Action 0 prop 0x0D is a byte;
callback 0x36 results are 15-bit but the property is a byte in the NFO spec).
Usage: python3 -I scripts/claude_forensics/infer_cost_factors.py <repo_root>
"""
import csv, sys, os, re, collections

root = sys.argv[1] if len(sys.argv) > 1 else '.'
R = os.path.join(root, 'docs', 'research')
START = {'steam': 5600, 'diesel': 5200, 'electric': 4800}
PRICE = {k: v * 6 >> 3 for k, v in START.items()}
IDX = {'15': 'train_purchase', '16': 'wagon_purchase', '42': 'steam', '43': 'diesel', '44': 'electric'}

# --- parse exponents from the engine's own debug output
FILE2GRF = {'newnars.grf': '44440302', 'proj1000.grf': '44441000', 'nars_add_on_set.grf': '4E4D0518',
            'gets0.7.grf': '53410808', 'polishtrainset3.0.3.grf': '4D560103',
            'polish-rolling-stock-pack-0.19.11.grf': '4D560105'}
exp = collections.defaultdict(dict)
pat = re.compile(r"'([^']+)' sets local price base multiplier (\d+) to (-?\d+)")
for line in open(os.path.join(R, 'vehicle_runtime_mapping.log'), encoding='utf-8', errors='replace'):
    m = pat.search(line)
    if not m: continue
    fn = m.group(1).replace('\\', '/').split('/')[-1]
    if fn in FILE2GRF and m.group(2) in IDX:
        exp[FILE2GRF[fn]][IDX[m.group(2)]] = int(m.group(3))

def cost(cls, f, e):
    v = PRICE[cls] * f
    s = e - 8
    return v << s if s >= 0 else v >> -s

def infer(grf, rc, label):
    hits = []
    for cls in ('steam', 'diesel', 'electric'):
        e = exp[grf].get(cls, 0)  # unset -> neutral 0 (newgrf.cpp FinalisePriceBaseMultipliers)
        for f in range(1, 256):
            if cost(cls, f, e) == rc:
                hits.append((cls, f, e))
    pref = [h for h in hits if h[0] == label]
    return hits, (pref[0] if pref else (hits[0] if hits else None))

rows = list(csv.DictReader(open(os.path.join(R, 'vehicle_economy_normalized.csv'), encoding='utf-8-sig')))
out = []
for r in rows:
    if r['kind'] != 'powered' or r['source_grfid'] not in FILE2GRF.values():
        continue
    rc = int(r['display_running_gbp_year'])
    if rc <= 0: continue
    hits, best = infer(r['source_grfid'], rc, r['traction'].lower())
    out.append(dict(snapshot_year=r['snapshot_year'], grfid=r['source_grfid'], set=r['set_name'],
                    local_id=r['local_vehicle_id'], name=r['vehicle_name'], intro=r['introduction_year'],
                    traction_label=r['traction'], running_gbp=rc,
                    power_hp=r['power_hp'], te_kn=r['tractive_effort_kn'], weight_t=r['weight_t'],
                    speed=r['speed_kmish_h'], purchase_gbp=r['purchase_gbp'],
                    matched_classes='|'.join(sorted({h[0] for h in hits})),
                    best_class=best[0] if best else '', factor=best[1] if best else '',
                    exponent=best[2] if best else ''))

od = os.path.join(R, 'claude_forensics'); os.makedirs(od, exist_ok=True)
with open(os.path.join(od, 'running_cost_factor_inference.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)

print('Exponents parsed from JGRPP debug log:')
for g, d in exp.items(): print(' ', g, d)
# summary: for each set and traction label, which classes reproduce costs (1830 snapshot, all engines)
s = collections.defaultdict(collections.Counter)
for o in out:
    if o['snapshot_year'] != '1830': continue
    s[(o['set'], o['traction_label'])][o['matched_classes'] or 'NONE'] += 1
print('\n1830 snapshot: set / traction label -> base classes giving an exact integer factor')
for k in sorted(s): print(' ', k, dict(s[k]))
