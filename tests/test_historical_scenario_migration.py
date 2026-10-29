"""Safety gates and retained engine evidence for the specific empty-world migration."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from repair_industry_free_editor_candidate import validate_empty_world


def read(name):return json.loads((ROOT/'docs/research'/name).read_text())


class EmptyScenarioMigrationTests(unittest.TestCase):
    def setUp(self):
        evidence=read('axis_migration_editor_pilot.json')
        self.original=evidence['source'];self.pilot=evidence['candidate']

    def test_specific_empty_source_and_editor_selection(self):
        validate_empty_world(self.original,self.pilot)
        self.assertEqual(self.original['town_records'],613)
        self.assertEqual(self.original['map_dimensions'],[4096,4096])

    def test_refuses_industries_and_hidden_industry_tiles(self):
        for field in ['industry_records','industry_tiles']:
            for side in ['source','pilot']:
                a=copy.deepcopy(self.original);b=copy.deepcopy(self.pilot)
                (a if side=='source' else b)[field]=1
                with self.assertRaises(AssertionError):validate_empty_world(a,b)

    def test_refuses_existing_vehicles_stations_or_persistent_storage(self):
        for field in ['VEHS','STNN','PSAC']:
            a=copy.deepcopy(self.original);a['chunks'][field]['records']=2
            with self.assertRaises(AssertionError):validate_empty_world(a,self.pilot)

    def test_refuses_other_set_or_parameter_changes(self):
        b=copy.deepcopy(self.pilot);b['newgrfs'][2]['params'][0]=99
        with self.assertRaises(AssertionError):validate_empty_world(self.original,b)
        b=copy.deepcopy(self.pilot);b['newgrfs'][13]['params'][2]=4
        with self.assertRaises(AssertionError):validate_empty_world(self.original,b)

    def test_engine_editor_preserved_every_other_chunk(self):
        result=read('axis_migration_editor_roundtrip.json')
        self.assertEqual(set(result['changed_chunks']),{'DATE','GLOG','NGRF','IIDS','TIDS'})
        self.assertEqual(result['source']['chunks']['CITY'],result['candidate']['chunks']['CITY'])
        for tag in result['source']['chunks']:
            if tag.startswith(('MAP','M3')):self.assertEqual(result['source']['chunks'][tag],result['candidate']['chunks'][tag])

    def test_actual_game_load_save_reload(self):
        report=read('axis_europe_migration_runtime.json')
        self.assertTrue(report['passed']);self.assertEqual(len(report['phases']),2)
        for phase in report['phases']:
            self.assertTrue(phase['passed']);self.assertFalse(phase['allocation_overflow'])
            self.assertEqual(sum('HMIG INDUSTRY|' in s for s in phase['lines']),92)
            self.assertEqual(sum('HMIG CARGO|' in s for s in phase['lines']),64)
        self.assertFalse(report['delivered_candidate_modified_by_test'])

    def test_delivery_and_original_preservation(self):
        report=read('axis_europe_scenario_delivery.json')
        self.assertTrue(report['passed']);self.assertEqual(report['calendar_date'],'1830-01-01')
        self.assertEqual(report['industry_instances'],0);self.assertEqual(report['industry_tiles'],0)
        self.assertTrue(report['town_chunk_bit_identical']);self.assertEqual(report['towns'],613)
        self.assertEqual(report['spawning_parameter_preserved'],0)
        self.assertEqual(len(report['map_arrays_bit_identical']),10)


if __name__=='__main__':unittest.main()
