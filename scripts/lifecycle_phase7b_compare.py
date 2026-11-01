"""Causal full-Europe pilot: same 1830 originals, with/without paid road service.

Uses real five-calendar-year notice and real 36-economy-month transport history.
Only fixture policy has 1837/1839 exhaustion; production policy is not changed.
"""
import argparse,json,shutil
from pathlib import Path
from lifecycle_phase7b_runtime import ROOT,BASE,prepare,execute,source7a,bundle,sha
from lifecycle_phase7b_policy import fixture,compile_policy
from lifecycle_phase7a_schedule import historical,compile_schedule
from industrial_phase6b_controls import builder,COMMON

METHODS='''
 function TestSample(){if(state!=null && ("comparison" in state)&&state.comparison.service!=null){local cm=GSCompanyMode(0);Sample(state.comparison.service);}}
 function ComparisonHook(now){
  if(!("comparison" in state))state.comparison<-{service=null,attempted=false,paid=false,start=now};
  if(TEST_SERVED && !state.comparison.attempted){
   state.comparison.attempted=true;while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
   local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];GSRoad.SetCurrentRoadType(0);
   Log("comparison_cash","fixture","before="+GSCompany.GetBankBalance(0));
   state.comparison.service=Service("legacy_baseline_coal_paid","COAL",1,TEST_CONSUMER,true);
   Log("comparison_cash","fixture","after="+GSCompany.GetBankBalance(0));
  }
  if(state.comparison.service!=null&&state.comparison.service.paid&&!state.comparison.paid){state.comparison.paid=true;Log("comparison_paid","legacy_1","calendar="+now+"|loaded_and_positive_vehicle_income=true");}
  local year=GSDate.GetYear(now);
  if(!("last_year" in state.comparison)||year!=state.comparison.last_year){
   state.comparison.last_year<-year;local alive=0;foreach(i,_ in GSIndustryList())alive++;
   Log("comparison_year","fixture","calendar="+now+"|industries="+alive+"|towns="+GSTownList().Count()+"|paid="+state.comparison.paid);
  }
  if(TEST_STAGE==0 && now>=GSDate.GetDate(1831,1,1) || TEST_STAGE==1 && now>=GSDate.GetDate(1833,1,1) || TEST_STAGE==2 && now>=GSDate.GetDate(1836,12,1) || TEST_STAGE==3 && now>=GSDate.GetDate(1840,1,1)){
   Log("comparison_checkpoint","fixture","stage="+TEST_STAGE+"|calendar="+now);
   if(TEST_STAGE==3){
    local intact=0;foreach(s in state.baseline){local managed=false;foreach(e in LEGACY_POLICY.sites)if(e.industry_id==s.id)managed=true;if(!managed&&Matches(s.id,s))intact++;}
    foreach(id,r in state.legacy)Log("comparison_final",id,"state="+r.status+"|forecast="+r.forecast+"|bonus="+r.extension);
    Log("comparison_done","fixture","calendar="+now+"|unmanaged_intact="+intact+"|towns="+GSTownList().Count()+"|paid="+state.comparison.paid);
   }
   GSGame.Pause();while(true)Sleep(365);
  }
 }
'''

def consumer():
    graph=json.loads((ROOT/'docs/research/industry_chain_graph.json').read_text())['industries']
    rows=[(abs(n['x']-2984)+abs(n['y']-1091),int(i)) for i,n in graph.items() if 'COAL' in n['accepted']]
    return min(rows)[1]

def code(served,stage):
    text=bundle();index=text.index('class LegacyLifecycleController')
    text=text[:index]+text[index:].replace(' function Start(){try{',METHODS+'\n function Start(){try{\nGSGame.Unpause();',1)
    # A quarter-monthly sample observes loaded vehicles, while lifecycle samples
    # actual last-month industry counters once per economy month.
    text=text.replace('while(true){now=Calendar();Tick(now);Sleep(74*14);}','while(true){now=Calendar();Tick(now);ComparisonHook(now);for(local sample=0;sample<104;sample++){TestSample();Sleep(10);}}')
    common=COMMON.replace('fleet=2','fleet=8').replace('::FLEET=2','::FLEET=8')
    return 'TEST_SERVED <- '+str(served).lower()+';TEST_STAGE <- '+str(stage)+';TEST_CONSUMER <- '+str(consumer())+';\n'+builder()+text.replace(METHODS,common+METHODS)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['served','control']);ap.add_argument('--resume',type=Path);a=ap.parse_args();served=a.mode=='served'
    home=a.resume or prepare('legacy-comparison-'+a.mode,code(served,0))
    compile_policy(fixture(),home/'game/lifecycle/legacy_policy.nut');compile_schedule(historical(),home/'game/lifecycle/schedule.nut')
    (home/'scripts').mkdir(exist_ok=True);(home/'scripts/game_start.scr').write_text('unpause\n')
    outcomes=[];source=source7a()
    for stage in range(4):
        cached=home/f'stage{stage}-result.json';checkpoint=home/f'checkpoint-{stage}.sav'
        if a.resume and cached.exists() and checkpoint.exists():
            result=json.loads(cached.read_text());outcomes.append(result);source=checkpoint;continue
        (home/'game/lifecycle/main.nut').write_text(code(served,stage),encoding='utf-8-sig')
        result=execute(home,150000,source=source,tag='stage'+str(stage),timeout=900)
        assert any('comparison_checkpoint|fixture|stage='+str(stage) in s for s in result['observations']),result['log']
        assert not any('FATAL|' in s for s in result['observations']),result['log']
        shutil.copyfile(home/'save/autosave/exit.sav',checkpoint);source=checkpoint;outcomes.append(result)
    report=dict(mode=a.mode,case=str(home),test_scope='FULL EUROPE ENGINE; genuine baseline mines, compressed exhaustion policy but actual calendar-year warning and monthly service',
        policy=fixture(),starting_scenario=str(source7a()),runs=outcomes)
    (BASE/('comparison-'+a.mode+'.json')).write_text(json.dumps(report,indent=2));print('COMPLETE',home)
if __name__=='__main__':main()
