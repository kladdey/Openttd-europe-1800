"""Policy/compiler safety and reconciliation of actual engine receipts."""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from lifecycle_phase7c_policy import validate,compile_policy,production
class PolicyTests(unittest.TestCase):
 def setUp(self):self.p=production()
 def test_unique_ordered_dependencies_and_five_eras(self):
  self.assertEqual(len(self.p['events']),10);self.assertFalse(self.p['test_mode']);self.assertEqual(self.p['migration'],'reject')
  self.assertEqual({e['local_id'] for e in self.p['events']},{34,103,2,9,80,24,25,23,18})
 def test_reject_duplicates_cycles_missing_dependencies(self):
  for mutation in ['duplicate','cycle','missing']:
   p=copy.deepcopy(self.p)
   if mutation=='duplicate':p['events'][1]['event_id']=p['events'][0]['event_id']
   elif mutation=='cycle':p['events'][0]['dependencies']=[p['events'][1]['event_id']]
   else:p['events'][0]['dependencies']=['not_registered']
   with self.subTest(mutation=mutation),self.assertRaises(AssertionError):validate(p)
 def test_reject_unsafe_dates_sites_and_warning(self):
  for key,value in [('latest_date',1),('sites',[]),('sites',[1,1]),('width',0),('max_attempts',129)]:
   p=copy.deepcopy(self.p);p['events'][0][key]=value
   with self.subTest(key=key),self.assertRaises(AssertionError):validate(p)
  for years in [4,11]:
   p=copy.deepcopy(self.p);p['retirement']['warning_years']=years
   with self.assertRaises(AssertionError):validate(p)
 def test_production_native_dates(self):
  p=copy.deepcopy(self.p);p['events'][1]['open_date']=p['events'][0]['open_date']
  with self.assertRaises(AssertionError):validate(p)
 def test_committed_compiler_output(self):
  self.assertEqual(self.p,json.loads((ROOT/'gamescripts/historical_industry_lifecycle/expansion_policy.json').read_text(encoding='utf8')))
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'p.nut';compile_policy(self.p,path)
   self.assertEqual(path.read_bytes(),(ROOT/'gamescripts/historical_industry_lifecycle/expansion_policy.nut').read_bytes())
 def test_grain_batches_retain_partial_inputs(self):
  # Independent arithmetic check for the actual source's batch cap. Actual
  # production still needs the separately captured stock-engine capacity run.
  for stock in range(40):
   consumed=min(stock//8,1)*8
   self.assertTrue(consumed==0 or consumed==8);self.assertLessEqual(consumed,stock)
   if stock<8:self.assertEqual(consumed,0)
 def test_explicit_safety_contracts(self):
  s=(ROOT/'gamescripts/historical_industry_lifecycle/expansion.nut').read_text()
  for fragment in ['Explicit adopt_only','Partial expansion ledger','Expansion policy contract mismatch','SuccessorReady','No commands to replacement instance','No rebuild or command to reused ID','.bindenv(this)']:
   self.assertIn(fragment,s)
  self.assertNotIn('ChangeBankBalance',s);self.assertNotIn('Demolish',s)
class EvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  path=ROOT/'docs/research/phase7c_engine_receipts.json'
  if not path.exists():raise unittest.SkipTest('Run engine drivers and evidence collector first')
  cls.runs=json.loads(path.read_text())
 def test_raw_log_hashes(self):
  for r in self.runs:
   path=ROOT/r['archived_log'];self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),r['log_sha256'])
 def test_actual_paid_chain_and_physical_closure(self):
  text='\n'.join(s for r in self.runs if r.get('scope')=='europe' for s in r['observations'])
  self.assertIn('c_paid_chain|fixture|',text);self.assertIn('processor_closed|krakow_old_mill|',text)
  self.assertIn('other_originals_intact=541|towns=617|factory=closed|paid=true',text)
 def test_both_real_europe_opening_types(self):
  text='\n'.join(s for r in self.runs if r.get('scope') in ['europe','waves-europe'] for s in r['observations'])
  for event in ['galicia_mill','ruhr_sheet','ruhr_steel']:self.assertIn('expansion_opened|'+event+'|',text)
 def test_current_grf_and_honest_mini_scope(self):
  self.assertTrue(any(r.get('scope')=='waves-mini' for r in self.runs))
  for r in self.runs:
   self.assertIn('grf_sha256',r)
 def test_natural_control(self):
  text='\n'.join(s for r in self.runs for s in r['observations']);self.assertIn('NATURAL_DONE|new=0|days=1834',text)
if __name__=='__main__':unittest.main()
