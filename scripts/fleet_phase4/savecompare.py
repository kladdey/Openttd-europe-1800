"""Compare original / balanced / rollback loads of the cloned campaign save (RUNTIME)."""
import csv, json, sys
from collections import defaultdict
import p4lib as P

ROSTER = {int(r['runtime_engine_id']): r for r in csv.DictReader(open(P.OUT.parents[0] / 'vehicle_roster.csv', encoding='utf-8-sig'))}


def obs(tag):
    veh, eng = defaultdict(dict), defaultdict(dict)
    for f in P.A.lines(tag):
        if f[0] == 'VEH':
            m = int(f[1]); veh[m][int(f[2])] = dict(owner=f[3], unit=f[4], engine=int(f[5]), wagons=int(f[6]), length=int(f[7]), cost=int(f[8]), age=int(f[9]), state=f[10], speed=int(f[11]))
        if f[0] == 'OENGINE':
            eng[int(f[1])][int(f[2])] = dict(name=f[3], price=int(f[4]), running=int(f[5]))
    return veh, eng


def compare(variant):
    o, oe = obs(f'save-{variant}-original')
    b, be = obs(f'save-{variant}-balanced')
    r, re_ = obs(f'save-{variant}-rollback')
    ident = lambda v: {k: (x['owner'], x['unit'], x['engine'], x['wagons'], x['length']) for k, x in v.items()}
    last = max(b)
    res = dict(trains=len(o[0]),
               identity_original_vs_balanced=ident(o[0]) == ident(b[0]),
               identity_balanced_end_vs_rollback=ident(b[last]) == ident(r[0]),
               engines_in_use=len(oe[0]))
    changed = []
    for e, x in oe[0].items():
        y = be[0].get(e); z = re_[0].get(e)
        g = ROSTER.get(e, {}).get('source_grfid')
        changed.append(dict(engine=e, name=x['name'], set=g, price_o=x['price'], price_b=y['price'] if y else None, run_o=x['running'],
                            run_b=y['running'] if y else None, run_rollback=z['running'] if z else None))
    res['engines_cost_changed'] = [c for c in changed if c['run_o'] != c['run_b']]
    res['engines_price_changed'] = [c for c in changed if c['price_o'] != c['price_b']]
    res['rollback_restores_all_costs'] = all(c['run_rollback'] in (None, c['run_o']) for c in changed)
    # per-train cost comparison in the same state class at load (month 0)
    same = [(k, o[0][k], b[0][k]) for k in o[0] if k in b[0] and o[0][k]['state'] == b[0][k]['state'] and (o[0][k]['speed'] > 0) == (b[0][k]['speed'] > 0)]
    res['trains_same_state_at_load'] = len(same)
    res['train_cost_changed_only_for_changed_engines'] = all((x['cost'] == y['cost']) == (x['engine'] not in {c['engine'] for c in res['engines_cost_changed']}) for _, x, y in same)
    res['example_trains'] = [dict(vehicle=k, engine=x['engine'], name=oe[0][x['engine']]['name'], cost_original=x['cost'], cost_balanced=y['cost'], state=x['state'])
                             for k, x, y in same if x['cost'] != y['cost']][:10]
    return res


if __name__ == '__main__':
    v = sys.argv[1]
    res = compare(v)
    (P.OUT / f'savecompare_{v}.json').write_text(json.dumps(res, indent=2))
    print(json.dumps({k: res[k] for k in res if k not in ('example_trains', 'engines_cost_changed')}, indent=1))
    for c in res['engines_cost_changed']: print(c)
