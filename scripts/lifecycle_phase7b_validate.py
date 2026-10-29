"""Focused real-engine regression, policy gates, migration and dedicated checks."""
import argparse,json,shutil
from pathlib import Path
from lifecycle_phase7b_runtime import ROOT,BASE,prepare,execute,bundle,source7a,sha
from lifecycle_phase7b_policy import production,compile_policy
from lifecycle_phase7a_schedule import historical,fixture,compile_schedule
from lifecycle_phase7a_soak import CONTROL

def candidate():return Path(json.loads((BASE/'candidate-delivery.json').read_text())['candidate'])
def setup(home,p=None,s=None):
    compile_policy(p or production(),home/'game/lifecycle/legacy_policy.nut');compile_schedule(s or historical(),home/'game/lifecycle/schedule.nut')
def run_case(name,text,source=None,p=None,ticks=2500,expected=None,**kwargs):
    home=prepare(name,text);setup(home,p);r=execute(home,ticks,source=source or candidate(),fail_on_fatal=expected is None,**kwargs)
    if expected:assert any(expected in line for line in r['observations']),(name,r['log'])
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['roundtrip','controls','soak','migration','dedicated','replay']);a=ap.parse_args();results=[]
    if a.case=='roundtrip':
        text=bundle().replace('Initialize(now);','Initialize(now);Log("roundtrip_pass","production","sites="+state.legacy.len()+"|calendar="+now+"|economy="+GSDate.GetCurrentDate()+"|types="+GSIndustryTypeList().Count()+"|cargos="+GSCargoList().Count());GSGame.Pause();while(true)Sleep(365);')
        r=run_case('normal-production-start',text,expected='roundtrip_pass|production|sites=4|calendar=668394|economy=657437');results.append(r)
        home=Path(r['case']);save=home/'normal-start.sav';shutil.copyfile(home/'save/autosave/exit.sav',save)
        results.append(execute(home,2500,source=save,tag='reloaded'))
        from coastal_phase6_preservation import parts,maps
        before=parts(candidate())
        for path in [save,home/'save/autosave/exit.sav']:
            after=parts(path)
            for tag in ['CITY','INDY','PATS','PSAC']:assert before[tag]==after[tag],tag
            assert maps(before)==maps(after)
    elif a.case=='migration':
        manifest=json.loads((ROOT/'docs/research/phase7a_candidate_delivery.json').read_text());old=Path(manifest['actual_production_script_gameplay_save_reload'][0]['case'])/'production-start.sav'
        results.append(run_case('migration-rejected',bundle(),source=old,expected='P7 FATAL|Phase 7A migration requires explicit adopt_only'))
        p=production();p.update(migration='adopt_only',enroll_legacy=False,sites=[])
        text=bundle().replace('Initialize(now);','Initialize(now);Log("migration_verified","scheduler","events="+state.events.len()+"|legacy="+state.legacy.len());GSGame.Pause();while(true)Sleep(365);')
        r=run_case('migration-adopt-only',text,source=old,p=p,expected='legacy_migrated|scheduler|schema=1->2|enrolled=0');results.append(r)
        home=Path(r['case']);save=home/'migrated.sav';shutil.copyfile(home/'save/autosave/exit.sav',save);results.append(execute(home,2500,source=save,tag='migrated-reloaded'))
    elif a.case=='controls':
        # Explicitly disabled embedded parameter; no normal configuration changes.
        off=Path(json.loads((BASE/'editor.json').read_text())['case'])/'scenario/o.scn';assert off.exists()
        results.append(run_case('parameter-off-controller',bundle(),source=off,expected='P7 FATAL|Lifecycle disabled'))
        p=production();p.update(enroll_legacy=False,sites=[])
        text=bundle().replace('Initialize(now);','Initialize(now);Log("no_enrollment","scheduler","sites="+state.legacy.len());GSGame.Pause();while(true)Sleep(365);')
        results.append(run_case('no-registered-sites',text,p=p,expected='no_enrollment|scheduler|sites=0'))
        wrong=prepare('wrong-grf-version',bundle(),v5=False);setup(wrong)
        shutil.copyfile(ROOT/'gamescripts/historical_industry_lifecycle/legacy_info.nut',wrong/'game/lifecycle/info.nut')
        r=execute(wrong,1800,source=source7a(),fail_on_fatal=False);assert any('P7 FATAL|Legacy controller requires separate AXIS 0.5' in line for line in r['observations']);results.append(r)
        # Direct native requests: no lifecycle controller. OFF and expired nonce
        # must keep original industry 1 and unregistered same-type 0 alive.
        for mode,source,expiry in [('off',off,45),('expired',candidate(),150)]:
            text='''class LegacyLifecycleController extends GSController {function Start(){
GSGame.Unpause();GSIndustry.SetControlFlags(1,GSIndustry.GetControlFlags(1)|GSIndustry.INDCTL_NO_CLOSURE);GSIndustry.SetProductionLevel(1,5,false,null);GSIndustry.SetProductionLevel(379,4,false,null);
local started=GSDate.GetCurrentDate();while(GSDate.GetCurrentDate()-started<EXPIRE)Sleep(20);
GSIndustry.SetControlFlags(1,GSIndustry.GetControlFlags(1)&~GSIndustry.INDCTL_NO_CLOSURE);GSIndustry.SetProductionLevel(1,4,false,null);
while(GSDate.GetCurrentDate()-started<EXPIRE+120)Sleep(20);
if(!GSIndustry.IsValidIndustry(1)||!GSIndustry.IsValidIndustry(0)||!GSIndustry.IsValidIndustry(379)||GSIndustryList().Count()!=542)throw "Unsafe closure";
GSLog.Info("P7 SAFETY_NATIVE|MODE|selected_exists=true|unregistered_exists=true|different_type_exists=true|count=542");GSGame.Pause();while(true)Sleep(365);}}
'''.replace('EXPIRE',str(expiry)).replace('MODE',mode)
            home=prepare('native-'+mode,text);(home/'scripts').mkdir();(home/'scripts/game_start.scr').write_text('unpause\n')
            r=execute(home,22000,source=source);assert any('SAFETY_NATIVE|'+mode in s for s in r['observations']);results.append(r)
        home=prepare('missing-gamescript','// Deliberately no registered script');assert (home/'game/lifecycle/info.nut').resolve().is_relative_to(BASE.resolve())
        (home/'game/lifecycle/info.nut').rename(home/'game/lifecycle/info.disabled')
        (home/'scripts').mkdir();(home/'scripts/game_start.scr').write_text('unpause\n')
        r=execute(home,12000,source=candidate());results.append(r)
        from lifecycle_phase7b_inventory import records
        # Save decoding is inspection only: no compressed-byte writes.
        from coastal_phase6_preservation import parts
        assert len(parts(home/'save/autosave/exit.sav')['INDY'][1])-1==542
        # A five-year nonzero-density control independently challenges spawning.
        home=prepare('natural-five-year','YEARS <- 5;\n'+CONTROL.replace('class LifecycleController','class LegacyLifecycleController'),density=4)
        r=execute(home,150000);assert any('NATURAL_DONE|new=0|' in s for s in r['observations']);results.append(r)
    elif a.case=='soak':
        p=production();p.update(enroll_legacy=False,sites=[])
        s=fixture();s['id']='phase7b-scheduled-regression-31-year'
        text=bundle();needle='local now=Calendar();Initialize(now);'
        text=text.replace(needle,'local now=Calendar();if(loaded==null && !GSIndustryType.BuildIndustry(Type(0),GSMap.GetTileIndex(25,35)))throw "Fixture baseline producer failed";Initialize(now);')
        text=text.replace('Tick(now);Sleep(74*14);','Tick(now);if(GSDate.GetYear(now)>=1861){Log("regression_done","fixture","calendar="+now+"|industries="+GSIndustryList().Count());GSGame.Pause();while(true)Sleep(365);}\nSleep(74*14);')
        home=prepare('scheduled-31year-regression',text);setup(home,p,s);cfg=home/'test.cfg';cfg.write_text(cfg.read_text().replace('custom_town_number = 3','custom_town_number = 12'))
        r=execute(home,870000);assert any('regression_done|' in line for line in r['observations'])
        for e in s['events']:
            assert sum('EVENT|opened|'+e['event_id']+'|' in line for line in r['observations'])==1
            assert sum('EVENT|closed|'+e['event_id']+'|' in line for line in r['observations'])==1
        results.append(r)
    elif a.case=='dedicated':
        comp=json.loads((BASE/'comparison-served.json').read_text());source=Path(comp['case'])/'checkpoint-1.sav'
        text=bundle().replace('Initialize(now);','Initialize(now);GSLog.Info("P7 DEDICATED|multiplayer="+GSGame.IsMultiplayer());LegacyNews(LEGACY_POLICY.sites[0],"Dedicated-server restored deadline year "+GSDate.GetYear(state.legacy.legacy_1.forecast));GSLog.Info("P7 DEDICATED_SMOKE_DONE|legacy="+state.legacy.len());GSGame.Pause();while(true)Sleep(365);')
        home=prepare('dedicated-legacy-restoration',text);setup(home,comp['policy']);cfg=home/'test.cfg';cfg.write_text(cfg.read_text()+'\n[network]\nserver_game_type = local\nserver_advertise = false\nmin_active_clients = 0\n')
        r=execute(home,source=source,dedicated=True);assert any('DEDICATED|multiplayer=true' in s for s in r['observations']);assert not r['dedicated_forced_stop'];assert any('EVENT|news|legacy_1|ok=true' in s for s in r['observations']);results.append(r)
    elif a.case=='replay':
        from lifecycle_phase7b_compare import code
        comp=json.loads((BASE/'comparison-control.json').read_text());source=Path(comp['case'])/'checkpoint-2.sav'
        home=prepare('checkpoint-replay',code(False,3));setup(home,comp['policy']);(home/'scripts').mkdir();(home/'scripts/game_start.scr').write_text('unpause\n')
        r=execute(home,150000,source=source,timeout=900);results.append(r)
        significant=lambda run:[line.split('P7 EVENT|',1)[1] for line in run['observations'] if any('EVENT|'+kind+'|' in line for kind in ['legacy_authorization','legacy_closed','comparison_final','opened','closed'])]
        assert significant(r)==significant(comp['runs'][3]),'Checkpoint replay changed significant transitions'
        post=home/'post-closed.sav';shutil.copyfile(home/'save/autosave/exit.sav',post)
        observer=bundle().replace('Initialize(now);','Initialize(now);Log("post_closed","scheduler","industries="+GSIndustryList().Count()+"|legacy="+state.legacy.len());GSGame.Pause();while(true)Sleep(365);')
        (home/'game/lifecycle/main.nut').write_text(observer,encoding='utf-8-sig');results.append(execute(home,2000,source=post,tag='post-closure-reload'))
    (BASE/('validation-'+a.case+'.json')).write_text(json.dumps(dict(scope=a.case,runs=results),indent=2))
if __name__=='__main__':main()
