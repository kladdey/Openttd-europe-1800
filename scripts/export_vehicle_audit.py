"""Join observed runtime engine data to GRF allocation diagnostics and hashes."""
import csv,json,re,hashlib,datetime,collections
from pathlib import Path

ROOT=Path('docs/research')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    raw=json.loads((ROOT/'vehicle_audit_v2/newgrf_inventory.json').read_text(encoding='utf8'))
    refs=json.loads((ROOT/'scenario_vehicle_references.json').read_text(encoding='utf8'))
    log=Path('.vehicle-audit-runtime/probe-detailed.log').read_text(encoding='utf8',errors='replace')
    mapping={}
    for m in re.finditer(r'(?:Created new|Replaced) engine at index (\d+) for GRFID ([0-9A-F]{8}), type (\d+), index (\d+)',log):
        idx,g,typ,local=m.groups();mapping[int(idx)]=(g,int(typ),int(local))
    byid={g['grfid']:g for g in raw['newgrfs'] if g.get('grfid')}
    rows=[];evidence=[]
    for line in log.splitlines():
        if 'AUDIT_ROW|' not in line:continue
        parts=line.split('AUDIT_ROW|',1)[1].split('|'); assert len(parts)==14,parts
        idx,typ,name,date,price,running,speed,power,weight,te,cap,reliability,wagon,cargos=parts
        idx=int(idx);g,t,local=mapping[idx];assert t==int(typ)
        grf=byid[g];date=int(date);year=datetime.date.fromordinal(date-365).year
        price,running,power,te=map(int,(price,running,power,te))
        kind='ship' if t==2 else 'wagon' if wagon=='true' else 'powered_control_or_dummy' if power<=1 else 'multiple_unit_or_railcar' if int(cap)>0 or re.search(r'\b(?:EMU|DMU|Railcar|Railbus|ICE|TGV|Pendolino|HST)\b',name,re.I) else 'locomotive_or_powered_unit'
        row=dict(source_grfid=g,source_name=grf.get('internal_name',''),source_path=grf['path'],archive_member=grf.get('member',''),source_sha256=grf['sha256'],local_vehicle_id=local,runtime_engine_id=idx,vehicle_name=name,category=kind,classification_status='wagon/ship from engine API; powered subcategory heuristic',introduction_year=year,design_date_days_since_year_zero=date,retirement_year='UNVERIFIED',purchase_price_gbp=price,annual_running_cost_gbp=running,max_speed_kmish_h=int(speed),power_hp=power if power>=0 else 'UNVERIFIED',tractive_effort_kn=te if te>=0 else 'UNVERIFIED',weight_t=int(weight) if int(weight)>=0 else 'UNVERIFIED',default_capacity=int(cap) if int(cap)>=0 else 'UNVERIFIED',cargo_refit_labels=cargos,reliability_percent=int(reliability) if int(reliability)>=0 else 'UNVERIFIED',parameters=json.dumps(next(r['params'] for r in refs['references'] if r['grfid']==g)),purchase_per_hp=round(price/power,4) if power>0 else 'UNVERIFIED',running_per_hp=round(running/power,4) if power>0 else 'UNVERIFIED',purchase_per_kn=round(price/te,4) if te>0 else 'UNVERIFIED',annual_running_to_purchase=round(running/price,6) if price>0 else 'UNVERIFIED',measurement_status='VERIFIED JGRPP API; disposable map at 1830; not depot-built consist',date_status='Runtime design date includes engine introduction randomisation',retirement_status='Not exposed by engine API; model life is not an exact retirement date')
        rows.append(row);evidence.append(line)
    assert len(rows)==int(re.findall(r'AUDIT_DONE\|(\d+)',log)[-1]);assert len({r['runtime_engine_id'] for r in rows})==len(rows)
    with (ROOT/'vehicle_roster.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (ROOT/'vehicle_runtime_evidence.log').write_text('\n'.join(evidence)+'\n'+next(l for l in log.splitlines() if 'AUDIT_DONE|' in l)+'\n',encoding='utf8')
    diag=[l for l in log.splitlines() if re.search(r'(?:Created new|Replaced) engine at index|sets local price base multiplier',l)]
    (ROOT/'vehicle_runtime_mapping.log').write_text('\n'.join(diag)+'\n',encoding='utf8')
    scenario_log=Path('.vehicle-audit-runtime/scenario-load.log').read_text(encoding='utf8',errors='replace')
    (ROOT/'vehicle_scenario_load_evidence.log').write_text('\n'.join(l for l in scenario_log.splitlines() if re.search(r'GRFInfo: Loaded GRF|sets local price base multiplier|disabling|[Dd]eactivat|[Ee]rror',l))+'\n',encoding='utf8')
    groups=collections.Counter(r['source_grfid'] for r in rows)
    inventory=[]
    for g in raw['newgrfs']:
        item={k:v for k,v in g.items() if k not in ('names','train_assignments','base_cost_actions','description')}
        item['referenced_by_newest_scenario']=g.get('grfid') in {r['grfid'] for r in refs['references']}
        item['runtime_inventory_count']=groups.get(g.get('grfid'),0)
        item['static_extraction_note']='Raw Action 0 candidates are not a resolved roster; Action 6/7/9 and callbacks require the engine'
        inventory.append(item)
    duplicate_groups=collections.defaultdict(list)
    for g in inventory:
        if g.get('grfid'):duplicate_groups[g['grfid']].append({'path':g['path'],'member':g.get('member'),'sha256':g['sha256']})
    paths=[Path(r'C:\Users\Kladd\Downloads\OpenTTD\openttd.exe'),Path(r'C:\Program Files (x86)\Steam\steamapps\common\OpenTTD\openttd.exe'),Path(r'C:\Users\Kladd\Documents\OpenTTD\openttd.cfg'),Path(r'C:\Users\Kladd\Downloads\OpenTTD\openttd.cfg')]
    result=dict(audit_date='2026-10-28',roots=raw['roots'],scenario=refs,installed_newgrfs=inventory,duplicate_grfids={k:v for k,v in duplicate_groups.items() if len(v)>1},runtime_counts=dict(groups),runtime_total=len(rows),runtime_train_count=sum(r['category']!='ship' for r in rows),runtime_ship_count=sum(r['category']=='ship' for r in rows),fingerprints=[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'mtime':p.stat().st_mtime} for p in paths],scenario_metadata=[{k:v for k,v in s.items() if k in ('path','sha256','mtime','error','header')} for s in raw['scenarios']],scope='Installed paths read only. Runtime on local copies in ignored workspace. No runtime binary/assets redistributed.')
    (ROOT/'newgrf_inventory.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    early=[r for r in rows if r['introduction_year']<=1850 and r['category']!='ship']
    with (ROOT/'early_vehicle_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(early)
    print('Counts',groups,'total',len(rows),'early',len(early))
    for r in early:print(r['source_grfid'],r['local_vehicle_id'],ascii(r['vehicle_name']),r['introduction_year'],r['category'],r['purchase_price_gbp'],r['annual_running_cost_gbp'],r['power_hp'],r['tractive_effort_kn'],r['weight_t'],r['max_speed_kmish_h'])

if __name__=='__main__':main()
