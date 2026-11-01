"""Focused policy/safety checks only; engine claims come from separate receipts."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from lifecycle_phase7d_policy import production,validate,compile_policy,RULES
from lifecycle_phase7c_policy import production as prior
class ProgressionTests(unittest.TestCase):
 def test_regions_dates_and_chain_dependencies(self):
  p=production();self.assertEqual(len(p['events']),32);self.assertEqual(p['schema'],4);self.assertEqual(p['migration'],'reject')
  regions=' '.join(e['region'] for e in p['events'])
  for r in ['Britain','France','Italy','Iberia','Scandinavia','Silesia','Rhine']:self.assertIn(r,regions)
  self.assertEqual(p['retirement'],prior()['retirement'])
 def test_reject_duplicate_missing_dependencies_and_early_native_date(self):
  for mode in ['duplicate','dependency','date','footprint']:
   p=production()
   if mode=='duplicate':p['events'][1]['event_id']=p['events'][0]['event_id']
   elif mode=='dependency':p['events'][0]['dependencies']=['does_not_exist']
   elif mode=='date':p['events'][1]['open_date']=p['events'][0]['open_date']
   else:p['events'][0]['footprint']=[[0,0]]
   with self.subTest(mode=mode),self.assertRaises(AssertionError):validate(p)
 def test_exact_native_footprint_not_rectangle_and_house_rules(self):
  e=next(e for e in production()['events'] if e['local_id']==25);r=RULES[25]
  actual={tuple(t[:2]) for layout in r['layouts'] for t in layout['layout']}
  self.assertEqual({tuple(p) for p in e['footprint']},actual);self.assertLess(len(actual),e['width']*e['height']);self.assertTrue(e['houses_nearby'])
  self.assertEqual(next(e for e in production()['events'] if e['local_id']==24)['minimum_population'],800)
 def test_reproducible_source_compilation(self):
  p=production();self.assertEqual(p,json.loads((ROOT/'gamescripts/historical_industry_lifecycle/progression_policy.json').read_text(encoding='utf8')))
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'policy.nut';compile_policy(p,out);self.assertEqual(out.read_bytes(),(ROOT/'gamescripts/historical_industry_lifecycle/progression_policy.nut').read_bytes())
 def test_migration_guard_and_no_demolition_or_closure_rewrite(self):
  source=(ROOT/'gamescripts/historical_industry_lifecycle/progression.nut').read_text()
  self.assertIn('loaded.schema!=4',source);self.assertIn('no automatic migration',source)
  self.assertIn('local saved=clone state;saved.schema=4',source)
  self.assertIn('house_preserved',source)
  for forbidden in ['Demolish','Terraform','ChangeBankBalance','SetProductionLevel','STORE_PERM']:self.assertNotIn(forbidden,source)
if __name__=='__main__':unittest.main()
