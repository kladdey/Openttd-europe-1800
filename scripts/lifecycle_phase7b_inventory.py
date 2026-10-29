"""Read-only baseline fingerprints and source-backed extractive inventory."""
import csv,json,hashlib,sys
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,SOURCE,guards,sha
from coastal_phase6_preservation import parts
from industrial_phase6b_candidate import field_offset
from industrial_phase6b_plan import write_csv
from lifecycle_phase7b_runtime import registration

DATA=ROOT/'docs/research';OUT=ROOT/'newgrfs/axis-historical-legacy/.work';OUT.mkdir(parents=True,exist_ok=True)
def records():
    p=parts(SOURCE);schema,rows=p['INDY'][1][0],p['INDY'][1][1:];result=[]
    fields=['location.tile','location.w','location.h','type','founder','construction_date','construction_type','selected_layout','random','prod_level','ctlflags']
    for i,row in enumerate(rows):
        if not row:continue
        r={'industry_id':i,'record_sha256':hashlib.sha256(row).hexdigest()}
        for f in fields:
            q,w,count=field_offset(schema,row,f);assert count==1;r[f]=int.from_bytes(row[q:q+w],'big',signed=f=='construction_date')
        r.update(tile=r['location.tile'],x=r['location.tile']%4096,y=r['location.tile']//4096);result.append(r)
    assert len(result)==542
    return result

def main():
    guards();rows=records();graph=json.loads((DATA/'industry_chain_graph.json').read_text())['industries']
    matrix=json.loads((DATA/'industrial_1830_candidate_matrix.json').read_text())['industries'];rules={r['local_id']:r for r in matrix}
    with (DATA/'industry_placement_results.csv').open(encoding='utf8') as f:placements={int(r['industry_id']):r for r in csv.DictReader(f) if r['industry_id'] and r['status']=='PLACED'}
    with (DATA/'inland_town_population_changes.csv').open(encoding='utf8') as f:towns=list(csv.DictReader(f))
    mapping={int(k):v for k,v in registration()['mapping'].items()};extractives=[]
    for r in rows:
        placement=placements.get(r['industry_id'],{});local=mapping[r['type']];rule=rules[local];name=rule['industry']
        node=graph.get(str(r['industry_id']),dict(region='UNRESOLVED',accepted=rule['accepted'],produced=rule['produced']))
        if rule['model_class']!='IndustryPrimaryExtractive' or name=='trading_post':continue
        t=min(towns,key=lambda t:(abs(int(t['x'])-r['x'])+abs(int(t['y'])-r['y']),int(t['town_id'])))
        producers={label for label,rate in node['produced']}
        # Labels in the graph are inspected rather than inferred from names.
        raw=rules.get(local,{})
        consumers=[int(k) for k,n in graph.items() if set(n['accepted'])&producers]
        extractives.append(r|dict(local_id=local,industry=name,region=node['region'],nearest_town=t['town_name'],
            cargo_outputs=sorted(producers),cargo_inputs=node['accepted'],downstream_industry_ids=consumers,
            historical_locality=placement.get('locality','Inherited baseline site'),historical_source=placement.get('history_source','UNRESOLVED'),
            historical_confidence=placement.get('confidence','UNVERIFIED inherited provenance'),
            lifecycle_class='finite fossil deposit' if name=='coal_mine' else 'finite mineral deposit; extraction-specific policy required',
            reserves='UNVERIFIED — no numerical mineral reserve claimed',
            provenance_flag='UNRESOLVED inherited soda-ash; preserve unmanaged' if 'soda_ash' in name else 'Regional game representation; not exact shaft identity'))
    (DATA/'phase7b_baseline_fingerprints.json').write_text(json.dumps(dict(source=str(SOURCE),sha256=sha(SOURCE),industries=rows),indent=2))
    (DATA/'phase7b_extractive_inventory.json').write_text(json.dumps(extractives,indent=2))
    write_csv(DATA/'phase7b_extractive_inventory.csv',extractives)
    print('Extractives',len(extractives));print('example graph',next(iter(graph.values())))
    for r in extractives:
        if r['region'] in ['GB','DE','PL']:print(r['industry_id'],r['local_id'],r['industry'],r['region'],r['x'],r['y'],r['historical_locality'],r['construction_date'],r['random'],r['founder'])

if __name__=='__main__':main()
