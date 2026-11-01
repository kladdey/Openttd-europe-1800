"""Phase 7F policy/isolated runtime, preserving the 7D and 7E work."""
import copy,json,csv,re
from pathlib import Path
import lifecycle_phase7d_runtime as d
from lifecycle_phase7d_policy import production as original,enrich,RULES,offsets,squirrel,absolute_date,setup as old_setup
ROOT=d.ROOT;BASE=d.BASE/'phase7f';BASE.mkdir(exist_ok=True)
SOURCE=Path(json.loads((ROOT/'docs/research/phase7d_candidate_delivery.json').read_text())['candidate'])
ENGINE=d.ENGINE;GRF=d.GRF;sha=d.sha;guards=d.guards
DIR=ROOT/'gamescripts/historical_industry_lifecycle'

def port_event(key,local,year,region,x,y,inputs,outputs,source):
 e=copy.deepcopy(original()['events'][0]);r=RULES[local]
 e.update(event_id=key,local_id=local,industry=r['industry'],name=region+' maritime '+r['industry'].replace('_',' '),region=region,dependencies=[],required_producers=inputs,required_consumers=outputs,inputs=r['accepted'],outputs=r['produced'],open_date=absolute_date(f'{year}-01-01'),announce_date=absolute_date(f'{max(1830,year-5)}-01-01'),latest_date=absolute_date(f'{year+20}-12-31'),earliest_native_year=r['earliest_year'],anchor_x=x,anchor_y=y,sites=offsets(x,y,radius=32,step=1),source=source,date_basis='APPROXIMATE REGIONAL GAMEPLAY WINDOW; not a terminal founding date',confidence='Native construction/transport conditional',max_attempts=96,max_batches=6)
 enrich(e)
 e.update(recipe_rule=r['historical_rule'],native_location_checks=r['industry_location_checks'],native_tile_checks=r['tile_location_checks'])
 e['coastal']=local in [39,46,51,74]
 if e['coastal']:
  e['footprint']=sorted({tuple(v-256 if v>127 else v for v in point) for point in e['footprint']})
  e['footprint']=[list(p) for p in e['footprint']];e['width']=max(p[0] for p in e['footprint'])-min(p[0] for p in e['footprint'])+1;e['height']=max(p[1] for p in e['footprint'])-min(p[1] for p in e['footprint'])+1
 return e

def production():
 p=original();p['id']='phase7f-historical-ports-v1'
 for region,x,y,ref in [('Liverpool',3026,966,'https://whc.unesco.org/uploads/nominations/1150.pdf'),('Gdansk',767,811,'https://www.portgdansk.pl/en/sustainable-development/investments-and-development/the-port-and-the-city/')]:
  for local,year,inputs,outputs in [(39,1831,['FOOD'],['MPAR']),(46,1875,['GOOD'],['MNSP']),(51,1975,['STEL'],['COAL']),(69,1995,['BOOM'],['ENSP'])]:
   e=port_event(region.lower()+'_'+str(year),local,year,region,x+(12 if local==69 else 0),y+(12 if local==69 else 0),inputs,outputs,ref)
   p['events'].append(e)
 return validate(p)

def validate(p):
 assert p['schema']==4 and p['migration']=='reject'
 assert p['events'][:32]==original()['events'],'Preserve existing policy exactly'
 assert p['retirement']==original()['retirement']
 ids=[e['event_id'] for e in p['events']];assert len(ids)==len(set(ids))
 for e in p['events'][32:]:
  assert e['open_date']>=absolute_date(f"{max(1,RULES[e['local_id']]['earliest_year']):04d}-01-01")
  assert e['announce_date']<=e['open_date']<=e['latest_date'] and 0<e['max_attempts']<=96 and e['max_batches']<=6
  assert e['sites'] and all(0<t<4096**2 for t in e['sites'])
  assert all(abs(v)<32 for xy in e['footprint'] for v in xy)
 return p

def setup(h,p=None):
 p=p or production();old_setup(h)
 contract=json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False)
 (h/'game/lifecycle/expansion_policy.nut').write_text('EXPANSION_CONTRACT_TEXT <- '+squirrel(contract)+';\nEXPANSION <- '+squirrel(p)+';\n',encoding='utf-8-sig')

def bundle():return d.bundle()+'\n'+(DIR/'ports.nut').read_text(encoding='utf-8-sig')
def prepare(tag,code=None):
 old=d.BASE
 try:d.BASE=BASE;h=d.prepare(tag,code or bundle())
 finally:d.BASE=old
 (h/'game/lifecycle/info.nut').write_text((DIR/'ports_info.nut').read_text(encoding='utf-8-sig'))
 setup(h);return h

def execute(h,ticks=6000,source=None):return d.execute(h,ticks,source=source or SOURCE,timeout=300)
if __name__=='__main__':
 p=production();text=json.dumps(dict(id=p['id'],schema=4,extends='progression_policy.json',added_events=p['events'][32:]),indent=2);text=re.sub(r'("sites": )\[\n((?: +\d+,?\n)+) *\]',lambda m:m[1]+'['+','.join(re.findall(r'\d+',m[2]))+']',text);(DIR/'ports_policy.json').write_text(text+'\n');print('events',len(p['events']))
