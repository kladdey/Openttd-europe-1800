"""Focused real-engine negative tests, migration, registration and natural control."""
import json,shutil
from pathlib import Path
from lifecycle_phase7c_runtime import *
from lifecycle_phase7c_policy import setup,production
from lifecycle_phase7a_soak import CONTROL
def run(name,text,source=SOURCE,p=None,expected=None,**kw):
    h=prepare(name,text);setup(h,p);r=execute(h,kw.pop('ticks',2000),source=source,fail_on_fatal=expected is None,**kw)
    if expected:assert any(expected in x for x in r['observations']),r['log']
    return r
def main():
    results=[]
    observer=bundle().replace('Initialize(Calendar());while(true)','Initialize(Calendar());Log("c_roundtrip","fixture","events="+state.expansion.len()+"|old_mines="+state.legacy.len()+"|industries="+GSIndustryList().Count()+"|towns="+GSTownList().Count()+"|cargos="+GSCargoList().Count()+"|types="+GSIndustryTypeList().Count()+"|calendar="+Calendar()+"|economy="+GSDate.GetCurrentDate());GSGame.Pause();while(true)')
    r=run('normal-start',observer);results.append(r);h=Path(r['case']);save=h/'initial.sav';shutil.copyfile(h/'save/autosave/exit.sav',save);results.append(execute(h,2000,source=save,tag='reload'))
    # Existing live v2 games are not silently enrolled or reset.
    old=Path(json.loads((b.BASE/'validation-roundtrip.json').read_text())['runs'][0]['case'])/'normal-start.sav'
    results.append(run('v2-migration-refused',bundle(),old,expected='Explicit adopt_only required'))
    p=production();p['migration']='adopt_only'
    r=run('v2-adopt-only',observer,old,p,expected='expansion_adopted|scheduler|events=0|new_enrollment=0');results.append(r)
    h=Path(r['case']);save=h/'adopted.sav';shutil.copyfile(h/'save/autosave/exit.sav',save);results.append(execute(h,2000,source=save,tag='adopted-reload'))
    # A changed contract or incomplete ledger is rejected before new commands.
    p=production();p['events'][0]['max_batches']-=1
    results.append(run('contract-refused',bundle(),Path(results[0]['case'])/'initial.sav',p,expected='Expansion policy contract mismatch'))
    for field in ['expansion','factory']:
        code=bundle().replace('loaded=clone incoming;loaded.schema=2;',f'loaded=clone incoming;delete loaded.{field};loaded.schema=2;')
        results.append(run('partial-'+field,code,Path(results[0]['case'])/'initial.sav',expected='Partial expansion ledger'))
    # An unloaded controller must not make the allowlisted mill close by itself.
    text='YEARS <- 5;\n'+CONTROL.replace('class LifecycleController','class ExpansionLifecycleController')
    h=prepare('natural-five-year',text,density=4);r=execute(h,150000);assert any('NATURAL_DONE|new=0|' in x for x in r['observations']);results.append(r)
    # Actual registration and historical availability. This is not production proof.
    text='''class ExpansionLifecycleController extends GSController {function Start(){
GSLog.Info("P7 C_REG|version="+GSNewGRF.GetVersion(0x4B484531)+"|types="+GSIndustryTypeList().Count()+"|cargos="+GSCargoList().Count());
foreach(local_id in [34,2,103,9,80,24,25,23,18]){local t=GSIndustryType.ResolveNewGRFID(0x4B484531,local_id);GSLog.Info("P7 C_TYPE|local="+local_id+"|runtime="+t+"|available="+GSIndustryType.CanBuildIndustry(t));}
GSGame.Pause();while(true)Sleep(365);}}'''
    results.append(run('registration',text))
    (BASE/'controls.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
