"""Reproducible Phase 2 analysis of preserved Phase 1 and disposable probes.

All output is metadata or numerical research; no game asset is redistributed.
Original Phase 1 CSV/JSON/logs are never rewritten. Run from repository root.
"""
import argparse,collections,csv,datetime,hashlib,itertools,json,math,re,statistics,tarfile
from pathlib import Path
from audit_vehicle_newgrfs import actions,ext

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'docs/research'
RUN=ROOT/'.vehicle-audit-runtime/phase2'
SETS={'53410808':'GETS','44441000':'UKRS2','4D560103':'Polish Train Set','4D560105':'Polish Rolling Stock Pack','44440302':'NARS 2.52','4E4D0518':'NARS Add-On 2cc'}
ERAS=[(1830,1849),(1850,1879),(1880,1913),(1914,1945),(1946,1970),(1971,1990),(1991,2025)]
def era(y):
    return next((f'{a}-{b}' for a,b in ERAS if a<=y<=b),'outside_campaign')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def loadcsv(path):return list(csv.DictReader(path.open(encoding='utf-8-sig')))
def writecsv(path,rows,fields=None):
    fields=fields or list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def year(days):return datetime.date.fromordinal(int(days)-365).year
def ratio(a,b):return round(a/b,6) if b>0 else None
def median(values):
    v=[x for x in values if x is not None and math.isfinite(x)]
    return statistics.median(v) if v else None
def jgr_sqrt(n):
    """JGRPP IntSqrt rounds to nearest, unlike Python math.isqrt."""
    s=math.isqrt(n)
    return s+int(n-s*s>s)
def log_mad(value,values):
    v=[math.log(x) for x in values if x is not None and x>0]
    if value is None or value<=0 or len(v)<6:return None
    m=statistics.median(v);mad=statistics.median(abs(x-m) for x in v)
    # A zero MAD has no usable dispersion; do not manufacture infinities.
    return (math.log(value)-m)/max(mad/0.67448975,math.log(1.10)) if mad>1e-10 else None

def parse_probe(path):
    log=path.read_text(encoding='utf8',errors='replace')
    if 'P2_DONE|' not in log:raise ValueError(f'Incomplete probe: {path}')
    mapping={}
    for m in re.finditer(r'(?:Created new|Replaced) engine at index (\d+) for GRFID ([0-9A-F]{8}), type (\d+), index (\d+)',log):
        i,g,t,l=m.groups();mapping[int(i)]=(g,int(l),int(t))
    data={'mapping':mapping,'engines':{},'available':{},'cargo':{},'payments':{},'trains':{},'contexts':{},'infra':{},'infra_final':{},'settings':{},'evidence':[]}
    fields=['runtime_id','purchase','display_running','life_days','default_cargo','railtype','articulated','capacity','reliability','hp','te','weight','speed','design_date']
    train_fields=['case_id','vehicle_id','runtime_id','wagon_runtime_id','wagon_count','cargo_id','purchase_actual','depot_running','capacity_primary','length_16ths','num_wagons_api','failed']
    for line in log.splitlines():
        if 'P2_' not in line:continue
        record=line[line.index('P2_'):];data['evidence'].append(record);p=record.split('|');tag=p[0];v=p[1:]
        if tag=='P2_ENGINE':
            assert len(v)==len(fields),v
            e={k:(x=='true' if k=='articulated' else int(x)) for k,x in zip(fields,v)}
            g,local,t=mapping[e['runtime_id']];e.update(grfid=g,local_id=local,type=t);data['engines'][e['runtime_id']]=e
        elif tag=='P2_AVAILABLE':data['available'][int(v[0])]=v[1]=='true'
        elif tag=='P2_SETTING':data['settings'][v[0]]=int(v[1])
        elif tag=='P2_CARGO':data['cargo'][int(v[0])]={'label':v[1],'weight_1000':int(v[2])}
        elif tag=='P2_PAYMENT':data['payments'][tuple(map(int,v[:3]))]=int(v[3])
        elif tag=='P2_TRAIN':
            assert len(v)==len(train_fields),v
            t={k:x if k=='case_id' else x=='true' if k=='failed' else int(x) for k,x in zip(train_fields,v)};t['caps']={}
            if t['case_id'] in data['trains'] and 'blocker' in data['trains'][t['case_id']]:t['blocker']=data['trains'][t['case_id']]['blocker']
            data['trains'][t['case_id']]=t
        elif tag=='P2_TRAIN_CAP':data['trains'][v[0]]['caps'][int(v[1])]=int(v[2])
        elif tag=='P2_TRAIN_MOTION':data['trains'][v[0]].update(moving_rate=int(v[1]),peak_empty_speed=int(v[2]),returned=v[3]=='true')
        elif tag=='P2_TRAIN_BLOCKED':
            if v[0] not in data['trains']:data['trains'][v[0]]={'case_id':v[0],'blocker':'|'.join(v[1:])}
            else:data['trains'][v[0]]['blocker']='|'.join(v[1:])
        elif tag=='P2_CONTEXT':
            names=['runtime_id','purchase','depot_rate','moving_peak','stopped_query','peak_speed','track_cost','returned','outside_stopped']
            data['contexts'][int(v[0])]={k:(x=='true' if k in ('returned','outside_stopped') else int(x)) for k,x in zip(names,v)}
        elif tag=='P2_INFRA':data['infra'][int(v[0])]=dict(zip(['track_unit','depot_unit','station_unit','monthly_observed'],map(int,v[1:])))
        elif tag=='P2_INFRA_FINAL':data['infra_final'][int(v[0])]={'track_pieces':int(v[1]),'monthly_cost':int(v[2])}
    assert len(data['engines'])==2887
    assert len(data['available'])==2887
    assert all(data['settings'][k]==val for k,val in {'difficulty.vehicle_costs':0,'difficulty.construction_cost':0,'economy.inflation':0,'economy.day_length_factor':1,'economy.timekeeping_units':0,'economy.infrastructure_maintenance':1}.items())
    return data

def static_metadata():
    raw=json.loads((R/'vehicle_audit_v2/newgrf_inventory.json').read_text(encoding='utf8'));by={g.get('grfid'):g for g in raw['newgrfs']}
    props=collections.defaultdict(lambda:collections.defaultdict(set))
    for g in SETS:
        for a in by[g]['train_assignments']:
            if a['property'] in ('19','20','07','03','26','1E','31'):props[g,a['id']][a['property']].add(a['value'])
    return props

def traction(name,props):
    vals=props.get('19',set())
    # Some sets transform Action 0 vehicle IDs via Action 6. A unique raw
    # candidate at the same number can therefore describe a different engine.
    # Explicit traction in the resolved runtime vehicle name takes precedence.
    for token,t in [('steam','Steam'),('electric','Electric'),('diesel','Diesel')]:
        if re.search(r'\b'+token+r'\b',name,re.I):
            return t,'explicit resolved GRF vehicle-name traction label; overrides unexecuted static candidates'
    if len(vals)==1:
        v=next(iter(vals));t='Steam' if v<=7 else 'Diesel' if v<=39 else 'Electric' if v<=49 else 'Monorail' if v<=55 else 'Maglev' if v<=65 else 'Unknown'
        return t,'unique static Action0 property19 candidate; not a runtime engine-class getter'
    return 'Unknown','UNVERIFIED'

def role(e,name):
    n=name.lower();hp,te,s,cap=e['hp'],e['te'],e['speed'],e['capacity'];y=year(e['design_date'])
    if hp<=1:return 'Control or auxiliary','inferred: <=1 hp; excluded from locomotive efficiency ranking'
    if cap>0 or re.search(r'\b(?:EMU|DMU|railcar|railbus|Acela|Pendolino|TGV|HST)\b',name,re.I):return 'Multiple units','inferred: powered capacity or named unit/power head; may include single railcars'
    if re.search(r'shunter|switcher|industrial|yard|jinty|dock|\basf\b|tow truck',n):return 'Shunting','inferred from GRF name'
    if re.search(r'freight|goods|class 66|br 266|\bet2[12]\b|\bet4[012]\b|\bst4[34]\b',n):return ('Heavy freight' if te>=150 else 'Light freight'),'inferred from name and TE'
    express_limit=90 if y<1880 else 120 if y<1946 else 160
    if s>=express_limit:return 'Express','inferred from era-relative speed; not exclusive historical usage'
    if te>=200 and s<=110:return 'Heavy freight','inferred: >=200 kN and <=110 speed'
    if s<=65 and te>=50 and hp>=250:return 'Light freight','inferred low-speed duty'
    if te<60 and hp<500:return 'Light passenger','inferred low-power/light duty; mixed use possible'
    if s>=110 and hp>=1500:return 'Heavy passenger','inferred medium-fast high-power duty; mixed use possible'
    return 'Mixed traffic','inferred fallback; uncertain historical role'

def model_income(profile,distance,days,amount=1,aging_rate=100):
    """Integer JGRPP 0.73.4 modern payment algorithm, conditional on no CB39."""
    t=(days*2//5)*aging_rate//100;p1,p2=profile['period1'],profile['period2'];over1=max(t-p1,0);over2=max(over1-p2,0)
    overmax=-224+(t-p1 if p2>224 else 2*(t-p1)-p2)
    if overmax>0:
        factor=max(2*31*16*16//(overmax+32),1)
        return distance*factor*amount*profile['payment']//(1<<25)
    return distance*max(255-over1-over2,31)*amount*profile['payment']//(1<<21)

def cargo_profiles(probes,inventory):
    g=next(g for g in inventory['installed_newgrfs'] if g.get('grfid')=='4A4B8808')
    with tarfile.open(g['path']) as tar:b=tar.extractfile(g['member']).read()
    assert hashlib.sha256(b).hexdigest()==g['sha256']
    widths={8:1,9:2,10:2,11:2,12:2,13:2,14:2,15:1,16:1,17:1,18:4,19:1,20:1,21:1,22:2,23:4,24:1,25:2,26:1,27:2,28:2,29:2,30:1,31:2}
    candidates=collections.defaultdict(list)
    for offset,a in actions(b):
        if len(a)<6 or a[:2]!=bytes([0,11]):continue
        np,count=a[2:4];first,p=ext(a,4);values=collections.defaultdict(dict)
        for _ in range(np):
            prop=a[p];p+=1;width=widths[prop]
            for i in range(count):values[first+i][prop]=a[p:p+width];p+=width
        assert p==len(a)
        for local,props in values.items():
            if all(k in props for k in (16,17,18,23)):
                label=props[23].decode('ascii',errors='replace')
                candidates[label].append(dict(label=label,payment=int.from_bytes(props[18],'little'),period1=props[16][0],period2=props[17][0],callback_mask=props.get(26,b'\0')[0],weight_sixteenths=props.get(15,b'\0')[0],offset=offset))
    validated={};checks=0;errors=[]
    for y,p in probes.items():
        for cid,c in p['cargo'].items():
            matching=[]
            for profile in candidates[c['label']]:
                points=[(d,days,value) for (cc,d,days),value in p['payments'].items() if cc==cid]
                if profile['callback_mask']&1:continue
                if all(model_income(profile,d,days)==value for d,days,value in points):matching.append(profile)
            unique={tuple((k,pr[k]) for k in ('payment','period1','period2','callback_mask')):pr for pr in matching}
            if len(unique)==1:
                profile=next(iter(unique.values()));validated[y,cid]=profile;checks+=len(points)
            else:errors.append({'year':y,'cargo':c['label'],'matching_profiles':len(unique)})
    return validated,dict(api_points_matched=checks,errors=errors,rule='Exact integer matching at 54 distance/time points per cargo and snapshot; CB39-profit mask must be absent')

def normalize(probes,base,props):
    normalized=[]
    for y,p in probes.items():
        for i,e in p['engines'].items():
            g=e['grfid'];key=(g,e['local_id'])
            if e['type']!=0 or g not in SETS:continue
            original=base[key];name=original['vehicle_name'];tr,ts=traction(name,props.get(key,{}));rr,rs=role(e,name)
            iswagon=original['category']=='wagon';role_name=rr
            if iswagon:
                label=p['cargo'].get(e['default_cargo'],{}).get('label','')
                role_name='Passenger carriage' if label=='PASS' else 'Mail carriage' if label=='MAIL' else 'Brake/control van' if e['capacity']<=0 else 'Bulk wagon' if label in ('COAL','IORE','CORE','AORE','GRAI','CLAY','SAND','COKE') else 'Liquid wagon' if label in ('OIL_','EOIL','CTAR','PETR','ACID','MILK') else 'General freight wagon'
                rs='Inferred from default cargo and capacity; refit options may span several roles'
            r=dict(snapshot_year=y,source_grfid=g,set_name=SETS[g],local_vehicle_id=e['local_id'],runtime_engine_id=i,vehicle_name=name,kind='wagon' if iswagon else 'control' if e['hp']<=1 else 'powered',introduction_year=year(e['design_date']),introduction_era=era(year(e['design_date'])),traction='Unpowered' if iswagon else tr,traction_evidence=ts,role=role_name,role_evidence=rs,buildable_for_test_company=p['available'][i],railtype=e['railtype'],articulated=e['articulated'],purchase_gbp=e['purchase'],display_running_gbp_year=e['display_running'],power_hp=e['hp'],tractive_effort_kn=e['te'],weight_t=e['weight'],speed_kmish_h=e['speed'],default_capacity=e['capacity'],default_cargo=e['default_cargo'],refit_labels=original['cargo_refit_labels'],model_reliability_percent=e['reliability'],vehicle_life_days=e['life_days'],currency_rate=1,inflation_multiplier=1,cost_basis='engine-list callback context; not a measured operating bill')
            P,C,hp,te,w,s=e['purchase'],e['display_running'],e['hp'],e['te'],e['weight'],e['speed']
            r.update(purchase_per_hp=ratio(P,hp),running_per_hp=ratio(C,hp),purchase_per_kn=ratio(P,te),running_per_kn=ratio(C,te),annual_running_to_purchase=ratio(C,P),power_to_weight_hp_t=ratio(hp,w) if hp>0 else None,speed_per_purchase=ratio(s,P),speed_per_running=ratio(s,C),purchase_per_capacity=ratio(P,e['capacity']),running_per_capacity=ratio(C,e['capacity']))
            for horizon in (5,10,20,30):
                r[f'cost_{horizon}y_frozen_display_full_duty_gbp']=P+C*horizon
                r[f'horizon_{horizon}y_within_nominal_vehicle_life']=e['life_days']>=horizon*365 if e['life_days']>=0 else None
            r['lifecycle_limit']='Undiscounted frozen-rate scenario, no resale/replacements/repairs; not actual aged-vehicle lifecycle'
            normalized.append(r)
    # Equal economic profiles, not proven identical historical prototypes.
    signatures={};nextid=0
    for r in normalized:
        sig=tuple(r[k] for k in ('snapshot_year','source_grfid','kind','traction','role','introduction_year','power_hp','tractive_effort_kn','weight_t','speed_kmish_h','default_capacity','default_cargo','railtype','articulated','refit_labels','purchase_gbp','display_running_gbp_year','buildable_for_test_company'))
        if sig not in signatures:nextid+=1;signatures[sig]=f'EP{nextid:05d}'
        r['economic_profile_id']=signatures[sig]
    counts=collections.Counter(r['economic_profile_id'] for r in normalized)
    for r in normalized:r['profile_entry_count']=counts[r['economic_profile_id']]
    return normalized

def comparisons(normalized):
    unique={r['economic_profile_id']:r for r in normalized};profiles=list(unique.values())
    available=[r for r in profiles if r['buildable_for_test_company'] and r['kind'] in ('powered','wagon') and r['introduction_year']<=r['snapshot_year']]
    cells=collections.defaultdict(list)
    for r in available:
        if r['kind']=='powered':band=math.floor(math.log2(max(r['power_hp'],1)))
        else:band=math.floor(math.log2(max(r['default_capacity'],1)))
        capacity_band=math.floor(math.log2(max(r['default_capacity'],1))) if r['role']=='Multiple units' else 0
        cell=(r['snapshot_year'],r['kind'],r['introduction_era'],r['traction'],r['role'],r['railtype'],band,capacity_band)
        cells[cell].append(r)
    metrics=['purchase_per_hp','running_per_hp','purchase_per_kn','running_per_kn','annual_running_to_purchase','speed_per_purchase','speed_per_running','purchase_per_capacity','running_per_capacity']
    outliers=[];ratios=collections.defaultdict(lambda:collections.defaultdict(list))
    for cell,items in cells.items():
        nsets=len({r['source_grfid'] for r in items})
        for r in items:
            scores={m:log_mad(r.get(m),[i.get(m) for i in items]) for m in metrics}
            flagged=[m for m,z in scores.items() if z is not None and abs(z)>3.5 and abs(math.log(r[m]/median([i.get(m) for i in items])))>=math.log(1.5)]
            if flagged:
                outliers.append(dict(r,group_profiles=len(items),group_sets=nsets,flagged_metrics=';'.join(flagged),max_abs_log_mad_z=max(abs(scores[m]) for m in flagged),statistical_status='screen only; investigate role/performance/availability/callbacks',**{m+'_log_mad_z':scores[m] for m in metrics}))
        if nsets>=2 and len(items)>=6:
            for g in {r['source_grfid'] for r in items}:
                subset=[r for r in items if r['source_grfid']==g]
                for m in ('purchase_per_hp','running_per_hp','purchase_per_kn','running_per_kn','annual_running_to_purchase'):
                    denom=median([r.get(m) for r in items]);num=median([r.get(m) for r in subset])
                    if denom and num:ratios[g,cell[0]][m].append(num/denom)
    summary=[]
    for y in sorted({r['snapshot_year'] for r in profiles}):
        for g in SETS:
            for kind in ('powered','wagon'):
                rows=[r for r in available if r['snapshot_year']==y and r['source_grfid']==g and r['kind']==kind]
                row=dict(snapshot_year=y,source_grfid=g,set_name=SETS[g],kind=kind,available_economic_profiles=len(rows),raw_available_entries=sum(r['profile_entry_count'] for r in rows),median_purchase_gbp=median([r['purchase_gbp'] for r in rows]),median_display_running_gbp_year=median([r['display_running_gbp_year'] for r in rows]),median_purchase_per_hp=median([r.get('purchase_per_hp') for r in rows]),median_running_per_hp=median([r.get('running_per_hp') for r in rows]),median_purchase_per_kn=median([r.get('purchase_per_kn') for r in rows]),median_running_per_kn=median([r.get('running_per_kn') for r in rows]),median_annual_running_to_purchase=median([r.get('annual_running_to_purchase') for r in rows]),median_wagon_purchase_per_default_capacity=median([r['purchase_gbp']/r['default_capacity'] for r in rows if r['default_capacity']>0]) if kind=='wagon' else None,comparison_limit='Raw medians mix roles; matched ratios use same year/era/traction/role/railtype/power octave and >=6 profiles across >=2 sets')
                for m in ('purchase_per_hp','running_per_hp','purchase_per_kn','running_per_kn','annual_running_to_purchase'):
                    v=ratios[g,y][m] if kind=='powered' else []
                    row['matched_'+m+'_relative_median']=median(v);row['matched_'+m+'_cells']=len(v)
                summary.append(row)
    return profiles,outliers,summary

def family(name):
    n=name.upper()
    m=re.match(r'(ST\d+|SM\d+|SP\d+|SU\d+|ET\d+|EU\d+|EP\d+|EN\d+|ED\d+)(?:\b|\s|\()',n)
    if m:return m[1]
    if 'CLASS 66' in n or 'BR 266' in n:return 'CLASS66'
    if 'VECTRON' in n:return 'VECTRON'
    return re.sub(r'\s*\((?:STEAM|DIESEL|ELECTRIC|EMU|DMU)\)\s*','',n).strip()

def overlaps(profiles,normalized=None):
    pairs=[]
    if normalized is not None:
        # Economic de-duplication must not erase a named locomotive merely
        # because another prototype/livery has identical economic properties.
        profiles=list(profiles);seen={(r['economic_profile_id'],family(r['vehicle_name'])) for r in profiles}
        for r in normalized:
            f=family(r['vehicle_name']);k=(r['economic_profile_id'],f)
            if (f=='CLASS66' or re.fullmatch(r'(ST|SM|SP|SU|ET|EU|EP|EN|ED)\d+',f)) and k not in seen:profiles.append(r);seen.add(k)
    byyear=collections.defaultdict(list)
    for r in profiles:
        if r['kind']=='powered' and r['buildable_for_test_company'] and r['introduction_year']<=r['snapshot_year'] and r['introduction_year']>=1830:byyear[r['snapshot_year']].append(r)
    for y,rows in byyear.items():
        for a,b in itertools.combinations(rows,2):
            if a['source_grfid']==b['source_grfid'] or a['traction']!=b['traction'] or a['railtype']!=b['railtype'] or a['role']!=b['role']:continue
            if abs(a['introduction_year']-b['introduction_year'])>10:continue
            named=family(a['vehicle_name'])==family(b['vehicle_name'])
            dims=('power_hp','tractive_effort_kn','weight_t','speed_kmish_h','default_capacity')
            diffs={k:abs(a[k]-b[k])/max(abs(a[k]),abs(b[k]),1) for k in dims}
            close=all(diffs[k]<=limit for k,limit in [('power_hp',.1),('tractive_effort_kn',.15),('weight_t',.1),('speed_kmish_h',.1),('default_capacity',.05)])
            if not named and not close:continue
            # Name matches with materially different physics are preserved as
            # distinct-variant evidence, not forced into duplicate equality.
            same_stats=all(a[k]==b[k] for k in dims)
            def dominates(x,z):
                good=(x['purchase_gbp']<=z['purchase_gbp'] and x['display_running_gbp_year']<=z['display_running_gbp_year'] and x['power_hp']>=z['power_hp'] and x['tractive_effort_kn']>=z['tractive_effort_kn'] and x['speed_kmish_h']>=z['speed_kmish_h'] and x['default_capacity']>=z['default_capacity'] and x['weight_t']<=z['weight_t'] and set(x['refit_labels'].split(','))>=set(z['refit_labels'].split(',')))
                return good and any(x[k]!=z[k] for k in ('purchase_gbp','display_running_gbp_year',*dims))
            winner='a' if dominates(a,b) else 'b' if dominates(b,a) else 'tradeoff'
            row=dict(snapshot_year=y,match_type='name_family_and_identical_principal_stats' if named and same_stats else 'name_family_distinct_variant' if named and not close else 'name_family_near_equivalent' if named else 'statistical_neighbour_not_identity',family_a=family(a['vehicle_name']),family_b=family(b['vehicle_name']),principal_stats_identical=same_stats,display_stat_dominance=winner,dominance_limit='Conditional on listed dimensions only; excludes age/reliability/callback duty/hidden rail and refit behaviour',purchase_ratio_b_over_a=ratio(b['purchase_gbp'],a['purchase_gbp']),running_ratio_b_over_a=ratio(b['display_running_gbp_year'],a['display_running_gbp_year']))
            for prefix,r in [('a',a),('b',b)]:
                for key in ('source_grfid','local_vehicle_id','vehicle_name','introduction_year','role','traction','power_hp','tractive_effort_kn','weight_t','speed_kmish_h','default_capacity','purchase_gbp','display_running_gbp_year','refit_labels','model_reliability_percent'):row[prefix+'_'+key]=r[key]
            pairs.append(row)
    return pairs

def train_results(probes,base,normalized):
    results=[];lookup={(r['snapshot_year'],r['runtime_engine_id']):r for r in normalized}
    for y,p in probes.items():
        for key,t in p['trains'].items():
            if 'blocker' in t and 'purchase_actual' not in t:results.append(dict(snapshot_year=y,test_id=key,status='BLOCKED',blocker=t['blocker']));continue
            e=lookup[y,t['runtime_id']];w=lookup.get((y,t['wagon_runtime_id']));n=t['wagon_count'];caps=t['caps'];empty=e['weight_t']+n*(w['weight_t'] if w else 0)
            # Recover the integral sixteenths-tonne cargo property from a
            # 1000-unit API query, rather than multiplying its rounded tonnes.
            load=sum(round(p['cargo'][c]['weight_1000']*16/1000)*amount/16 for c,amount in caps.items())
            loaded=empty+load;te=e['tractive_effort_kn'];speed=e['speed_kmish_h'] if not w or w['speed_kmish_h']<=0 else min(e['speed_kmish_h'],w['speed_kmish_h'])
            row=dict(snapshot_year=y,test_id=key,status='PARTIAL_OR_FAILED' if t['failed'] else 'BUILT_REFITTED_ATTACHED',blocker=t.get('blocker',''),source_grfid=e['source_grfid'],local_vehicle_id=e['local_vehicle_id'],locomotive=e['vehicle_name'],wagon_grfid=w['source_grfid'] if w else '',wagon_local_id=w['local_vehicle_id'] if w else '',wagon=w['vehicle_name'] if w else '',wagon_count=n,cargo_capacities_json=json.dumps({p['cargo'][c]['label']:v for c,v in caps.items()},sort_keys=True),purchase_actual_gbp=t['purchase_actual'],purchase_sum_engine_display_gbp=e['purchase_gbp']+n*(w['purchase_gbp'] if w else 0),built_depot_running_rate_gbp_year=t['depot_running'],moving_empty_rate_peak_gbp_year=t.get('moving_rate'),peak_empty_speed_kmish_h=t.get('peak_empty_speed'),returned_after_empty_motion=t.get('returned'),display_rate_sum_gbp_year=e['display_running_gbp_year']+n*(w['display_running_gbp_year'] if w else 0),length_tiles=t['length_16ths']/16,empty_weight_estimate_t=empty,cargo_weight_continuous_estimate_t=load,loaded_weight_estimate_t=loaded,power_hp=e['power_hp'],tractive_effort_kn=te,speed_upper_bound_kmish_h=speed,flat_low_speed_force_margin_kn=round(te-.025*loaded,3),whole_train_1pct_grade_margin_kn=round(te-.125*loaded,3),whole_train_3pct_grade_margin_kn=round(te-.325*loaded,3),loaded_start_accel_upper_m_s2=round(max(0,(te-.025*loaded)/loaded),4) if loaded>0 else None,physics_status='SCREEN: sum of engine weights and continuous cargo-weight estimate from AXIS API per 1000 units; actual train cargo rounds per part. 25 N/t low-speed rolling+axle; air drag/curves/braking/actual slope occupancy excluded',operation_status='Empty motion observed where present; loaded operation and delivered revenue NOT observed')
            row['purchase_difference_from_display_sum_gbp']=row['purchase_actual_gbp']-row['purchase_sum_engine_display_gbp']
            row['motion_status']='OBSERVED_EMPTY_MOVEMENT' if t.get('moving_rate',-1)>0 else 'NO_POSITIVE_SPEED_IN_WINDOW' if 'moving_rate' in t else 'NOT_REQUESTED'
            row['role_test_limit']='Legacy maximum-power screen; excluded from route economics because not a verified freight role' if key.startswith('heavy_') else 'Role inferred; auto_heavy candidates capped at 140 speed, auto_express uses fastest available locomotive'
            results.append(row)
    return results

def route_results(trains,probes,cargo):
    """Conditional engineering/economic envelopes, never claimed route runs.

    Cruise time follows the JGRPP axis-motion clock, not a real-world tile-km
    assumption. Dwell/fill/grade/duty are explicit sensitivity inputs. Payments
    use packet-size integer formula verified against 27,648 engine API points.
    """
    output=[]
    routes=[('short_industrial_feeder',32,('COAL','GOOD'),False),('medium_coal',128,('COAL',),False),('long_bulk',512,('COAL','IORE'),False),('short_regional_passenger',32,('PASS',),True),('intercity_passenger',256,('PASS',),True),('early_mail',64,('MAIL',),False)]
    for t in trains:
        if t['status']!='BUILT_REFITTED_ATTACHED' or t['test_id'].startswith('heavy_') or t.get('wagon_count',0) not in (0,4,12):continue
        y=t['snapshot_year'];p=probes[y];caps=json.loads(t['cargo_capacities_json']);vmax=t['speed_upper_bound_kmish_h']
        if vmax<=0:continue
        for route,distance,labels,backhaul in routes:
            if route=='long_bulk' and y<1945:continue
            if route=='intercity_passenger' and (not t['test_id'].startswith(('auto_express','auto_unit','en','ed')) or vmax<(120 if y>=1945 else 80)):continue
            for label in labels:
                cap=caps.get(label,0)
                if cap<=0:continue
                cid=next(c for c,v in p['cargo'].items() if v['label']==label)
                profile=cargo.get((y,cid))
                if profile is None:
                    output.append(dict(snapshot_year=y,test_id=t['test_id'],route_id=route,status='BLOCKED',blocker='Batch cargo-income model not validated'));continue
                rail=next(e['railtype'] for e in p['engines'].values() if e['grfid']==t['source_grfid'] and e['local_id']==t['local_vehicle_id'])
                infra=p['infra'].get(rail)
                if not infra:continue
                platform=max(1,math.ceil(t['length_tiles']));station_tiles=2*platform;track_pieces=distance+station_tiles
                # Core default railtype multipliers, checked against the live
                # test-layout infrastructure accessor for every sample.
                mult={0:8,1:12,2:16,3:24}.get(rail)
                calibration=p['infra_final'].get(rail)
                total_calibration=sum(x['track_pieces'] for x in p['infra_final'].values())
                infra_ok=mult is not None and calibration is not None and calibration['track_pieces']>0 and (7*mult*calibration['track_pieces']*(1+jgr_sqrt(total_calibration))>>11)==calibration['monthly_cost']
                rail_month=(7*mult*track_pieces*(1+jgr_sqrt(track_pieces))>>11) if infra_ok else None
                station_month=75*station_tiles*(1+jgr_sqrt(station_tiles))>>7
                infrastructure_annual=(rail_month+station_month)*12 if rail_month is not None else None
                capital=t['purchase_actual_gbp']+distance*infra['track_unit']+station_tiles*infra['station_unit']+2*infra['depot_unit']
                for dwell in (2,10,30):
                    # Two train motion updates/tick; 192*16*4/3 progress per
                    # map-axis tile; 74 ticks/day. This is cruise-only, with no
                    # acceleration/braking/path/queue loss: an optimistic bound.
                    transit=max(1,math.ceil(distance*2048/(74*vmax)))
                    cycle=2*transit+dwell;cycles=365/cycle
                    active_share=2*transit/cycle
                    for fill in (.25,.5,.75,1.0):
                        amount=math.floor(cap*fill);payment=model_income(profile,distance,transit,amount)
                        revenue=payment*cycles*(2 if backhaul else 1)
                        for basis,rate in [('engine_list_proxy',t['display_rate_sum_gbp_year']),('observed_empty_motion_proxy',t.get('moving_empty_rate_peak_gbp_year'))]:
                            if rate is None or rate<=0:continue
                            annual_vehicle=rate*active_share
                            annual_opex=annual_vehicle+infrastructure_annual if infrastructure_annual is not None else None
                            profit=revenue-annual_opex if annual_opex is not None else None
                            breakeven=annual_opex/(model_income(profile,distance,transit,cap)*cycles*(2 if backhaul else 1)) if annual_opex is not None and cap>0 and model_income(profile,distance,transit,cap)>0 else None
                            row=dict(snapshot_year=y,test_id=t['test_id'],route_id=route,status='CALCULATED_CONDITIONAL_ENVELOPE',source_grfid=t['source_grfid'],local_vehicle_id=t['local_vehicle_id'],locomotive=t['locomotive'],cargo=label,capacity_verified=cap,fill_assumption=fill,delivered_units_per_loaded_leg=amount,distance_tiles=distance,grade_assumption_percent=0,cruise_transit_days_lower_bound=transit,loading_unloading_turnaround_days_assumed=dwell,cycle_days_assumed=cycle,cycles_per_year_calculated=round(cycles,5),loaded_return_assumed=backhaul,cost_rate_basis=basis,vehicle_active_share=round(active_share,6),packet_payment_gbp=payment,initial_capital_estimate_gbp=round(capital,2),vehicle_annual_opex_proxy_gbp=round(annual_vehicle,2),infrastructure_annual_model_gbp=infrastructure_annual,total_annual_opex_model_gbp=round(annual_opex,2) if annual_opex is not None else None,revenue_model_gbp=round(revenue,2),annual_profit_model_gbp=round(profit,2) if profit is not None else None,payback_years_model=round(capital/profit,4) if profit is not None and profit>0 else None,breakeven_fill_model=round(breakeven,5) if breakeven is not None else None,infrastructure_model_validated_on_test_layout=infra_ok,model_limits='Not a cargo-delivery observation: full cruise assumed; loaded callback expense, actual supply/acceptance/queue/service/reliability, land/terraform/bridges/signals/finance excluded. Maintenance depends on whole company network size.')
                            for horizon in (5,10,20,30):row[f'net_{horizon}y_frozen_model_gbp']=round(horizon*profit-capital,2) if profit is not None else None
                            output.append(row)
    # Maritime catalogues exist, but this test layout deliberately has no
    # seaway or matched producer/consumer; do not fake ship refit capacity.
    for y in (1830,1849):
        output.append(dict(snapshot_year=y,test_id='maritime_rail_competition',route_id='early_maritime_vs_rail',status='BLOCKED_END_TO_END',blocker='No matched navigable route, refitted ship, controlled cargo supply and accepting destination; catalogue costs alone cannot establish maritime profitability'))
    attempt_evidence=[]
    for path in sorted((ROOT/'.vehicle-audit-runtime/route').glob('*campaign-density.log')):
        text=path.read_text(encoding='utf8',errors='replace')
        records=[line[line.index('ROUTE_'):] for line in text.splitlines() if 'ROUTE_' in line]
        attempt_evidence.extend(path.name+'|'+line for line in records)
        match=re.search(r'route-(\d+)-(\d+)-',path.name)
        blocks=[line.split('|',1)[1] for line in records if line.startswith('ROUTE_BLOCKED|')]
        if blocks:
            output.append(dict(snapshot_year=int(match[2]),test_id='controlled_coal_fixture_'+match[1],route_id='observed_fixture_attempt',status='BLOCKED_FIXTURE_CREATION',blocker=blocks[-1],runtime_engine_id=int(match[1]),evidence_sha256=sha(path),model_limits='Actual disposable GS attempt; CanBuildIndustry was false for coal-producing types. Does not imply the campaign has no existing coal producers. No delivered revenue was observed.'))
        elif any(line.startswith('ROUTE_OBSERVED|') for line in records):
            raise ValueError('A real fixture completed: inspect and explicitly export its observed finance semantics before reporting')
    (R/'vehicle_route_attempt_evidence.log').write_text('\n'.join(attempt_evidence)+'\n',encoding='utf8')
    return output

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--tag',default='motion');args=ap.parse_args()
    source_files=[R/n for n in ('vehicle_roster.csv','newgrf_inventory.json','vehicle_economy_snapshots.csv','vehicle_runtime_evidence.log','vehicle_grf_parameters.json','scenario_economy_settings.json')]+[ROOT/'docs'/n for n in ('VEHICLE_NEWGRF_INVENTORY.md','LOCOMOTIVE_PRICE_AUDIT.md','VEHICLE_BALANCING_RECOMMENDATIONS.md')]
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in source_files}
    base={(r['source_grfid'],int(r['local_vehicle_id'])):r for r in loadcsv(R/'vehicle_roster.csv')}
    inv=json.loads((R/'newgrf_inventory.json').read_text(encoding='utf8'))
    probes={};manifest=[];evidence=[]
    for y in [1830]+[b for a,b in ERAS]:
        path=RUN/f'phase2-{args.tag}-{y}.log';p=parse_probe(path);probes[y]=p
        for i,e in p['engines'].items():assert int(base[e['grfid'],e['local_id']]['runtime_engine_id'])==i
        manifest.append({'year':y,'runtime_log':str(path.relative_to(ROOT)),'sha256':sha(path),'engines':len(p['engines']),'settings':p['settings'],'config_sha256':sha(RUN/f'phase2-{args.tag}-{y}.cfg')})
        evidence.extend(str(y)+'|'+r for r in p['evidence'])
    (R/'vehicle_phase2_runtime_evidence.log').write_text('\n'.join(evidence)+'\n',encoding='utf8')
    props=static_metadata();normalized=normalize(probes,base,props);profiles,outliers,sets=comparisons(normalized);pairs=overlaps(profiles,normalized);trains=train_results(probes,base,normalized)
    writecsv(R/'vehicle_economy_normalized.csv',normalized);writecsv(R/'vehicle_economy_outliers.csv',outliers);writecsv(R/'vehicle_set_comparison.csv',sets);writecsv(R/'vehicle_overlap_comparison.csv',pairs);writecsv(R/'representative_train_tests.csv',trains)
    cargo,validation=cargo_profiles(probes,inv)
    for (y,c),pr in cargo.items():assert 1000*pr['weight_sixteenths']//16==probes[y]['cargo'][c]['weight_1000']
    validation['cargo_weight_profiles_matched']=len(cargo)
    (R/'axis_cargo_economy_phase2.json').write_text(json.dumps({'validation':validation,'profiles':[dict(snapshot_year=y,cargo_id=c,**pr) for (y,c),pr in cargo.items()]},indent=2),encoding='utf8')
    payment_rows=[dict(snapshot_year=y,cargo_id=c,cargo_label=p['cargo'][c]['label'],distance_tiles=d,transit_economy_days=days,income_one_unit_gbp=value) for y,p in probes.items() for (c,d,days),value in p['payments'].items()]
    writecsv(R/'axis_cargo_payment_measurements.csv',payment_rows)
    routes=route_results(trains,probes,cargo);writecsv(R/'route_profitability_tests.csv',routes)
    context_rows=[dict(snapshot_year=y,source_grfid=p['mapping'][i][0],local_vehicle_id=p['mapping'][i][1],stopped_query_valid_for_expense=False,stopped_query_limit='Stopped flag masks speed in GS API; this instantaneous query is not a billed stopped expense',**c) for y,p in probes.items() for i,c in p['contexts'].items()]
    writecsv(R/'vehicle_running_context_tests.csv',context_rows)
    summary=dict(method_version=2,phase1_input_hashes=source_hashes,probe_runs=manifest,raw_train_observations=len(normalized),economic_profiles=len(profiles),statistically_flagged_profiles=len(outliers),overlap_pairs=len(pairs),train_tests=len(trains),built_train_tests=sum(t['status']=='BUILT_REFITTED_ATTACHED' for t in trains),route_envelopes=sum(r['status']=='CALCULATED_CONDITIONAL_ENVELOPE' for r in routes),cargo_validation=validation,config_corrections=json.loads((RUN/'config-corrections.json').read_text()),scope='No original game/scenario/save/GRF changes; statistical screens are not balance verdicts')
    (R/'vehicle_phase2_manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('probe_runs','config_corrections','phase1_input_hashes','cargo_validation')},indent=2));print('Cargo validation',len(validation['errors']),'errors;',validation['api_points_matched'],'points')
if __name__=='__main__':main()
