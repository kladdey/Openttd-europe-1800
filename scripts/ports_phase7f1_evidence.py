"""Summarize only observed 7F.1 outcomes; keep raw logs/checkpoints local."""
import csv,json
from ports_phase7f1 import BASE,PRIOR,ROOT,sha
from modern_phase7e_evidence import records

def paid(row):return int(row.get('loaded',0))>0 and int(row.get('unloaded',0))>0 and int(row.get('payment',0))>0

def main():
 runs=[];rows=[]
 for phase in ['access','delivery','reload','fixed']:
  file=BASE/(phase+'.json')
  if not file.exists():continue
  r=json.loads(file.read_text());obs=r['observations'];results=records(obs,'F1_RESULT')
  runs.append(dict(phase=phase,command=r['command'],seconds=r['seconds'],case=r['case'],source=r['source'],source_sha256=r['source_sha256'],script_sha256=r['script_sha256'],raw_log=r['log'],log_sha256=r['log_sha256'],observations=[s.split('P7 ',1)[1] for s in obs if any(k in s for k in ['F1_ACCESS|','F1_SHIP|','F1_DIAG|','F1_RELOAD|','F1_LOAD|','F1_UNLOAD|','F1_PAID|','F1_RESULT|','F1_ERROR|','F1_DONE|'])]))
  for row in results:rows.append(dict(phase=phase,**row,evidence='VERIFIED IN GAME',status='PAID DELIVERY' if paid(row) else 'NO PAID DELIVERY OBSERVED'))
 manifest=json.loads((ROOT/'docs/research/phase7f_candidate_delivery.json').read_text())
 for key in ['candidate','source','engine','grf','script']:assert sha(__import__('pathlib').Path(manifest[key]))==manifest[key+'_sha256'],key
 for item in manifest['script_files']+manifest['asset_files']:assert sha(__import__('pathlib').Path(item['path']))==item['sha256']
 report=dict(verdict='PASS' if any(paid(r) for r in rows) else 'PARTIAL',engine_invocations=len(runs),budget_note='Fourth permitted run tests a clear-water loading approach after reload proved active source production and a non-loading moving ship',normal_candidate_unchanged=True,normal_candidate_sha256=manifest['candidate_sha256'],grf_sha256=manifest['grf_sha256'],engine_sha256=manifest['engine_sha256'],source_industry=458,destination_industry=260,cargo_label='MNSP',cargo_id=38,ship_engine=616,date_basis='GSDate economy days; calendar starts 1830, economy 1800; payments are GBP API values',runs=runs)
 (ROOT/'docs/research/phase7f1_receipts.json').write_text(json.dumps(report,indent=2)+'\n')
 if rows:
  with (ROOT/'docs/research/phase7f1_route_results.csv').open('w',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(report['verdict'],len(runs),'runs')
if __name__=='__main__':main()
