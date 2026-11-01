"""Phase 7D: new isolated GS v4 candidate, unchanged pinned AXIS 0.6."""
import json,shutil
from pathlib import Path
import lifecycle_phase7a_runtime as a
import lifecycle_phase7c_runtime as c
ROOT=c.ROOT;ENGINE=c.ENGINE;GRF=c.GRF;sha=c.sha
BASE=ROOT/'newgrfs/axis-historical-progression/.work/runtime';BASE.mkdir(parents=True,exist_ok=True)
SOURCE=Path(json.loads((ROOT/'docs/research/phase7c_candidate_delivery.json').read_text())['candidate'])
def guards():
 c.guards();assert sha(GRF)=='023099757b94573f33e0c8380804cdbe80d3155b914d5441f98e89e55c9d8b84'
 assert sha(SOURCE)=='3064ea27afd485a59a3a4c71d30ee8c96d28968ecdf31aa2b056fb537924dbda'
def bundle():
 return c.bundle()+'\n'+(ROOT/'gamescripts/historical_industry_lifecycle/progression.nut').read_text(encoding='utf-8-sig')
def prepare(tag,script=None,year=1830,policy=True,density=0):
 guards();old=c.BASE
 try:
  c.BASE=BASE;h=c.prepare(tag,script if script is not None else bundle(),policy=policy,density=density)
 finally:c.BASE=old
 shutil.copyfile(ROOT/'gamescripts/historical_industry_lifecycle/progression_info.nut',h/'game/lifecycle/info.nut')
 cfg=h/'test.cfg';cfg.write_text(cfg.read_text().replace('starting_year = 1830',f'starting_year = {year}').replace('custom_town_number = 3','custom_town_number = 18'))
 return h
def execute(*args,**kwargs):return c.execute(*args,**kwargs)
