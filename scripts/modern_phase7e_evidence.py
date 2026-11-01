"""Compact observed receipts; no payment estimates or annualization."""
import csv,datetime,json,re
from pathlib import Path
from modern_phase7e import BASE,ROOT,d

def records(lines,event):
 out=[]
 for line in lines:
  marker='P7 '+event+'|'
  if marker not in line:continue
  fields=dict(p.split('=',1) for p in line.split(marker,1)[1].split('|') if '=' in p)
  out.append(fields)
 return out

def validate_paid(result):
 if result.get('loaded')!='true' or result.get('unloaded')!='true' or result.get('paid')!='true' or int(result.get('positive_income_samples','0'))<=0:
  raise ValueError('Paid route requires observed load, unloading and positive vehicle profit increments')
 return True

def summarize(lines):
 if not any('P7 E_DELIVERY_DONE' in s for s in lines) or any('P7 E_ERROR|' in s for s in lines):raise ValueError('Incomplete or failed delivery run')
 rows=[]
 for result in records(lines,'E_RESULT'):
  validate_paid(result);tag=result['tag']
  route=next(r for r in records(lines,'E_ROUTE') if r['tag']==tag)
  paid=next(r for r in records(lines,'E_PAID') if r['tag']==tag)
  vehicles=[r for r in records(lines,'E_VEHICLE') if r['tag']==tag]
  t=lambda tile:(int(tile)%4096,int(tile)//4096)
  a,b=t(route['a']),t(route['b'])
  rows.append(dict(evidence='VERIFIED IN GAME',**route,loaded=result['loaded'],unloaded=result['unloaded'],paid=result['paid'],cargo=tag.split('_')[0],vehicles=' '.join(v['id'] for v in vehicles),engine_ids=' '.join(sorted({v['engine'] for v in vehicles})),capacity_each=vehicles[0]['capacity'],station_manhattan_tiles=abs(a[0]-b[0])+abs(a[1]-b[1]),first_paid_vehicle=paid['vehicle'],first_paid_economy_date=paid['date'],first_paid_economy_iso=(datetime.date.fromordinal(int(paid['date'])-365)).isoformat(),first_positive_vehicle_delta_gbp=paid['delta'],sampled_peak_load=result['peak'],positive_vehicle_income_samples_gbp=result['positive_income_samples'],current_plus_last_year_vehicle_profit_gbp=result['current_plus_last_year_vehicle_profit']))
 return rows

def main():
 receipts=[];rows=[]
 for case in sorted(BASE.glob('*-*/')):
  log=case/'engine.log'
  if not log.exists():continue
  text=log.read_text(encoding='utf8',errors='replace');lines=text.splitlines();errors=[s.split('P7 E_ERROR|',1)[1] for s in lines if 'P7 E_ERROR|' in s]
  result_file=case/'engine-result.json'
  raw=json.loads(result_file.read_text()) if result_file.exists() else None
  kind=case.name.rsplit('-',1)[0]
  success=not errors and ('E_CAPABILITY_DONE' in text if kind=='capability' else 'E_DELIVERY_DONE' in text)
  if success and kind!='capability':
   group=summarize(lines)
   for row in group:row['run']=kind
   rows.extend(group)
  maxima={}
  for r in records(lines,'E_PRODUCTION'):
   key=r['industry']+':'+r['cargo'];maxima[key]=max(maxima.get(key,0),int(r['last_month']))
  receipts.append(dict(kind=kind,status='COMPLETED' if success else 'FAILED / stopped after observed fixture error',error=errors,command=raw['command'] if raw else [str(d.ENGINE),'-X','-x','-c',str(case/'test.cfg'),'-g',json.loads((case/'source.json').read_text())['path'],'-v','null:ticks=180000','-s','null','-m','null','-d','script=4'],seconds=raw['seconds'] if raw else None,source=json.loads((case/'source.json').read_text()),raw_log=str(log),log_sha256=d.sha(log),script_sha256=d.sha(case/'game/lifecycle/main.nut'),max_sampled_monthly_production=maxima,selected_capabilities=[r for r in records(lines,'E_ENGINE') if (r['cargo'],r['engine']) in [('48','407'),('52','407'),('44','369'),('38','369')]],finance_begin=records(lines,'E_FINANCE_BEGIN'),finance_end=records(lines,'E_FINANCE_END'),observations=[s.split('P7 ',1)[1] for s in lines if any('P7 '+k in s for k in ['E_EAF_BUILT','E_RELOAD','E_SELECTED','E_LOADED','E_PAID','E_RESULT','E_ROUTE','E_ERROR','E_BASE','E_CARGO','E_VEHICLE','E_DELIVERY_DONE'])]))
 # Pin all normal candidate assets without modifying them.
 m=json.loads((ROOT/'docs/research/phase7d_candidate_delivery.json').read_text())
 for key in ['candidate','engine','grf','script']:assert d.sha(Path(m[key]))==m[key+'_sha256'],key
 for item in m['script_files']+m['asset_files']:assert d.sha(Path(item['path']))==item['sha256']
 report=dict(engine='JGRPP 0.73.4',engine_sha256=d.sha(d.ENGINE),grf_sha256=d.sha(d.GRF),normal_candidate=str(m['candidate']),normal_candidate_sha256=m['candidate_sha256'],normal_assets_unchanged=True,total_engine_invocations=len(receipts),completed=sum(r['status']=='COMPLETED' for r in receipts),failed=sum(r['status']!='COMPLETED' for r in receipts),date_basis='GSDate log values are ECONOMY dates, not modern calendar dates; fixture starts at Phase7D 1985 calendar snapshot',money_basis='Internal GBP, rate 1; sampled increments are not route profit or exact gross receipts',probe_scope='Standalone disposable transport probe deliberately replaces the test GS controller and ignores fixture-only saved GS data; does not migrate normal saves or certify GS ledger persistence',receipts=receipts)
 data=ROOT/'docs/research';(data/'phase7e_engine_receipts.json').write_text(json.dumps(report,indent=2)+'\n')
 with (data/'phase7e_paid_routes.csv').open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 # Actual matching compiled/source contracts, not inferred recipes from names.
 source=ROOT/'newgrfs/axis-historical-expansion/.work/source'
 contracts=[]
 matrix=json.loads((data/'industrial_1830_candidate_matrix.json').read_text())
 for i in matrix['industries']:
  if i['local_id'] not in [18,23,24,25,56,79]:continue
  file=source/i['source_file'];compiled=source/'generated/nml'/Path(i['source_file']).with_suffix('.nml').name
  contracts.append(dict(local_id=i['local_id'],industry=i['industry'],accepted=i['accepted'],input_ratios=i['properties']['accept_cargos_with_input_ratios'],produced=i['produced'],source=str(file),source_sha256=d.sha(file),compiled_nml=str(compiled),compiled_sha256=d.sha(compiled)))
 (data/'phase7e_cargo_contracts.json').write_text(json.dumps(dict(economy='BASIC_TEMPERATE / historical Europe',industries=contracts,native_combination_rule='Plastics and EAF production calculate a weighted sum of supplied cargos; both accepted inputs improve production but are not an all-inputs-required gate. Actual PLAS-only MNSP and SCMT-only steel observations confirm this for tested chains.'),indent=2)+'\n')
 print('Engine invocations:',len(receipts),'completed:',report['completed'],'failed:',report['failed'],'paid routes:',len(rows))
if __name__=='__main__':main()
