"""Blocked/dependency/date controls, one-shot native safety, replay and server."""
import argparse,copy,json,shutil
from pathlib import Path
from lifecycle_phase7c_runtime import *
from lifecycle_phase7c_policy import production,setup,absolute_date
from lifecycle_phase7b_policy import production as bp
from lifecycle_phase7c_waves import parked,code
def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['blocked','replay','native','dedicated','assets','off']);a=ap.parse_args();results=[]
    if a.case=='off':
        h=prepare('default-off-gate',bundle(),policy=False);setup(h)
        r=execute(h,1800,fail_on_fatal=False)
        assert any('P7 FATAL|Lifecycle opt-in disabled' in line for line in r['observations'])
        assert not any('expansion_opened|' in line or 'processor_enrolled|' in line for line in r['observations']);results.append(r)
    elif a.case=='blocked':
        for mode in ['no_safe_site','occupied_with_alternative','unavailable','missing_chain']:
            p=production();p.update(id='phase7c-negative-'+mode,test_mode=True,retirement=None);p['events']=p['events'][:1];e=p['events'][0]
            e.update(open_date=absolute_date('1831-01-01'),announce_date=absolute_date('1830-01-01'),latest_date=absolute_date('1831-12-31'),sites=[257],dependencies=[],required_producers=[],required_consumers=[],max_batches=2)
            seed=''
            if mode=='occupied_with_alternative':
                e['sites']=[55*256+55,60*256+75];seed='if(loaded==null&&!GSIndustryType.BuildIndustry(Type(26),GSMap.GetTileIndex(55,55)))throw "Fixture farm blocked";'
            elif mode=='unavailable':e.update(local_id=2,sites=[70*256+70])
            elif mode=='missing_chain':e.update(sites=[70*256+70],required_producers=['GRAI'])
            legacy=bp();legacy.update(enroll_legacy=False,sites=[])
            s=code(1832).replace('GSGame.Unpause();Initialize(Calendar());','GSGame.Unpause();'+seed+'Initialize(Calendar());')
            h=prepare('negative-'+mode,s);setup(h,p,legacy,parked());r=execute(h,65000);results.append(r)
            expected='built' if mode=='occupied_with_alternative' else 'cancelled'
            assert any('c_wave_final|galicia_mill|state='+expected in line for line in r['observations']),r['log']
    elif a.case=='native':
        for mode in ['bare','expired','mine']:
            target,arm=(1,5) if mode=='mine' else (275,11)
            command='GSIndustry.SetProductionLevel(TARGET,ARM,false,null);' if mode!='bare' else ''
            delay=150 if mode=='expired' else 45
            s='''class ExpansionLifecycleController extends GSController {function Start(){GSGame.Unpause();
local count=GSIndustryList().Count();GSIndustry.SetControlFlags(TARGET,GSIndustry.GetControlFlags(TARGET)|GSIndustry.INDCTL_NO_CLOSURE);COMMAND
local started=GSDate.GetCurrentDate();while(GSDate.GetCurrentDate()-started<DELAY)Sleep(20);
GSIndustry.SetControlFlags(TARGET,GSIndustry.GetControlFlags(TARGET)&~GSIndustry.INDCTL_NO_CLOSURE);GSIndustry.SetProductionLevel(TARGET,4,false,null);
GSIndustry.SetProductionLevel(276,4,false,null);
while(GSDate.GetCurrentDate()-started<DELAY+150)Sleep(20);
GSLog.Info("P7 C_NATIVE|MODE|target_exists="+GSIndustry.IsValidIndustry(TARGET)+"|non_target_exists="+GSIndustry.IsValidIndustry(276)+"|count="+GSIndustryList().Count());
if(!GSIndustry.IsValidIndustry(276))throw "Non-target closure";
GSGame.Pause();while(true)Sleep(365);}}'''.replace('COMMAND',command).replace('TARGET',str(target)).replace('ARM',str(arm)).replace('DELAY',str(delay)).replace('MODE',mode)
            h=prepare('native-'+mode,s);(h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n');r=execute(h,32000,source=SOURCE,timeout=600)
            assert any('C_NATIVE|'+mode+'|target_exists='+('false' if mode=='mine' else 'true') in line for line in r['observations']);results.append(r)
    elif a.case=='replay':
        from lifecycle_phase7c_validate import code as compare_code
        m=json.loads((BASE/'europe.json').read_text());source=Path(m['case'])/'checkpoint-2.sav'
        h=prepare('Europe-checkpoint-replay',compare_code(1838));setup(h,m['policy']);(h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
        r=execute(h,180000,source=source,timeout=900);results.append(r)
        key=lambda run:[s.split('P7 EVENT|')[1] for s in run['observations'] if any(x in s for x in ['EVENT|processor_arm|','EVENT|processor_commit|','EVENT|processor_closed|','EVENT|c_checkpoint|','EVENT|expansion_opened|'])]
        assert key(r)==key(m['runs'][3]),'Checkpoint replay diverged'
        # Reload a terminal ledger without a second closure or opening.
        closed=h/'closed.sav';shutil.copyfile(h/'save/autosave/exit.sav',closed)
        observer=bundle().replace('Initialize(Calendar());while(true)','Initialize(Calendar());Log("c_post_closed","fixture",state.factory.status);GSGame.Pause();while(true)')
        (h/'game/lifecycle/main.nut').write_text(observer,encoding='utf-8-sig');results.append(execute(h,2000,source=closed,tag='post-closed-reload'))
    elif a.case=='assets':
        m=json.loads((BASE/'europe.json').read_text());snapshots=[]
        s=bundle().replace('Initialize(Calendar());while(true)','''Initialize(Calendar());{local cm=GSCompanyMode(0);
foreach(v,_ in GSVehicleList())GSLog.Info("P7 C_ASSET_VEHICLE|"+v+"|"+GSVehicle.GetEngineType(v));
foreach(st,_ in GSStationList(GSStation.STATION_ANY))GSLog.Info("P7 C_ASSET_STATION|"+st+"|"+GSStation.GetLocation(st));
}GSGame.Pause();while(true)''')
        for stage in [2,3]:
            h=prepare('closure-assets-'+str(stage),s);setup(h,m['policy']);r=execute(h,2000,source=Path(m['case'])/f'checkpoint-{stage}.sav');results.append(r)
            snapshots.append([line.split('P7 ')[1] for line in r['observations'] if 'P7 C_ASSET_' in line])
        assert snapshots[0] and snapshots[0]==snapshots[1],'Player vehicle/station identities changed across closure'
    else:
        m=json.loads((BASE/'europe.json').read_text());source=Path(m['case'])/'checkpoint-1.sav'
        s=bundle().replace('Initialize(Calendar());while(true)','Initialize(Calendar());GSLog.Info("P7 DEDICATED_SMOKE_DONE|multiplayer="+GSGame.IsMultiplayer()+"|factory="+state.factory.status+"|expansions="+state.expansion.len());GSGame.Pause();while(true)')
        h=prepare('dedicated-v3-restore',s);setup(h,m['policy']);cfg=h/'test.cfg';cfg.write_text(cfg.read_text()+'\n[network]\nserver_game_type = local\nserver_advertise = false\nmin_active_clients = 0\n')
        r=execute(h,source=source,dedicated=True);assert not r['dedicated_forced_stop'];assert any('DEDICATED_SMOKE_DONE|multiplayer=true' in x for x in r['observations']);results.append(r)
    (BASE/('safety-'+a.case+'.json')).write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
