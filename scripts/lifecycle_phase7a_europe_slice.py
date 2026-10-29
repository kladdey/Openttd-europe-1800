"""Actual Europe-map vertical slice, test dates only; no save-byte edits."""
import argparse,json,shutil
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,prepare,execute,sha
from lifecycle_phase7a_europe_plan import plan
from lifecycle_phase7a_schedule import compile_schedule
from industrial_phase6b_controls import builder,COMMON

METHODS='''
 function TestSample(){if(state!=null && ("test" in state) && state.test.service!=null)Sample(state.test.service);}
 function TestHook(now){
  if(!("test" in state))state.test<-{service=null,attempted=false,paid=false,unknown={}};
  local event=SCHEDULE.events[0],r=state.events[event.event_id];
  if(!state.test.attempted && r.status=="operating"){
   state.test.attempted=true;while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
   local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];GSRoad.SetCurrentRoadType(0);
   GSLog.Info("P7 EUROPE_ROUTE_CASH|before="+GSCompany.GetBankBalance(0));
   state.test.service=Service("europe_lifecycle_coal","COAL",r.signature.id,event.test_consumer,true);
   GSLog.Info("P7 EUROPE_ROUTE_CASH|after="+GSCompany.GetBankBalance(0));cm=null;
  }
  if(state.test.service!=null && state.test.service.paid && !state.test.paid){state.test.paid=true;Log("paid","europe","actual_loaded_delivery=true|calendar="+now);}
  foreach(i,_ in GSIndustryList()){
   local known=false;foreach(s in state.baseline)if(Matches(i,s)){known=true;break;}
   if(!known)foreach(id,row in state.events)if(row.signature!=null && Matches(i,row.signature)){known=true;break;}
   if(!known){local key=i+"_"+GSIndustry.GetLocation(i)+"_"+GSIndustry.GetConstructionDate(i);if(!(key in state.test.unknown)){state.test.unknown[key]<-true;Log("unplanned","europe",key);}}
  }
  if(TEST_PHASE==1 && r.status=="warned" && state.test.paid){GSGame.Pause();Log("checkpoint","europe","calendar="+now+"|baseline="+state.baseline.len());while(true)Sleep(365);}
  if(TEST_PHASE==2 && now>=SCHEDULE.events[0].open_date+1050){
   local preserved=0;foreach(s in state.baseline)if(Matches(s.id,s))preserved++;
   foreach(e in SCHEDULE.events)Log("final",e.event_id,"state="+state.events[e.event_id].status);
   local remaining=0;if(state.test.service!=null)foreach(v in state.test.service.vehicles)if(GSVehicle.IsValidVehicle(v))remaining++;
   Log("europe_done","europe","calendar="+now+"|baseline_preserved="+preserved+"|towns="+GSTownList().Count()+"|unplanned="+state.test.unknown.len()+"|service_vehicles_remaining="+remaining);
   GSGame.Pause();while(true)Sleep(365);
  }
 }
'''

def code(phase):
    text=(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text()
    text=text.replace(' function Start(){try{',COMMON+METHODS+'\n function Start(){try{\nGSGame.Unpause();')
    text=text.replace('Tick(now);Sleep(74*14);','Tick(now);TestHook(now);for(local sample=0;sample<104;sample++){TestSample();Sleep(10);}')
    return 'TEST_PHASE <- '+str(phase)+';\n'+builder()+text

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resume',type=Path);a=ap.parse_args()
    candidate=Path(json.loads((BASE/'europe-editor.json').read_text())['candidate'])
    if a.resume:home=a.resume
    else:
        home=prepare('europe-vertical-slice',code(1));compile_schedule(plan(),home/'game/lifecycle/schedule.nut')
        # Engine-supported startup console script only unpauses this test game.
        # It does not change DATE bytes, economics or normal user configuration.
        (home/'scripts').mkdir();(home/'scripts/game_start.scr').write_text('unpause\n')
        initial=execute(home,65000,source=candidate,tag='initial')
        assert any('EVENT|checkpoint|europe|' in s for s in initial['observations']),'No paid/warned Europe checkpoint'
        shutil.copyfile(home/'save/autosave/exit.sav',home/'checkpoint.sav');(BASE/'europe-slice-case.txt').write_text(str(home))
    (home/'game/lifecycle/main.nut').write_text(code(2),encoding='utf-8-sig')
    result=execute(home,120000,source=home/'checkpoint.sav',tag='reloaded')
    lines=(home/'initial.log').read_text(encoding='utf8')+(home/'reloaded.log').read_text(encoding='utf8')
    for event in plan()['events']:assert lines.count('EVENT|opened|'+event['event_id']+'|')==1,event['event_id']
    assert 'EVENT|europe_done|europe|' in lines and 'baseline_preserved=542|towns=617|unplanned=0' in lines
    assert 'EVENT|closed|test_gb_coalfield|' in lines and 'EVENT|loaded|scheduler|' in lines
    (BASE/'europe-slice.json').write_text(json.dumps(dict(case=str(home),checkpoint_sha256=sha(home/'checkpoint.sav'),source_scenario_sha256=sha(candidate),result=result),indent=2))

if __name__=='__main__':main()
