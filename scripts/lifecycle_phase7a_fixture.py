"""End-to-end accelerated fixture, normal company funds, real Save/Load."""
import argparse,json,shutil
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,prepare,execute,sha
from lifecycle_phase7a_schedule import fixture,compile_schedule
from industrial_phase6b_controls import builder,COMMON

METHODS='''
 function TestSetup(){
  if(loaded==null){Build(0,25,35);local consumer=Build(45,75,35);GSLog.Info("P7 TEST_INITIAL|consumer="+consumer+"|industries="+GSIndustryList().Count());}
 }
 function TestSample(){if(state!=null && ("test" in state) && state.test.service!=null){Sample(state.test.service);}}
 function TestHook(now){
  if(!("test" in state))state.test<-{service=null,route_attempted=false,paid_logged=false};
  local r=state.events[SCHEDULE.events[0].event_id];
  if(!state.test.route_attempted && r.status=="operating"){
   state.test.route_attempted=true;local customer=-1;foreach(i,_ in GSIndustryList())if(GSIndustry.GetIndustryType(i)==Type(45))customer=i;
   while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
   {local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];GSRoad.SetCurrentRoadType(0);
    GSLog.Info("P7 TEST_CASH|before="+GSCompany.GetBankBalance(0));
    state.test.service=Service("lifecycle_coal_paid","COAL",r.signature.id,customer,true);
    GSLog.Info("P7 TEST_CASH|after="+GSCompany.GetBankBalance(0));}
  }
  if(state.test.service!=null && state.test.service.paid && !state.test.paid_logged){state.test.paid_logged=true;Log("paid","fixture","actual_coal_delivery=true|calendar="+now);}
  if(TEST_PHASE==1 && r.status=="warned" && state.test.paid_logged){
   GSGame.Pause();Log("checkpoint","fixture","calendar="+now+"|warned=true|paid=true");while(true)Sleep(365);
  }
  if(TEST_PHASE==2 && now>=SCHEDULE.events[0].open_date+1700){
   foreach(e in SCHEDULE.events){local row=state.events[e.event_id];Log("final",e.event_id,"state="+row.status+"|attempts="+row.attempts+"|signature="+(row.signature==null?"none":row.signature.id));}
   GSGame.Pause();Log("done","fixture","calendar="+now+"|industries="+GSIndustryList().Count());while(true)Sleep(365);
  }
 }
'''

def code(phase):
    text=(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text()
    text=text.replace(' function Start(){try{',COMMON+METHODS+'\n function Start(){try{\nGSGame.Unpause();')
    text=text.replace('local now=Calendar();Initialize(now);','local now=Calendar();TestSetup();Initialize(now);')
    text=text.replace('Tick(now);Sleep(74*14);','Tick(now);TestHook(now);for(local sample=0;sample<104;sample++){TestSample();Sleep(10);}')
    return 'TEST_PHASE <- '+str(phase)+';\n'+builder()+text

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resume',type=Path);a=ap.parse_args()
    if a.resume:
        home=a.resume;checkpoint=home/'checkpoint.sav'
    else:
        home=prepare('vertical-slice',code(1));compile_schedule(fixture(),home/'game/lifecycle/schedule.nut')
        config=home/'test.cfg';config.write_text(config.read_text().replace('custom_town_number = 3','custom_town_number = 12'))
        initial=execute(home,65000,tag='initial')
        assert any('EVENT|checkpoint|' in s for s in initial['observations']),'No warned/paid checkpoint'
        checkpoint=home/'checkpoint.sav';shutil.copyfile(home/'save/autosave/exit.sav',checkpoint)
        (BASE/'vertical-slice-case.txt').write_text(str(home))
    (home/'game/lifecycle/main.nut').write_text(code(2),encoding='utf-8-sig')
    result=execute(home,150000,source=checkpoint,tag='reloaded')
    assert any('EVENT|loaded|' in s for s in result['observations']),'Save/Load was not observed'
    assert any('EVENT|closed|' in s for s in result['observations']),'No real closure'
    all_lines=(home/'initial.log').read_text(encoding='utf8')+(home/'reloaded.log').read_text(encoding='utf8')
    for event in fixture()['events']:assert all_lines.count('EVENT|opened|'+event['event_id']+'|')==1,event['event_id']
    assert any('EVENT|opened|test_replacement|' in s for s in result['observations']),'No replacement'
    assert any('EVENT|done|' in s for s in result['observations']),'No terminal fixture observation'
    (BASE/'vertical-slice.json').write_text(json.dumps(dict(case=str(home),checkpoint_sha256=sha(checkpoint),result=result),indent=2))

if __name__=='__main__':main()
