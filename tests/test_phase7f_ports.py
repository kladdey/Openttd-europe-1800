import sys,json,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import ports_phase7f as p
class PortsTests(unittest.TestCase):
 def test_existing_policy_preserved(self):
  n=p.production();self.assertEqual(n['events'][:32],p.original()['events']);self.assertEqual(n['retirement'],p.original()['retirement']);self.assertEqual(len(n['events']),40)
 def test_regions_eras_and_native_dates(self):
  events=p.production()['events'][32:];self.assertEqual({e['region'] for e in events},{'Liverpool','Gdansk'})
  self.assertEqual({__import__('datetime').date.fromordinal(e['open_date']-365).year for e in events},{1831,1875,1975,1995})
  for e in events:self.assertGreaterEqual(e['open_date'],p.absolute_date(f"{max(1,e['earliest_native_year']):04d}-01-01"))
 def test_signed_offsets_and_bounded_native_search(self):
  for e in p.production()['events'][32:]:
   self.assertTrue(all(abs(v)<32 for xy in e['footprint'] for v in xy));self.assertLessEqual(e['max_attempts'],96);self.assertLessEqual(e['max_batches'],6)
 def test_duplicate_or_mutated_original_rejected(self):
  a=p.production();a['events'][32]['event_id']=a['events'][0]['event_id']
  with self.assertRaises(AssertionError):p.validate(a)
  a=p.production();a['events'][0]['name']='changed'
  with self.assertRaises(AssertionError):p.validate(a)
 def test_native_metadata_uses_actual_type(self):
  for e in p.production()['events'][32:]:
   r=p.RULES[e['local_id']];self.assertEqual(e['native_location_checks'],r['industry_location_checks']);self.assertEqual(e['inputs'],r['accepted'])
 def test_no_demolition_or_subsidy_in_ports_controller(self):
  s=(p.DIR/'ports.nut').read_text(encoding='utf-8-sig')
  for bad in ['DemolishTile','Terraform','ChangeBankBalance','SetProductionLevel']:self.assertNotIn(bad,s)
  self.assertIn('GSTile.IsHouseTile(t)',s);self.assertIn('return base.SiteReason(tile,e)',s)
 def test_negative_receipts_remain_negative(self):
  r=json.loads((p.ROOT/'docs/research/phase7f_test_receipts.json').read_text());self.assertEqual(r['total_engine_invocations'],7);self.assertEqual(r['actual_paid_ship_deliveries'],0);self.assertEqual(r['verdict'],'PARTIAL')
  self.assertTrue(any('COMPLETED NEGATIVE'==v['status'] for v in r['runs']))
 def test_no_silent_migration_or_new_grf(self):
  m=json.loads((p.ROOT/'docs/research/phase7f_candidate_delivery.json').read_text());self.assertEqual(m['gs_version'],5);self.assertEqual(m['gs_schema'],4);self.assertEqual(len(m['newgrfs']),15);self.assertTrue(m['all_map_planes_unchanged'])
  s=(p.DIR/'expansion.nut').read_text(encoding='utf-8-sig');self.assertIn('ExpansionContract()',s);self.assertEqual(p.production()['migration'],'reject')
if __name__=='__main__':unittest.main()
