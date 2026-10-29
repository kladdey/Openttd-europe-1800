"""Explicit injected-state engine boundary tests; not observed service histories."""
import json
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,prepare,execute
from lifecycle_phase7a_schedule import compile_schedule

def main():
    source=Path((BASE/'europe-slice-case.txt').read_text())/'checkpoint.sav'
    schedule=json.loads((BASE/'europe-test-schedule.json').read_text(encoding='utf8'))
    canonical=(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text()
    cases={
      'bounded_retry':'''local e=SCHEDULE.events[0],r=state.events[e.event_id];e.sites=[-1];e.open_date=now;r.status="planned";r.attempts=0;r.batches=0;r.last_attempt_month=-1;
local count=GSIndustryList().Count();for(local month=0;month<4;month++)Open(e,r,now,month);
if(r.status!="failed"||r.batches!=3||r.attempts!=0||GSIndustryList().Count()!=count)throw "Unsafe site retry budget failed";
Log("boundary_pass","bounded_retry","Injected invalid-only candidates; three batches, zero unsafe construction commands, explicit failure");''',
      'late_warning':'''local e=SCHEDULE.events[0],r=state.events[e.event_id];SCHEDULE.test_mode=false;r.status="operating";r.close_date=now-4000;r.bonus=15;r.last_observation_month=0;
Operate(e,r,now,0);if(r.status!="warned"||r.close_date<AddYears(now,e.warning_years))throw "Late load shortened warning";
Log("boundary_pass","late_warning","Injected overdue unannounced deadline; actual new warning grants full ten calendar years");''',
      'longevity':'''local e=SCHEDULE.events[0],r=state.events[e.event_id];SCHEDULE.test_mode=false;r.status="operating";r.bonus=0;r.close_date=AddYears(now,30);
local original=r.close_date,month=GSDate.GetYear(now)*12+GSDate.GetMonth(now);r.service_months=11;r.last_observation_month=-1;Operate(e,r,now,month);
if(r.bonus!=10||r.close_date!=AddYears(original,10))throw "First longevity boundary failed";
r.service_months=59;r.last_observation_month=-1;Operate(e,r,now,month);if(r.bonus!=15)throw "Second longevity boundary failed";
local capped=r.close_date;r.service_months=1000;r.last_observation_month=-1;Operate(e,r,now,month);if(r.close_date!=capped)throw "Longevity became immortal";
Log("boundary_pass","longevity","Injected prior service counts 11/59/1000; actual current transported cargo qualified; total bonus capped at 15 years");''',
      'closure_timeout':'''local e=SCHEDULE.events[0],r=state.events[e.event_id];r.status="closing";r.close_requested_economy<-GSDate.GetCurrentDate()-121;Operate(e,r,now,0);
if(r.status!="failed_closure"||!GSIndustry.IsValidIndustry(r.signature.id))throw "Blocked closure falsely reported closed";
Log("boundary_pass","closure_timeout","Injected overdue pending state; site remains alive, protected and explicitly failed");''',
      'europe_post_closed':None,
    }
    results=[]
    for name,body in cases.items():
        if name=='europe_post_closed':
            final_source=Path(json.loads((BASE/'europe-slice.json').read_text())['case'])/'save/autosave/exit.sav'
            body='''local missing=0;foreach(id,r in state.events)if(r.status=="closed" && !Matches(r.signature.id,r.signature))missing++;
local fc=0,gc=0;foreach(c,_ in GSCargoList())foreach(i,_ in GSIndustryList()){if(GSCargo.GetCargoLabel(c)=="FOOD"&&GSIndustry.IsCargoAccepted(i,c)==GSIndustry.CAS_ACCEPTED)fc++;if(GSCargo.GetCargoLabel(c)=="GOOD"&&GSIndustry.IsCargoAccepted(i,c)==GSIndustry.CAS_ACCEPTED)gc++;}
Log("boundary_pass","europe_post_closed","industries="+GSIndustryList().Count()+"|towns="+GSTownList().Count()+"|closed_instances_absent="+missing+"|FOOD="+fc+"|GOOD="+gc);
if(missing!=4||GSIndustryList().Count()!=542||fc!=76||gc!=69)throw "Europe post-closure state mismatch";'''
        else:final_source=source
        text=canonical.replace('Initialize(now);','Initialize(now);'+body+'\nGSGame.Pause();while(true)Sleep(365);')
        home=prepare('boundary-'+name,text);compile_schedule(schedule,home/'game/lifecycle/schedule.nut');r=execute(home,3500,source=final_source)
        assert any('EVENT|boundary_pass|'+name+'|' in s for s in r['observations']),name
        results.append(dict(name=name,scope='FULL EUROPE ENGINE: injected state boundary' if name!='europe_post_closed' else 'FULL EUROPE ENGINE: physical closure and market persistence',result=r))
    for name,replacement,expected in [
      ('lost_ledger','function Load(version,data){loaded=null;}','Missing lifecycle ledger after schedule start'),
      ('unknown_schema','function Load(version,data){loaded=data;loaded.schema=99;}','Unsupported saved lifecycle schema')]:
        text=canonical.replace('function Load(version,data){loaded=data;}',replacement)
        home=prepare('boundary-'+name,text);compile_schedule(schedule,home/'game/lifecycle/schedule.nut');r=execute(home,3500,source=source)
        assert any('P7 FATAL|'+expected in s for s in r['observations'])
        assert not any('EVENT|opened|' in s for s in r['observations'])
        results.append(dict(name=name,scope='FULL EUROPE ENGINE: intentional failure injection, expected rejection',result=r))
        if name=='unknown_schema':
            saved=home/'save/autosave/exit.sav';checkpoint=home/'unknown.sav';__import__('shutil').copyfile(saved,checkpoint)
            probe='''class LifecycleController extends GSController {data=null;function Load(v,d){data=d;}function Save(){return data;}function Start(){GSLog.Info("P7 UNKNOWN_SCHEMA_PRESERVED|schema="+data.schema+"|events="+data.events.len());GSGame.Pause();while(true)Sleep(365);}}'''
            (home/'game/lifecycle/main.nut').write_text(probe,encoding='utf-8-sig');post=execute(home,2000,source=checkpoint,tag='preserved-payload')
            assert any('UNKNOWN_SCHEMA_PRESERVED|schema=99|events=4' in s for s in post['observations'])
            results.append(dict(name='unknown_payload_preserved',scope='FULL EUROPE ENGINE: supported Save preserves rejected schema',result=post))
    (BASE/'boundary-tests.json').write_text(json.dumps(results,indent=2))

if __name__=='__main__':main()
