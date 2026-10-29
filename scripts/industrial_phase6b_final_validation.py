"""Final read-only guards plus a disposable JGRPP gameplay round trip."""
import json,time,re
from pathlib import Path
from industrial_phase6b_runtime import ROOT,BASE,SOURCE,EXPECTED,run,sha
from industrial_phase6b_candidate import verify
from coastal_phase6_preservation import parts,maps


def main():
    candidate=Path(json.loads((BASE/'additions-candidate-final.json').read_text())['candidate'])
    old=Path(json.loads((BASE/'candidate.json').read_text())['candidate'])
    migration=json.loads((BASE/'migration-0.3.json').read_text())
    guard=verify(candidate,True)
    a=parts(old);b=parts(candidate)
    assert a['INDY'][1]==b['INDY'][1][:len(a['INDY'][1])]
    gui=Path((BASE/'editor-proof-case.txt').read_text().strip());saved=gui/'scenario/UNNAMED.scn';g=parts(saved)
    assert b['CITY']==g['CITY'] and b['INDY']==g['INDY'] and b['NGRF']==g['NGRF'] and maps(b)==maps(g)
    script='''class CoastalProbe extends GSController {function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSLog.Info("I6 FINAL|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|types="+GSIndustryTypeList().Count()+"|cargos="+GSCargoList().Count()+"|grfs="+GSNewGRFList().Count()+"|version="+GSNewGRF.GetVersion(0x4B484531));
foreach(name in ["construction.raw_industry_construction","construction.industry_platform","vehicle.max_train_length","economy.infrastructure_maintenance","economy.timekeeping_units","economy.inflation","economy.industry_daily_change","difficulty.max_loan","difficulty.vehicle_breakdowns","economy.town_growth_rate"]){if(GSGameSettings.IsValid(name))GSLog.Info("I6 FINAL_SETTING|"+name+"|"+GSGameSettings.GetValue(name));}
GSLog.Info("I6 ECONOMY_DATE|"+GSDate.GetYear(GSDate.GetCurrentDate()));
GSLog.Info("C6 DONE final reload");while(true)Sleep(365);}}'''
    probes=[];source=candidate
    for n in range(2):
        t=time.monotonic();home=run(script,'final-reload',3500,source=source,candidate_grf=Path(migration['candidate_assets']));elapsed=time.monotonic()-t
        log=(home/'engine.log').read_text(encoding='utf8')
        assert 'I6 FINAL|towns=617|industries=467|types=96|cargos=64|grfs=15|version=3' in log
        assert 'I6 FINAL_SETTING|vehicle.max_train_length|7' in log
        assert 'I6 FINAL_SETTING|economy.infrastructure_maintenance|1' in log
        source=home/'save/autosave/exit.sav';after=parts(source)
        assert b['CITY']==after['CITY'] and b['INDY']==after['INDY'] and b['NGRF']==after['NGRF'] and maps(b)==maps(after)
        probes.append(dict(case=str(home),combined_load_probe_and_exit_save_seconds=round(elapsed,3),saved_sha256=sha(source),events=[line.split(' I6 ',1)[1] for line in log.splitlines() if ' I6 ' in line]))
    guard.update(completed_438_industry_records_bit_identical=True,scenario_editor_load_save_reload_verified=True,editor_saved_file=str(saved),editor_saved_sha256=sha(saved),editor_roundtrip_all_map_arrays_and_town_industry_newgrf_rows_identical=True,gameplay_roundtrips=probes,source_scenario_unchanged=sha(SOURCE)==EXPECTED)
    (ROOT/'docs/research/industrialized_scenario_validation.json').write_text(json.dumps(guard,indent=2),encoding='utf8');print(json.dumps(guard,indent=2))


if __name__=='__main__':main()
