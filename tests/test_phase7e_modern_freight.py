import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import modern_phase7e as e
from modern_phase7e_evidence import records,summarize,validate_paid
def receipt(kind):
 report=json.loads((e.ROOT/'docs/research/phase7e_engine_receipts.json').read_text())
 return next(r for r in report['receipts'] if r['kind']==kind and r['status']=='COMPLETED')
def lines(kind):return ['P7 '+s for s in receipt(kind)['observations']]
class ModernFreightTests(unittest.TestCase):
 def test_parser_retains_negative_amounts(self):
  self.assertEqual(records(['dbg P7 E_RESULT|tag=x|profit=-648'],'E_RESULT')[0]['profit'],'-648')
 def test_reject_unpaid_or_unloaded(self):
  for key,value in [('loaded','false'),('unloaded','false'),('paid','false'),('positive_income_samples','0')]:
   row=dict(loaded='true',unloaded='true',paid='true',positive_income_samples='20');row[key]=value
   with self.assertRaises(ValueError):validate_paid(row)
 def test_failed_run_cannot_be_success(self):
  with self.assertRaises(ValueError):summarize(['P7 E_DELIVERY_DONE','P7 E_ERROR|bad'])
  with self.assertRaises(ValueError):summarize([])
 def test_paid_primary_routes_are_supported_by_receipts(self):
  rows=summarize(lines('delivery'))
  self.assertEqual({r['tag'] for r in rows},{'RCYC_547_549','PLAS_549_550','MNSP_550_546','RCYC_547_548'})
  self.assertTrue(all(int(r['first_positive_vehicle_delta_gbp'])>0 for r in rows))
 def test_secondary_paid_and_native_output(self):
  r=receipt('secondary');rows=summarize(lines('secondary'));self.assertEqual(rows[0]['cargo'],'SCMT')
  self.assertGreaterEqual(r['max_sampled_monthly_production']['551:STEL'],6)
  self.assertTrue(any('E_RELOAD|towns=617|industry_count=552|original_vehicle0=true' in s for s in r['observations']))
 def test_fixture_never_forces_money_cargo_or_production(self):
  for s in [e.delivery_code(),e.secondary_code()]:
   for forbidden in ['ChangeBankBalance','SetProductionLevel','EnableForCompany','DemolishTile','Terraform','GSGameSettings.SetValue']:self.assertNotIn(forbidden,s)
   self.assertIn('GSIndustry.GetIndustryID(cur)',s)
 def test_native_site_and_dispatch_guards(self):
  s=e.secondary_code();self.assertIn('attempts++>=96',s);self.assertIn('GSTile.IsHouseTile(t)',s);self.assertIn('GSTile.GetMaxHeight(t)!=height',s)
  s=e.delivery_code();self.assertIn('route[1],route[2],false)',s);self.assertIn('foreach(s in services)Toggle(s)',s)
  self.assertIn('Path(Step(tile,1,0),tile,Step(tile,-1,0))==null',s)
 def test_capability_list_covers_selected_engines(self):
  pairs={(int(r['cargo']),int(r['engine'])) for r in receipt('capability')['selected_capabilities']}
  self.assertEqual(pairs,{(48,407),(52,407),(44,369),(38,369)})
if __name__=='__main__':unittest.main()
