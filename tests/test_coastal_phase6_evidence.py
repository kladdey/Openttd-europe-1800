"""Independent reconciliation of Phase 6A CSVs with retained engine evidence."""
import csv,json,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/research'


def rows(name):
    with (DATA/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))


class CoastalEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery=json.loads((DATA/'coastal_scenario_delivery.json').read_text(encoding='utf8'))
        cls.evidence=json.loads((DATA/'coastal6a_run_evidence.json').read_text(encoding='utf8'))

    def test_original_town_inventory_is_complete_and_unique(self):
        original=rows('existing_coastal_towns.csv')
        self.assertEqual(len(original),613)
        self.assertEqual({int(r['town_id']) for r in original},set(range(613)))
        self.assertEqual(sum(int(r['practical_dock_tile'])>=0 for r in original),82)
        self.assertEqual(len({r['practical_dock_tile'] for r in original if int(r['practical_dock_tile'])>=0}),80)

    def test_new_towns_reconcile_and_have_no_duplicate_identity(self):
        added=rows('added_port_towns.csv');original=rows('existing_coastal_towns.csv')
        self.assertEqual(len(added),self.delivery['added_towns'])
        self.assertEqual(len(added)+len(original),self.delivery['final_towns'])
        self.assertEqual(len({r['name'].casefold() for r in added}),len(added))
        self.assertFalse({r['name'].casefold() for r in added}&{r['name'].casefold() for r in original})
        for r in added:
            self.assertTrue(r['history_source'].startswith('https://'))
            self.assertEqual(r['actual_dock_built'],'true')
            self.assertEqual(r['water_edge_connected'],'true')
            self.assertLessEqual(abs(int(r['x'])-int(r['seed_x']))+abs(int(r['y'])-int(r['seed_y'])),10)

    def test_all_proposals_have_a_decision_and_deferrals_are_retained(self):
        proposals=rows('proposed_port_towns.csv');rejected=rows('rejected_port_candidates.csv')
        self.assertEqual(len(proposals),11)
        self.assertTrue(all(r['decision'] in ('ACCEPTED','DEFERRED') for r in proposals))
        deferred={r['name'] for r in proposals if r['decision']=='DEFERRED'}
        self.assertTrue(deferred<={r['name'] for r in rejected})
        self.assertTrue({'Fleetwood','Esbjerg','Memel','Londonderry'}<={r['name'] for r in rejected})

    def test_shipping_claims_match_actual_engine_lines(self):
        results=rows('coastal_accessibility_results.csv')
        voyages=[r for r in results if r['test_type']=='Actual ship voyage']
        self.assertEqual(len(voyages),4)
        self.assertTrue(all(r['arrived']=='true' for r in voyages))
        for r in voyages:
            case=next(p for p in self.evidence if p['case']==r['case'])
            self.assertEqual(case['engine_log_sha256'],r['engine_log_sha256'])
            self.assertTrue(any(f'C6 SHIP_RESULT|{r["name"]}|true|true|' in line for line in case['measurements']))
            self.assertTrue(any(f'C6 SHIP_ARRIVED|{r["name"]}|' in line for line in case['measurements']))

    def test_changed_tile_inventory_has_only_authorized_land_changes(self):
        changed=rows('coastal_changed_tiles.csv');added=rows('added_port_towns.csv')
        self.assertEqual(len(changed),self.delivery['guards']['changed_tiles'])
        self.assertEqual(len({r['tile'] for r in changed}),len(changed))
        for r in changed:
            self.assertIn(int(r['before_type']),(0,4))
            self.assertIn(int(r['after_type']),(0,2,3,4))
            self.assertNotIn('MAPH',r['changed_fields'])
            self.assertTrue(any(abs(int(r['x'])-int(t['x']))+abs(int(r['y'])-int(t['y']))<=35 for t in added))

    def test_all_grfs_and_original_settings_survived(self):
        self.assertEqual(len(self.delivery['newgrfs']),15)
        self.assertTrue(self.delivery['original_town_records_bit_identical'])
        self.assertTrue(self.delivery['all_other_chunks_bit_identical'])
        self.assertTrue(self.delivery['real_save_and_reload_passed'])
        for key in ['height_changes','water_type_changes','existing_infrastructure_changes']:
            self.assertEqual(self.delivery['guards'][key],0)
        load=next(p for p in self.evidence if p['case'].endswith(Path(self.delivery['load_case']).name))
        self.assertEqual(sum('C6 ACTIVE_GRF|' in line for line in load['measurements']),15)
        self.assertTrue(any('C6 SETTINGS|train_limit|7' in line for line in load['measurements']))


if __name__=='__main__':unittest.main()
