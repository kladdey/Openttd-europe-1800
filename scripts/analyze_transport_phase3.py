"""Export actual Phase 3 logs; never substitute predicted cargo payments for revenue."""
import csv,hashlib,json,collections,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'docs/research'; RUNTIME=ROOT/'.vehicle-audit-runtime/phase3'
FINAL_TAGS={'rail-coal-ledger','horse-coal-final','horse-coal-fleet4','horse-passenger-final2','ship-pax-final','rail-lodi','horse-lodi','horse-mail','ship-mail','ship-barque','rail-mail','rail-grasshopper','rail-general','rail-general2','horse-general','rail-medium','ship-bulk','horse-local','rail-local','rail-coal-keep'}
FINAL_TAGS.update({'horse-local3','horse-local-bridge3','horse-existing-road','horse-city-road','horse-london','rail-coast','horse-coast','rail-wood-final','rail-wood-grasshopper'})
FINAL_TAGS.update({'rail-coal-12-brake','rail-coal-24-brake','ship-schooner'})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with (DATA/name).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def day_date(n):return datetime.date.fromordinal(int(n)-365).isoformat()
def records(path):
    for line in path.read_text(errors='replace').splitlines():
        if 'P3_' in line:yield line[line.index('P3_'):].split('|')
def collect(path):
    data=collections.defaultdict(list)
    for row in records(path):data[row[0]].append(row[1:])
    return data
def export():
    settings=json.loads((DATA/'scenario_economy_settings.json').read_text()); dates=settings['DATE'][0]; offset=dates['date']-dates['economy_date']
    manifest=DATA/'transport_phase3_inputs.json'
    if not manifest.exists():
        prior=[p for p in (ROOT/'docs').rglob('*') if p.is_file() and 'transport' not in p.name.lower() and 'TRANSPORT' not in p.name]
        manifest.write_text(json.dumps({'prior_research_sha256':{str(p.relative_to(ROOT)):sha(p) for p in prior},'calendar_day_offset':offset,'original_calendar_start':day_date(dates['date']),'original_economy_start':day_date(dates['economy_date'])},indent=2))
    rows=[];growth=[];attempts=[];summary=[];evidence=[];sources=[]
    for path in sorted(RUNTIME.rglob('*.log')):
        d=collect(path)
        raw=path.read_text(errors='replace')
        error=next((line for line in raw.splitlines() if 'Your script made an error:' in line or '[S] Error ' in line),'')
        if not d:
            if error:
                attempts.append(dict(tag=path.stem,case='Harness compilation/initialization',selected=False,built=False,years_observed=0,completed=False,status='BLOCKED / NOT TESTED',blocker=error,source_log=str(path.relative_to(ROOT))))
                evidence.append(path.stem+'|HARNESS_ERROR|'+error)
                sources.append({'log':str(path.relative_to(ROOT)),'sha256':sha(path),'selected_financial_case':False})
            continue
        tag=path.stem;selected=tag in FINAL_TAGS
        sources.append({'log':str(path.relative_to(ROOT)),'sha256':sha(path),'selected_financial_case':selected})
        evidence.extend(tag+'|'+('|'.join(r)) for r in records(path))
        case=d['P3_CASE'][0] if d['P3_CASE'] else ['UNKNOWN']*7
        why='; '.join('|'.join(r) for r in d['P3_BLOCKED']) or error
        test_status='VERIFIED IN GAME' if d['P3_YEAR'] or (d['P3_DONE'] and d['P3_INDUSTRY']) else ('ENGINE-CALCULATED' if d['P3_DONE'] and d['P3_COAST'] else 'BLOCKED / NOT TESTED')
        attempts.append(dict(tag=tag,case=case[0],selected=selected,built=bool(d['P3_BUILT']),years_observed=len(d['P3_YEAR']),completed=bool(d['P3_SERVICE_DONE'] or d['P3_DONE']),status='BLOCKED / NOT TESTED' if why else test_status,blocker=why or ('No completed financial year; inspect evidence' if not d['P3_YEAR'] and not d['P3_DONE'] else ''),source_log=str(path.relative_to(ROOT))))
        if not selected or not d['P3_BUILT']:continue
        b=d['P3_BUILT'][0]; fleet=int(d['P3_FLEET'][0][1]) if d['P3_FLEET'] else 1
        ledgers={int(r[1]):list(map(int,r[2].rstrip(',').split(',')))[:15] for r in d['P3_LEDGER']}
        prev_cash=int(b[11]); prev_loan=int(b[12]); initialcash=prev_cash; capex=int(b[3])+int(b[4]); cumulative=0; actual_payback=''; annual=[]
        for r in d['P3_YEAR']:
            year=int(r[1]); cash=int(r[5]);loan=int(r[6]);net=cash-prev_cash-(loan-prev_loan);cumulative+=net
            ledger=ledgers.get(year);income=-sum(ledger[i] for i in [7,8,9,10,14]) if ledger else int(r[2]);operating=sum(ledger[i] for i in [2,3,4,5,6,11,12,13]) if ledger else -int(r[3])+300
            n=year-int(d['P3_YEAR'][0][1])+1
            if cumulative>=capex and not actual_payback:actual_payback=n
            common=dict(tag=tag,case=case[0],mode=case[1],cargo_id=case[2],origin_id=case[3],destination_id=case[4],economy_year=year,calendar_period_start=day_date((datetime.date(year,1,1).toordinal()+365)+offset),calendar_period_end_exclusive=day_date((datetime.date(year+1,1,1).toordinal()+365)+offset),status='VERIFIED IN GAME')
            row=dict(**common,engine_id=b[1],vehicle_name=b[2].strip(),fleet_count=fleet,capacity_per_vehicle_or_train=int(b[5]),origin_x=b[6],origin_y=b[7],destination_x=b[8],destination_y=b[9],endpoint_manhattan_tiles=abs(int(b[6])-int(b[8]))+abs(int(b[7])-int(b[9])),path_nodes=b[10],infrastructure_capital_gbp=int(b[3]),fleet_capital_gbp=int(b[4]),revenue_gbp=income,operating_expenses_gbp=operating,ledger_net_gbp=income-operating,net_cash_change_gbp=net,cash_gbp=cash,loan_gbp=loan,actual_property_expense_gbp=ledger[6] if ledger else '',actual_vehicle_running_expense_gbp=sum(ledger[2:6]) if ledger else '',actual_interest_gbp=ledger[11] if ledger else '',actual_other_expense_gbp=ledger[12] if ledger else '',monthly_maintenance_quote_gbp=int(r[7]),maintenance_quote_status='ENGINE-CALCULATED; instantaneous rate, not annual paid',sampled_lead_vehicle_max_load=r[8],sampled_lead_loaded_fraction=round(int(r[9])/int(r[10]),5) if int(r[10]) else '',sampled_load_decreases=r[11],lead_station_a_visits=r[12],lead_station_b_visits=r[13],vehicle_age_days=r[14],lead_reliability_percent=r[15],delivered_cargo_units=r[16] if len(r)>16 else '',delivery_verified=int(r[8])>0 and len(r)>16 and int(r[16])>0 and income>0,expense_method='Annual finance ledger' if ledger else 'Income minus observed cash change; includes Other/interest; boundary timing applies',source_log=str(path.relative_to(ROOT)))
            rows.append(row);annual.append(row)
            row['financial_fields_status']='Annual finance ledger observed in game; arithmetic totals' if ledger else 'ENGINE-CALCULATED expense total: measured quarterly expenses plus verified fixed Other 300/year'
            row['expense_method']='Annual finance ledger' if ledger else 'Quarterly operating expenses plus fixed Other 300/year; not inferred from transport-payment formula'
            row['ledger_raw_json']=json.dumps(ledger) if ledger else ''
            length=d['P3_TRAIN_LENGTH'][0] if d['P3_TRAIN_LENGTH'] else None
            row['configured_wagons']=length[1] if length else ('4' if case[1]=='rail' else '')
            row['actual_train_length_tiles']=int(length[2])/16 if length else 'UNVERIFIED'
            row['platform_length_tiles']=length[3] if length else ('2' if case[1]=='rail' else '')
            monthly=[m for m in d['P3_MONTH'] if int(m[3])>0]
            speeds=[int(m[4]) for m in monthly]
            row['whole_run_loaded_monthly_sample_peak_speed']=max(speeds) if speeds else 'UNVERIFIED'
            row['whole_run_loaded_monthly_sample_min_positive_speed']=min((s for s in speeds if s>0),default='UNVERIFIED')
            row['speed_sample_scope']='Whole run monthly point samples, not annual average or sustained grade performance'
            row['calendar_service_built_date']=day_date(int(b[13])+offset)
            row['quoted_maintenance_vs_actual_expenses']='Annual ledger Property is paid amount where populated; monthly quote is a separate instantaneous rate'
            growth.append(dict(**common,years_after_start=n,cash_gbp=cash,loan_gbp=loan,cumulative_post_construction_cash_profit_gbp=cumulative,initial_capital_investment_gbp=capex,capital_repaid_by_observed_cash_profit=cumulative>=capex,headroom_with_max_loan_gbp=cash+300000-loan,headroom_status='ENGINE-CALCULATED from observed bank and unchanged loan ceiling; not demonstrated expansion',fleet_policy='No expansion, replacement or additional borrowing; initial idle-loan repayment only',source_log=str(path.relative_to(ROOT))))
            prev_cash=cash;prev_loan=loan
        if annual:
            last=annual[-1];summary.append(dict(tag=tag,case=case[0],mode=case[1],status='VERIFIED IN GAME',observed_years=len(annual),initial_capital_gbp=capex,mean_annual_revenue_gbp=round(sum(x['revenue_gbp'] for x in annual)/len(annual),2),mean_annual_net_cash_gbp=round(cumulative/len(annual),2),cumulative_cash_profit_gbp=cumulative,observed_capital_payback_years=actual_payback or 'NOT REACHED',first_year_delivery_verified=annual[0]['delivery_verified'],last_year_reliability_percent=last['lead_reliability_percent'],scope='Single route/company; geographically different routes are not matched modal experiments'))
            common=annual[1:5]
            summary[-1].update(common_period='Economy 1801-1804, mapped to calendar 1831-1834; excludes construction year',common_period_years=len(common),common_mean_revenue_gbp=round(sum(x['revenue_gbp'] for x in common)/len(common),2) if common else '',common_mean_net_cash_gbp=round(sum(x['net_cash_change_gbp'] for x in common)/len(common),2) if common else '',common_mean_delivered_units=round(sum(int(x['delivered_cargo_units']) for x in common)/len(common),2) if common else '')
    expansion=[];transition=RUNTIME/'horse-transition/horse-transition.log'
    if transition.exists():
        first=None;extra=0;capex=0;ledger=None;stage='horse fleet'
        for rec in records(transition):
            p=rec[1:]
            if rec[0]=='P3_BUILT':
                capital=int(p[3])+int(p[4]);capex+=capital
                if first is None:first=(int(p[11]),int(p[12]))
                else:extra+=capital;stage='horse fleet plus railway'
            if rec[0]=='P3_LEDGER':ledger=list(map(int,p[2].rstrip(',').split(',')))[:15]
            if rec[0]=='P3_YEAR' and first:
                cash=int(p[5]);loan=int(p[6]);profit=cash-loan-(first[0]-first[1])+extra
                g=dict(tag='horse-transition',case=p[0],mode='road then road and rail',cargo_id='14 then 14+0',origin_id='438 then 189',destination_id='456 then 96',economy_year=int(p[1]),calendar_period_start=day_date(datetime.date(int(p[1]),1,1).toordinal()+365+offset),calendar_period_end_exclusive=day_date(datetime.date(int(p[1])+1,1,1).toordinal()+365+offset),status='VERIFIED IN GAME',years_after_start=int(p[1])-1800+1,cash_gbp=cash,loan_gbp=loan,cumulative_post_construction_cash_profit_gbp=profit,initial_capital_investment_gbp=capex,capital_repaid_by_observed_cash_profit=profit>=capex,headroom_with_max_loan_gbp=cash+300000-loan,headroom_status='ENGINE-CALCULATED from observed bank',fleet_policy='Eight horses continue; add Planet passenger railway after ten years, using existing cash',source_log=str(transition.relative_to(ROOT)))
                growth.append(g)
                expansion.append(dict(g,stage=stage,revenue_gbp=-sum(ledger[i] for i in [7,8,9,10,14]) if ledger else '',operating_expenses_gbp=sum(ledger[i] for i in [2,3,4,5,6,11,12,13]) if ledger else '',newest_vehicle_profit_last_year_gbp=p[4],delivered_company_units=p[16],cargo_unit_warning='Company aggregate mixes tonnes and passengers after expansion; do not interpret as single-cargo throughput'))
    write('transport_expansion_test.csv',expansion)
    write('transport_route_results.csv',rows);write('company_growth_simulations.csv',growth);write('transport_mode_comparison.csv',summary);write('transport_test_attempts.csv',attempts)
    inv=collect(RUNTIME/'inventory.log')
    write('transport_existing_industries.csv',[dict(industry_id=r[0],type_id=r[1],industry_type=r[2],x=r[3],y=r[4],produced_cargo_and_previous_month_units=r[5],accepted_cargo=r[6],status='VERIFIED IN GAME') for r in inv['P3_INDUSTRY']])
    write('transport_existing_towns.csv',[dict(town_id=r[0],name=r[1],x=r[2],y=r[3],population=r[4],status='VERIFIED IN GAME') for r in inv['P3_TOWN']])
    write('transport_available_1830.csv',[dict(engine_id=r[0],mode_id=r[1],name=r[2],purchase_gbp=r[3],quoted_running_gbp_year=r[4],default_capacity=r[5],quoted_speed=r[6],status='VERIFIED IN GAME; engine catalogue, not refitted capacity or annual expense') for r in inv['P3_VEHICLE']])
    (DATA/'transport_economic_settings.json').write_text(json.dumps({'embedded_scenario':settings,'runtime_confirmation':dict(inv['P3_SETTING']),'company_initial_cash_loan_maxloan':inv['P3_COMPANY'],'calendar_day_offset':offset},indent=2))
    coast=collect(RUNTIME/'coastal-industry-check/coastal-industry-check.log')
    write('transport_coastal_coal_sites.csv',[dict(industry_id=r[0],name=r[1],produces_coal=r[2],accepts_coal=r[3],has_builtin_dock=r[4],unmodified_coast_dock_sites=r[5],example_site=r[6],status='ENGINE-CALCULATED; live command test mode, radius 5, no terraforming') for r in coast['P3_COAST']])
    (DATA/'transport_runtime_evidence.log').write_text('\n'.join(evidence)+'\n',encoding='utf8')
    (DATA/'transport_log_manifest.json').write_text(json.dumps(sources,indent=2))
    frozen={};configs=[]
    for p in sorted(RUNTIME.glob('*/game/p3/main.nut')):
        text=p.read_text(encoding='utf8');h=sha(p);frozen[h]=text
        home=p.parents[2];m=home/'run_manifest.json'
        config=json.loads(m.read_text()) if m.exists() else {'tag':home.name,'constants':text.split('// All services',1)[0].split('class TransportProbe',1)[0],'note':'Manifest reconstructed from retained per-case source'}
        config['script_sha256']=h;configs.append(config)
    (DATA/'transport_harness_sources.json').write_text(json.dumps(frozen,indent=2))
    (DATA/'transport_run_configs.json').write_text(json.dumps(configs,indent=2))
    print(json.dumps({'annual_rows':len(rows),'cases_with_annual_observations':len(summary),'attempts':len(attempts),'delivery_verified_rows':sum(r['delivery_verified'] for r in rows),'calendar_offset_days':offset,'summary':summary},indent=2))
if __name__=='__main__':export()
