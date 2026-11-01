import sys,unittest,copy,csv,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cycles_phase7g as g
from ports_phase7f import production as ports
class CycleTests(unittest.TestCase):
 def test_two_bounded_events_and_native_limits(self):
  c=g.policy();self.assertEqual(c['events'],['ruhr_expansion','ruhr_downturn']);self.assertEqual(c['schema'],5);self.assertEqual((c['down_level'],c['boom_level']),(8,32))
  for key,value in [('down_level',4),('boom_level',129),('end_date',c['down_date'])]:
   x=copy.deepcopy(c);x[key]=value
   with self.assertRaises(AssertionError):g.validate(x)
 def test_no_changes_to_previous_expansion(self):
  before=ports();g.policy();self.assertEqual(before,ports());self.assertEqual(len(before['events']),40);self.assertEqual(len(before['events'][32:]),8)
 def test_own_site_only_and_clear_ground(self):
  s=(g.DIR/'cycles.nut').read_text();self.assertIn('foreach(s in state.baseline)',s);self.assertIn('Cycle cannot control original industry',s);self.assertIn('Matches(r.signature.id,r.signature)',s);self.assertIn('r.attempts>=96',s);self.assertIn('ProgressionController.SiteReason.bindenv(this)',s)
 def test_schema_contract_and_autosave_root(self):
  s=(g.DIR/'cycles.nut').read_text();self.assertIn('loaded.schema!=5',s);self.assertIn('loaded.cycle_contract!=Hash(CYCLE_CONTRACT_TEXT)',s);self.assertIn('out.schema=5',s);self.assertIn('cycle_loading',s);self.assertEqual(g.policy()['migration'],'reject')
 def test_real_production_effect_and_recovery_flags(self):
  rows=list(csv.DictReader((g.ROOT/'docs/research/phase7g_production_samples.csv').read_text(encoding='utf8').splitlines()))
  chosen={r['stage']:r for r in rows if r['mature_sample']=='True'}
  self.assertGreater(int(chosen['boom']['coal']),int(chosen['baseline']['coal']));self.assertLess(int(chosen['downturn']['coal']),int(chosen['baseline']['coal']));self.assertGreater(int(chosen['ended']['coal']),int(chosen['downturn']['coal']));self.assertEqual(chosen['ended']['flags'],'0')
  r=json.loads((g.ROOT/'docs/research/phase7g_engine_receipts.json').read_text());self.assertEqual(r['total_engine_invocations'],4);self.assertEqual(r['original_industries_intact'],542);self.assertEqual(r['local_height_changes_within_10_tiles'],0)
 def test_fairness_and_no_cargo_injection(self):
  s=(g.DIR/'cycles.nut').read_text()
  for bad in ['ChangeBankBalance','GSCompanyMode(','SetExclusive','DemolishTile','Terraform']:self.assertNotIn(bad,s)
  self.assertIn('r.base_flags&mask',s);self.assertIn('r.stage="ended"',s);self.assertIn('r.stage="cancelled"',s)
if __name__=='__main__':unittest.main()
