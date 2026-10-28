"""Check observed finances, interventions, negative results and unit boundaries."""
import collections,csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/research'
def read(name):
    with (D/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def meanprofit(rr):return sum(int(r['annual_operating_profit_gbp']) for r in rr)/len(rr)
class Phase4Tests(unittest.TestCase):
    def test_two_complete_three_company_worlds(self):
        rr=read('three_company_simulation.csv');self.assertEqual(len(rr),120)
        for tag in ['three-final','three-credit-matched']:
            for c in range(3):
                r=[x for x in rr if x['tag']==tag and x['company_id']==str(c)]
                self.assertEqual([int(x['economy_year']) for x in r],list(range(1800,1820)))
                self.assertTrue(all(int(x['cash_gbp'])>0 for x in r))
    def test_equal_normal_start_and_intentional_settings(self):
        evidence=(D/'transport_phase4_runtime_evidence.log').read_text()
        for tag in ['three-final','three-credit-matched']:
            for c in range(3):self.assertIn(f'{tag}|P4_START|{c}|100000|100000|300000|1|7',evidence)
    def test_first_decade_is_matched(self):
        rr=read('three_company_simulation.csv');key={(r['tag'],r['company_id'],r['economy_year']):r for r in rr}
        for c in range(3):
            for year in range(1800,1810):
                a=key['three-final',str(c),str(year)];b=key['three-credit-matched',str(c),str(year)]
                for field in ['ledger_json','cash_gbp','loan_gbp','company_value_gbp','delivered_units']:self.assertEqual(a[field],b[field])
    def test_ordinary_credit_buys_real_railway(self):
        rr=read('three_company_simulation.csv');c=[r for r in rr if r['tag']=='three-credit-matched' and r['company_id']=='2']
        self.assertEqual(c[9]['loan_gbp'],'20000');self.assertEqual(c[10]['loan_gbp'],'30000')
        self.assertEqual(int(c[10]['annual_capex_gbp']),14930)
        self.assertEqual(c[-1]['actual_fleet'],'9');self.assertEqual(c[-1]['cash_gbp'],'92167')
    def test_ledger_categories_and_noncapital_profit(self):
        for r in read('three_company_simulation.csv'):
            l=json.loads(r['ledger_json']);self.assertEqual(len(l),15)
            self.assertEqual(int(r['annual_revenue_gbp']),-sum(l[i] for i in [7,8,9,10,14]))
            self.assertEqual(int(r['annual_operating_expenses_gbp']),sum(l[i] for i in [2,3,4,5,6,11,12,13]))
            self.assertEqual(int(r['annual_capex_gbp']),l[0]+l[1]);self.assertEqual(l[12],300)
    def test_horse_niche_not_assumed_from_loading(self):
        rr=read('horse_transport_tests.csv')
        passenger=[r for r in rr if r['tag']=='road-access-horse_straight_pass']
        mail=[r for r in rr if r['tag']=='road-access-horse_straight_mail']
        self.assertEqual(len(passenger),3);self.assertLess(meanprofit(passenger),0)
        self.assertGreater(sum(float(r['sampled_load_factor']) for r in passenger)/3,.8)
        self.assertGreater(meanprofit(mail),0)
        small=[r for r in rr if r['tag']=='road-access-horse_farm_small'];large=[r for r in rr if r['tag']=='road-access-horse_farm_fleet']
        self.assertLess(meanprofit(small),0);self.assertGreater(meanprofit(large),0)
    def test_real_fish_delivery_and_long_route_startup_losses(self):
        rr=read('maritime_profitability_tests.csv')
        fish=[r for r in rr if r['tag']=='fish-fixed'];self.assertTrue(any(r['delivery_verified']=='True' for r in fish));self.assertGreater(meanprofit(fish),0)
        long=[r for r in rr if r['tag']=='final-ship_low_demand'];self.assertEqual(len(long),5)
        self.assertEqual(long[0]['annual_revenue_gbp'],'0');self.assertEqual(long[1]['annual_revenue_gbp'],'0')
        self.assertTrue(any(r['delivery_verified']=='True' for r in long));self.assertTrue(all(r['status']=='VERIFIED IN GAME' for r in long))
    def test_unverified_mail_is_not_claimed_as_delivered(self):
        rr=[r for r in read('maritime_profitability_tests.csv') if r['tag']=='final-ship_mail']
        self.assertTrue(rr);self.assertTrue(all(r['status']=='BLOCKED' for r in rr))
        self.assertTrue(all(r['delivery_verified']=='False' for r in rr))
    def test_market_order_mirror_follows_site_not_company_id(self):
        rr=read('competition_tests.csv')
        for tag,preferred in [('final-shared_coast_navigable','0'),('final-shared_coast_navigable_reverse','1')]:
            a=[r for r in rr if r['tag']==tag and r['company_id']==preferred]
            b=[r for r in rr if r['tag']==tag and r['company_id']!=preferred]
            self.assertGreater(meanprofit(a),meanprofit(b));self.assertGreater(meanprofit(b),0)
    def test_mixed_cargo_has_no_fictitious_common_unit(self):
        rr=[r for r in read('three_company_simulation.csv') if r['mode']=='road and rail']
        self.assertEqual(len(rr),10)
        for r in rr:
            self.assertEqual(r['cargo_id'],'28+0');self.assertEqual(r['sampled_load_factor'],'')
            self.assertEqual(r['revenue_per_delivered_unit_gbp'],'')
if __name__=='__main__':unittest.main()
