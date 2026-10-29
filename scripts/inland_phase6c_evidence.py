"""Reconcile retained JGRPP observations into portable Phase 6C evidence.

Raw cases remain under .work/inland6c. No game installation files are written.
Operating profit includes running, property maintenance, interest and other
operating expense; excludes construction and vehicle purchase. GBP rate is 1.
"""
import csv,json,re
from pathlib import Path
from inland_phase6c_runtime import ROOT,BASE,sha
from industrial_phase6b_plan import write_csv


def main():
    proof=json.loads((BASE/'proof.json').read_text());proof_home=Path(proof['case'])
    proof['engine_log_sha256']=sha(proof_home/'engine.log')
    proof['manifest']=json.loads((proof_home/'manifest.json').read_text())
    (ROOT/'docs/research/inland_house_replacement_proof.json').write_text(json.dumps(proof,indent=2))
    inventory_log=sorted(BASE.glob('inventory*/engine.log'))[-1]
    (ROOT/'docs/research/inland_retail_availability.json').write_text(json.dumps(dict(case=str(inventory_log.parent),engine_log_sha256=sha(inventory_log),
        measurements=[l for l in inventory_log.read_text(encoding='utf8').splitlines() if 'M6 TYPE|' in l],
        fields='local ID | resolved runtime type | deity CanBuildIndustry | company CanBuildIndustry | accepted cargo labels',evidence='VERIFIED IN GAME'),indent=2))
    placement_csv=ROOT/'docs/research/inland_market_placements.csv'
    with placement_csv.open(encoding='utf8',newline='') as f:markets=list(csv.DictReader(f))
    placement_logs=[(p,p.read_text(encoding='utf8')) for p in sorted(BASE.glob('placement*/engine.log'))]
    receipts=[]
    for market in markets:
        prefix='M6 MARKET|'+'|'.join(market[k] for k in ['request_id','industry_id','local_id','town_id','tile','house_id','population_before','population_after'])+'|'
        matches=[(p,line) for p,text in placement_logs for line in text.splitlines() if prefix in line]
        assert matches,market['industry_id']
        path,line=matches[-1];market['engine_case']=str(path.parent)
        receipts.append(dict(industry_id=int(market['industry_id']),case=str(path.parent),engine_log_sha256=sha(path),measurement=line))
    write_csv(placement_csv,markets)
    (ROOT/'docs/research/inland_market_engine_receipts.json').write_text(json.dumps(receipts,indent=2))
    diagnostic=[]
    for path in sorted(BASE.glob('archived-*.json')):
        j=json.loads(path.read_text())
        if 'engine_case' not in j:continue
        home=Path(j['engine_case']);diagnostic.append(j|dict(engine_log_sha256=sha(home/'engine.log'),scope='Superseded diagnostic; excluded from final economic comparison'))
    (ROOT/'docs/research/inland_superseded_diagnostics.json').write_text(json.dumps(diagnostic,indent=2))
    files=sorted(BASE.glob('service-*-fleet*.json'))
    results=[];annual=[];deliveries=[];retained=[]
    for path in files:
        j=json.loads(path.read_text());home=Path(j['engine_case']);log=(home/'engine.log').read_text(encoding='utf8')
        manifest=json.loads((home/'manifest.json').read_text());events=j['events']
        capital=next((list(map(int,e.split('|')[1:])) for e in events if e.startswith('CAPITAL|')),None)
        completed=next((e for e in events if e.startswith('COMPLETE|')),None)
        initial=next((e for e in events if e.startswith('INITIAL|')),None)
        engines=sorted(set(re.findall(r'P4_BUILT\|[^|]+\|(\d+)\|([^|]+)',log)))
        scope='Technical functionality only' if j['grant'] else 'Superseded horse-tram diagnostic' if any(e=='315' for e,n in engines) else 'Normal starting-finance comparison'
        first_chain=next((int(e.split('|')[1]) for e in events if e.startswith('CHAIN_PAID|')),None)
        failure='; '.join(e for e in events if e.startswith('SERVICE_ERROR|'))
        key=home.name;yearrows=[]
        for event in events:
            if not event.startswith('FINANCE|'):continue
            _,year,cash,loan,value,ledger=event.split('|');a=list(map(int,ledger.rstrip(',').split(',')));assert len(a)==15
            revenue=-sum(a[7:11]);running=sum(a[2:6]);operating=running+a[6]+sum(a[11:14])+a[14]
            r=dict(test_id=key,case=j['case'],economy_year=int(year),calendar_year=int(year)+30,
                revenue_gbp=revenue,vehicle_running_gbp=running,infrastructure_property_gbp=a[6],interest_gbp=a[11],other_expense_gbp=a[12],
                operating_expense_gbp=operating,operating_profit_gbp=revenue-operating,construction_gbp=a[0],vehicle_purchase_gbp=a[1],
                closing_cash_gbp=int(cash),closing_loan_gbp=int(loan),quarterly_company_value_gbp=int(value),grant_requested=j['grant'],
                evidence='VERIFIED IN GAME',engine_case=str(home))
            yearrows.append(r);annual.append(r)
        # Validate observation chronology rather than silently correcting old labels.
        assert len({r['economy_year'] for r in yearrows})==len(yearrows),key
        for event in j['paid_events']:
            tag,v,delta,d,tile=event.split('|');label,a,b=tag.split('_')
            leg=next(l for l in j['legs'] if l['label']==label and l['a']==int(a) and l['b']==int(b))
            deliveries.append(dict(test_id=key,case=j['case'],cargo=label,source_industry=int(a),destination_industry=int(b),mode=leg['mode'],
                manhattan_tiles=leg['manhattan'],vehicle_id=int(v),observed_profit_increase_gbp=int(delta),distance_to_destination=int(d),
                vehicle_tile=int(tile),load_observed=True,evidence='VERIFIED IN GAME',payment_caveat='Sampled net vehicle-profit increase near destination, not whole-year route revenue',engine_case=str(home)))
        recovery='NOT OBSERVED' if capital else 'NOT TESTED: construction blocked'
        if capital:
            total=0
            for r in yearrows:
                total+=r['operating_profit_gbp']
                if total>=sum(capital[:2]):recovery=f'Observed cumulative operating surplus covered capital after {len([x for x in yearrows if x["economy_year"]<=r["economy_year"]])} years';break
        results.append(dict(test_id=key,case=j['case'],status=j['status'],comparison_scope=scope,engines='; '.join(e+': '+n for e,n in engines),scenario_sha256=j['scenario_sha256'],
            vehicle_policy=j['vehicle_policy'],road_fleet_per_leg=j['road_fleet_per_leg'],origin_load_policy=j.get('origin_load_policy','partial/empty departures allowed'),
            grant_requested=j['grant'],initial_state=initial,infrastructure_capital_gbp=capital[0] if capital else '',vehicle_capital_gbp=capital[1] if capital else '',
            years_observed=len(yearrows),paid_legs=len(j['paid_events']),planned_legs=len(j['legs']),all_legs_first_paid_after_economy_days=first_chain if first_chain is not None else '',
            revenue_sum_gbp=sum(r['revenue_gbp'] for r in yearrows),operating_profit_sum_gbp=sum(r['operating_profit_gbp'] for r in yearrows),
            capital_recovery=recovery,failure=failure,completion=completed or '',engine_case=str(home),engine_log_sha256=sha(home/'engine.log')))
        retained.append(j|dict(manifest=manifest,engine_log_sha256=sha(home/'engine.log'),measurements=[l for l in log.splitlines() if any(k in l for k in ['M6 ','I6 CONTROL_','I6 PERIOD_ENGINE','RESULT|','RAIL_RESULT','ROAD_RESULT','SHIP_RESULT','BUILD_ERROR','Error '])]))
    write_csv(ROOT/'docs/research/inland_route_results.csv',results)
    write_csv(ROOT/'docs/research/inland_route_finances.csv',annual)
    write_csv(ROOT/'docs/research/inland_paid_deliveries.csv',deliveries)
    (ROOT/'docs/research/inland_gameplay_evidence.json').write_text(json.dumps(retained,indent=2),encoding='utf8')
    copper=json.loads((BASE/'controlled-copper-regression.json').read_text())
    (ROOT/'docs/research/inland_copper_regression.json').write_text(json.dumps(copper,indent=2))
    print('Routes',len(results),'annual ledgers',len(annual),'observed paid legs',len(deliveries))


if __name__=='__main__':main()
