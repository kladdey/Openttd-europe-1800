"""Publish measured company ledgers and fleet duty; never estimate delivery income."""
import collections,csv,datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/research';BASE=ROOT/'.vehicle-audit-runtime/phase4'
def readcsv(name):
    with (D/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    if not rows:raise ValueError('No evidence rows for '+name)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (D/name).open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def date(day):return datetime.date.fromordinal(int(day)-365).isoformat()
def records(path):
    for line in path.read_text(errors='replace').splitlines():
        for mark in ('P4_','P3_BLOCKED','P3_WATER'):
            if mark in line:yield line[line.index(mark):].split('|');break
def analyze():
    out=[];attempts=[];evidence=[];configs=[];frozen={};openings=[];months=[];route_details=[]
    for manifest in sorted(BASE.glob('*/manifest.json')):
        home=manifest.parent;tag=home.name;m=json.loads(manifest.read_text());p=home/'game.log'
        if not p.exists():continue
        records_all=list(records(p));group=collections.defaultdict(list)
        for r in records_all:group[r[0]].append(r[1:]);evidence.append(tag+'|'+'|'.join(r))
        raw=p.read_text(errors='replace');error=next((l for l in raw.splitlines() if '[S] Error ' in l or 'Your script made an error:' in l),'')
        configs.append(m);code=(home/'game/p3/main.nut').read_text(encoding='utf8');frozen[m['script_sha256']]=code
        conf=m['configuration'];comm={};commissioned=collections.defaultdict(list)
        for r in group['P4_COMMISSION']:
            comm.setdefault(int(r[1]),r);commissioned[int(r[1])].append(r)
        built={r[0]:r for r in group['P4_BUILT']};duty={}
        for r in group['P4_DUTY']:
            key=(int(r[0]),int(r[1]))
            if key not in duty:duty[key]=r.copy()
            else:
                for i in range(3,12):duty[key][i]=str(int(duty[key][i])+int(r[i]))
        started={int(r[0]):r for r in group['P4_START']}
        why='; '.join('|'.join(r) for r in group['P3_BLOCKED']) or '; '.join('|'.join(r) for r in group['P4_BLOCKED']) or error
        complete=bool(group['P4_DONE']);is_pilot=tag in ('main-pilot','three-credit-final')
        for c,cfg in enumerate(conf['routes']):
            com=comm.get(c);has_service=com is not None
            attempts.append(dict(tag=tag,case=m['case'],company_id=c,mode=cfg['mode'],cargo_id=cfg['cargo'],status='VERIFIED IN GAME' if has_service and group['P4_YEAR'] else 'BLOCKED',commissioned=has_service,completed=complete,pilot=is_pilot,blocker=why if not has_service else '',verification_procedure='Replay this retained configuration with the frozen source; inspect station approaches/depot connections and require loaded cargo plus credited revenue',source_log=str(p.relative_to(ROOT))))
            if com:
                b=built[com[0]]
                route_details.append(dict(tag=tag,case=m['case'],company_id=c,mode=cfg['mode'],cargo_id=cfg['cargo'],origin=cfg['a'],destination=cfg['b'],vehicle=b[2].strip(),engine_id=cfg['engine'],fleet_configured=cfg['fleet'],capacity_per_vehicle=int(com[4]),infrastructure_gbp=int(com[2]),vehicles_gbp=int(com[3]),origin_x=int(b[6]),origin_y=int(b[7]),destination_x=int(b[8]),destination_y=int(b[9]),straight_distance_tiles=abs(int(b[6])-int(b[8]))+abs(int(b[7])-int(b[9])),path_nodes=b[10],built_calendar_date=date(int(com[6])+10957),status='VERIFIED IN GAME',source_log=str(p.relative_to(ROOT))))
                for extra in commissioned[c][1:]:
                    b=built[extra[0]];details=next(x for x in group['P4_CASE'] if x[0]==extra[0])
                    route_details.append(dict(tag=tag,case=extra[0],company_id=c,mode=details[1],cargo_id=details[2],origin=details[3],destination=details[4],vehicle=b[2].strip(),engine_id=b[1],fleet_configured=int(extra[5]),capacity_per_vehicle=int(extra[4]),infrastructure_gbp=int(extra[2]),vehicles_gbp=int(extra[3]),origin_x=b[6],origin_y=b[7],destination_x=b[8],destination_y=b[9],straight_distance_tiles=abs(int(b[6])-int(b[8]))+abs(int(b[7])-int(b[9])),path_nodes=b[10],built_calendar_date=date(int(extra[6])+10957),status='VERIFIED IN GAME',source_log=str(p.relative_to(ROOT))))
        for r in group['P4_OPENING']:
            if int(r[0])==0:openings.append(dict(tag=tag,engine_id=r[1],buildable=r[2],name=r[3].strip(),design_date_calendar=date(r[4]),status='VERIFIED IN GAME',note='Engine design date is calendar time; company financial time has a separate saved offset'))
        for r in group['P4_MONTH']:months.append(dict(tag=tag,company_id=r[0],economy_date=r[1],cash=r[2],origin_rating_percent=r[3],origin_waiting_units=r[4],status='VERIFIED IN GAME'))
        accum=collections.defaultdict(int);invested=collections.defaultdict(int);payback={};prevbank={c:int(started[c][1]) for c in started};prevloan={c:int(started[c][2]) for c in started}
        for r in group['P4_YEAR']:
            c=int(r[0]);year=int(r[1]);cfg=conf['routes'][c];ledger=list(map(int,r[8].rstrip(',').split(',')));assert len(ledger)==15
            revenue=-sum(ledger[i] for i in [7,8,9,10,14]);operating=sum(ledger[i] for i in [2,3,4,5,6,11,12,13]);profit=revenue-operating;accum[c]+=profit
            com=comm.get(c);invested[c]+=ledger[0]+ledger[1];capital=invested[c]
            if com and accum[c]>=capital and c not in payback:payback[c]=year-1799
            sample=duty.get((c,year));bank=int(r[2]);loan=int(r[3]);cashflow=bank-prevbank.get(c,bank)-(loan-prevloan.get(c,loan));prevbank[c]=bank;prevloan[c]=loan
            row=dict(tag=tag,case=m['case'],company_id=c,mode=cfg['mode'],cargo_id=cfg['cargo'],engine_id=cfg['engine'],configured_fleet=cfg['fleet'],economy_year=year,calendar_period_start=date(datetime.date(year,1,1).toordinal()+365+10957),calendar_period_end_exclusive=date(datetime.date(year+1,1,1).toordinal()+365+10957),status='VERIFIED IN GAME',service_commissioned=com is not None,observation_complete=complete,pilot=is_pilot,infrastructure_initial_gbp=int(com[2]) if com else '',fleet_initial_gbp=int(com[3]) if com else '',capacity_per_vehicle=int(com[4]) if com else '',cash_gbp=bank,loan_gbp=loan,company_value_gbp=int(r[4]),annual_revenue_gbp=revenue,annual_running_gbp=sum(ledger[2:6]),annual_property_gbp=ledger[6],annual_interest_gbp=ledger[11],annual_other_gbp=ledger[12],annual_operating_expenses_gbp=operating,annual_operating_profit_gbp=profit,annual_capex_gbp=ledger[0]+ledger[1],cash_change_excluding_loan_gbp=cashflow,cumulative_operating_profit_gbp=accum[c],observed_capital_recovery_year=payback.get(c,'NOT REACHED'),actual_fleet=int(r[6]),delivered_units=int(r[5]),fleet_vehicle_profit_gbp=int(r[7]),sampled_load_factor=float(sample[5])/int(sample[6]) if sample and int(sample[6]) else '',sampled_loaded_time_fraction=float(sample[4])/int(sample[3]) if sample and int(sample[3]) else '',sampled_breakdown_fraction=float(sample[7])/int(sample[3]) if sample and int(sample[3]) else '',sampled_station_time_fraction=float(sample[9])/int(sample[3]) if sample and int(sample[3]) else '',sampled_mean_loaded_speed=float(sample[10])/int(sample[11]) if sample and int(sample[11]) else '',finance_distress='NEGATIVE CASH' if bank<0 else 'No negative cash at year-end',ledger_json=json.dumps(ledger),source_log=str(p.relative_to(ROOT)))
            row['delivery_verified']=bool(com and int(r[5])>0 and revenue>0 and sample and int(sample[4])>0)
            row['capital_invested_to_date_gbp']=invested[c]
            row['scenario_role']='ordinary-credit mixed strategy' if tag=='three-credit-matched' else ('cash-only control' if tag=='three-final' else 'targeted fixture')
            expansion_dates=[int(x[6]) for x in commissioned[c][1:]]
            if expansion_dates and year>=datetime.date.fromordinal(expansion_dates[0]-365).year:
                row['mode']='road and rail';row['cargo_id']='28+0';row['delivered_unit_limit']='Mixed grain/passenger company aggregate; not tonnage or a common-unit throughput'
                row['sampled_load_factor']=''
            row['utilization_status']='ENGINE-CALCULATED ratios of fleet-wide in-game samples; not exact timetabled utilization'
            row['layout_version']='two-sided stops and depot checks' if 'GSRoad.BuildRoad(b,Step(b,1,0))' in code else 'earlier constrained stop/depot layout'
            row['revenue_per_delivered_unit_gbp']=revenue/int(r[5]) if int(r[5]) else ''
            row['rail_revenue_gbp']=-ledger[7];row['road_revenue_gbp']=-ledger[8];row['ship_revenue_gbp']=-ledger[10]
            row['rail_running_gbp']=ledger[2];row['road_running_gbp']=ledger[3];row['ship_running_gbp']=ledger[5]
            if row['mode']=='road and rail':row['engine_id']='402+1534';row['revenue_per_delivered_unit_gbp']=''
            out.append(row)
    paid={(r['tag'],r['company_id']) for r in out if r['delivery_verified']}
    for r in out:
        r['financial_observation_status']='VERIFIED IN GAME'
        if not r['service_commissioned']:
            r['status']='BLOCKED';r['service_result']='No commissioned service; empty-company expenses are not mode profitability'
        elif (r['tag'],r['company_id']) not in paid:
            r['status']='BLOCKED';r['service_result']='No confirmed loaded paid delivery during observation; inspect approach/pathfinding, not price alone'
        else:r['service_result']='At least one loaded paid delivery verified; zero-income opening years remain in the financial series'
        if r['tag'] in ('coast-three','coast-spaced','coast-clear'):
            r['comparison_limit']='Physical port/depot interference; not a valid clean demand-sharing comparison'
        elif r['case'].startswith('shared_coast_navigable'):
            r['comparison_limit']='Both companies deliver; placement-order mirror also changes chosen sites/catchments and paid distance. No time-only first-mover effect established'
        elif r['case']=='shared_coal':r['comparison_limit']='Third service never loaded; only the two functioning services establish shared-producer coexistence'
        else:r['comparison_limit']='Strategy, geography, fleet and site selection remain distinct experimental factors'
        if r['status']=='BLOCKED':
            r['blocker']=r['service_result']
            r['verification_procedure']='Inspect this retained company and its current orders, station acceptance and both depot/terminal approaches in a disposable replay. Require two completed loaded cycles and credited revenue before comparing profitability.'
            if r['tag'] in ('final-ship_long','final-ship_mail'):
                r['blocker']='Venice-origin fixture: built/refitted/ordered and water-component query connected, but no loaded paid delivery in five years. Actual docking/pathfinding unresolved.'
                r['verification_procedure']='Inspect the first wharf docking tiles and ship order; test supported buoys or an accessible alternative wharf with genuine cargo catchment, then record actual paid delivery.'
            elif r['tag']=='final-shared_coal' and r['company_id']==2:
                r['blocker']='Third road service commissioned but never loaded or delivered; station/depot approach unresolved. Not proven ratings-based starvation.'
                r['verification_procedure']='Inspect company 2 depot-front road bits and both drive-through station approaches. Verify physical access and loading before measuring shared-producer allocation.'
            elif r['tag'] in ('coast-three','coast-spaced','coast-clear'):
                r['blocker']='Port layout includes access interference or an unconnected third dock; clean demand-sharing inference is invalid.'
                r['verification_procedure']='Keep ship-depot exit water and docking water open; compare the clear-approach navigable fixture and reverse placement order.'
    for a in attempts:
        if a['commissioned'] and (a['tag'],a['company_id']) not in paid and not a['pilot']:
            a['status']='BLOCKED';a['blocker']='Commissioned service did not establish a loaded paid delivery; see annual rows and source log for physical-access checks.'
    previous_revenue={};previous_value={}
    for r in out:
        key=(r['tag'],r['company_id']);prior=previous_revenue.get(key);value=previous_value.get(key)
        r['annual_revenue_growth_percent']=(r['annual_revenue_gbp']/prior-1)*100 if prior and prior>0 else ''
        r['company_value_growth_percent']=(r['company_value_gbp']/value-1)*100 if value and value>1 else ''
        r['operating_profit_margin']=r['annual_operating_profit_gbp']/r['annual_revenue_gbp'] if r['annual_revenue_gbp'] else ''
        previous_revenue[key]=r['annual_revenue_gbp'];previous_value[key]=r['company_value_gbp']
    horses=[r for r in out if r['mode']=='road' and r['service_commissioned'] and not r['pilot'] and r['case']!='shared_coal']
    ships=[r for r in out if r['mode']=='ship' and r['service_commissioned'] and not r['pilot'] and not r['case'].startswith('shared_')]
    company=[r for r in out if r['tag'] in ('three-final','three-credit-matched')]
    competition=[r for r in out if r['case'].startswith('shared_')]
    for a in attempts:
        if a['status']=='BLOCKED' and not a['pilot']:
            key=(a['tag'],a['company_id'])
            if a['mode']=='road' and not any((r['tag'],r['company_id'])==key for r in horses):horses.append(a)
            if a['mode']=='ship' and not any((r['tag'],r['company_id'])==key for r in ships):ships.append(a)
            if a['case'].startswith('shared_') and not any((r['tag'],r['company_id'])==key for r in competition):competition.append(a)
    write('horse_transport_tests.csv',horses);write('maritime_profitability_tests.csv',ships);write('three_company_simulation.csv',company);write('competition_tests.csv',competition)
    write('transport_phase4_attempts.csv',attempts);write('transport_phase4_routes.csv',route_details);write('transport_phase4_opening.csv',openings);write('transport_phase4_station_samples.csv',months)
    (D/'transport_phase4_runtime_evidence.log').write_text('\n'.join(evidence)+'\n',encoding='utf8')
    (D/'transport_phase4_run_configs.json').write_text(json.dumps(configs,indent=2));(D/'transport_phase4_harness_sources.json').write_text(json.dumps(frozen,indent=2))
    # Reuse prior observations only where a launch-relevant hypothesis needs them.
    context=readcsv('vehicle_running_context_tests.csv');gets=[r for r in context if r.get('source_grfid')=='53410808']
    normalized=readcsv('vehicle_economy_normalized.csv');early_gets=min(int(r['introduction_year']) for r in normalized if r['source_grfid']=='53410808' and r['kind']=='powered')
    trains=readcsv('representative_train_tests.csv')
    moving_gets={r['local_vehicle_id'] for r in trains if r['source_grfid']=='53410808' and r.get('peak_empty_speed_kmish_h','').lstrip('-').isdigit() and int(r['peak_empty_speed_kmish_h'])>0}
    (D/'transport_phase4_postlaunch.json').write_text(json.dumps({'earliest_gets_powered_intro_year':early_gets,'gets_running_context_rows':len(gets),'gets_other_models_with_positive_speed':sorted(moving_gets),'class66_status':'MANUAL TEST REQUIRED; no ordered loaded Class 66 route has been tested. Phase 2 used an orderless short track. No inference of a set-wide or opening-era movement defect is justified.','polish_duplicate_status':'Post-launch targeted tests; Phase 2 evidence retained, no implementation and no new operational endorsement'},indent=2))
    print(json.dumps({'company_year_rows':len(company),'horse_rows':len(horses),'ship_rows':len(ships),'competition_rows':len(competition),'runs_read':len(configs)},indent=2))
if __name__=='__main__':analyze()
