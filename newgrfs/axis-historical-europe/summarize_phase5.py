# SPDX-License-Identifier: GPL-2.0-only
"""Summarize retained engine observations and verify protected installed assets."""
import csv
import hashlib
import json
import re
from pathlib import Path
import sys
import tarfile
from integration_test import ROOT, REPO, M, sha, write_matrix


def write(name, rows):
    assert rows
    with (REPO / 'docs/research' / name).open('w', newline='', encoding='utf8') as f:
        fields=list(dict.fromkeys(k for row in rows for k in row))
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def main():
    data=REPO/'docs/research'
    inv=json.loads((data/'newgrf_inventory.json').read_text())
    checked={}
    fingerprint_drift=[]
    for f in inv['fingerprints']:
        p=Path(f['path']);current=sha(p)
        if current!=f['sha256']:
            # Older audit fingerprints are not a new-run baseline. Never reset
            # a user's current config just to satisfy a historical checksum.
            assert p.suffix=='.cfg',str(p)
            fingerprint_drift.append(dict(path=str(p),historical_sha256=f['sha256'],current_sha256=current,
                                          last_write_unix=p.stat().st_mtime))
    for f in inv['installed_newgrfs']:
        p=Path(f['path']);checked.setdefault(str(p),sha(p))
        assert checked[str(p)]==f.get('archive_sha256',f['sha256']),str(p)
    ref=json.loads((data/'scenario_vehicle_references.json').read_text())
    assert sha(Path(ref['scenario']))==ref['sha256']
    sys.path.insert(0,str(REPO/'scripts'))
    from validate_vehicle_audit import grfmd5
    matched=[]
    for r in ref['references']:
        name=r['filename'].replace('\\','/');outer,sep,member=name.partition('.tar/')
        root=ROOT/'.work/integration/newgrf'
        if sep:
            with tarfile.open(root/(outer+'.tar')) as tf:
                members=[m for m in tf.getmembers() if m.name.replace('\\','/').lstrip('./').lower()==member.lower()]
                assert len(members)==1
                content=tf.extractfile(members[0]).read()
        else:content=(root/name).read_bytes()
        assert grfmd5(content)==r['md5'];matched.append(r['grfid'])
    prior=json.loads((data/'transport_phase4_inputs.json').read_text())['prior_research_sha256']
    authorized={'docs\\AXIS_HISTORICAL_IMPLEMENTATION.md'}
    unchanged=[]
    for p,h in prior.items():
        if p not in authorized:assert sha(REPO/p)==h,p;unchanged.append(p)
    write_matrix()
    annual=[];attempts=[];controls=[]
    paths=[ROOT/'gameplay-result.json']+sorted(ROOT.glob('gameplay-*-result.json'))+sorted(ROOT.glob('stock-gameplay-*-result.json'))
    for path in paths:
        report=json.loads(path.read_text())
        for r in report['results']:
            tag=path.stem+'/'+r['case']
            commission=next((s.split('P4_COMMISSION|')[1].split('|') for s in r['lines'] if 'P4_COMMISSION|' in s),None)
            blockers=[s for s in r['lines'] if 'BLOCKED' in s]
            attempts.append(dict(test=tag,cargo=r['cargo'],mode=r['mode'],evidence=r['evidence'],
                                 actual_paid_delivery=r['paid_delivery_verified'],observed_years=len(r['years']),
                                 infrastructure_gbp=commission[2] if commission else '',fleet_gbp=commission[3] if commission else '',
                                 blocker='; '.join(blockers) if blockers else ('No revenue observed; inspect retained full log' if not r['paid_delivery_verified'] else ''),
                                 source=path.name,log=r['log'],log_sha256=r['log_sha256']))
            for year in r['years']:
                l=year['ledger'];revenue=-sum(l[7:11])-l[14];opex=sum(l[2:7])+sum(l[11:14])
                annual.append(dict(test=tag,stock_control=r.get('stock_control',False),controlled=r.get('controlled',False),
                                   mode=r['mode'],cargo=r['cargo'],year=year['year'],revenue_gbp=revenue,
                                   running_gbp=sum(l[2:6]),property_gbp=l[6],interest_gbp=l[11],other_gbp=l[12],
                                   operating_profit_gbp=revenue-opex,capital_gbp=l[0]+l[1],
                                   cash_gbp=year['cash'],loan_gbp=year['loan'],delivered_units=year['delivered'],
                                   evidence='VERIFIED BY ENGINE TEST',ledger_json=json.dumps(l),source=path.name))
    for name in ['coal_rail','grain_horse','timber_rail']:
        h=json.loads((ROOT/f'gameplay-controlled-{name}-result.json').read_text())['results'][0]
        s=json.loads((ROOT/f'stock-gameplay-controlled-{name}-result.json').read_text())['results'][0]
        for a,b in zip(h['years'],s['years']):
            controls.append(dict(case=name,year=a['year'],historical_delivered=a['delivered'],stock_delivered=b['delivered'],
                                 historical_revenue=-sum(a['ledger'][7:11]),stock_revenue=-sum(b['ledger'][7:11]),
                                 historical_cash=a['cash'],stock_cash=b['cash'],
                                 note='Same flat-map seed/fixture coordinates; actual outcomes, not assumed identical RNG'))
    write('axis_historical_gameplay_years.csv',annual)
    write('axis_historical_gameplay_attempts.csv',attempts)
    write('axis_historical_stock_controls.csv',controls)
    matrix=json.loads((data/'axis-2.3.1-extreme-classic.json').read_text())['industries']
    items={i['id']:i for i in matrix}
    items['steel_mill']=dict(model_class='IndustrySecondary',inputs=['IRON','COKE'],outputs=[['STEL',3],['SLAG',1]])
    graph=[]
    for year in [1830,1850,1870,1900,1925,1950,1975,2000,2025]:
        enabled={k:i for k,i in items.items() if M['industries'][k]['earliest_year']<=year and M['industries'][k]['allow_map_generation']}
        reachable={'PASS','MAIL'};old=None
        while old!=reachable:
            old=reachable.copy()
            for name,i in enabled.items():
                ready=i['model_class'].startswith(('IndustryPrimary','IndustryTownProducer')) or bool(set(i['inputs'])&reachable)
                if name=='steel_mill':ready={'IRON','COKE'}<=reachable
                if ready:reachable.update(c for c,_ in i['outputs'])
        for name,i in enabled.items():
            graph.append(dict(year=year,industry=name,accepted=' '.join(i['inputs']),produced=' '.join(c for c,_ in i['outputs']),
                              missing_input_sources=' '.join(sorted(set(i['inputs'])-reachable)),
                              evidence='MODELLED',note='Potential cargo-label reachability only; optional boosts, recipes, site availability and town sinks need runtime verification'))
    write('axis_historical_chain_review.csv',graph)
    models=json.loads((ROOT/'.work/historical-model.json').read_text())['BASIC_TEMPERATE']['industries']
    languages=[dict(re.findall(r'(?m)^(STR_\w+)\s*:(.*)$',p.read_text()))
               for p in (ROOT/'.work/source/generated/lang').glob('english*.lng')]
    by_name={}
    for name,item in models.items():
        token=re.fullmatch(r'string\((STR_\w+)\)',item['properties']['name'])
        if token:
            for english in languages:
                if token[1] in english:by_name[english[token[1]].strip().lower()]=name
        elif item['properties']['name'].startswith('TTD_STR_INDUSTRY_NAME_'):
            by_name[item['properties']['name'].removeprefix('TTD_STR_INDUSTRY_NAME_').replace('_',' ').lower()]=name
    existing=[]
    with (data/'transport_existing_industries.csv').open(newline='',encoding='utf8') as f:
        for row in csv.DictReader(f):
            name=by_name.get(row['industry_type'].strip().lower())
            rule=M['industries'].get(name,{})
            permitted=rule.get('earliest_year',99999)<=1830 and rule.get('allow_map_generation',False)
            existing.append(dict(industry_id=row['industry_id'],display_name=row['industry_type'],source_id=name or 'UNRESOLVED',
                                 x=row['x'],y=row['y'],matches_1830_construction_policy=permitted if name else 'UNVERIFIED',
                                 evidence='STATICALLY VERIFIED' if name else 'BLOCKED',
                                 note='Read-only English-name/source crosswalk. Availability never deletes an existing instance.'))
    write('axis_historical_existing_industry_review.csv',existing)
    result=dict(passed=True,original_asset_paths_checked=len(checked),original_fingerprints=len(inv['fingerprints']),
                original_scenario_sha256=sha(Path(ref['scenario'])),original_grf_identities_verified=matched,
                historical_configuration_fingerprint_drift=fingerprint_drift,
                protected_prior_research_unchanged=len(unchanged),authorized_report_update=list(authorized),
                annual_observation_rows=len(annual),matched_control_years=len(controls))
    result['original_instances_reviewed']=len(existing)
    result['original_instances_unresolved']=sum(r['source_id']=='UNRESOLVED' for r in existing)
    result['original_instances_outside_1830_policy']=sum(r['matches_1830_construction_policy'] is False for r in existing)
    (ROOT/'preservation-phase5-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
