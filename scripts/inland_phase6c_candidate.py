"""Promote engine-built markets and genuine town changes, never patch population."""
import json,lzma,re
from pathlib import Path
import numpy as np
from inland_phase6c_runtime import ROOT,BASE,SOURCE,EXPECTED,sha
from coastal_phase6_preservation import parts,maps,differences
from industrial_phase6b_candidate import neutral_industries
from transport_phase3 import encode
from industrial_phase6b_plan import write_csv


def main():
    state=json.loads((BASE/'placement.json').read_text());home=Path(state['case']);saved=home/'save/autosave/exit.sav'
    original=parts(SOURCE);engine=parts(saved);em=maps(engine)
    assert original['INDY'][1]==engine['INDY'][1][:len(original['INDY'][1])],'Existing industry records changed'
    assert original['NGRF']==engine['NGRF'] and original['PATS']==engine['PATS']
    log=(home/'engine.log').read_text(encoding='utf8')
    town_rows={}
    for when in ['BEFORE','AFTER']:
        town_rows[when]={int(i):dict(name=n,tile=int(t),population=int(p)) for i,n,t,p in re.findall(r'M6 '+when+r'_TOWN\|(\d+)\|([^|]+)\|(\d+)\|(\d+)',log)}
    assert len(town_rows['BEFORE'])==len(town_rows['AFTER'])==617
    original_towns={t['town_id']:dict(name=t['name'],tile=t['tile'],population=t['population']) for t in json.loads((BASE/'towns.json').read_text(encoding='utf8'))}
    town_rows['BEFORE']=original_towns
    towns=[]
    for id_,before in town_rows['BEFORE'].items():
        after=town_rows['AFTER'][id_];assert before['name']==after['name'] and before['tile']==after['tile']
        loss=before['population']-after['population'];assert 0<=loss<=before['population']*.05
        towns.append(dict(town_id=id_,town_name=before['name'],x=before['tile']%4096,y=before['tile']//4096,population_before=before['population'],population_after=after['population'],population_loss=loss,population_loss_percent=round(100*loss/before['population'],6),new_markets=sum(r.get('town_id')==id_ and r['status']=='PLACED' for r in state['results'])))
    payload=[]
    for tag,(kind,rows) in original.items():
        if tag in em:rows=[em[tag]]
        elif tag=='INDY':rows=neutral_industries(engine[tag][1])
        elif tag in ['CITY','PSAC','ANIT','STNN']:rows=engine[tag][1]
        payload.append(encode(tag,kind,rows))
    dest=home/'inland-markets-candidate.scn'
    with dest.open('xb') as f:f.write(SOURCE.read_bytes()[:8]+lzma.compress(b''.join(payload)+b'\0'*4))
    a,b,changed,guard=differences(SOURCE,dest);n=4096**2
    at=np.frombuffer(a['MAPT'],dtype='u1')>>4;bt=np.frombuffer(b['MAPT'],dtype='u1')>>4
    placed=[r for r in state['results'] if r['status']=='PLACED'];targets=np.zeros(n,dtype=bool);targets[[r['tile'] for r in placed]]=True
    assert not np.any(changed & ~targets),'Unexpected changes outside authorized house sites'
    assert np.all(at[targets]==3) and np.all(bt[targets]==8)
    assert guard['height_changes']==guard['existing_infrastructure_changes']==guard['water_type_changes']==0
    candidate=parts(dest);assert original['INDY'][1]==candidate['INDY'][1][:len(original['INDY'][1])]
    for tag in original:
        if tag in set(a)|{'CITY','INDY','PSAC','ANIT','STNN'}:continue
        assert original[tag]==candidate[tag],tag
    assert sum(t['population_loss'] for t in towns)==sum(r['population_loss'] for r in placed)
    assert sha(SOURCE)==EXPECTED
    result=guard|dict(source=str(SOURCE),source_sha256=EXPECTED,candidate=str(dest),candidate_sha256=sha(dest),original_industries_bit_identical=467,original_town_identities_names_centres_preserved=617,new_markets=len(placed),final_industry_count=467+len(placed),house_tiles_replaced=int(changed.sum()),population_loss=sum(t['population_loss'] for t in towns),max_town_population_loss_percent=max(t['population_loss_percent'] for t in towns),population_changes_from_engine_only=True,all_other_scenario_chunks_preserved=True,normal_settings_preserved=True)
    (BASE/'candidate.json').write_text(json.dumps(result,indent=2));(ROOT/'docs/research/inland_preservation.json').write_text(json.dumps(result,indent=2))
    write_csv(ROOT/'docs/research/inland_town_population_changes.csv',towns)
    requests={r['request_id']:r for filename in ['market-plan.json','market-extension-plan.json','market-fruit-plan.json'] if (BASE/filename).exists() for r in json.loads((BASE/filename).read_text(encoding='utf8'))['requests']}
    write_csv(ROOT/'docs/research/inland_market_placements.csv',[{k:v for k,v in requests[r['request_id']].items() if k!='sites'}|r|dict(engine_case=r.get('engine_case',str(home))) for r in state['results']])
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
