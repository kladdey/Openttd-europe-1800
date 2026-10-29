"""Test-only coalfield extensions; never claim these are exact historical shafts.

Find legal-looking sites near sourced Phase 6B coalfields and actual consumers.
The engine still decides every siting rule. No setting is changed to fit sites.
"""
import csv,json,datetime
import numpy as np
from lifecycle_phase7a_runtime import ROOT,BASE,SOURCE
from lifecycle_phase7a_schedule import historical,validate
from coastal_phase6_preservation import parts,maps

def plan():
    graph=json.loads((ROOT/'docs/research/industry_chain_graph.json').read_text())['industries']
    nodes=[dict(industry_id=int(k),**v) for k,v in graph.items()]
    with (ROOT/'docs/research/inland_town_population_changes.csv').open(encoding='utf8') as f:towns=list(csv.DictReader(f))
    towns=[dict(id=int(t['town_id']),name=t['town_name'],x=int(t['x']),y=int(t['y'])) for t in towns]
    def nearest(x,y,square=False):return min(towns,key=lambda t:((x-t['x'])**2+(y-t['y'])**2 if square else abs(x-t['x'])+abs(y-t['y']),t['id']))
    coal=[n for n in nodes if n['local_id']==0];occupied={nearest(n['x'],n['y'],q)['id'] for n in coal for q in [False,True]}
    tile=maps(parts(SOURCE));types=(np.frombuffer(tile['MAPT'],dtype='u1')>>4).reshape(4096,4096);height=np.frombuffer(tile['MAPH'],dtype='u1').reshape(4096,4096)
    schedule=historical();schedule.update(id='phase7a-europe-accelerated-coalfields-v1',test_mode=True)
    chosen=[]
    for idx,(e,region) in enumerate(zip(schedule['events'],['GB','DE','PL'])):
        options=[];seen=set()
        for field in [n for n in coal if n['region']==region]:
            for dx in range(-40,41,2):
                for dy in range(-40,41,2):
                    if abs(dx)+abs(dy)>40:continue
                    x,y=field['x']+dx,field['y']+dy
                    if (x,y) in seen:continue
                    seen.add((x,y))
                    if min(abs(x-n['x'])+abs(y-n['y']) for n in coal)<25:continue
                    if min(abs(x-n['x'])+abs(y-n['y']) for n in nodes)<19:continue
                    town=nearest(x,y);town2=nearest(x,y,True)
                    if town['id'] in occupied or town2['id'] in occupied:continue
                    if not(np.all(np.isin(types[y:y+5,x:x+5],[0,4])) and np.all(height[y:y+6,x:x+6]==height[y,x])):continue
                    customers=[n for n in nodes if n['local_id']==45]
                    consumer=min(customers,key=lambda n:abs(x-n['x'])+abs(y-n['y']))
                    d=abs(x-consumer['x'])+abs(y-consumer['y'])
                    options.append((d,abs(dx)+abs(dy),y,x,field['industry_id'],town,consumer['industry_id']))
        options.sort(key=lambda r:r[:4]);assert options,'No bounded coalfield site in '+region
        best=options[0];_,_,y,x,field,town,consumer=best
        same=[o for o in options if o[5]['id']==town['id'] and abs(o[3]-x)+abs(o[2]-y)<=12][:48]
        e.update(event_id='test_'+region.lower()+'_coalfield',name='TEST regional coalfield extension '+region,region=region,
            open_date=668394+31+idx*120,calendar_open=datetime.date.fromordinal(668394+31+idx*120-365).isoformat(),sites=[o[2]*4096+o[3] for o in same],
            test_life_days=420,test_warning_days=210,test_service_bonus_days=45,test_consumer=consumer,
            reference_coalfield_industry=field,test_nearby_town=town['name'],test_scope='Test-only regional capacity near existing sourced coalfield, not a named historical opening')
        chosen.append((e,options));occupied.add(town['id'])
    # A separate nearby-town extension after actual closure; not same old site.
    first,options=chosen[0];first_sites=set(first['sites']);replacement=dict(first)
    alternatives=[o for o in options if o[5]['name']!=first['test_nearby_town'] and o[5]['id'] not in occupied]
    assert alternatives,'No distinct replacement town'
    o=alternatives[0];replacement.update(event_id='test_replacement',name='TEST replacement coalfield',after_closed=first['event_id'],open_date=668394+500,
        calendar_open=datetime.date.fromordinal(668394+500-365).isoformat(),sites=[o[2]*4096+o[3]],test_nearby_town=o[5]['name'])
    schedule['events'].append(replacement);validate(schedule)
    (BASE/'europe-test-schedule.json').write_text(json.dumps(schedule,indent=2,ensure_ascii=False),encoding='utf8')
    return schedule

if __name__=='__main__':
    s=plan();print([(e['event_id'],e['sites'][0]%4096,e['sites'][0]//4096,e['test_nearby_town'],e['test_consumer']) for e in s['events']])
