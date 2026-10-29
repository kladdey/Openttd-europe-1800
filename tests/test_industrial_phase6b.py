"""Regression checks on real compiled/runtime/preservation evidence, no game edits."""
import csv,hashlib,json,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/research'


def read(name):return json.loads((DATA/name).read_text(encoding='utf8'))


class IndustrialCandidateTests(unittest.TestCase):
    def test_cargo_slots_and_original_industry_recipes(self):
        old=read('industrial_1830_source_matrix.json');new=read('industrial_1830_candidate_matrix.json')
        self.assertEqual(len(old['industries']),92);self.assertEqual(len(new['industries']),96)
        self.assertEqual(len(new['cargo_slots']),64);self.assertEqual(old['cargo_slots'],new['cargo_slots'])
        lookup={r['local_id']:r for r in new['industries']}
        self.assertEqual(len(lookup),96)
        for row in old['industries']:
            with self.subTest(industry=row['industry']):
                for field in ['accepted','produced','properties','layouts','earliest_year']:
                    self.assertEqual(row[field],lookup[row['local_id']][field])
        self.assertEqual(set(lookup)-{r['local_id'] for r in old['industries']},{105,123,124,125})

    def test_no_unsupported_new_cargos_or_id_collisions(self):
        matrix=read('industrial_1830_candidate_matrix.json');labels={r['cargo_label'] for r in matrix['cargo_slots']}
        ids=[r['local_id'] for r in matrix['industries']]
        self.assertTrue(all(0<=id_<128 for id_ in ids))
        for row in matrix['industries']:
            self.assertTrue(set(row['accepted'])<=labels,row['industry'])
            self.assertTrue({c[0] for c in row['produced']}<=labels,row['industry'])

    def test_all_six_economies_preserved(self):
        result=read('copper_salt_source_preservation.json')
        self.assertTrue(result['all_existing_industry_models_identical']);self.assertTrue(result['all_economy_cargo_orders_identical'])
        self.assertEqual(len(result['changes']),6)
        for economy,row in result['changes'].items():
            self.assertFalse(row['changed_existing'],economy)
            self.assertEqual(len(row['added']),4 if economy=='BASIC_TEMPERATE' else 0)

    def test_real_loaded_output_and_negative_controls(self):
        tests=read('copper_salt_runtime_validation.json')['tests'];self.assertEqual(len(tests),3)
        for row in tests:
            self.assertEqual(row['evidence'],'VERIFIED IN GAME');self.assertGreater(row['production_first_observed'],0)
            self.assertTrue(row['negative_controls']);self.assertEqual(len(row['paid_events']),4 if row['kind']=='copper' else 3)
            self.assertTrue(all(e['positive_vehicle_profit_delta']>0 for e in row['paid_events']))
            self.assertEqual(row['persistence'][0]['row'],row['persistence'][1]['row'])

    def test_availability_and_deity_rejection_are_not_hidden(self):
        events=read('copper_salt_availability_validation.json')['events']
        for id_ in [56,67]:self.assertIn(f'POLICY|{id_}|deity=false|company_raw_disabled=false|company_raw_enabled=false',events)
        self.assertIn('DEITY_BUILD|false|ERR_PRECONDITION_FAILED|0|0',events)

    def test_placement_counts_and_actual_ids(self):
        with (DATA/'industry_placement_results.csv').open(encoding='utf8') as f:rows=list(csv.DictReader(f))
        good=[r for r in rows if r['status']=='PLACED']
        self.assertEqual(len(rows),708);self.assertEqual(len(good),467)
        self.assertEqual(len({r['industry_id'] for r in good}),467)
        self.assertEqual(len({r['local_id'] for r in good}),40)
        self.assertTrue(all(r['x'] and r['y'] and r['engine_case'] for r in good))
        self.assertEqual(sum(r['status']=='FAILED' for r in rows),241)

    def test_critical_new_chain_edges_and_explicit_waste(self):
        graph=read('industry_chain_graph.json')['cargos']
        for label in ['CORE','COPR','SALT','FOOD']:
            self.assertTrue(graph[label]['producers']);self.assertTrue(graph[label]['consumers'])
        self.assertFalse(graph['SLAG']['consumers'],'Do not silently add a future slag consumer')

    def test_preservation_and_real_engine_roundtrips(self):
        p=read('industrialized_scenario_validation.json')
        self.assertEqual(p['original_towns'],617);self.assertEqual(p['industry_instances'],467)
        self.assertEqual(p['height_changes'],0);self.assertEqual(p['existing_infrastructure_changes'],0)
        for key in ['original_town_rows_bit_identical','completed_438_industry_records_bit_identical','scenario_editor_load_save_reload_verified','editor_roundtrip_all_map_arrays_and_town_industry_newgrf_rows_identical','source_scenario_unchanged']:self.assertTrue(p[key],key)
        self.assertEqual(len(p['gameplay_roundtrips']),2)

    def test_actual_europe_deliveries(self):
        rows=read('industrial_route_validation.json')['tests']
        self.assertEqual({r['name'] for r in rows},{'british_coal','ruhr_coal','grain','timber','iron','salt','coastal_fish','passengers','mail'})
        for r in rows:
            self.assertEqual(r['status'],'VERIFIED IN GAME',r['name'])
            self.assertTrue(any(e.startswith('CONTROL_PAID|') for e in r['events']))
            self.assertTrue(any(e.startswith('CAMPAIGN_PASS|') for e in r['events']))

    def test_delivered_files_match_verified_checksums(self):
        result=read('industrialized_scenario_delivery.json')
        for key in ['candidate','newgrf','legacy_0_2']:
            p=Path(result[key]['path'])
            if not p.exists():self.skipTest('Local game files are not redistributed with the repository')
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),result[key]['sha256'])
        self.assertFalse(result['normal_configuration_modified']);self.assertFalse(result['existing_newgrf_files_modified'])


if __name__=='__main__':unittest.main()
