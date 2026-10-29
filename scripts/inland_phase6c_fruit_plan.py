"""Add six regional fresh-produce markets using existing FOOD-market recipes.

Run after the 59-market base and ten-market extension have been constructed.
The named anchors address the six existing orchard regions, not a market quota.
This planning step is read-only with respect to the game installation.
"""
import collections,json,math
import numpy as np
from inland_phase6c_runtime import BASE,ROOT,SOURCE
from inland_phase6c_inventory import houses
from coastal_phase6_preservation import parts,maps
from industrial_phase6b_plan import write_csv


def main():
    towns=json.loads((BASE/'towns.json').read_text(encoding='utf8'))
    placed=json.loads((BASE/'placement.json').read_text())['results']
    assert len(placed)==69,'Run only after the ten-market extension'
    used={r['tile'] for r in placed};sites,_=houses();m=maps(parts(SOURCE))
    h=np.frombuffer(m['MAPH'],dtype='u1');types=np.frombuffer(m['MAPT'],dtype='u1')>>4
    owners=np.frombuffer(m['MAP2'],dtype='>u2');counts=collections.Counter(map(int,owners[types==3]))
    graph=json.loads((ROOT/'docs/research/industry_chain_graph.json').read_text())['industries']
    orchards=[dict(industry_id=int(k),**v) for k,v in graph.items() if v['local_id']==47]
    requests=[]
    for name in ['BORDEAUX','REIMS','VALENCIA','SEVILLA','FIRENZE','CALTAGIRONE']:
        town=next(t for t in towns if t['name']==name)
        loss=sum(r['population_loss'] for r in placed if r['town_id']==town['town_id'])
        budget=math.floor(town['population']*.05)
        choices=[r for r in sites if r['town_id']==town['town_id'] and r['tile'] not in used
                 and r['estimated_population_loss']+loss<=budget
                 and len({int(h[r['tile']+d]) for d in [0,1,4096,4097]})==1]
        choices=sorted(choices,key=lambda r:(r['estimated_population_loss'],abs(r['x']-town['x'])+abs(r['y']-town['y'])))[:100]
        assert choices,name
        orchard=min(orchards,key=lambda p:abs(p['x']-town['x'])+abs(p['y']-town['y']))
        requests.append(dict(request_id=69+len(requests),town_id=town['town_id'],town_name=name,
            town_x=town['x'],town_y=town['y'],population=town['population'],population_budget=budget,
            base_house_tiles=counts[town['town_id']],tier='regional fresh-produce market',local_id=59,
            coverage_gain=0,improved_cargo_nodes=1,sites=choices,
            historical_status='Representative regional market, not an identified shop address',
            historical_basis='Existing commercial town anchor; FRUT compatibility gap not served by General Stores',
            fruit_producer_id=orchard['industry_id'],fruit_producer_distance=abs(orchard['x']-town['x'])+abs(orchard['y']-town['y'])))
    result=dict(policy=dict(reason='General Stores reject FRUT; six existing orchard regions need regional fresh-produce destinations',max_cumulative_population_loss_fraction=.05),requests=requests)
    (BASE/'market-fruit-plan.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    write_csv(ROOT/'docs/research/inland_fruit_market_plan.csv',[{k:v for k,v in r.items() if k!='sites'}|dict(candidate_count=len(r['sites'])) for r in requests])
    print('Six regional Food Market requests prepared; no game files changed')


if __name__=='__main__':main()
