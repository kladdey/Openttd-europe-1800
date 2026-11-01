"""Modest regional rollout; inherited policies remain frozen in their own files."""
import copy,csv,json,re
from lifecycle_phase7d_runtime import ROOT,BASE
from lifecycle_phase7c_policy import production as cp,squirrel,absolute_date
from lifecycle_phase7a_schedule import historical,compile_schedule
from lifecycle_phase7b_policy import production as bp,compile_policy as bc
DATA=ROOT/'docs/research';DIR=ROOT/'gamescripts/historical_industry_lifecycle'
MATRIX=json.loads((DATA/'industrial_1830_candidate_matrix.json').read_text());RULES={r['local_id']:r for r in MATRIX['industries']}
def enrich(e):
 r=RULES[e['local_id']];points=sorted({(int(p[0]),int(p[1])) for layout in r['layouts'] for p in layout['layout']})
 e.update(footprint=[list(p) for p in points],width=max(p[0] for p in points)+1,height=max(p[1] for p in points)+1,
  houses_nearby=any(t['checks'].get('require_houses_nearby',False) for t in r['tile_location_checks']),
  minimum_population=r['industry_location_checks'].get('require_town_min_population') or 0)
 keystone=r['industry_location_checks'].get('near_at_least_one_of_these_keystone_industries')
 e.update(keystone_local_ids=[next(i['local_id'] for i in RULES.values() if i['industry']==name) for name in keystone[0]] if keystone else [],keystone_distance=keystone[1] if keystone else 0)
 e['action']='replacement' if e['event_id']=='galicia_successor' else 'opening'
 return e
def offsets(x,y,width=4096,radius=24,step=2):
 return [(y+dy)*width+x+dx for r in range(0,radius+1,step) for dx in range(-r,r+1,step) for dy in range(-r,r+1,step) if abs(dx)+abs(dy)==r]
def production():
 p=cp();p.update(id='phase7d-regional-rollout-v1',schema=4,migration='reject',test_mode=False)
 for e in p['events']:
  enrich(e)
  if e['local_id'] in [24,25]:e['sites']=offsets(e['anchor_x'],e['anchor_y'],step=1)
  if e['event_id'].startswith('rhine_'):
   # Dusseldorf's baseline population is only 358. Cologne is already 1015,
   # satisfying the unchanged native collection-depot threshold of 800.
   anchors=[('KOLN',1990,1371),('DUSSELDORF',2008,1323),('ELBERFELD',1971,1316)]
   e.update(anchor_x=1990,anchor_y=1371,regional_fallback_towns=[a[0] for a in anchors],
    sites=list(dict.fromkeys(tile for _,x,y in anchors for tile in offsets(x,y,step=1 if e['houses_nearby'] else 2))))
 # Reuse recorded regional geography/provenance, not new exact founding claims.
 with (DATA/'inland_town_population_changes.csv').open(encoding='utf8') as f:towns=list(csv.DictReader(f))
 with (DATA/'industry_placement_results.csv').open(encoding='utf8') as f:placements=list(csv.DictReader(f))
 specs=[
 ('gb_milling',34,1840,'MANCHESTER','Britain',[],['GRAI'],['FOOD']),
 ('fr_milling',34,1845,'LILLE','France/Benelux',[],['GRAI'],['FOOD']),
 ('iberian_food',56,1870,'BARCELONA','Iberia',[],['FISH'],['FOOD']),
 ('fr_oil_food',56,1860,'LILLE','France/Benelux',[],['EOIL'],['FOOD']),
 ('gb_sheet',103,1870,'SHEFFIELD','Britain',[],[],['BDMT']),
 ('gb_steel',2,1870,'SHEFFIELD','Britain',['gb_sheet'],['IRON','COKE'],['STEL']),
 ('silesia_sheet',103,1880,'KATOWICE','Silesia/Polish lands',[],[],['BDMT']),
 ('silesia_steel',2,1880,'KATOWICE','Silesia/Polish lands',['silesia_sheet'],['IRON','COKE'],['STEL']),
 ('italy_workshop',9,1900,'TORINO','Italy',[],['STEL'],['MPAR']),
 ('italy_machinery',38,1920,'TORINO','Italy',['italy_workshop'],['MPAR'],['GOOD']),
 ('scandi_machinery',38,1930,'GOTEBORG','Scandinavia',[],['MPAR'],['GOOD']),
 ('fr_postwar_food',56,1955,'LYON','France',[],['EOIL'],['FOOD']),
 ('silesia_depot',24,1990,'KATOWICE','Silesia/Polish lands',[],[],[]),
 ('silesia_junk',25,1990,'KATOWICE','Silesia/Polish lands',['silesia_depot'],['RCYC'],[]),
 ('silesia_recycling',23,1990,'KATOWICE','Silesia/Polish lands',['silesia_junk'],['RCYC'],[]),
 ('silesia_plastics',18,1990,'KATOWICE','Silesia/Polish lands',['silesia_recycling'],['PLAS'],['MNSP']),
 ('rhine_eaf',79,1995,'DUSSELDORF','Lower Rhine',['rhine_junk'],['SCMT'],['STEL']),
 ('silesia_eaf',79,2000,'KATOWICE','Silesia/Polish lands',['silesia_junk'],['SCMT'],['STEL'])]
 specs += [
 ('lille_depot',24,1990,'LILLE','France/Benelux',[],[],[]),
 ('lille_junk',25,1990,'LILLE','France/Benelux',['lille_depot'],['RCYC'],[]),
 ('lille_recycling',23,1990,'LILLE','France/Benelux',['lille_junk'],['RCYC'],[]),
 ('lille_plastics',18,1990,'LILLE','France/Benelux',['lille_recycling'],['PLAS'],['MNSP'])]
 for index,(key,local,year,townname,region,deps,raw,sinks) in enumerate(specs):
  town=next(t for t in towns if t['town_name'].upper()==townname);x,y=int(town['x']),int(town['y'])
  if local not in [24,25]:x+=12+(index%3)*8;y+=12
  r=RULES[local];near=min(placements,key=lambda a:abs(int(a.get('x') or 0)-x)+abs(int(a.get('y') or 0)-y))
  template=copy.deepcopy(p['events'][0]);template.update(event_id=key,local_id=local,industry=r['industry'],name=region+' '+r['industry'].replace('_',' ')+' expansion',region=region,
    open_date=absolute_date(f'{year}-01-01'),announce_date=absolute_date(f'{max(1830,year-5)}-01-01'),latest_date=absolute_date(f'{year+15}-12-31'),
    dependencies=deps,required_producers=raw,required_consumers=sinks,sites=offsets(x,y,step=1 if local in [24,25] else 2),anchor_x=x,anchor_y=y,inputs=r['accepted'],outputs=r['produced'],
    earliest_native_year=r['earliest_year'],recipe_rule=r['historical_rule'],native_location_checks=r['industry_location_checks'],native_tile_checks=r['tile_location_checks'],
    source=near.get('history_source') or 'Existing Phase 6B regional geography; see historical_industry_locations.csv',
    provenance_locality=near.get('locality',''),date_basis='PROPOSED REGIONAL GAMEPLAY WINDOW; not an exact establishment date',confidence='Regional proxy; transport viability unverified')
  p['events'].append(enrich(template))
 return validate(p)
def validate(p):
 assert __debug__ and p['schema']==4 and p['migration']=='reject'
 keys=[e['event_id'] for e in p['events']];assert len(keys)==len(set(keys))
 for e in p['events']:
  assert e['local_id'] in RULES and e['announce_date']<=e['open_date']<=e['latest_date']
  assert e['sites'] and len(e['sites'])==len(set(e['sites'])) and all(type(t) is int and 0<t<16777216 for t in e['sites'])
  assert e['footprint'] and all(d in keys[:keys.index(e['event_id'])] for d in e['dependencies'])
  native=enrich(dict(local_id=e['local_id'],event_id=e['event_id']))
  for field in ['footprint','width','height','houses_nearby','minimum_population','keystone_local_ids','keystone_distance']:assert e[field]==native[field],field
  assert 0<e['max_attempts']<=128 and 0<e['max_batches']<=12
  if not p['test_mode']:assert e['open_date']>=absolute_date(f"{max(1,RULES[e['local_id']]['earliest_year']):04d}-01-01")
 if p['retirement']:assert p['retirement']==cp()['retirement'],'No retirement expansion'
 return p
def compile_policy(p,path):
 validate(p);contract=json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False)
 path.write_text('/* Phase 7D: schema 4; deliberate fresh-candidate policy. */\nEXPANSION_CONTRACT_TEXT <- '+squirrel(contract)+';\nEXPANSION <- '+squirrel(p)+';\n',encoding='utf-8-sig')
def setup(home,p=None,legacy=None,schedule=None):
 compile_policy(p or production(),home/'game/lifecycle/expansion_policy.nut');bc(legacy or bp(),home/'game/lifecycle/legacy_policy.nut');compile_schedule(schedule or historical(),home/'game/lifecycle/schedule.nut')
if __name__=='__main__':
 p=production();text=json.dumps(p,indent=2,ensure_ascii=False)
 text=re.sub(r'("sites": )\[\n((?: +\d+,?\n)+) *\]',lambda m:m[1]+'['+','.join(re.findall(r'\d+',m[2]))+']',text)
 (DIR/'progression_policy.json').write_text(text,encoding='utf8');compile_policy(p,DIR/'progression_policy.nut')
 from industrial_phase6b_plan import write_csv
 write_csv(DATA/'phase7d_event_policy.csv',[{k:v for k,v in e.items() if k not in ['sites','native_tile_checks','recipe_rule','native_location_checks']} for e in p['events']]);print('events',len(p['events']))
