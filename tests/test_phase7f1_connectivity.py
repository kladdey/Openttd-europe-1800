import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ports_phase7f1 import code,fixed_code
from ports_phase7f1_evidence import paid
class MaritimeConnectivityTests(unittest.TestCase):
 def test_payment_requires_load_and_unload(self):
  self.assertTrue(paid(dict(loaded=50,unloaded=50,payment=100)))
  for r in [dict(loaded=0,unloaded=0,payment=100),dict(loaded=50,unloaded=0,payment=100),dict(loaded=50,unloaded=50,payment=0)]:self.assertFalse(paid(r))
 def test_station_join_and_acceptance_are_native(self):
  s=code('access');self.assertIn('GSRoad.ROADVEHTYPE_TRUCK,bs)',s);self.assertIn('GetStationID(ext)!=bs',s);self.assertIn('acceptance<8',s);self.assertIn('GSIndustry.IsCargoAccepted(260,cargo)',s)
 def test_approach_fix_and_correct_orders(self):
  s=fixed_code();self.assertIn('along<=5',s);self.assertIn('GSTile.SLOPE_FLAT',s);self.assertIn('!ClearDock(tile)',s);self.assertIn('GSOrder.OF_UNLOAD|GSOrder.OF_NO_LOAD',s);self.assertIn('if(!(data.bw in water))throw',s)
 def test_no_forced_production_or_subsidy(self):
  s=fixed_code()
  for forbidden in ['ChangeBankBalance','SetProductionLevel','EnableForCompany','Terraform','DemolishTile','GSGameSettings.SetValue']:self.assertNotIn(forbidden,s)
  self.assertIn('BuildVehicleWithRefit(depot,616,cargo)',s);self.assertIn('F1_RELOAD',s)
if __name__=='__main__':unittest.main()
