"""Coverage-driven regional retail network; no game writes."""
import argparse,collections,csv,json,math,unicodedata
import numpy as np
from inland_phase6c_runtime import ROOT,BASE,SOURCE
from inland_phase6c_inventory import houses
from coastal_phase6_preservation import parts,maps
from industrial_phase6b_plan import write_csv

MAJOR='GOTEBORG GOTHENBURG HELSINGBORG KOLN WARSZAWA PRAHA RIGA LONDON PARIS WIEN AMSTERDAM LISBOA MADRID ROMA DUBLIN BERLIN PALERMO VENEZIA MILANO BARCELONA COPENHAGEN BIRMINGHAM MANCHESTER LEEDS SHEFFIELD BRISTOL GLASGOW EDINBURGH LILLE LYON TOULOUSE STRASBOURG BRUSSELS LIEGE COLOGNE FRANKFURT LEIPZIG DRESDEN HAMBURG MUNICH KRAKOW WROCLAW POZNAN WARSAW LUBLIN LWOW PRAGUE BRNO GRAZ LINZ ZARAGOZA VALLADOLID SALAMANCA SEVILLE CORDOBA TORINO FIRENZE BOLOGNA NAPOLI BUDAPEST BUCHAREST BELGRADE SOFIA KIEV ODESSA RIGA VILNIUS TALLINN'.split()


def key(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.upper()) if c.isalnum())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--target-distance',type=int,default=160);ap.add_argument('--max-population-loss',type=float,default=.05);ap.add_argument('--extend',action='store_true');a=ap.parse_args()
    assert 0<a.max_population_loss<=.05
    towns=json.loads((BASE/'towns.json').read_text(encoding='utf8'));sites,_=houses();group=collections.defaultdict(list)
    m=maps(parts(SOURCE));heights=np.frombuffer(m['MAPH'],dtype='u1');types=np.frombuffer(m['MAPT'],dtype='u1')>>4
    for r in sites:
        t=r['tile'];corners=[heights[t+d] for d in [0,1,4096,4097]]
        if max(corners)!=min(corners):continue
        group[r['town_id']].append(r)
    house_towns=np.frombuffer(m['MAP2'],dtype='>u2')[types==3];counts=collections.Counter(map(int,house_towns))
    graph=json.loads((ROOT/'docs/research/industry_chain_graph.json').read_text());industries=graph['industries'];nodes=[]
    for label in ['FOOD','GOOD']:
        for id_ in graph['cargos'][label]['producers']:nodes.append(dict(label=label,industry_id=id_,**industries[str(id_)]))
    distance=[]
    for n in nodes:distance.append(min(abs(n['x']-industries[str(i)]['x'])+abs(n['y']-industries[str(i)]['y']) for i in graph['cargos'][n['label']]['consumers']))
    baseline=distance[:];fixed=[];offset=0
    if a.extend:
        prior=json.loads((BASE/'placement.json').read_text())
        old_requests={r['request_id']:r for r in json.loads((BASE/'market-plan.json').read_text(encoding='utf8'))['requests']}
        fixed_ids=set()
        for market in prior['results']:
            if market['status']!='PLACED':continue
            fixed_ids.add(market['town_id'])
            for i,n in enumerate(nodes):
                if n['label'] in market['accepted_labels'].split(','):distance[i]=min(distance[i],abs(n['x']-market['x'])+abs(n['y']-market['y']))
        fixed=[t for t in towns if t['town_id'] in fixed_ids];offset=max(old_requests)+1
    eligible=[]
    for t in towns:
        budget=math.floor(t['population']*a.max_population_loss)
        options=sorted([r for r in group[t['town_id']] if r['estimated_population_loss']<=budget],key=lambda r:(r['estimated_population_loss'],abs(r['x']-t['x'])+abs(r['y']-t['y'])))[:100]
        if t['population']<(300 if a.extend else 400) or counts[t['town_id']]<15 or not options:continue
        t=t|dict(sites=options,base_house_tiles=counts[t['town_id']],population_budget=budget,historical_major=any(name in key(t['name']) for name in MAJOR))
        eligible.append(t)
    selected=[];used={t['town_id'] for t in fixed}
    while True:
        best=None
        for t in eligible:
            if t['town_id'] in used:continue
            if any(abs(t['x']-s['x'])+abs(t['y']-s['y'])<110 for s in selected+fixed):continue
            nd=[abs(n['x']-t['x'])+abs(n['y']-t['y']) for n in nodes]
            improved=[i for i,d in enumerate(distance) if d>a.target_distance and nd[i]<d]
            if len(improved)<2 and not (len(improved)==1 and (t['population']>=900 or (t['historical_major'] and t['population']>=300)) and distance[improved[0]]>350):continue
            gain=sum(max(0,d-a.target_distance)-max(0,min(d,nd[i])-a.target_distance) for i,d in enumerate(distance))
            if gain<40:continue
            score=gain*(1.12 if t['historical_major'] else 1)*(1+min(t['population'],6000)/60000)
            if best is None or score>best[0]:best=(score,t,nd,gain,len(improved))
        if best is None:break
        score,t,nd,gain,improved=best;used.add(t['town_id']);selected.append(t|dict(coverage_gain=gain,improved_cargo_nodes=improved))
        distance=[min(x,y) for x,y in zip(distance,nd)]
    requests=[]
    for t in selected:
        # Major hubs have complementary FOOD/FRUT and GOOD/BDMT stores when
        # two ordinary houses can fit the aggregate five-percent budget.
        pair=t['historical_major'] and t['population']>=1200 and len(t['sites'])>=2 and sum(r['estimated_population_loss'] for r in t['sites'][:2])<=t['population_budget']
        ids=[59,57] if pair else [61]
        for localid in ids:
            requests.append(dict(request_id=offset+len(requests),town_id=t['town_id'],town_name=t['name'],town_x=t['x'],town_y=t['y'],population=t['population'],population_budget=t['population_budget'],base_house_tiles=t['base_house_tiles'],tier='major commercial hub' if pair else 'regional market town',local_id=localid,coverage_gain=t['coverage_gain'],improved_cargo_nodes=t['improved_cargo_nodes'],sites=t['sites'],historical_status='Representative town retail, not a documented individual shop address',historical_basis='Existing town anchor; major centres prioritized from user request and regional commerce context'))
    result=dict(policy=dict(target_manhattan_distance=a.target_distance,practical_definition='Diagnostic regional access threshold, not a constructed route or profitability limit',min_town_population=300 if a.extend else 400,min_house_tiles=15,min_hub_spacing=110,max_cumulative_population_loss_fraction=a.max_population_loss),requests=requests)
    (BASE/('market-extension-plan.json' if a.extend else 'market-plan.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    write_csv(ROOT/('docs/research/inland_market_extension_plan.csv' if a.extend else 'docs/research/inland_market_plan.csv'),[{k:v for k,v in r.items() if k!='sites'}|dict(candidate_count=len(r['sites'])) for r in requests])
    print('Selected hubs',len(selected),'markets',len(requests),'types',dict(collections.Counter(r['local_id'] for r in requests)))
    for label in ['FOOD','GOOD']:
        idx=[i for i,n in enumerate(nodes) if n['label']==label]
        print(label,'before',np.percentile([baseline[i] for i in idx],[50,90,100]),'planned',np.percentile([distance[i] for i in idx],[50,90,100]))


if __name__=='__main__':main()
