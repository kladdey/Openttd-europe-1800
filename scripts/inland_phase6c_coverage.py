"""Before/after acceptance distances using actual market locations, not quotas."""
import collections,csv,json
import numpy as np
from inland_phase6c_runtime import ROOT,BASE
from industrial_phase6b_plan import write_csv


def main():
    graph=json.loads((ROOT/'docs/research/industry_chain_graph.json').read_text());old=graph['industries']
    state=json.loads((BASE/'placement.json').read_text());markets=[r for r in state['results'] if r['status']=='PLACED']
    towns={t['town_id']:t for t in json.loads((BASE/'towns.json').read_text(encoding='utf8'))}
    coastal={}
    with (ROOT/'docs/research/existing_coastal_towns.csv').open(encoding='utf8') as f:
        for t in csv.DictReader(f):coastal[int(t['town_id'])]=t['classification'].startswith('Coastal')
    details=[];summary=[];regions=[]
    for label in ['FOOD','GOOD']:
        before=[dict(industry_id=i,**old[str(i)],coastal=True) for i in graph['cargos'][label]['consumers']]
        added=[]
        for r in markets:
            if label not in r['accepted_labels'].split(','):continue
            nearest=min(old.values(),key=lambda p:abs(p['x']-r['x'])+abs(p['y']-r['y']))
            added.append(r|dict(region=nearest['region'],coastal=coastal.get(r['town_id'],False)))
        after=before+added
        for i in graph['cargos'][label]['producers']:
            p=old[str(i)];a=min(before,key=lambda q:abs(p['x']-q['x'])+abs(p['y']-q['y']));b=min(after,key=lambda q:abs(p['x']-q['x'])+abs(p['y']-q['y']))
            details.append(dict(cargo_label=label,producer_id=i,producer_local_id=p['local_id'],region=p['region'],x=p['x'],y=p['y'],before_consumer_id=a['industry_id'],before_distance=abs(p['x']-a['x'])+abs(p['y']-a['y']),after_consumer_id=b['industry_id'],after_distance=abs(p['x']-b['x'])+abs(p['y']-b['y']),after_consumer_coastal=b['coastal'],after_consumer_town=towns[b['town_id']]['name'] if 'town_id' in b else 'existing export industry',evidence='ENGINE-CALCULATED Manhattan diagnostic; industry placement and acceptance verified separately',route_access='NOT TESTED except recorded gameplay routes'))
        subset=[r for r in details if r['cargo_label']==label]
        for phase,consumers in [('before',before),('after',after)]:
            distances=[r[phase+'_distance'] for r in subset]
            summary.append(dict(cargo_label=label,phase=phase,producers=len(subset),consumers=len(consumers),median=float(np.percentile(distances,50)),p90=float(np.percentile(distances,90)),maximum=max(distances),over_160_tiles=sum(d>160 for d in distances),over_300_tiles=sum(d>300 for d in distances),inland_consumers=sum(not r['coastal'] for r in consumers),coastal_consumers=sum(r['coastal'] for r in consumers),distance_unit='Manhattan tiles, not route length or cost'))
            for region in sorted({r['region'] for r in old.values()}):regions.append(dict(cargo_label=label,phase=phase,region=region,consumers=sum(r['region']==region for r in consumers)))
    write_csv(ROOT/'docs/research/inland_market_coverage_summary.csv',summary)
    write_csv(ROOT/'docs/research/inland_producer_market_distances.csv',details)
    write_csv(ROOT/'docs/research/inland_market_regional_coverage.csv',regions)
    (BASE/'coverage.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
    for label in ['FOOD','GOOD']:print('Worst',label,[(r['producer_id'],r['region'],r['after_distance'],r['after_consumer_town']) for r in sorted([x for x in details if x['cargo_label']==label],key=lambda x:-x['after_distance'])[:5]])


if __name__=='__main__':main()
