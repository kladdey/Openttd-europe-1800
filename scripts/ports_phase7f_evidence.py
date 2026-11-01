"""Concise Phase 7F evidence, including negative outcomes and editor invocation."""
import csv,json
from ports_phase7f import *
from modern_phase7e_evidence import records

def main():
 runs=[];routes=[]
 for h in sorted(BASE.glob('*-*/')):
  log=h/'engine.log'
  if not log.exists():continue
  lines=log.read_text(encoding='utf8',errors='replace').splitlines();kind=h.name.rsplit('-',1)[0];text='\n'.join(lines)
  error=[s.split('P7 F_ERROR|',1)[1] for s in lines if 'P7 F_ERROR|' in s]
  if 'Failed to compile' in text:error.append('Squirrel statement terminator error; corrected before probe rerun')
  result=records(lines,'F_SHIP_RESULT')
  done=any('F_PROBE_DONE' in s or 'F_FREIGHT_DONE' in s for s in lines)
  state='FAILED FIXTURE' if error else 'COMPLETED NEGATIVE' if result and result[0]['paid']=='false' else 'COMPLETED' if done else 'INCOMPLETE'
  rfile=h/'engine-result.json';raw=json.loads(rfile.read_text()) if rfile.exists() else {}
  src=SOURCE if kind.startswith('native') else Path(json.loads((BASE/'probe.json').read_text())['case'])/'save/autosave/exit.sav' if kind.startswith('early') else Path(json.loads((BASE/'candidate.json').read_text())['candidate'])
  command=raw.get('command') or [str(ENGINE),'-X','-x','-c',str(h/'test.cfg'),'-g',str(src),'-v','null:ticks='+('12000' if kind.startswith('native') else '230000'),'-s','null','-m','null','-d','script=4']
  runs.append(dict(kind=kind,status=state,errors=error,command=command,source_sha256=sha(src),case=str(h),log_sha256=sha(log),script_sha256=sha(h/'game/lifecycle/main.nut'),seconds=raw.get('seconds'),diagnostics=[s for s in lines if any(k in s for k in ['P3_BLOCKED|','P3_WATER|','P4_BUILT|'])],observations=[s.split('P7 ',1)[1] for s in lines if 'P7 ' in s and any(k in s for k in ['F_BASE|','F_PORT|','F_DEFERRED|','F_ROUTE|','F_VEHICLE|','F_SHIP_RESULT|','F_ERROR|','E_PAID|','E_LOADED|','initialized|scheduler','legacy_enrolled|','processor_enrolled|'])]))
  if 'freight' in kind:
   routes.append(dict(test=kind,status=state,cargo='FOOD' if 'early' in kind else 'MNSP',source_industry=150 if 'early' in kind else 458,destination_industry=542 if 'early' in kind else 260 if kind.startswith('direct') else 410,ship_engine=616,observed_ship_loaded=result[0]['loaded'] if result else 'NOT OBSERVED',observed_ship_paid=result[0]['paid'] if result else 'NOT VERIFIED',observed_paid_amount_gbp=result[0]['sample_income'] if result else 'UNVERIFIED',peak_cargo=result[0]['peak'] if result else 'UNVERIFIED',vehicle_profit_current_last_year_gbp=result[0]['current_last_year_vehicle_profit'] if result else 'UNVERIFIED',observation_economy_days=result[0]['days'] if result else 'NOT COMPLETED',blocker='; '.join(error+[s.split('P3_',1)[1] for s in lines if 'P3_BLOCKED|' in s or 'P3_WATER|' in s]) if error else 'No feeder or ship load observed; grain paid and occasional FOOD production observed, dock FOOD remained zero' if result and result[0]['paid']=='false' else ''))
 editor=json.loads((BASE/'editor.json').read_text());m=json.loads((BASE/'candidate.json').read_text())
 runs.append(dict(kind='scenario-editor',status='SAVED SEPARATE CANDIDATE',command=editor['command'],candidate_sha256=m['candidate_sha256']))
 for key in ['candidate','source','engine','grf','script']:assert sha(Path(m[key]))==m[key+'_sha256'],key
 for r in m['script_files']+m['asset_files']:assert sha(Path(r['path']))==r['sha256']
 report=dict(verdict='PARTIAL',total_engine_invocations=len(runs),budget_note='Seventh invocation was announced as indispensable targeted alternative after Dublin station catchment failure; it also failed the bounded water-connectivity check. No further engine tests.',actual_paid_ship_deliveries=0,normal_assets_verified=True,engine_sha256=sha(ENGINE),grf_sha256=sha(GRF),gs_version=5,schema=4,evidence_scope='No paid maritime freight or normal-policy save/reload certification; earlier Phase7E paid modern freight is retained separately',runs=runs)
 data=ROOT/'docs/research';(data/'phase7f_test_receipts.json').write_text(json.dumps(report,indent=2)+'\n')
 for name,items in [('phase7f_route_results.csv',routes),('phase7f_port_events.csv',[dict(event_id=e['event_id'],region=e['region'],local_id=e['local_id'],industry=e['industry'],opening_year=__import__('datetime').date.fromordinal(e['open_date']-365).year,inputs=' '.join(e['inputs']),outputs=' '.join(c for c,_ in e['outputs']),native_min_year=e['earliest_native_year'],max_attempts=e['max_attempts'],max_batches=e['max_batches'],status='CONDITIONAL / NORMAL SCHEDULING UNVERIFIED',date_basis=e['date_basis']) for e in production()['events'][32:]])]:
  with (data/name).open('w',newline='',encoding='utf8') as f:w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
 print('Invocations',len(runs),'paid maritime deliveries',0)
if __name__=='__main__':main()
