"""Two bounded Ruhr cycles; exact existing expansion/mine/mill policies retained."""
import json,copy,re
from pathlib import Path
import ports_phase7f as p
from lifecycle_phase7d_policy import enrich,offsets,absolute_date,squirrel
ROOT=p.ROOT;DIR=p.DIR;ENGINE=p.ENGINE;GRF=p.GRF;sha=p.sha;guards=p.guards
BASE=p.BASE.parent/'phase7g';BASE.mkdir(exist_ok=True)
SOURCE=Path(json.loads((ROOT/'docs/research/phase7f_candidate_delivery.json').read_text())['candidate'])

def policy(fixture=False):
 site=enrich(dict(event_id='ruhr_cycle_site',local_id=0));site['sites']=offsets(2039,1285,radius=24,step=2)
 dates=['1830-01-02','1830-04-01','1830-07-01','1830-10-01','1830-03-15'] if fixture else ['1850-01-01','1851-01-01','1873-01-01','1879-01-01','1850-12-31']
 return validate(dict(id='ruhr_cycle_fixture' if fixture else 'ruhr_cycle_1850_1879_v1',schema=5,migration='reject',fixture=fixture,region='Ruhr',site=site,open_date=absolute_date(dates[0]),boost_date=absolute_date(dates[1]),down_date=absolute_date(dates[2]),end_date=absolute_date(dates[3]),latest_open=absolute_date(dates[4]),boom_level=32,down_level=8,events=['ruhr_expansion','ruhr_downturn'],date_basis='Proposed gameplay approximation, not a precise historical output multiplier'))

def validate(c):
 assert c['schema']==5 and c['migration']=='reject' and len(c['events'])==2 and len(set(c['events']))==2
 assert c['open_date']<c['boost_date']<c['down_date']<c['end_date'] and c['latest_open']<c['boost_date']
 assert 4<c['down_level']<16<c['boom_level']<=128 and c['site']['local_id']==0
 assert c['site']['footprint'] and c['site']['sites'] and all(0<t<4096**2 for t in c['site']['sites'])
 return c

def setup(h,c=None):
 p.setup(h);c=c or policy();validate(c);contract=json.dumps(c,sort_keys=True,separators=(',',':'))
 (h/'game/lifecycle/cycles_policy.nut').write_text('CYCLE_CONTRACT_TEXT <- '+squirrel(contract)+';\nCYCLE <- '+squirrel(c)+';\n',encoding='utf-8-sig')
def bundle():return p.bundle()+'\n'+(DIR/'cycles.nut').read_text(encoding='utf-8-sig')
def prepare(tag,code=None,c=None):
 old=p.BASE
 try:p.BASE=BASE;h=p.prepare(tag,code or bundle())
 finally:p.BASE=old
 (h/'game/lifecycle/info.nut').write_text((DIR/'cycles_info.nut').read_text(encoding='utf8'));setup(h,c);return h
def execute(h,ticks=30000,source=None):return p.execute(h,ticks,source=source or SOURCE)
if __name__=='__main__':(DIR/'cycles_policy.json').write_text(json.dumps(policy(),indent=2)+'\n')
