"""Actual-engine corrupt-state, stale command and instance-reuse tests."""
import json,shutil
from pathlib import Path
from lifecycle_phase7b_runtime import ROOT,BASE,prepare,execute,bundle,source7a
from lifecycle_phase7b_policy import fixture,compile_policy
from lifecycle_phase7a_schedule import historical,compile_schedule

def configure(home,policy=None):
    compile_policy(policy or fixture(),home/'game/lifecycle/legacy_policy.nut');compile_schedule(historical(),home/'game/lifecycle/schedule.nut')

def main():
    comparisons=json.loads((BASE/'comparison-control.json').read_text());case=Path(comparisons['case']);source=case/'checkpoint-1.sav';results=[]
    # Deliberate errors are separate labelled engine rejection cases.
    for name,patch,expected in [
      ('missing_state','loaded=null;','Legacy enrollment requires intact original 1830 baseline'),
      ('partial_state','delete loaded.legacy.legacy_1.status;','Partial legacy row'),
      ('missing_site','delete loaded.legacy.legacy_1;','Partial legacy enrollment'),
      ('wrong_contract','loaded.policy_contract=0;','Legacy policy contract mismatch'),
      ('wrong_identity','loaded.legacy.legacy_1.signature.born=1;','Legacy saved identity mismatch'),
      ('early_deadline','loaded.legacy.legacy_1.forecast=1;','Legacy forecast outside authorized window'),
      ('unknown_state','loaded.legacy.legacy_1.status="garbled";','Unknown legacy state'),
      ('scheduled_alias','loaded.events.gb_south_hetton_1833.signature={id=0,type=0,tile=5045247,born=668394};','Scheduled instance fingerprint outside event')]:
        text=bundle().replace('function Load(version,data){loaded=data;}','function Load(version,data){loaded=data;'+patch+'}')
        home=prepare('safety-'+name,text);configure(home,comparisons['policy']);r=execute(home,1700,source=source,fail_on_fatal=False)
        assert any('P7 FATAL|'+expected in s for s in r['observations']),(name,r['log'])
        assert not any('legacy_authorization|' in s or 'legacy_closed|' in s for s in r['observations'])
        results.append(dict(name=name,scope='FULL EUROPE ENGINE: injected corrupt/missing state; expected safe rejection',result=r))
    (BASE/'safety-results.json').write_text(json.dumps(results,indent=2))
    # Reuse real closed baseline ID and its old tile through ordinary construction.
    reuse='''
local s=LEGACY_POLICY.sites[0],r=state.legacy[s.site_id];if(GSIndustry.IsValidIndustry(s.industry_id))throw "Old mine not physically closed";
local count=GSIndustryList().Count(),type=Type(0),before_ids={};foreach(i,_ in GSIndustryList())before_ids[i]<-true;
local exact=GSIndustryType.BuildIndustry(type,s.tile);local exact_error=exact?"NONE":GSError.GetLastErrorString();
if(!exact){
 local e=clone SCHEDULE.events[0];e.event_id="test_legacy_regional_replacement";e.name="TEST replacement regional coal working";e.region="GB";e.open_date=now;e.sites=REUSE_CANDIDATES;
 local rr={status="planned",signature=null,attempts=0,batches=0,last_attempt_month=-1,close_date=-1};
 local scheduler_open=LifecycleController.Open.bindenv(this);scheduler_open(e,rr,now,GSDate.GetYear(now)*12+GSDate.GetMonth(now));
 if(rr.status!="operating")throw "No legal same-region replacement site";
 state.test_replacement<-{event=e,row=rr};
}
local replacement=-1;foreach(i,_ in GSIndustryList())if(!(i in before_ids))replacement=i;if(!GSIndustry.IsValidIndustry(replacement))throw "No replacement identity";
// Deliberately restore an old pending ledger row. No native closure command is allowed.
local original_forecast=r.forecast;r.status="warning";r.warn_date=now-5000;r.forecast=now;local before=GSIndustry.GetProductionLevel(replacement);LegacyTick(s,r,now);r.forecast=original_forecast;
if(r.status!="lost"||GSIndustry.GetProductionLevel(replacement)!=before)throw "Stale ledger commanded replacement";
// Even an adversarial native level-4 request at the old tile must be rejected by
// the independent GRF original-instance fingerprint, not just the ledger.
if(exact)GSIndustry.SetProductionLevel(replacement,4,false,null);local date=GSDate.GetCurrentDate();GSGame.Unpause();while(GSDate.GetCurrentDate()-date<100)Sleep(20);
if(!GSIndustry.IsValidIndustry(replacement))throw "Reused-tile replacement closed through stale identity";
Log("safety_pass","reused_instance","old_id="+s.industry_id+"|new_id="+replacement+"|old_tile="+s.tile+"|new_tile="+GSIndustry.GetLocation(replacement)+"|new_born="+GSIndustry.GetConstructionDate(replacement)+"|exists=true|stale_ledger_rejected=true|replacement_via_scheduler="+(!exact)+"|exact_tile="+exact+"|exact_tile_error="+exact_error);
GSGame.Pause();while(true)Sleep(365);
'''
    from lifecycle_phase7a_schedule import squirrel
    stored=json.loads((ROOT/'docs/research/phase7a_europe_test_schedule.json').read_text());tiles=stored['events'][0]['sites']+stored['events'][-1]['sites']
    home=prepare('safety-reused-instance','REUSE_CANDIDATES <- '+squirrel(tiles)+';\n'+bundle().replace('Initialize(now);','Initialize(now);'+reuse));configure(home,comparisons['policy'])
    (home/'scripts').mkdir();(home/'scripts/game_start.scr').write_text('unpause\n')
    r=execute(home,15000,source=case/'checkpoint-3.sav');assert any('safety_pass|reused_instance|' in s for s in r['observations'])
    results.append(dict(name='reused_instance',scope='FULL EUROPE ENGINE: actual construction at a deleted legacy mine tile; stale ledger and native command rejected',result=r))
    (BASE/'safety-results.json').write_text(json.dumps(results,indent=2))

if __name__=='__main__':main()
