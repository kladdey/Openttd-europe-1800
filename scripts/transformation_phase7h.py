"""Exactly two new events; old 40 expansion rows and Ruhr cycle unchanged."""
import json
from pathlib import Path
import cycles_phase7g as g
from lifecycle_phase7d_policy import enrich,offsets,RULES,absolute_date,squirrel
ROOT=g.ROOT;DIR=g.DIR;ENGINE=g.ENGINE;GRF=g.GRF;sha=g.sha;guards=g.guards
BASE=g.BASE.parent/'phase7h';BASE.mkdir(exist_ok=True)
SOURCE=Path(json.loads((ROOT/'docs/research/phase7g_candidate_delivery.json').read_text())['candidate'])

def policy(fixture=False):
 specs=[('lancashire_textiles',42,'open','Lancashire',2966,968,'FICR','GOOD'),('silesian_transition',0,'retire','Upper Silesia',749,1490,'ENSP','COAL')]
 events=[]
 for key,local,kind,region,x,y,producer,consumer in specs:
  e=enrich(dict(event_id=key,local_id=local));e.update(id=key,kind=kind,region=region,industry=RULES[local]['industry'],producer=producer,consumer=consumer,producer_radius=160 if kind=='open' else 0,sites=offsets(x,y,radius=24,step=2))
  normal='1840-01-01' if kind=='open' else '1975-01-01';start='1830-01-15' if kind=='open' else '1830-01-02'
  e.update(open_date=absolute_date(start if fixture else normal),latest_open=absolute_date('1830-03-31' if fixture else '1845-12-31' if kind=='open' else '1980-12-31'),decline_date=absolute_date('1830-05-01' if fixture else '1991-01-01'),retire_date=absolute_date('1830-09-01' if fixture else '2000-01-01'),date_basis='Regional gameplay approximation, not an identified factory/colliery biography')
  events.append(e)
 return validate(dict(id='phase7h_fixture' if fixture else 'phase7h_two_region_v1',schema=6,migration='reject',fixture=fixture,events=events))

def validate(p):
 assert p['schema']==6 and p['migration']=='reject' and len(p['events'])==2
 assert len({e['id'] for e in p['events']})==2
 existing={e['event_id'] for e in g.p.production()['events']}|set(g.policy()['events'])
 assert not ({e['id'] for e in p['events']} & existing)
 for e in p['events']:
  assert (e['local_id'],e['kind']) in [(42,'open'),(0,'retire')] and e['producer'] in RULES[e['local_id']]['accepted'] and e['consumer'] in [c for c,_ in RULES[e['local_id']]['produced']]
  assert e['open_date']<=e['latest_open'] and e['open_date']>=absolute_date(f"{max(1,RULES[e['local_id']]['earliest_year']):04d}-01-01")
  if e['kind']=='retire':assert e['latest_open']<e['decline_date']<e['retire_date']
  assert e['sites'] and all(0<t<4096**2 for t in e['sites'])
 return p

def setup(h,p=None):
 g.setup(h);p=p or policy();validate(p);text=json.dumps(p,sort_keys=True,separators=(',',':'))
 (h/'game/lifecycle/transformation_policy.nut').write_text('TRANSFORMATION_TEXT <- '+squirrel(text)+';\nTRANSFORMATION <- '+squirrel(p)+';\n',encoding='utf-8-sig')
def bundle():return g.bundle()+'\n'+(DIR/'transformation.nut').read_text(encoding='utf-8-sig')
def prepare(tag,code=None,p=None):
 old=g.BASE
 try:g.BASE=BASE;h=g.prepare(tag,code or bundle())
 finally:g.BASE=old
 (h/'game/lifecycle/info.nut').write_text((DIR/'transformation_info.nut').read_text(encoding='utf8'));setup(h,p);return h
def execute(h,ticks=33000,source=None):return g.execute(h,ticks,source=source or SOURCE)
if __name__=='__main__':(DIR/'transformation_policy.json').write_text(json.dumps(policy(),indent=2)+'\n')
