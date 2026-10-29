"""Bounded genuine calendar progression and natural-opening controls."""
import argparse,json
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,prepare,execute
from lifecycle_phase7a_schedule import historical,compile_schedule,fixture

CONTROL='''class LifecycleController extends GSController {
 function Start(){local seen={},new_count=0,started=GSDate.GetCurrentDate(),end=GSDate.GetYear(started)+YEARS,year=-1;
 foreach(i,_ in GSIndustryList())seen[i+"_"+GSIndustry.GetConstructionDate(i)+"_"+GSIndustry.GetLocation(i)]<-true;
 GSLog.Info("P7 NATURAL_BASELINE|"+seen.len()+"|deity_available="+GSIndustryType.CanBuildIndustry(GSIndustryType.ResolveNewGRFID(0x4B484531,0)));
 while(GSDate.GetYear(GSDate.GetCurrentDate())<end){
  foreach(i,_ in GSIndustryList()){local key=i+"_"+GSIndustry.GetConstructionDate(i)+"_"+GSIndustry.GetLocation(i);if(!(key in seen)){seen[key]<-true;new_count++;GSLog.Info("P7 UNEXPECTED_NEW|"+key);}}
  if(year!=GSDate.GetYear(GSDate.GetCurrentDate())){year=GSDate.GetYear(GSDate.GetCurrentDate());GSLog.Info("P7 NATURAL_YEAR|"+year+"|new="+new_count+"|industries="+GSIndustryList().Count());}
  Sleep(74*14);
 }
 GSLog.Info("P7 NATURAL_DONE|new="+new_count+"|days="+(GSDate.GetCurrentDate()-started));GSGame.Pause();while(true)Sleep(365);}}
'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['natural','historical']);a=ap.parse_args()
    if a.case=='natural':
        results=[]
        for old in [True,False]:
            home=prepare('natural-03' if old else 'natural-04', 'YEARS <- 5;\n'+CONTROL,policy=not old,old=old,density=4)
            result=execute(home,150000);assert any('NATURAL_DONE|new=0|' in s for s in result['observations']);results.append(result)
        (BASE/'natural-controls.json').write_text(json.dumps(results,indent=2))
    else:
        text=(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text()
        text=text.replace('Tick(now);Sleep(74*14);','Tick(now);if(GSDate.GetYear(now)>=1861){Log("soak_done","historical","calendar="+now);GSGame.Pause();while(true)Sleep(365);};Sleep(74*14);')
        home=prepare('historical-31-years',text)
        config=home/'test.cfg';config.write_text(config.read_text().replace('custom_town_number = 3','custom_town_number = 12'))
        schedule=historical();mini=fixture()
        for e,m in zip(schedule['events'],mini['events']):e['sites']=m['sites']
        compile_schedule(schedule,home/'game/lifecycle/schedule.nut')
        result=execute(home,870000)
        assert any('soak_done|' in s for s in result['observations'])
        for e in schedule['events']:assert sum('EVENT|opened|'+e['event_id']+'|' in s for s in result['observations'])==1,e['event_id']
        assert not any('EVENT|closed|' in s for s in result['observations'])
        (BASE/'historical-soak.json').write_text(json.dumps(result,indent=2))

if __name__=='__main__':main()
