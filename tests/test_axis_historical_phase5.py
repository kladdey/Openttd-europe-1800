"""Acceptance checks for retained Phase 5 runtime evidence and policy contracts."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

REPO=Path(__file__).resolve().parents[1]
ROOT=REPO/'newgrfs/axis-historical-europe'


def read(name):return json.loads((ROOT/name).read_text())


class HistoricalIntegrationTests(unittest.TestCase):
    def test_complete_stable_industry_ids(self):
        original=json.loads((REPO/'docs/research/axis-2.3.1-extreme-classic.json').read_text())
        rules=read('historical_manifest.json')['industries']
        self.assertEqual(set(rules),{i['id'] for i in original['industries']}|{'steel_mill'})
        self.assertEqual(len({r['local_id'] for r in rules.values()}),92)
        for i in original['industries']:self.assertEqual(rules[i['id']]['local_id'],i['local_id'])
        self.assertEqual(rules['steel_mill']['local_id'],2)

    def test_no_automatic_retirement(self):
        for r in read('historical_manifest.json')['industries'].values():
            self.assertIsNone(r['final_construction_year'])
            self.assertIn(r['date_status'],['PROVISIONAL CAMPAIGN POLICY','SOURCED ADOPTION POLICY'])

    def test_cargo_and_production_preservation(self):
        r=read('validation-phase5-result.json')
        self.assertTrue(r['passed']);self.assertEqual(r['cargo_slots'],64)
        self.assertEqual(r['binary_cargo_slot_label_records_identical'],320)
        self.assertTrue(r['all_original_classic_industries_unchanged_models'])
        self.assertTrue(r['other_economies_identical_enabled_models'])

    def test_permission_and_final_year_boundaries(self):
        spec=importlib.util.spec_from_file_location('ahe_validate',ROOT/'validate.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        spec=importlib.util.spec_from_file_location('ahe_policy',ROOT/'overlay/historical_availability.py')
        # Overlay intentionally reads its manifest beside itself in prepared src.
        source=(ROOT/'overlay/historical_availability.py').read_text()
        ns={'__file__':str(ROOT/'historical_availability.py')};exec(compile(source,'policy','exec'),ns)
        rule=dict(earliest_year=1860,final_construction_year=1900,allow_map_generation=False,
                  allow_natural_and_gs=True,allow_player_funding_and_prospecting=False)
        condition=ns['condition_for_rule'](rule)
        for year in [1859,1860,1900,1901]:
            for route in range(4):self.assertEqual(module.condition_allows(condition,year,route),1860<=year<=1900 and route==1)

    def test_all_fresh_milestones_observed(self):
        r=read('integration-result.json')
        self.assertEqual([x['year'] for x in r['results']],[1830,1850,1870,1900,1925,1950,1975,2000,2025])
        self.assertTrue(all(x['passed'] for x in r['results']))
        for x in r['results']:
            self.assertEqual(sum('AHE5 DEITY id=' in s for s in x['lines']),92)
            self.assertEqual(sum('AHE5 FUND id=' in s for s in x['lines']),92)

    def test_executed_construction_boundaries_and_parameter_controls(self):
        r=read('runtime-phase5-result.json')
        self.assertTrue(r['passed']);self.assertEqual(len(r['cases']),16)
        self.assertTrue(all(c['passed'] for c in r['cases']))

    def test_persistent_world_and_reload(self):
        r=read('progression-result.json');self.assertTrue(r['passed'])
        lines=[s for phase in r['results'] for s in phase['lines']]
        self.assertEqual(sum('AHE5P MILESTONE' in s for s in lines),9)
        self.assertTrue(any('RELOADED year=1872' in s for s in lines))

    def test_real_steel_delivery_not_only_payments(self):
        r=read('production-phase5-result.json');self.assertTrue(r['passed'])
        lines=[s for phase in r['results'] for s in phase['lines']]
        self.assertTrue(any('RELOAD iron=8 coke=0' in s for s in lines))
        self.assertTrue(any('delivered_steel=4 remaining_iron=2 failures=0' in s for s in lines))

    def test_paid_services_and_stock_controls(self):
        for name in ['coal_rail','grain_horse','timber_rail']:
            for prefix in ['', 'stock-']:
                r=read(prefix+'gameplay-controlled-'+name+'-result.json')['results'][0]
                self.assertTrue(r['paid_delivery_verified']);self.assertEqual(len(r['years']),5)
        self.assertTrue(read('gameplay-passenger_ship-result.json')['results'][0]['paid_delivery_verified'])
        self.assertTrue(next(x for x in read('gameplay-result.json')['results'] if x['case']=='passenger_horse')['paid_delivery_verified'])

    def test_artifact_evidence_matches(self):
        version=read('historical_manifest.json')['version']
        artifact=ROOT/f'dist/axis-historical-europe-{version}.grf'
        expected=read('validation-phase5-result.json')['artifact_sha256']
        if artifact.exists():self.assertEqual(hashlib.sha256(artifact.read_bytes()).hexdigest(),expected)
        for name in ['integration-result.json','progression-result.json','production-phase5-result.json','runtime-phase5-result.json']:
            self.assertEqual(read(name)['grf_sha256'],expected)
        self.assertEqual(read('bundle-rebuild-phase5-result.json')['rebuilt_grf_sha256'],expected)

    def test_complete_original_scenario_review(self):
        with (REPO/'docs/research/axis_historical_existing_industry_review.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),1387)
        self.assertFalse(any(r['source_id']=='UNRESOLVED' for r in rows))
        self.assertEqual(sum(r['matches_1830_construction_policy']=='False' for r in rows),463)
        self.assertTrue(read('preservation-phase5-result.json')['passed'])


if __name__=='__main__':unittest.main()
