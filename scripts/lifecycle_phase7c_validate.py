"""Actual stock-engine Europe fixtures. No edits to scenario/save bytes."""
import argparse,json,shutil,re
from pathlib import Path
from lifecycle_phase7c_runtime import *
from lifecycle_phase7c_policy import production,setup,absolute_date
from industrial_phase6b_controls import builder,COMMON
METHODS='''
 function CTest(now){
  if(!("ctest" in state))state.ctest<-{services=[],built=false,paid=false};
  local r=state.expansion.galicia_mill;
  if(r.status=="built"&&!state.ctest.built){
   while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
   state.ctest.built=true;local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];GSRoad.SetCurrentRoadType(0);
   state.ctest.services.append(Service("new_mill_grain","GRAI",66,r.signature.id,true));
   state.ctest.services.append(Service("new_mill_food","FOOD",r.signature.id,474,true));
   Log("c_capital","fixture","cash="+GSCompany.GetBankBalance(0));
  }
  if(state.ctest.services.len()>0){
   local cm=GSCompanyMode(0);local allpaid=true;
   foreach(service in state.ctest.services){Sample(service);if(!service.paid)allpaid=false;}
   if(allpaid&&!state.ctest.paid){state.ctest.paid=true;Log("c_paid_chain","fixture","calendar="+now+"|new_industry="+r.signature.id+"|both_legs_loaded_and_positive_sampled_net=true");}
  }
  if(now>=GSDate.GetDate(STOP_YEAR,STOP_MONTH,1)){
   local intact=0;foreach(s in state.baseline)if(s.id!=275&&Matches(s.id,s))intact++;
   Log("c_checkpoint","fixture","calendar="+now+"|industry_count="+GSIndustryList().Count()+"|other_originals_intact="+intact+"|towns="+GSTownList().Count()+"|factory="+state.factory.status+"|paid="+state.ctest.paid);
   GSGame.Pause();while(true)Sleep(365);
  }
 }
'''
def fixture():
    p=production();p.update(id='phase7c-CLEARLY-ACCELERATED-Europe-fixture',test_mode=True)
    p['events']=[p['events'][0],p['events'][3]]
    for e,year in zip(p['events'],[1831,1832]):e.update(open_date=absolute_date(f'{year}-01-01'),announce_date=absolute_date('1830-01-01'),latest_date=absolute_date('1836-12-31'))
    p['retirement'].update(warning_date=absolute_date('1831-01-01'),close_date=absolute_date('1837-01-01'),latest_close=absolute_date('1840-12-31'),warning_years=5)
    return p
def code(year,month=1):
    s=bundle();index=s.index('class ExpansionLifecycleController');s=s[:index]+s[index:].replace(' function Start(){try{',COMMON.replace('fleet=2','fleet=8').replace('::FLEET=2','::FLEET=8')+METHODS+'\n function Start(){try{GSGame.Unpause();',1)
    s=s.replace('Tick(Calendar());Sleep(74*14);','local now=Calendar();Tick(now);CTest(now);for(local n=0;n<104;n++){if(("ctest" in state)&&state.ctest.services.len()>0){local cm=GSCompanyMode(0);foreach(service in state.ctest.services)Sample(service);}Sleep(10);}')
    return f'STOP_YEAR <- {year};STOP_MONTH <- {month};\n'+re.sub(r'}(?=(?:Sleep|return|if\())','}\n',builder()+s)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['europe','native']);ap.add_argument('--resume',type=Path);a=ap.parse_args()
    if a.case=='europe':
        home=a.resume or prepare('accelerated-Europe',code(1831,2));setup(home,fixture());(home/'scripts').mkdir(exist_ok=True);(home/'scripts/game_start.scr').write_text('unpause\n');results=[];source=SOURCE
        (BASE/'europe-active.json').write_text(json.dumps(dict(case=str(home)),indent=2))
        for stage,(year,month) in enumerate([(1831,2),(1833,1),(1836,1),(1838,1)]):
            checkpoint=home/f'checkpoint-{stage}.sav';cached=home/f'stage{stage}-result.json'
            if a.resume and cached.exists() and checkpoint.exists():results.append(json.loads(cached.read_text()));source=checkpoint;continue
            (home/'game/lifecycle/main.nut').write_text(code(year,month),encoding='utf-8-sig')
            r=execute(home,180000,source=source,tag='stage'+str(stage),timeout=900)
            assert any('c_checkpoint|fixture|' in s for s in r['observations']),r['log']
            shutil.copyfile(home/'save/autosave/exit.sav',checkpoint);source=checkpoint;results.append(r)
        (BASE/'europe.json').write_text(json.dumps(dict(policy=fixture(),case=str(home),runs=results),indent=2))
    else:
        text='''class ExpansionLifecycleController extends GSController {function Start(){GSGame.Unpause();
local initial=GSIndustryList().Count();GSIndustry.SetProductionLevel(275,4,false,null);local date=GSDate.GetCurrentDate();while(GSDate.GetCurrentDate()-date<65)Sleep(20);
if(!GSIndustry.IsValidIndustry(275))throw "Bare level four closed mill";GSLog.Info("P7 C_NATIVE_UNARMED|survives=true");
GSIndustry.SetControlFlags(275,GSIndustry.GetControlFlags(275)|GSIndustry.INDCTL_NO_CLOSURE);GSIndustry.SetProductionLevel(275,11,false,null);date=GSDate.GetCurrentDate();while(GSDate.GetCurrentDate()-date<45)Sleep(20);
GSIndustry.SetControlFlags(275,GSIndustry.GetControlFlags(275)&~GSIndustry.INDCTL_NO_CLOSURE);GSIndustry.SetProductionLevel(275,4,false,null);date=GSDate.GetCurrentDate();while(GSDate.GetCurrentDate()-date<120&&GSIndustry.IsValidIndustry(275))Sleep(20);
if(GSIndustry.IsValidIndustry(275)||GSIndustryList().Count()!=initial-1)throw "Factory did not physically close";
GSLog.Info("P7 C_NATIVE_CLOSED|selected=false|count="+GSIndustryList().Count());GSGame.Pause();while(true)Sleep(365);}}'''
        h=prepare('native-factory',text);(h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n');r=execute(h,22000,source=SOURCE);assert any('C_NATIVE_CLOSED' in s for s in r['observations']);(BASE/'native.json').write_text(json.dumps(r,indent=2))
if __name__=='__main__':main()
