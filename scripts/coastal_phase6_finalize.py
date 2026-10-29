"""Supported name correction, load/save/reload checks and guarded delivery."""
import csv,json,re,shutil
from pathlib import Path
import numpy as np
from coastal_phase6_runtime import BASE,ROOT,SOURCE,EXPECTED,sha,run
from coastal_phase6_preservation import parts,maps,differences
from coastal_phase6_implement import clean
from historical_scenario_migration import inspect


def main():
    state=json.loads((BASE/'implementation.json').read_text(encoding='utf8'))
    accepted=[r for r in state['decisions'] if r['status']=='ACCEPTED'];assert accepted
    current=Path(state['candidate'])
    s='class CoastalProbe extends GSController {function Start(){while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);\n'
    for r in accepted:s+=f'GSTown.SetName({r["town_id"]},{json.dumps(r["name"],ensure_ascii=False)});\n'
    s+='foreach(t,_ in GSTownList())if(t>=613)GSLog.Info("C6 NAME|"+t+"|"+GSTown.GetName(t));GSLog.Info("C6 DONE names");while(true)Sleep(365);}}'
    home=run(s,'names-verified',800,source=current)
    log=(home/'engine.log').read_text(encoding='utf8');assert 'C6 DONE names' in log
    for r in accepted:assert f'C6 NAME|{r["town_id"]}|{r["name"]}' in log
    dest=home/'candidate.scn';clean(SOURCE,home/'save/autosave/exit.sav',dest)
    before=inspect(SOURCE);after=inspect(dest);assert after['town_records']==613+len(accepted)
    assert before['newgrfs']==after['newgrfs'] and len(after['newgrfs'])==15
    assert after['industry_records']==after['industry_tiles']==0
    a,b,changed,guards=differences(SOURCE,dest)
    assert all(guards[k]==0 for k in ('height_changes','water_type_changes','existing_infrastructure_changes'))
    original=parts(SOURCE);candidate=parts(dest)
    assert original['CITY'][1]==candidate['CITY'][1][:614]
    allowed={'CITY'}|set(a)
    changed_chunks=[t for t in original if original[t]!=candidate[t]]
    assert set(changed_chunks)<=allowed
    for t in ['PATS','NGRF','DATE','ECMY','VEHS','STNN','INDY','OBJS','PLYR','GSDT']:
        assert original[t]==candidate[t],t
    # Verify a real engine save then a second real engine load of that save.
    probe=(ROOT/'scripts/coastal_phase6_inventory.nut').read_text(encoding='utf-8-sig').replace('foreach(town,_ in GSTownList()){','foreach(town,_ in GSTownList()){if(town<613)continue;')
    probe=probe.replace('  local passengers=', '  foreach(g,_ in GSNewGRFList())GSLog.Info("C6 ACTIVE_GRF|"+g+"|"+GSNewGRF.GetVersion(g)+"|"+GSNewGRF.GetName(g));\n  GSLog.Info("C6 SETTINGS|train_limit|"+GSGameSettings.GetValue("vehicle.max_train_length"));\n  local passengers=')
    reload_home=run(probe,'final-load-save',2000,source=dest)
    text=(reload_home/'engine.log').read_text(encoding='utf8')
    assert f'C6 DONE towns={613+len(accepted)} industries=0' in text
    assert text.count('C6 ACTIVE_GRF|')==15
    assert 'C6 SETTINGS|train_limit|7' in text
    saved=reload_home/'save/autosave/exit.sav'
    assert parts(saved)['CITY']==candidate['CITY']
    assert parts(saved)['NGRF']==original['NGRF']
    assert maps(parts(saved))==b
    # Rewrap the compressed engine save for a separate measurement reload;
    # the harness accepts both OTTS and OTTX and preserves its version header.
    second=run(probe,'final-reload',2000,source=saved)
    assert f'C6 DONE towns={613+len(accepted)} industries=0' in (second/'engine.log').read_text(encoding='utf8')
    out=SOURCE.with_name('Europe 1830 Historical AXIS 0.2.0 - Coastal Towns.scn')
    # Exclusive creation is atomic and can never overwrite an older scenario.
    with dest.open('rb') as src,out.open('xb') as dst:shutil.copyfileobj(src,dst)
    assert sha(out)==sha(dest) and sha(SOURCE)==EXPECTED
    changed_rows=[];n=4096**2
    for i in np.flatnonzero(changed):
        fields=[t for t in a if a[t][i*(len(a[t])//n):(i+1)*(len(a[t])//n)]!=b[t][i*(len(b[t])//n):(i+1)*(len(b[t])//n)]]
        changed_rows.append(dict(tile=int(i),x=int(i%4096),y=int(i//4096),before_type=a['MAPT'][i]>>4,after_type=b['MAPT'][i]>>4,changed_fields=';'.join(fields),before=';'.join(t+':'+a[t][i*(len(a[t])//n):(i+1)*(len(a[t])//n)].hex() for t in fields),after=';'.join(t+':'+b[t][i*(len(b[t])//n):(i+1)*(len(b[t])//n)].hex() for t in fields)))
    with (ROOT/'docs/research/coastal_changed_tiles.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(changed_rows[0]));w.writeheader();w.writerows(changed_rows)
    report=dict(source=str(SOURCE),source_sha256=EXPECTED,output=str(out),output_sha256=sha(out),original_towns=613,added_towns=len(accepted),final_towns=after['town_records'],guards=guards,original_town_records_bit_identical=True,changed_chunks=changed_chunks,all_other_chunks_bit_identical=True,newgrfs=after['newgrfs'],industry_instances=0,industry_tiles=0,real_save_and_reload_passed=True,load_case=str(reload_home),reload_case=str(second),name_case=str(home),accepted=accepted)
    (ROOT/'docs/research/coastal_scenario_delivery.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    state['candidate']=str(out);state['candidate_sha256']=sha(out)
    (BASE/'implementation.json').write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
