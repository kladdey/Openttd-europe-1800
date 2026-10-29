"""Join actual engine placement results to the historical plan; no game edits."""
import csv,json,collections,math
from industrial_phase6b_runtime import ROOT,BASE
from industrial_phase6b_plan import write_csv


def records():
    plan={r['placement_id']:r for f in ['placement-plan.json','additions-plan-pass1.json'] for r in json.loads((BASE/f).read_text(encoding='utf8'))}
    observed={}
    for name in ['placement-result.json','additions-result.json','additions-retry-result.json']:
        data=json.loads((BASE/name).read_text(encoding='utf8'))
        for r in data['results']:
            if r['placement_id'] in observed and observed[r['placement_id']]['status']=='PLACED':raise AssertionError('Attempted to replace a completed placement')
            observed[r['placement_id']]={k:v for k,v in plan[r['placement_id']].items() if k!='candidate_tiles'}|r|dict(engine_case=data['case'])
    with (ROOT/'docs/research/existing_coastal_towns.csv').open(encoding='utf8') as f:towns=list(csv.DictReader(f))
    with (ROOT/'docs/research/added_port_towns.csv').open(encoding='utf8') as f:towns+=list(csv.DictReader(f))
    for row in observed.values():
        if row['placement_id']>=10000 and any(k in row['locality'].lower() for k in ['representation','proxy']):
            row['historical_basis']='REGIONAL REPRESENTATION; documented trade, inferred site'
            row['confidence']='Not a verified named 1830 business or quarry address'
        if row['local_id']==86:
            row['historical_basis']='UNVERIFIED MINERAL SITE; inherited glass-support allocation'
            row['confidence']='No source establishes local natural soda-ash mining in 1830'
            row['history_source_context']='Regional trade context only; not proof of this mineral operation'
        if row['status']=='PLACED':
            nearest=min(towns,key=lambda t:abs(int(t['x'])-row['x'])+abs(int(t['y'])-row['y']))
            row.update(nearest_actual_town=nearest['name'],nearest_actual_town_id=int(nearest['town_id']),nearest_actual_town_manhattan=abs(int(nearest['x'])-row['x'])+abs(int(nearest['y'])-row['y']))
    return sorted(observed.values(),key=lambda r:r['placement_id'])


def main():
    rows=records();placed=[r for r in rows if r['status']=='PLACED']
    assert len(placed)==467 and len({r['industry_id'] for r in placed})==467
    matrix=json.loads((ROOT/'docs/research/industrial_1830_candidate_matrix.json').read_text(encoding='utf8'))
    rules={r['local_id']:r for r in matrix['industries']}
    coverage=[];graph={}
    for c in matrix['cargo_slots']:
        label=c['cargo_label'];producers=[r for r in placed if label in [x[0] for x in rules[r['local_id']]['produced']]];consumers=[r for r in placed if label in rules[r['local_id']]['accepted']]
        nearest=[]
        for p in producers:
            candidates=[abs(p['x']-s['x'])+abs(p['y']-s['y']) for s in consumers if p['industry_id']!=s['industry_id']]
            if candidates:nearest.append(min(candidates))
        # An acceptance edge alone does not prove all mandatory co-inputs or an
        # actual delivery. Runtime delivery observations are separate evidence.
        coverage.append(dict(cargo_slot=c['slot'],cargo_label=label,producers=len(producers),accepting_industries=len(consumers),producer_regions=' '.join(sorted({r['region'] for r in producers})),consumer_regions=' '.join(sorted({r['region'] for r in consumers})),max_nearest_consumer_manhattan=max(nearest) if nearest else 'UNAVAILABLE',status='NO INDUSTRY SINK' if producers and not consumers else 'ACCEPTANCE EDGES PRESENT' if producers and consumers else 'NO PRODUCER' if consumers else 'NOT USED BY PLACED INDUSTRIES',evidence='ENGINE-CALCULATED from source recipes and VERIFIED IN GAME placement',caveat='Acceptance graph, not delivered revenue. ENSP/FMSP/MNSP can be optional boosts. SLAG remains an 1830 waste by-product.'))
        graph[label]=dict(producers=[p['industry_id'] for p in producers],consumers=[p['industry_id'] for p in consumers])
    distribution=[]
    for region in sorted({r['region'] for r in placed}):
        subset=[r for r in placed if r['region']==region]
        for localid in sorted({r['local_id'] for r in subset}):
            subset2=[r for r in subset if r['local_id']==localid]
            distribution.append(dict(region=region,local_id=localid,industry=rules[localid]['industry'],count=len(subset2)))
    # Keep the earlier 0.2.0 plan as a distinct research artifact, and expose
    # the complete candidate plan under the requested primary filename.
    base_plan=json.loads((BASE/'placement-plan.json').read_text(encoding='utf8'))
    extra_plan=json.loads((BASE/'additions-plan-pass1.json').read_text(encoding='utf8'))
    def plan_rows(seq):
        result=[]
        for original in seq:
            row={k:v for k,v in original.items() if k!='candidate_tiles'}|{'candidate_count':len(original['candidate_tiles'])}
            if row['placement_id']>=10000 and any(k in row['locality'].lower() for k in ['representation','proxy']):
                row['historical_basis']='REGIONAL REPRESENTATION; documented trade, inferred site'
                row['confidence']='Not a verified named 1830 business or quarry address'
            if row['local_id']==86:
                row['historical_basis']='UNVERIFIED MINERAL SITE; inherited glass-support allocation'
                row['confidence']='No source establishes local natural soda-ash mining in 1830'
                row['history_source_context']='Regional trade context only; not proof of this mineral operation'
            result.append(row)
        return result
    write_csv(ROOT/'docs/research/historical_industry_locations_0_2.csv',plan_rows(base_plan))
    write_csv(ROOT/'docs/research/historical_industry_locations.csv',plan_rows(base_plan+extra_plan))
    write_csv(ROOT/'docs/research/copper_salt_industry_locations.csv',plan_rows(extra_plan))
    write_csv(ROOT/'docs/research/industry_placement_results.csv',rows)
    write_csv(ROOT/'docs/research/regional_industry_distribution.csv',distribution)
    write_csv(ROOT/'docs/research/industry_chain_coverage.csv',coverage)
    (ROOT/'docs/research/industry_chain_graph.json').write_text(json.dumps(dict(cargos=graph,industries={str(r['industry_id']):dict(local_id=r['local_id'],x=r['x'],y=r['y'],region=r['region'],accepted=rules[r['local_id']]['accepted'],produced=rules[r['local_id']]['produced']) for r in placed}),indent=2),encoding='utf8')
    routes=[]
    for name in ['british_coal','ruhr_coal','grain','timber','iron','salt','coastal_fish','passengers','mail']:
        path=BASE/('route-'+name+'.json')
        if path.exists():routes.append(json.loads(path.read_text(encoding='utf8')))
    if routes:(ROOT/'docs/research/industrial_route_validation.json').write_text(json.dumps(dict(tests=routes,interpretation='Actual loaded, paid deliveries in disposable Europe copies. Construction grants isolate functionality, not campaign profitability.'),indent=2),encoding='utf8')
    print('Industry count',len(placed),'distinct types',len({r['local_id'] for r in placed}),'regions',dict(collections.Counter(r['region'] for r in placed)))
    for label in ['CORE','COPR','SALT','FOOD','SLAG','GOOD']:
        print(next(r for r in coverage if r['cargo_label']==label))


if __name__=='__main__':main()
