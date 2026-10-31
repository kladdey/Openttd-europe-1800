"""Source-derived recipes, town-anchored bounded sites and explicit proxy dates."""
import csv,json
from lifecycle_phase7c_runtime import ROOT
from lifecycle_phase7a_schedule import absolute_date
def squirrel(v):
    if v is None:return 'null'
    if isinstance(v,bool):return 'true' if v else 'false'
    if isinstance(v,int):return str(v)
    if isinstance(v,str):return json.dumps(v,ensure_ascii=False)
    if isinstance(v,list):return '['+','.join(squirrel(x) for x in v)+']'
    if isinstance(v,dict):return '{'+','.join(k+'='+squirrel(x) for k,x in v.items())+'}'
    raise TypeError(type(v))
DATA=ROOT/'docs/research';FOLDER=ROOT/'gamescripts/historical_industry_lifecycle'
def sites(x,y,radius=32):
    return [(y+dy)*4096+x+dx for radius_ in range(0,radius+1,2) for dx in range(-radius_,radius_+1,2) for dy in range(-radius_,radius_+1,2) if abs(dx)+abs(dy)==radius_]
def production():
    matrix={r['local_id']:r for r in json.loads((DATA/'industrial_1830_candidate_matrix.json').read_text())['industries']}
    # Town coordinates come from the preserved 617-town inventory, never lat/lon.
    # Broad regional proxies are deliberately NOT claims of exact factory dates.
    specs=[
      ('galicia_mill',34,1835,1860,618,1538,'Galicia: Wieliczka','Regional grain-milling expansion',[],['GRAI'],['FOOD'],'https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-e4b3fd16-d0b9-435d-9ca9-62a628336f0a/c/Michalowski_Infrastruktura_PB_6_2024.pdf'),
      ('ruhr_sheet',103,1865,1880,0,0,'Ruhr','Sheet and pipe manufacturing expansion',[],[],['BDMT'],'https://www.thyssenkrupp.com/en/company/company-history/milestones'),
      ('ruhr_steel',2,1865,1880,0,0,'Ruhr','Bessemer-era steel district',['ruhr_sheet'],['IRON','COKE'],['STEL'],'https://www.thyssenkrupp.com/en/company/history/krupp-and-thyssen-history/krupp-corporate-history'),
      ('galicia_successor',34,1887,1894,580,1541,'Galicia: Bochnia','Nearby grain-mill modernization successor',[],['GRAI'],['FOOD'],'https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-e4b3fd16-d0b9-435d-9ca9-62a628336f0a/c/Michalowski_Infrastruktura_PB_6_2024.pdf'),
      ('ruhr_workshop',9,1910,1930,0,0,'Ruhr','Integrated metal manufacturing',['ruhr_steel'],['STEL'],['MPAR'],'https://www.thyssenkrupp.com/en/company/history/krupp-and-thyssen-history/thyssen-corporate-history'),
      ('ruhr_slag',80,1955,1980,0,0,'Ruhr','Postwar slag utilization',['ruhr_steel'],['SLAG'],['CMNT'],'https://www.heidelbergmaterials.com/en/company/heritage/publications/150-years-of-heidelberg-materials'),
      ('rhine_depot',24,1985,2000,0,0,'Lower Rhine','Municipal recycling collection',[],[],[],'https://www.europarl.europa.eu/workingpapers/envi/pdf/100_en.pdf'),
      ('rhine_junk',25,1985,2000,0,0,'Lower Rhine','Scrap recovery',['rhine_depot'],['RCYC'],[],'https://www.europarl.europa.eu/workingpapers/envi/pdf/100_en.pdf'),
      ('rhine_recycling',23,1985,2000,0,0,'Lower Rhine','Plastics recovery',['rhine_junk'],['RCYC'],[],'https://www.europarl.europa.eu/workingpapers/envi/pdf/100_en.pdf'),
      ('rhine_plastics',18,1985,2000,0,0,'Lower Rhine','Recovered-polymer manufacturing',['rhine_recycling'],['PLAS'],['MNSP'],'https://www.europarl.europa.eu/workingpapers/envi/pdf/100_en.pdf')]
    graph=json.loads((DATA/'industry_chain_graph.json').read_text())['industries']
    anchor=next(n for n in graph.values() if n['region']=='DE' and n['local_id']==7)
    events=[]
    for index,(key,local,year,last,x,y,region,name,deps,producers,consumers,url) in enumerate(specs):
        r=matrix[local]
        if not x:x,y=anchor['x']+16+(index%3)*18,anchor['y']+16+(index//3)*18
        # Town-dependent collection/scrap tiles must abut existing houses.
        # Anchor to the actual DUSSELDORF centre, not an arbitrary empty grid.
        if key in ['rhine_depot','rhine_junk']:x,y=2008,1323
        if key=='rhine_recycling':x,y=2030,1323
        if key=='rhine_plastics':x,y=2020,1350
        layouts=[p for layout in r['layouts'] for p in layout['layout']];w=max(p[0] for p in layouts)+1;h=max(p[1] for p in layouts)+1
        assert year>=r['earliest_year'],(key,r['earliest_year'])
        events.append(dict(event_id=key,local_id=local,name=name,industry=r['industry'],region=region,
            open_date=absolute_date(f'{year}-01-01'),announce_date=absolute_date(f'{max(1830,year-5)}-01-01'),latest_date=absolute_date(f'{last}-12-31'),
            dependencies=deps,required_producers=producers,required_consumers=consumers,sites=sites(x,y),anchor_x=x,anchor_y=y,
            width=w,height=h,max_attempts=96,max_batches=6,inputs=r['accepted'],outputs=r['produced'],
            earliest_native_year=r['earliest_year'],recipe_rule=r.get('historical_rule'),source=url,
            date_basis='REGIONAL GAME PROXY; not exact establishment or shutdown date',confidence='MEDIUM regional trend; LOW exact siting/date',
            native_location_checks=r['industry_location_checks'],native_tile_checks=r['tile_location_checks']))
    s=dict(site_id='krakow_old_mill',industry_id=275,local_id=34,engine_type=30,tile=6173294,born=668394,
        original_record_sha256='98bb982e686fd5938aad12e19c95b5a4b0e5977931227a89c4daa6b37a006486',
        warning_date=absolute_date('1885-01-01'),close_date=absolute_date('1895-01-01'),latest_close=absolute_date('1905-12-31'),warning_years=10,
        successor='galicia_successor',radius=96,token=int('98bb982',16),extension='DISABLED: pickup is not verified final payment',
        basis='Reviewed gameplay modernization proxy, not an identified historical mill closure')
    return validate(dict(id='phase7c-regional-vertical-slice-v1',schema=3,migration='reject',test_mode=False,events=events,retirement=s))
def validate(p):
    assert __debug__ and p['schema']==3 and p['migration'] in ['reject','adopt_only']
    keys=[e['event_id'] for e in p['events']];assert len(keys)==len(set(keys))
    for e in p['events']:
        assert e['announce_date']<=e['open_date']<=e['latest_date'] and len(e['sites'])==len(set(e['sites'])) and e['sites']
        assert e['local_id'] in [34,103,2,9,80,24,25,23,18] and all(type(t) is int and 0<t<4096*4096 for t in e['sites'])
        assert all(d in keys[:keys.index(e['event_id'])] for d in e['dependencies'])
        assert 0<e['max_attempts']<=128 and 0<e['max_batches']<=12 and 0<e['width']<=16 and 0<e['height']<=16
        if not p['test_mode']:assert e['open_date']>=absolute_date(f"{max(1,e['earliest_native_year']):04d}-01-01")
    s=p['retirement']
    if s:
        assert s['successor'] in keys and 5<=s['warning_years']<=10 and s['warning_date']<s['close_date']<=s['latest_close'] and 0<s['radius']<=96
        assert (s['industry_id'],s['tile'],s['born'],s['local_id'],s['engine_type'])==(275,6173294,668394,34,30)
    return p
def compile_policy(p,path):
    validate(p);contract=json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    path.write_text('/* Explicit v3 policy. Test fixtures never replace production policy. */\nEXPANSION_CONTRACT_TEXT <- '+squirrel(contract)+';\nEXPANSION <- '+squirrel(p)+';\n',encoding='utf-8-sig')
def setup(home,p=None,legacy=None,schedule=None):
    from lifecycle_phase7b_policy import production as bp,compile_policy as bc
    from lifecycle_phase7a_schedule import historical,compile_schedule
    compile_policy(p or production(),home/'game/lifecycle/expansion_policy.nut');bc(legacy or bp(),home/'game/lifecycle/legacy_policy.nut');compile_schedule(schedule or historical(),home/'game/lifecycle/schedule.nut')
if __name__=='__main__':
    p=production();(FOLDER/'expansion_policy.json').write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf8');compile_policy(p,FOLDER/'expansion_policy.nut')
    from industrial_phase6b_plan import write_csv
    write_csv(DATA/'phase7c_regional_chain_matrix.csv',[{k:v for k,v in e.items() if k!='sites'} for e in p['events']])
    print('events',len(p['events']), 'anchors',[(e['event_id'],e['anchor_x'],e['anchor_y']) for e in p['events']])
