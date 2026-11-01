"""Lean engine drivers: one timeline split at an event boundary, one Europe smoke.

No paid-chain/economy certification. Raw logs remain in ignored local profiles.
"""
import argparse,copy,json,shutil
from pathlib import Path
from lifecycle_phase7d_runtime import *
from lifecycle_phase7d_policy import production,setup,enrich,offsets,squirrel,absolute_date
from lifecycle_phase7b_policy import production as bp
from lifecycle_phase7c_waves import parked
def fixture_legacy():
 p=bp();p.update(enroll_legacy=False,sites=[]);return p
SEED='''
 function Seed(local_id,x,y){local before={};foreach(i,_ in GSIndustryList())before[i]<-true;
 for(local radius=0;radius<=12;radius+=2)for(local dx=-radius;dx<=radius;dx+=2)for(local dy=-radius;dy<=radius;dy+=2){
 if(abs(dx)+abs(dy)!=radius)continue;local tile=GSMap.GetTileIndex(x+dx,y+dy);
 if(GSIndustryType.BuildIndustry(Type(local_id),tile)){foreach(i,_ in GSIndustryList())if(!(i in before)){Log("d_seed","fixture","local="+local_id+"|industry="+i+"|tile="+GSIndustry.GetLocation(i));return;}}
 }
 throw "Controlled seed failed "+local_id;
 }
 function MarketSeed(local_id,which){
 local towns=[];foreach(t,_ in GSTownList())towns.append(t);towns.sort(function(a,b){return GSTown.GetPopulation(b)-GSTown.GetPopulation(a);});
 local town=towns[which],at=GSTown.GetLocation(town),x=GSMap.GetTileX(at),y=GSMap.GetTileY(at),pop=GSTown.GetPopulation(town);
 for(local dx=-15;dx<=15;dx++)for(local dy=-15;dy<=15;dy++){
 local tile=GSMap.GetTileIndex(x+dx,y+dy);if(!GSMap.IsValidTile(tile)||!GSTile.IsHouseTile(tile))continue;
 if(GSIndustryType.BuildIndustry(Type(local_id),tile)){local after=GSTown.GetPopulation(town);Log("d_fixture_house","market","town="+town+"|before="+pop+"|after="+after+"|one_building=true");
 if(pop-after>pop/20)throw "Fixture house loss exceeded five percent";return;}
 }
 throw "Controlled retail seed failed";
 }
'''
def timeline_code(end):
 s=bundle();index=s.index('class ProgressionController');s=s[:index]+s[index:].replace(' progression_contract=null;',SEED+'\n progression_contract=null;',1)
 s+='''
class TimelineProbe extends ProgressionController {
 function Start(){try{GSGame.Unpause();if(loaded==null){Seed(26,55,55);Seed(26,55,160);Seed(26,145,90);Seed(7,150,135);Seed(0,25,210);Seed(78,40,210);Seed(38,185,95);MarketSeed(61,0);MarketSeed(57,1);}
 Initialize(Calendar());local year=-1;
 while(true){local now=Calendar();Tick(now);if(GSDate.GetYear(now)!=year){year=GSDate.GetYear(now);Log("d_year","timeline","year="+year+"|industries="+GSIndustryList().Count());}
 if(year>=END){foreach(e in EXPANSION.events)Log("d_event_final",e.event_id,"state="+state.expansion[e.event_id].status+"|attempts="+state.expansion[e.event_id].attempts);
 Log("d_boundary","timeline","year="+year+"|schema="+state.schema+"|industries="+GSIndustryList().Count());GSGame.Pause();while(true)Sleep(365);}
 Sleep(74*14);}
 }catch(e){GSLog.Error("P7 FATAL|"+e);while(true)Sleep(365);}}
}
'''.replace('END',str(end))
 return s
def mini_policy():
 p=production();p.update(id='phase7d-abstract-map-normal-calendar',test_mode=True,retirement=None)
 anchors={'galicia':(65,100),'ruhr':(145,120),'rhine':(31,19),'gb':(40,40),'fr':(124,97),'iberian':(89,184),'silesia':(60,169),'italy':(135,44),'scandi':(213,29),'lille':(143,186)}
 for e in p['events']:
  prefix=e['event_id'].split('_')[0];x,y=anchors[prefix]
  if not e['houses_nearby']:x+=12;y+=6
  if e['event_id']=='galicia_successor':x,y=35,90
  e['sites']=offsets(x,y,width=256,step=1 if e['houses_nearby'] else 2)
 return p
def run_timeline():
 p=mini_policy();h=prepare('continuous-1830-2026',timeline_code(1991));setup(h,p,fixture_legacy(),parked())
 info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"ProgressionController"','"TimelineProbe"'))
 results=[];source=None
 for index,end in enumerate([1991,2026]):
  (h/'game/lifecycle/main.nut').write_text(timeline_code(end),encoding='utf-8-sig')
  r=execute(h,5500000,source=source,tag='part'+str(index),timeout=600);assert any('d_boundary|timeline|year='+str(end) in line for line in r['observations']);results.append(r)
  source=h/f'boundary-{end}.sav';shutil.copyfile(h/'save/autosave/exit.sav',source)
 opened=[s.split('expansion_opened|')[1].split('|')[0] for r in results for s in r['observations'] if 'EVENT|expansion_opened|' in s]
 assert len(opened)==len(set(opened)),'Duplicate opening after reload'
 (BASE/'timeline.json').write_text(json.dumps(dict(policy=p,runs=results,unique_openings=opened),indent=2))
def run_europe():
 p=production();p.update(id='phase7d-EUROPE-1984-editor-fixture',test_mode=True,retirement=None)
 keys=['rhine_depot','rhine_junk','rhine_recycling','rhine_plastics','lille_depot','lille_junk','lille_recycling','lille_plastics','fr_oil_food']
 p['events']=[e for e in p['events'] if e['event_id'] in keys]
 for e in p['events']:e.update(announce_date=absolute_date('1984-01-01'),open_date=absolute_date('1985-01-01'),latest_date=absolute_date('1987-12-31'))
 code=bundle()+'''
class EuropeProbe extends ProgressionController {function Start(){try{GSGame.Unpause();
if(GSTownList().Count()!=617||GSIndustryList().Count()!=542)throw "Europe fixture baseline changed";
Initialize(Calendar());while(true){local now=Calendar();Tick(now);local terminal=true;foreach(e in EXPANSION.events){local status=state.expansion[e.event_id].status;if(status!="built"&&status!="cancelled")terminal=false;}
if(terminal||GSDate.GetYear(now)>=1988){local intact=0;foreach(sig in state.baseline)if(Matches(sig.id,sig))intact++;
foreach(e in EXPANSION.events)Log("d_event_final",e.event_id,"state="+state.expansion[e.event_id].status+"|attempts="+state.expansion[e.event_id].attempts);
Log("d_europe_done","fixture","baseline_intact="+intact+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count());GSGame.Pause();while(true)Sleep(365);}
Sleep(74*14);}
}catch(e){GSLog.Error("P7 FATAL|"+e);while(true)Sleep(365);}}}
'''
 h=prepare('Europe-modern-and-food',code);setup(h,p,fixture_legacy(),parked());info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"ProgressionController"','"EuropeProbe"'))
 source=Path(json.loads((BASE/'editor.json').read_text())['case'])/'scenario/f.scn';assert source.exists(),'Save the supported 1984 editor fixture first'
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n');r=execute(h,160000,source=source,timeout=600)
 assert any('d_europe_done|fixture|baseline_intact=542|towns=617' in line for line in r['observations']);(BASE/'europe.json').write_text(json.dumps(dict(policy=p,run=r),indent=2))
def guard():
 s='''class GuardProbe extends GSController {function Save(){return {};}
function Start(){local before={},new_count=0,start=GSDate.GetCurrentDate();foreach(i,_ in GSIndustryList())before[i]<-true;
local available=GSIndustryType.CanBuildIndustry(GSIndustryType.ResolveNewGRFID(0x4B484531,0));
while(GSDate.GetCurrentDate()-start<365*5){foreach(i,_ in GSIndustryList())if(!(i in before)){before[i]<-true;new_count++;}
Sleep(74*14);}
GSLog.Info("P7 D_GUARD|optin_off_available="+available+"|unplanned="+new_count+"|days="+(GSDate.GetCurrentDate()-start));GSGame.Pause();while(true)Sleep(365);}}'''
 h=prepare('off-natural-control',s,policy=False,density=4);info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"ProgressionController"','"GuardProbe"'));r=execute(h,150000)
 assert any('D_GUARD|optin_off_available=false|unplanned=0' in line for line in r['observations']);(BASE/'guard.json').write_text(json.dumps(r,indent=2))
def legacy():
 from lifecycle_phase7b_probe import SCRIPT
 s=SCRIPT.replace('class LifecycleController extends GSController','class ClosureProbe extends ProgressionController').replace('GetVersion(0x4B484531)!=5','GetVersion(0x4B484531)!=6')
 s=s.replace('GSGame.Unpause();GSLog.Info', 'GSGame.Pause();Initialize(Calendar());Log("d_startup","candidate","schema="+state.schema+"|events="+state.expansion.len()+"|legacy="+state.legacy.len()+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|calendar="+Calendar()+"|economy="+GSDate.GetCurrentDate());GSGame.Unpause();GSLog.Info')
 h=prepare('targeted-original-mine-handshake',bundle()+'\n'+s);setup(h);info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"ProgressionController"','"ClosureProbe"'));(h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 candidate=Path(json.loads((BASE/'candidate.json').read_text())['candidate'])
 r=execute(h,26000,source=candidate);assert any('BPROBE_DONE' in line for line in r['observations']);assert any('d_startup|candidate|schema=4|events=32|legacy=4|towns=617|industries=542|calendar=668394|economy=657437' in line for line in r['observations']);(BASE/'legacy.json').write_text(json.dumps(r,indent=2))
def startup():
 s=bundle()+'''\nclass StartupProbe extends ProgressionController {function Start(){try{GSGame.Pause();Initialize(Calendar());
state.schema=3;local saved=Save();state.schema=4;if(saved.schema!=4)throw "Autosave root normalization failed";
Log("d_autosave","candidate","temporary_parent_view=3|serialized_root="+saved.schema);
Log("d_startup","candidate","schema="+state.schema+"|events="+state.expansion.len()+"|legacy="+state.legacy.len()+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|calendar="+Calendar()+"|economy="+GSDate.GetCurrentDate());
}catch(e){GSLog.Error("P7 FATAL|"+e);}
while(true)Sleep(365);}}'''
 m=json.loads((BASE/'candidate.json').read_text());h=prepare('normal-candidate-start',s);setup(h);info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"ProgressionController"','"StartupProbe"'))
 r=execute(h,4000,source=Path(m['candidate']));assert any('d_startup|candidate|schema=4|events=32|legacy=4|towns=617|industries=542|calendar=668394|economy=657437' in x for x in r['observations'])
 (BASE/'startup.json').write_text(json.dumps(r,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('case',choices=['timeline','europe','guard','legacy','startup']);a=ap.parse_args();{'timeline':run_timeline,'europe':run_europe,'guard':guard,'legacy':legacy,'startup':startup}[a.case]()
