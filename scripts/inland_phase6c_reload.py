"""Actual paused gameplay reload checks, plus opening engine availability."""
import json,re,time
from pathlib import Path
from inland_phase6c_runtime import ROOT,BASE,run,sha
from coastal_phase6_preservation import parts,maps


def main():
    state=json.loads((BASE/'candidate.json').read_text());source=Path(state['candidate']);initial=parts(source)
    script='''class CoastalProbe extends GSController {function Start(){while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSLog.Info("M6 RELOAD|"+GSTownList().Count()+"|"+GSIndustryList().Count()+"|"+GSIndustryTypeList().Count()+"|"+GSCargoList().Count()+"|"+GSNewGRFList().Count()+"|"+GSNewGRF.GetVersion(0x4B484531));
foreach(g,_ in GSNewGRFList())GSLog.Info("M6 GRF|"+g+"|"+GSNewGRF.GetVersion(g)+"|"+GSNewGRF.GetName(g));
foreach(name in ["construction.raw_industry_construction","construction.industry_platform","vehicle.max_train_length","economy.infrastructure_maintenance","economy.timekeeping_units","economy.inflation","economy.industry_daily_change","difficulty.max_loan","difficulty.vehicle_breakdowns","economy.town_growth_rate"]){if(GSGameSettings.IsValid(name))GSLog.Info("M6 SETTING|"+name+"|"+GSGameSettings.GetValue(name));}
foreach(t,_ in GSTownList())GSLog.Info("M6 TOWN|"+t+"|"+GSTown.GetName(t)+"|"+GSTown.GetLocation(t)+"|"+GSTown.GetPopulation(t)+"|"+GSTown.GetHouseCount(t));
{local cm=GSCompanyMode(0);foreach(e,_ in GSEngineList(GSVehicle.VT_RAIL))if(GSEngine.IsBuildable(e))GSLog.Info("M6 RAIL|"+e+"|"+GSEngine.GetName(e)+"|"+GSEngine.GetPower(e)+"|"+GSEngine.GetPrice(e));}
GSLog.Info("C6 DONE inland reload");while(true)Sleep(365);}}'''
    probes=[]
    for n in range(2):
        start=time.monotonic();home=run(script,'reload',3500,source=source);seconds=time.monotonic()-start
        log=(home/'engine.log').read_text(encoding='utf8');assert 'M6 RELOAD|617|'+str(state['final_industry_count'])+'|96|64|15|3' in log
        saved=home/'save/autosave/exit.sav';after=parts(saved)
        assert initial['CITY']==after['CITY'] and initial['INDY']==after['INDY'] and initial['NGRF']==after['NGRF'] and maps(initial)==maps(after)
        probes.append(dict(case=str(home),seconds=round(seconds,3),source_sha256=sha(source),saved_sha256=sha(saved),town_industry_newgrf_rows_and_maps_identical=True))
        source=saved
    (ROOT/'docs/research/inland_reload_validation.json').write_text(json.dumps(dict(evidence='VERIFIED IN GAME',tests=probes,opening_trains=[l.split('M6 RAIL|')[1] for l in log.splitlines() if 'M6 RAIL|' in l],settings=[l.split('M6 SETTING|')[1] for l in log.splitlines() if 'M6 SETTING|' in l],newgrfs=[l.split('M6 GRF|')[1] for l in log.splitlines() if 'M6 GRF|' in l]),indent=2))
    (BASE/'reload-case.txt').write_text(str(home));print('Two gameplay round trips passed')


if __name__=='__main__':main()
