"""Compile validated JSON rules to native Squirrel; no runtime JSON API assumed."""
import argparse,csv,datetime,json
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE
from coastal_phase6_proposals import project

def squirrel(value):
    if isinstance(value,bool):return 'true' if value else 'false'
    if isinstance(value,(int,float)):return str(value)
    if isinstance(value,str):return json.dumps(value,ensure_ascii=False)
    if isinstance(value,list):return '['+','.join(squirrel(v) for v in value)+']'
    if isinstance(value,dict):return '{'+','.join(k+'='+squirrel(v) for k,v in value.items())+'}'
    raise TypeError(type(value))

def absolute_date(text):return datetime.date.fromisoformat(text).toordinal()+365

def validate(schedule):
    assert __debug__,'Do not validate schedules with Python -O'
    assert schedule['schema']==1 and type(schedule['seed']) is int
    assert schedule['id'] and type(schedule['test_mode']) is bool and schedule['events']
    ids=[e['event_id'] for e in schedule['events']];assert len(ids)==len(set(ids))
    for e in schedule['events']:
        assert e['event_id'] and isinstance(e['event_id'],str)
        assert e['local_id']==0,'Only the verified managed-coal adapter is enabled'
        assert e['sites'] and len(e['sites'])<=64 and len(e['sites'])==len(set(e['sites']))
        assert all(type(tile) is int and tile>=0 for tile in e['sites'])
        assert 1<=e['max_attempts']<=64 and e['life_years']>=30 and 0<=e['life_jitter_years']<=50
        assert 5<=e['warning_years']<=10
        assert absolute_date(e['calendar_open'])==e['open_date']
        if 'after_closed' in e:assert e['after_closed'] in ids and e['after_closed']!=e['event_id']
        if schedule['test_mode']:
            assert 0<e['test_warning_days']<e['test_life_days'] and e['test_service_bonus_days']>=0
    by_id={e['event_id']:e for e in schedule['events']}
    for event_id in ids:
        seen=set();current=event_id
        while current is not None:
            assert current not in seen,'Cyclic replacement dependency'
            seen.add(current);current=by_id[current].get('after_closed')
    return schedule

def historical():
    # Coordinates describe mining districts; final map sites require the same
    # calibrated town residuals and terrain/GRF checks as the Phase 6B geography.
    specs=[('gb_south_hetton_1833','South Hetton regional colliery','GB','1833-08-05',54.8011,-1.4042,'https://www.dmm.org.uk/colliery/s007.htm'),
      ('de_zollverein_1851','Zollverein regional colliery','DE','1851-01-01',51.486,7.045,'https://www.zollverein.de/zollverein-unesco-world-heritage-site/history/'),
      ('pl_guido_1860','Guido regional colliery','PL','1860-01-01',50.2896,18.7913,'https://zabytek.pl/pl/obiekty/zabrze-zespol-zabudowan-i-wyrobisk-chodnikowych-dawnej-kopalni-g')]
    with (ROOT/'docs/research/existing_coastal_towns.csv').open(encoding='utf8') as f:towns=list(csv.DictReader(f))
    import numpy as np
    events=[]
    for event_id,name,region,date,lat,lon,url in specs:
        raw=project(lat,lon);anchors=[]
        for t in towns:
            try:p=project(float(t['latitude']),float(t['longitude']))
            except (ValueError,KeyError):continue
            distance=float(np.linalg.norm(p-raw))
            if distance<180:anchors.append((distance,t,np.array([int(t['x']),int(t['y'])])-p))
        anchors.sort(key=lambda r:r[0]);anchors=anchors[:4]
        if anchors:
            weights=np.array([1/max(d,1)**2 for d,_,_ in anchors]);raw+=np.clip(sum(w*r for w,(_,_,r) in zip(weights,anchors))/sum(weights),-8,8)
        x,y=[int(round(c)) for c in raw]
        offsets=sorted([(abs(dx)+abs(dy),dy,dx) for dx in range(-16,17) for dy in range(-16,17) if abs(dx)+abs(dy)<=16])[:64]
        events.append(dict(event_id=event_id,name=name,region=region,calendar_open=date,open_date=absolute_date(date),local_id=0,
            latitude=lat,longitude=lon,anchor_x=x,anchor_y=y,calibration_anchors=[t['name'] for _,t,_ in anchors],sites=[(y+dy)*4096+x+dx for _,dy,dx in offsets],
            life_years=110,life_jitter_years=30,warning_years=10,max_attempts=48,source=url,
            date_precision='Exact day' if region=='GB' else 'Opening year; 1 January is a scheduling convention',
            historical_status='Source-backed opening district; generic game mine, not an exact shaft reconstruction. Lifetime model is proposed, not a claimed historical closure date.'))
    return validate(dict(id='europe-phase7a-foundation-v1',schema=1,seed=7341830,test_mode=False,events=events))

def fixture(start=668394):
    schedule=historical();schedule.update(id='phase7a-accelerated-fixture-v1',test_mode=True)
    # Test-only dates do not alter the production schedule or GRF introductions.
    coords=[(150,40),(150,150),(210,210)]
    for i,(e,(x,y)) in enumerate(zip(schedule['events'],coords)):
        date=start+31+i*400;e.update(open_date=date,calendar_open=(datetime.date.fromordinal(date-365)).isoformat(),sites=[(y+dy)*256+x+dx for _,dy,dx in sorted((abs(dx)+abs(dy),dy,dx) for dx in range(-8,9) for dy in range(-8,9) if abs(dx)+abs(dy)<=8)[:48]],test_life_days=800,test_warning_days=360,test_service_bonus_days=90)
    replacement=dict(schedule['events'][0]);replacement.update(event_id='test_replacement',name='Test replacement coal working',region='TEST',open_date=start+500,calendar_open=datetime.date.fromordinal(start+500-365).isoformat(),sites=[210*256+40],after_closed=schedule['events'][0]['event_id'])
    schedule['events'].append(replacement);return validate(schedule)

def compile_schedule(schedule,destination):
    validate(schedule);Path(destination).write_text('/* Generated from validated schedule; do not hand-edit dates. */\nSCHEDULE <- '+squirrel(schedule)+';\n',encoding='utf-8-sig')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--fixture',action='store_true');a=ap.parse_args();s=fixture() if a.fixture else historical()
    target=ROOT/'gamescripts/historical_industry_lifecycle/schedule.nut';compile_schedule(s,target)
    if not a.fixture:
        (ROOT/'gamescripts/historical_industry_lifecycle/schedule.json').write_text(json.dumps(s,indent=2))
        from industrial_phase6b_plan import write_csv
        write_csv(ROOT/'docs/research/phase7a_event_schedule.csv',[{k:v for k,v in e.items() if k!='sites'}|dict(candidate_tiles=';'.join(map(str,e['sites']))) for e in s['events']])
    print(target)
