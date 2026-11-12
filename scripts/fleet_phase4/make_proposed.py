"""fleet_phase4_proposed_values.csv: the recommended Variant C, one row per changed engine (catalogue RUNTIME)."""
import csv
import p4lib as P
import variants as V
rows = [r for r in csv.DictReader(open(P.OUT / 'fleet_phase4_proposed_values_all_variants.csv')) if r['variant'] == 'C_cross']
early = {P.A and None}
out = []
for r in rows:
    nars = r['set'] == 'NARS'
    lid = int(r['local_id'])
    if nars and lid in V.EARLY_US:
        mech = f'running-cost class 42->44 (prop 0x0E) + NARS-local class-44 exponent +{V.EARLY_US_EXP}'
    elif nars:
        mech = 'NARS-local class-42 exponent +4 -> +3 (prop 0x08 via engine-allocation override 0x11)'
    else:
        mech = 'running-cost factor (prop 0x0D) on the Add-On engine'
    out.append(dict(r, mechanism=mech, purchase_change='none', status='EXPERIMENTAL - NOT APPROVED, NOT DEPLOYED'))
with open(P.OUT.parents[1] / 'fleet_phase4_proposed_values.csv', 'w', newline='', encoding='utf8') as fh:
    w = csv.DictWriter(fh, list(out[0])); w.writeheader(); w.writerows(out)
print(len(out), 'rows')
