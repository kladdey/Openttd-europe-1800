"""Prove 1830 availability and the disabled-spawning GameScript limitation."""
import json,re
from industrial_phase6b_runtime import ROOT,BASE,sha
from industrial_phase6b_controls import fresh


def main():
    script='''class CoastalProbe extends GSController {function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSGameSettings.SetValue("construction.raw_industry_construction",0);
GSLog.Info("I6 POLICY_CONTEXT|year="+GSDate.GetYear(GSDate.GetCurrentDate())+"|version="+GSNewGRF.GetVersion(0x4B484531)+"|types="+GSIndustryTypeList().Count()+"|cargos="+GSCargoList().Count()+"|grfs="+GSNewGRFList().Count());
foreach(id in [64,67,56,105,117,123,124,125]){
 local type=GSIndustryType.ResolveNewGRFID(0x4B484531,id),deity=GSIndustryType.CanBuildIndustry(type),company=false,raw=false;
 {local cm=GSCompanyMode(0);company=GSIndustryType.CanBuildIndustry(type);GSGameSettings.SetValue("construction.raw_industry_construction",1);raw=GSIndustryType.CanBuildIndustry(type);GSGameSettings.SetValue("construction.raw_industry_construction",0);}
 GSLog.Info("I6 POLICY|"+id+"|deity="+deity+"|company_raw_disabled="+company+"|company_raw_enabled="+raw);
}
local t=GSIndustryType.ResolveNewGRFID(0x4B484531,123),n=GSIndustryList().Count(),ok=GSIndustryType.BuildIndustry(t,GSMap.GetTileIndex(90,90));
GSLog.Info("I6 DEITY_BUILD|"+ok+"|"+GSError.GetLastErrorString()+"|"+n+"|"+GSIndustryList().Count());
GSGame.Pause();GSLog.Info("C6 DONE availability");while(true)Sleep(365);}}'''
    home=fresh(script,'availability-1830',2500,sea=False)
    log=(home/'engine.log').read_text(encoding='utf8')
    assert 'year=1830|version=3|types=96|cargos=64|grfs=15' in log
    for id_ in [123,124,125]:assert f'I6 POLICY|{id_}|deity=false|company_raw_disabled=true|company_raw_enabled=true' in log
    for id_ in [67,56]:assert f'I6 POLICY|{id_}|deity=false|company_raw_disabled=false|company_raw_enabled=false' in log
    assert 'I6 POLICY|105|deity=false|company_raw_disabled=false|company_raw_enabled=true' in log
    assert 'I6 DEITY_BUILD|false|' in log
    result=dict(evidence='VERIFIED IN GAME',case=str(home),script_sha256=sha(home/'game/registration/main.nut'),events=[s.split(' I6 ',1)[1] for s in log.splitlines() if ' I6 ' in s],interpretation='Normal spawning parameter remains zero. Deity-mode GS construction is blocked by the RandomCreation availability callback. Company-funded new processors are available in 1830. Raw mines require the raw-funding setting in disposable construction fixtures. Existing 1850 copper refinery and food processor remain unavailable in 1830.')
    (ROOT/'docs/research/copper_salt_availability_validation.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
