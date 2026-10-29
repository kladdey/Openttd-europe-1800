"""Use the GUI-created scenario without editing any scenario/save bytes."""
import argparse,json,shutil
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,SOURCE,prepare,execute,sha,guards
from lifecycle_phase7a_schedule import historical,compile_schedule
from coastal_phase6_preservation import parts,maps
from historical_scenario_migration import inspect

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
    editor=json.loads((BASE/'europe-editor.json').read_text());candidate=Path(editor['candidate'])
    before,after=parts(SOURCE),parts(candidate)
    for tag in ['CITY','INDY','PATS','PSAC']:assert before[tag]==after[tag],tag
    assert maps(before)==maps(after)
    old=inspect(SOURCE)['newgrfs'];new=inspect(candidate)['newgrfs']
    assert len(old)==len(new)==15
    for o,n in zip(old,new):
        if o['grfid']=='4B484531':assert n['version']==4 and n['params'][:11]==o['params'] and n['params'][11]==1
        else:assert o==n
    text=(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text()
    observe='''
  GSLog.Info("P7 EUROPE_START|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|types="+GSIndustryTypeList().Count()+"|cargos="+GSCargoList().Count()+"|grfs="+GSNewGRFList().Count()+"|calendar="+now+"|economy="+GSDate.GetCurrentDate());
  foreach(i,_ in GSIndustryList())GSLog.Info("P7 BASELINE_INDUSTRY|"+i+"|"+GSIndustry.GetIndustryType(i)+"|"+GSIndustry.GetLocation(i)+"|"+GSIndustry.GetConstructionDate(i));
  local food=-1,goods=-1;foreach(c,_ in GSCargoList()){if(GSCargo.GetCargoLabel(c)=="FOOD")food=c;if(GSCargo.GetCargoLabel(c)=="GOOD")goods=c;}
  local fc=0,gc=0;foreach(i,_ in GSIndustryList()){if(GSIndustry.IsCargoAccepted(i,food)==GSIndustry.CAS_ACCEPTED)fc++;if(GSIndustry.IsCargoAccepted(i,goods)==GSIndustry.CAS_ACCEPTED)gc++;}
  GSLog.Info("P7 MARKET_ACCEPTANCE|FOOD="+fc+"|GOOD="+gc);
'''
    if a.smoke:
        text=text.replace('Initialize(now);','Initialize(now);'+observe+'GSGame.Pause();Log("smoke_done","europe","preserved baseline");while(true)Sleep(365);')
    home=prepare('europe-smoke' if a.smoke else 'europe-test',text)
    compile_schedule(historical(),home/'game/lifecycle/schedule.nut')
    result=execute(home,3500,source=candidate)
    assert any('EUROPE_START|towns=617|industries=542|types=96|cargos=64|grfs=15' in s for s in result['observations'])
    assert any('MARKET_ACCEPTANCE|FOOD=76|GOOD=69' in s for s in result['observations'])
    assert not any('FATAL|' in s for s in result['observations'])
    saved=home/'save/autosave/exit.sav';saved_parts=parts(saved)
    assert after['INDY']==saved_parts['INDY'] and after['CITY']==saved_parts['CITY'] and maps(after)==maps(saved_parts)
    report=dict(candidate=str(candidate),candidate_sha256=sha(candidate),all_617_towns_542_industries_and_map_identical_at_start=True,settings_identical=True,other_14_newgrfs_identical=True,grf_reference=new,result=result,actual_gameplay_save=str(saved),actual_gameplay_save_sha256=sha(saved))
    (BASE/'europe-smoke.json').write_text(json.dumps(report,indent=2));guards()

if __name__=='__main__':main()
