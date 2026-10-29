"""Stage an append-only upgrade COPY using an engine-generated NGRF record.

The original 617-town scenario and the completed 438-industry 0.2.0 candidate
remain immutable. No invented checksum, parameter, industry or cargo IDs.
"""
import json,lzma,re,time
from pathlib import Path
from industrial_phase6b_runtime import ROOT,BASE,run,sha
from coastal_phase6_preservation import parts,maps
from historical_scenario_migration import inspect
from transport_phase3 import encode


def main():
    reg=json.loads((BASE/'candidate-registration.json').read_text());assets=Path(reg['case'])
    state=json.loads((BASE/'candidate.json').read_text());source=Path(state['candidate'])
    refs=inspect(source)['newgrfs'];fresh=inspect(Path(reg['saved']))['newgrfs']
    old=next(r for r in refs if r['grfid']=='4B484531');new=next(r for r in fresh if r['grfid']=='4B484531')
    assert old['version']==2 and new['version']==3
    for key in ['grfid','params','palette']:assert old[key]==new[key],(key,old[key],new[key])
    original=parts(source);engine=parts(Path(reg['saved']))
    index=next(i+1 for i,r in enumerate(refs) if r['grfid']=='4B484531')
    fresh_index=next(i+1 for i,r in enumerate(fresh) if r['grfid']=='4B484531')
    assert original['NGRF'][1][0]==engine['NGRF'][1][0]
    records=original['NGRF'][1][:];records[index]=engine['NGRF'][1][fresh_index]
    stage=BASE/('upgrade-stage-'+str(time.time_ns())+'.scn')
    out=[encode(t,k,records if t=='NGRF' else rows) for t,(k,rows) in original.items()]
    with stage.open('xb') as f:f.write(source.read_bytes()[:8]+lzma.compress(b''.join(out)+b'\0'*4))
    matrix=json.loads((ROOT/'docs/research/industrial_1830_source_matrix.json').read_text(encoding='utf8'))
    ids=[r['local_id'] for r in matrix['industries']]+[105,123,124,125]
    s='IDS <- '+json.dumps(ids)+';\n'+'''class CoastalProbe extends GSController {function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
local lookup={};foreach(id in IDS){local t=GSIndustryType.ResolveNewGRFID(0x4B484531,id);if(!GSIndustryType.IsValidIndustryType(t))throw "Unregistered local ID "+id;lookup[t]<-id;}
GSLog.Info("I6 UPGRADE|version="+GSNewGRF.GetVersion(0x4B484531)+"|types="+GSIndustryTypeList().Count()+"|cargos="+GSCargoList().Count()+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count());
foreach(i,_ in GSIndustryList()){local t=GSIndustry.GetIndustryType(i);GSLog.Info("I6 RETAINED|"+i+"|"+lookup[t]+"|"+GSIndustry.GetLocation(i));}
foreach(t,_ in GSTownList()){local center=GSTown.GetLocation(t),ac="";foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)=="GOOD" || GSCargo.GetCargoLabel(c)=="FOOD")ac+=GSCargo.GetCargoLabel(c)+":"+GSTile.GetCargoAcceptance(center,c,1,1,5)+",";GSLog.Info("I6 TOWN_SINK|"+t+"|"+ac);}
GSLog.Info("C6 DONE compatible migration");while(true)Sleep(365);}}
'''
    home=run(s,'migrated-industry-probe',6000,source=stage,candidate_grf=assets)
    log=(home/'engine.log').read_text(encoding='utf8');assert 'I6 UPGRADE|version=3|types=96|cargos=64|towns=617|industries=438' in log
    prior=json.loads((BASE/'placement-result.json').read_text())['results'];prior={r['industry_id']:(r['local_id'],r['tile']) for r in prior if r['status']=='PLACED'}
    observed={int(i):(int(l),int(t)) for i,l,t in re.findall(r'I6 RETAINED\|(\d+)\|(\d+)\|(\d+)',log)}
    assert prior==observed,'Existing industry identities changed'
    saved=home/'save/autosave/exit.sav';after=parts(saved)
    assert after['CITY']==original['CITY'] and maps(after)==maps(original)
    result=dict(source=str(source),source_sha256=sha(source),stage=str(stage),case=str(home),engine_save=str(saved),candidate_assets=str(assets),old_grf=old,new_grf=new,old_438_industry_ids_types_locations_identical=True,towns_and_map_bytes_identical=True)
    (BASE/'migration-0.3.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
