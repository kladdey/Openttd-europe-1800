"""Meaningful checks for economic comparison and packet-payment modelling."""
import csv,json,math,sys,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from vehicle_economy_phase2 import era,log_mad,model_income,ratio,family,jgr_sqrt,traction

class ModelTests(unittest.TestCase):
    def test_era_boundaries(self):
        self.assertEqual(era(1849),'1830-1849');self.assertEqual(era(1850),'1850-1879')
        self.assertEqual(era(2025),'1991-2025');self.assertEqual(era(2026),'outside_campaign')
    def test_no_fabricated_dispersion(self):
        self.assertIsNone(log_mad(100,[1,2,3,4,5]));self.assertIsNone(log_mad(100,[1]*10))
        self.assertGreater(log_mad(100,[1,1.2,1.4,1.6,1.8,2]),3.5)
        self.assertIsNone(ratio(100,0))
    def test_names_do_not_merge_physics(self):
        self.assertEqual(family('EU07 (Electric)'),'EU07')
        self.assertEqual(family('DB BR 266 "Class 66"'),'CLASS66')
        self.assertNotEqual(family('EU07A PKP'),'EU07')
    def test_maintenance_square_root_rounding(self):
        self.assertEqual(jgr_sqrt(55),7);self.assertEqual(jgr_sqrt(58),8)
        self.assertEqual(7*12*30*(1+jgr_sqrt(58))>>11,11)
    def test_runtime_name_overrides_transformed_static_vehicle_ids(self):
        self.assertEqual(traction('EMD Class 66 (Diesel)',{'19':{0}})[0],'Diesel')
    def test_all_game_payment_measurements(self):
        raw=json.loads((ROOT/'docs/research/axis_cargo_economy_phase2.json').read_text())
        self.assertFalse(raw['validation']['errors'])
        profiles={(p['snapshot_year'],p['cargo_id']):p for p in raw['profiles']}
        count=0
        with (ROOT/'docs/research/axis_cargo_payment_measurements.csv').open(encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                p=profiles[int(r['snapshot_year']),int(r['cargo_id'])]
                self.assertEqual(model_income(p,int(r['distance_tiles']),int(r['transit_economy_days'])),int(r['income_one_unit_gbp']))
                count+=1
        self.assertEqual(count,27648)
    def test_packet_rounding_not_unit_multiplication(self):
        p={'payment':5675,'period1':0,'period2':22}
        single=model_income(p,32,20);packet=model_income(p,32,20,36)
        self.assertGreater(packet,36*single)
        self.assertLess(packet,36*(single+1))
    def test_original_phase1_preserved(self):
        d=json.loads((ROOT/'docs/research/vehicle_phase2_manifest.json').read_text())
        for name,expected in d['phase1_input_hashes'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected)

class OutputTests(unittest.TestCase):
    def test_complete_years_and_unique_keys(self):
        with (ROOT/'docs/research/vehicle_economy_normalized.csv').open(encoding='utf-8-sig') as f:rs=list(csv.DictReader(f))
        self.assertEqual(len(rs),22832)
        self.assertEqual(len({(r['snapshot_year'],r['source_grfid'],r['local_vehicle_id']) for r in rs}),22832)
        self.assertEqual({int(r['snapshot_year']) for r in rs},{1830,1849,1879,1913,1945,1970,1990,2025})
    def test_built_train_accounting_and_route_labels(self):
        with (ROOT/'docs/research/representative_train_tests.csv').open(encoding='utf-8-sig') as f:trains=list(csv.DictReader(f))
        built=[r for r in trains if r['status']=='BUILT_REFITTED_ATTACHED']
        self.assertGreater(len(built),250)
        for r in built:
            self.assertGreater(float(r['purchase_actual_gbp']),0)
            self.assertGreater(float(r['length_tiles']),0)
        with (ROOT/'docs/research/route_profitability_tests.csv').open(encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                self.assertIn(r['status'],('CALCULATED_CONDITIONAL_ENVELOPE','BLOCKED_END_TO_END','BLOCKED_FIXTURE_CREATION','BLOCKED'))
                if r['status']=='CALCULATED_CONDITIONAL_ENVELOPE':
                    self.assertLessEqual(float(r['vehicle_active_share']),1)
                    self.assertAlmostEqual(float(r['annual_profit_model_gbp']),float(r['revenue_model_gbp'])-float(r['total_annual_opex_model_gbp']),places=1)
    def test_no_sparse_group_verdicts(self):
        with (ROOT/'docs/research/vehicle_economy_outliers.csv').open(encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                self.assertGreaterEqual(int(r['group_profiles']),6)
                self.assertIn('screen only',r['statistical_status'])

if __name__=='__main__':unittest.main()
