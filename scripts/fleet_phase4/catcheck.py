"""Catalogue integrity per variant (RUNTIME): which engines change, and which fields."""
import csv, json
import p4lib as P
import variants as V
ROSTER = {int(r['runtime_engine_id']): r for r in csv.DictReader(open(P.OUT.parents[0] / 'vehicle_roster.csv', encoding='utf-8-sig'))}
SET = {'44440302': 'NARS', '4E4D0518': 'Add-On', '44441000': 'UKRS2', '53410808': 'GETS', '4D560103': 'PTS', '4D560105': 'PRSP'}
FIELDS = ['price', 'running', 'power', 'te', 'weight', 'speed', 'wagon', 'design', 'capacity']


def full(tag):
    out = {}
    for f in P.A.lines(tag):
        if f[0] == 'ENGINE' and f[1] == 'start' and len(f) > 12:
            out[int(f[2])] = dict(name=f[3], **dict(zip(FIELDS, f[4:13])))
    return out


res, rows = {}, []
for v in V.VARIANTS:
    for year in (1850, 1925, 2000):
        b, t = full(f'cat-original-{year}'), full(f'cat-{v}-{year}')
        changed = {i for i in b if b[i]['running'] != t[i]['running']}
        other = {i: [k for k in FIELDS if k != 'running' and b[i][k] != t[i][k]] for i in b}
        other = {i: k for i, k in other.items() if k}
        expected = V.changed_engines(v)
        res[f'{v}-{year}'] = dict(engines=len(b), running_changed=len(changed), unexpected_running_changes=sorted(changed - expected),
                                  expected_but_unchanged=sorted(expected - changed), other_field_changes=other,
                                  by_set={s: sum(1 for i in changed if SET.get(ROSTER.get(i, {}).get('source_grfid')) == s) for s in SET.values()})
        if year == 1850:
            for i in sorted(changed):
                rows.append(dict(variant=v, engine=i, set=SET.get(ROSTER[i]['source_grfid']), local_id=ROSTER[i]['local_vehicle_id'], name=b[i]['name'],
                                 introduction=ROSTER[i]['introduction_year'], running_original=int(b[i]['running']), running_variant=int(t[i]['running']),
                                 ratio_DERIVED=round(int(t[i]['running']) / int(b[i]['running']), 4), purchase=int(b[i]['price'])))
(P.OUT / 'catalogue_integrity.json').write_text(json.dumps(res, indent=2))
with open(P.OUT / 'fleet_phase4_proposed_values_all_variants.csv', 'w', newline='', encoding='utf8') as fh:
    w = csv.DictWriter(fh, list(rows[0]))
    w.writeheader(); w.writerows(rows)
for k, r in res.items():
    print(k, {x: r[x] for x in ('engines', 'running_changed', 'unexpected_running_changes', 'expected_but_unchanged', 'by_set')}, 'other fields changed:', len(r['other_field_changes']))
