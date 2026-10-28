"""Financial and evidence checks against retained game logs, not payment estimates."""
import collections,csv,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from analyze_transport_phase3 import day_date
D=ROOT/'docs/research'
def rows(name):
    with (D/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
class TransportEvidenceTests(unittest.TestCase):
    def test_distinct_observation_keys(self):
        r=rows('transport_route_results.csv');keys=[(x['tag'],x['economy_year']) for x in r]
        self.assertEqual(len(keys),len(set(keys)))
    def test_calendar_economy_offset(self):
        self.assertEqual(day_date(668394),'1830-01-01')
        self.assertEqual(day_date(657437),'1800-01-01')
        self.assertEqual(668394-657437,10957)
    def test_ledger_signs_and_categories(self):
        for r in rows('transport_route_results.csv'):
            if not r['ledger_raw_json']:continue
            l=json.loads(r['ledger_raw_json']);self.assertEqual(len(l),15)
            self.assertEqual(int(r['revenue_gbp']),-sum(l[i] for i in [7,8,9,10,14]))
            self.assertEqual(int(r['operating_expenses_gbp']),sum(l[i] for i in [2,3,4,5,6,11,12,13]))
            self.assertEqual(l[12],300)
    def test_known_first_year_bank_not_loan_or_date(self):
        r=next(x for x in rows('transport_route_results.csv') if x['tag']=='rail-coal-ledger' and x['economy_year']=='1800')
        self.assertEqual(int(r['revenue_gbp']),2208)
        self.assertEqual(int(r['net_cash_change_gbp']),18158-17651)
        self.assertEqual(int(r['fleet_capital_gbp']),8059)
    def test_only_loaded_paid_cases_claim_delivery(self):
        r=[x for x in rows('transport_route_results.csv') if x['delivery_verified']=='True']
        self.assertTrue({'0','2','14','28','32'}<={x['cargo_id'] for x in r})
        for x in r:
            self.assertGreater(int(x['sampled_lead_vehicle_max_load']),0)
            self.assertGreater(int(x['delivered_cargo_units']),0)
            self.assertGreater(int(x['revenue_gbp']),0)
    def test_growth_payback_is_observed_not_projected(self):
        growth=rows('company_growth_simulations.csv')
        for s in rows('transport_mode_comparison.csv'):
            g=[x for x in growth if x['tag']==s['tag']]
            reached=[int(x['years_after_start']) for x in g if x['capital_repaid_by_observed_cash_profit']=='True']
            self.assertEqual(str(min(reached)) if reached else 'NOT REACHED',s['observed_capital_payback_years'])
    def test_twenty_year_runs_are_actual_rows(self):
        r=rows('transport_route_results.csv')
        for tag in ['rail-coal-ledger','horse-passenger-final2']:
            self.assertEqual([int(x['economy_year']) for x in r if x['tag']==tag],list(range(1800,1820)))
    def test_expansion_uses_same_loan(self):
        r=rows('transport_expansion_test.csv');self.assertEqual(len(r),15)
        self.assertEqual({x['loan_gbp'] for x in r},{'30000'})
        self.assertEqual(r[-1]['cash_gbp'],'20510')
        self.assertEqual(r[-1]['initial_capital_investment_gbp'],'27136')
        self.assertGreater(int(r[-1]['cumulative_post_construction_cash_profit_gbp']),0)
    def test_long_consists_retain_seven_tile_limit(self):
        r=rows('transport_route_results.csv')
        for tag,length,capacity in [('rail-coal-12-brake',44/16,72),('rail-coal-24-brake',80/16,144)]:
            found=[x for x in r if x['tag']==tag];self.assertEqual(len(found),5)
            for x in found:
                self.assertEqual(float(x['actual_train_length_tiles']),length)
                self.assertLessEqual(length,7)
                self.assertEqual(int(x['capacity_per_vehicle_or_train']),capacity)
if __name__=='__main__':unittest.main()
