"""Export comparable calendar snapshots and verify engine identity mapping."""
import csv,json,re,hashlib,collections
from pathlib import Path
ROOT=Path('docs/research')
def readlog(path):
    log=path.read_text(encoding='utf8',errors='replace');mapping={};rows=[]
    for m in re.finditer(r'(?:Created new|Replaced) engine at index (\d+) for GRFID ([0-9A-F]{8}), type (\d+), index (\d+)',log):
        i,g,t,l=m.groups();mapping[int(i)]=(g,int(t),int(l))
    for line in log.splitlines():
        if 'AUDIT_ROW|' in line:rows.append(line.split('AUDIT_ROW|',1)[1].split('|'))
    assert len(rows)==int(re.findall(r'AUDIT_DONE\|(\d+)',log)[-1])
    return mapping,rows
def main():
    output=[];manifest=[]
    for year in (1830,1850,1900,1950,2000,2025):
        path=Path('.vehicle-audit-runtime')/('probe-detailed.log' if year==1830 else f'probe-{year}.log')
        mapping,rows=readlog(path)
        for parts in rows:
            i,t,name,date,price,running,speed,power,weight,te,cap,rel,wagon,cargos=parts
            g,typ,local=mapping[int(i)];assert typ==int(t)
            output.append(dict(snapshot_year=year,source_grfid=g,local_vehicle_id=local,runtime_engine_id=int(i),vehicle_type=int(t),vehicle_name=name,design_date=int(date),purchase_price_gbp=int(price),annual_running_cost_gbp=int(running),max_speed_kmish_h=int(speed),power_hp=int(power),weight_t=int(weight),tractive_effort_kn=int(te),default_capacity=int(cap),reliability_percent=int(rel),wagon=wagon,refit_labels=cargos))
        manifest.append({'year':year,'runtime_log_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':len(rows),'seed':None if year==1830 else 1830,'note':'1830 initial snapshot predates fixed seed; cost values reproduced in later fixed-seed snapshots'})
    with (ROOT/'vehicle_economy_snapshots.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    (ROOT/'vehicle_snapshot_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    for year in (1830,1850,1900,1950,2000,2025):
        print('YEAR',year)
        for r in output:
            if r['snapshot_year']==year and (any(x.lower() in r['vehicle_name'].lower() for x in ['Planet','Grasshopper','Norris','EU07','BR 182','Class 66']) or r['source_grfid']=='44441000' and r['local_vehicle_id'] in [12,44]):
                print(r['source_grfid'],r['local_vehicle_id'],ascii(r['vehicle_name']),r['purchase_price_gbp'],r['annual_running_cost_gbp'],r['power_hp'],r['tractive_effort_kn'],r['default_capacity'])
if __name__=='__main__':main()
