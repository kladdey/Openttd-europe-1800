"""Require actual paid output, then test stockpile persistence on paused copies."""
import json,re
from pathlib import Path
from industrial_phase6b_runtime import ROOT,BASE,run,sha
from industrial_phase6b_controls import COMMON,builder


def main():
    registration=json.loads((BASE/'candidate-registration.json').read_text())
    assets=Path(registration['case'])
    evidence=[]
    for kind,localid,iid,labels,out in [('copper',123,3,['CORE','COAL','SAND'],'COPR'),('meat',125,2,['SALT','LVST'],'FOOD'),('fish',124,2,['SALT','FISH'],'FOOD')]:
        case=Path((BASE/('control-'+kind+'-case.txt')).read_text())
        log=(case/'engine.log').read_text(encoding='utf8')
        assert 'I6 CONTROL_PASS|' in log and 'I6 CONTROL_PRODUCTION|' in log,case
        assert not any(x in log for x in ['CONTROL_BLOCKED','CONTROL_ERROR','Your script made an error'])
        paid=re.findall(r'I6 CONTROL_PAID\|([^|]+)\|(\d+)\|(-?\d+)\|(\d+)\|(\d+)',log)
        assert len(paid)==(4 if kind=='copper' else 3),paid
        probes=[];source=case/'save/autosave/exit.sav'
        s=builder()+'class CoastalProbe extends GSController {\n'+COMMON+'''function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSLog.Info("I6 PERSISTENCE_CONTEXT|"+GSGame.IsPaused()+"|"+GSNewGRF.GetVersion(0x4B484531)+"|"+GSCargoList().Count());
local row="";foreach(label in LABELS){local c=Cargo(label);row+=label+":"+GSIndustry.GetStockpiledCargo(WORKS,c)+":"+GSIndustry.IsCargoAccepted(WORKS,c)+",";}
GSLog.Info("I6 PERSISTENCE|"+row+"|"+GSIndustry.GetLastMonthProduction(WORKS,Cargo(OUTPUT)));
GSLog.Info("C6 DONE persistence");while(true)Sleep(365);}}'''
        s='LABELS <- '+json.dumps(labels)+'; WORKS <- '+str(iid)+'; OUTPUT <- '+json.dumps(out)+';\n'+s
        for n in range(2):
            home=run(s,'persist-'+kind,2500,source=source,candidate_grf=assets)
            observed=(home/'engine.log').read_text(encoding='utf8')
            assert 'I6 PERSISTENCE_CONTEXT|true|3|64' in observed,observed[-3000:]
            row=re.search(r'I6 PERSISTENCE\|([^\r\n]+)',observed).group(1)
            probes.append(dict(case=str(home),row=row,source_sha256=sha(source)))
            source=home/'save/autosave/exit.sav'
        assert probes[0]['row']==probes[1]['row'],probes
        evidence.append(dict(kind=kind,local_id=localid,evidence='VERIFIED IN GAME',case=str(case),script_sha256=sha(case/'game/registration/main.nut'),save_sha256=sha(case/'save/autosave/exit.sav'),production_first_observed=int(re.search(r'I6 CONTROL_PRODUCTION\|(\d+)',log).group(1)),negative_controls=re.findall(r'I6 CONTROL_NEGATIVE\|([^\r\n]+)',log),paid_events=[dict(route=p[0],vehicle_id=int(p[1]),positive_vehicle_profit_delta=int(p[2]),distance_to_destination=int(p[3]),tile=int(p[4])) for p in paid],profit_unit='OpenTTD internal money units; these are delivery events, not annual profits',persistence=probes))
    result=dict(candidate_grf_sha256=registration['grf_sha256'],engine_sha256=registration['engine_sha256'],fixture_limitations='Disposable 256x256 flat control map, construction grant, raw funding enabled, economy/calendar 1830. Not a campaign profitability test. No vehicle price, introduction, capacity or performance modifications.',tests=evidence)
    (ROOT/'docs/research/copper_salt_runtime_validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print('All three loaded-output and save/reload controls passed')


if __name__=='__main__':main()
