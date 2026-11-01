import sys,json,csv,copy,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import transformation_phase7h as h
from cycles_phase7g import policy as old_cycle
from ports_phase7f import production as old_expansion
class TransformationTests(unittest.TestCase):
 def receipt(self):return json.loads((h.ROOT/'docs/research/phase7h_engine_receipts.json').read_text())
 def test_active_gate_real_once_only_transitions(self):
  r=self.receipt();self.assertEqual(r['active_gate'],'PASS');self.assertEqual(r['engine_invocations'],5);self.assertTrue(all(v==1 for v in r['gate_transition_counts'].values()))
  saved=next(v for v in r['runs'] if v['name']=='gate2');self.assertTrue(any('h_gate_saved|active|schema=5|stage=boom|target=542' in s for s in saved['observations']))
 def test_region_cargo_and_bounded_policy(self):
  p=h.policy();self.assertEqual({e['region'] for e in p['events']},{'Lancashire','Upper Silesia'});self.assertEqual({e['local_id'] for e in p['events']},{0,42})
  for mutate in ['duplicate','date','type']:
   q=copy.deepcopy(p)
   if mutate=='duplicate':q['events'][1]['id']=q['events'][0]['id']
   elif mutate=='date':q['events'][1]['retire_date']=q['events'][1]['decline_date']
   else:q['events'][0]['local_id']=74
   with self.assertRaises(AssertionError):h.validate(q)
 def test_existing_policies_unchanged(self):
  a,b=old_expansion(),old_cycle();h.policy();h.policy(True);self.assertEqual(a,old_expansion());self.assertEqual(b,old_cycle());self.assertEqual(len(a['events']),40);self.assertFalse({e['id'] for e in h.policy()['events']} & {e['event_id'] for e in a['events']})
 def test_real_decline_and_physical_retirement(self):
  rows=list(csv.DictReader((h.ROOT/'docs/research/phase7h_production_samples.csv').read_text().splitlines()));coal=[r for r in rows if r['event']=='silesian_transition' and r['mature']=='True']
  before=[int(r['production']) for r in coal if r['stage']=='operating'];after=[int(r['production']) for r in coal if r['stage']=='declining'];self.assertLess(max(after),min(before))
  r=self.receipt();run=next(v for v in r['runs'] if v['name']=='transformation');self.assertTrue(any('h_final|silesian_transition|status=ended|stage=retired|industry=542|exists=false' in s for s in run['observations']));self.assertEqual(r['original_industries_preserved'],542);self.assertTrue(all(v==0 for v in r['local_height_changes'].values()))
 def test_new_schema_reload_and_no_duplicates(self):
  r=self.receipt();run=next(v for v in r['runs'] if v['name']=='reload');self.assertTrue(any('h_reload_saved|native|schema=6|events=2' in s for s in run['observations']))
  self.assertFalse(any(any('EVENT|'+k+'|' in s for k in ['h_opened','h_decline','h_retire_command','h_retired']) for s in run['observations']))
  s=(h.DIR/'transformation.nut').read_text(encoding='utf-8-sig');self.assertIn('loaded.schema!=6',s);self.assertIn('loaded.transformation_contract!=Hash(TRANSFORMATION_TEXT)',s);self.assertIn('saved.schema=6',s)
 def test_safety_fairness_and_cancellation(self):
  s=(h.DIR/'transformation.nut').read_text(encoding='utf-8-sig')
  for bad in ['ChangeBankBalance','GSCompanyMode(','Terraform','DemolishTile','SetExclusive']:self.assertNotIn(bad,s)
  for guard in ['Original industry control forbidden','r.attempts>=96','r.batches>=6','r.status="cancelled"','r.closing_economy>180']:self.assertIn(guard,s)
if __name__=='__main__':unittest.main()
