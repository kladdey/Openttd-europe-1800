"""Static cargo graph; projections never stand in for actual delivered revenue."""
import collections,json
from lifecycle_phase7c_runtime import ROOT,BASE,sha
from lifecycle_phase7c_policy import production
from lifecycle_phase7b_inventory import records
from lifecycle_phase7b_runtime import registration
from industrial_phase6b_plan import write_csv
def main():
 data=ROOT/'docs/research';matrix=json.loads((data/'industrial_1830_candidate_matrix.json').read_text());rules={r['local_id']:r for r in matrix['industries']}
 mapping={int(t):int(local) for t,local in registration()['mapping'].items()};nodes=[]
 for r in records():
  local=mapping[r['type']];rule=rules[local]
  nodes.append(dict(id='original_'+str(r['industry_id']),local_id=local,x=r['x'],y=r['y'],inputs=rule['accepted'],outputs=[label for label,_ in rule['produced']],status='VERIFIED INITIAL BASELINE',available_from=1830))
 for e in production()['events']:
  nodes.append(dict(id=e['event_id'],local_id=e['local_id'],x=e['anchor_x'],y=e['anchor_y'],inputs=e['inputs'],outputs=[label for label,_ in e['outputs']],available_from=int(__import__('datetime').date.fromordinal(e['open_date']-365).year),status='CONDITIONAL POLICY PROJECTION; construction may defer/cancel'))
 edges=[]
 for a in nodes:
  for b in nodes:
   if a['id']==b['id']:continue
   if a['id'].startswith('original_') and b['id'].startswith('original_') and 'original_275' not in [a['id'],b['id']]:continue
   for cargo in set(a['outputs'])&set(b['inputs']):edges.append(dict(producer=a['id'],consumer=b['id'],cargo=cargo,distance_manhattan=abs(a['x']-b['x'])+abs(a['y']-b['y'])))
 (data/'phase7c_chain_graph.json').write_text(json.dumps(dict(nodes=nodes,edges=edges,scope='Static compatibility edges involving new events or retiring mill 275; unchanged baseline edges are in industry_chain_graph.json. NOT transport connectivity, affordability, actual construction or production proof. Original retirements excluded from projection; runtime successor safeguards apply.'),indent=2))
 rows=[]
 for year in [1835,1865,1910,1955,1985]:
  active=[n for n in nodes if n['available_from']<=year]
  for label in sorted({l for n in active for l in n['outputs']}):
   producers=[n['id'] for n in active if label in n['outputs']];consumers=[n['id'] for n in active if label in n['inputs']]
   rows.append(dict(year=year,cargo=label,producers=len(producers),consumers=len(consumers),unmatched_output=not consumers,evidence='MODELLED: conditional schedule projection; not actual engine chain completion'))
 write_csv(data/'phase7c_projected_chain_coverage.csv',rows)
 source=ROOT/'newgrfs/axis-historical-expansion/.work/source';checks=[]
 for r in matrix['industries']:
  path=source/r['source_file'];checks.append(dict(local_id=r['local_id'],file=r['source_file'],sha256=sha(path),matches_audited_model=sha(path)==r['source_sha256']))
 assert len(checks)==96 and all(r['matches_audited_model'] for r in checks)
 (data/'phase7c_recipe_source_checks.json').write_text(json.dumps(dict(matrix_sha256=sha(data/'industrial_1830_candidate_matrix.json'),registered_models=96,cargo_labels=matrix['cargo_slots'],models=checks,primary_template_unchanged=(source/'src/templates/industry_primary.pynml').read_bytes()==(ROOT/'newgrfs/axis-historical-legacy/.work/source/src/templates/industry_primary.pynml').read_bytes()),indent=2))
 print('Nodes',len(nodes),'compatible edges',len(edges),'model files unchanged',len(checks))
if __name__=='__main__':main()
