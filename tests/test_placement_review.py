import csv
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
DEPS = all(importlib.util.find_spec(n) for n in ['numpy', 'scipy', 'PIL'])


@unittest.skipUnless(DEPS, 'Install requirements-geography.txt')
class PlacementDeskReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import geography as g
        import review_europe_placements as r
        cls.g, cls.r = g, r
        cls.out = ROOT/'maps/calibration/geography_v8'
        cls.original = g.read_json(r.V7/'Europe_1800_V7_ALL_IN_BOUNDS_TEST.json')
        cls.full = g.read_json(cls.out/r.FULL_FILE)
        cls.core = g.read_json(cls.out/r.CORE_FILE)

    def test_all_records_accounted_and_master_preserved(self):
        master = {t['name']: t for t in self.g.read_json(self.g.MASTER)}
        self.g.validate(self.full)
        self.g.validate(self.core)
        decisions = self.r.rows(self.out/'all_600_decisions.csv')
        self.assertEqual(len(decisions), 600)
        self.assertEqual({r['name'] for r in decisions}, set(master))
        self.assertEqual(len(self.full), 576)
        self.assertEqual({t['name'] for t in self.full}, {t['name'] for t in self.original})
        self.assertEqual({t['name'] for t in self.core}, {r['name'] for r in decisions if r['state'] == 'RETAINED_DESK_CANDIDATE'})
        for t in self.full:
            for field in ('name', 'population', 'city'):
                self.assertEqual(t[field], master[t['name']][field])
        self.assertTrue(all(r['reason'] for r in decisions if r['state'].startswith('DEFERRED')))

    def test_only_supported_coordinate_inputs_change(self):
        before = {t['name']: t for t in self.original}
        changed = {t['name'] for t in self.full if t != before[t['name']]}
        self.assertEqual(changed, {'CASTROGIOVANNI', 'PIAZZA (ENNA)'})
        decisions = {r['name']: r for r in self.r.rows(self.out/'all_600_decisions.csv')}
        for name in changed:
            self.assertEqual(decisions[name]['direct_clear_land'], 'True')
            self.assertEqual(decisions[name]['v1_tile_type'], '0')
            self.assertEqual(decisions[name]['industries_tile_type'], '0')
        checks = self.r.rows(self.out/'coordinate_reference_audit.csv')
        self.assertEqual(len(checks), 31)
        for name in changed:
            c = next(r for r in checks if r['name'] == name)
            self.assertGreater(float(c['prior_difference_km']), 10)
            self.assertEqual(float(c['current_difference_km']), 0)
        self.assertNotIn('MODICA/POZZALLO', {t['name'] for t in self.core})
        self.assertIn('MODICA/POZZALLO', {t['name'] for t in self.full})

    def test_correct_geography_before_spacing_decision(self):
        pairs = self.r.rows(self.out/'spacing_review.csv')
        calta = next(r for r in pairs if r['town_a'] == 'CALTANISSETA')
        self.assertLess(float(calta['v7_distance_tiles']), 15)
        self.assertGreater(float(calta['corrected_distance_tiles']), 15)
        self.assertEqual(calta['recommendation'], 'RETAIN_BOTH')
        self.assertEqual(calta['both_in_candidate'], 'True')
        names = {t['name'] for t in self.core}
        self.assertTrue({'CASTROGIOVANNI', 'CALTANISSETA', 'PIAZZA (ENNA)'} <= names)
        self.assertFalse(any(d < 15 for d in self.r.close_pairs(self.core).values()))
        self.assertTrue({'MESSINA', 'REGGIO DI CALABRIA', 'KRAKOW', 'Wieliczka', 'Cetinje', 'Kotor', 'VERSAILLES'} <= names)

    def test_every_old_and_new_pair_has_a_consistent_decision(self):
        policy, deferred, old, new = self.r.checked_policy(self.original, self.full)
        self.assertEqual(set(policy), set(old) | set(new))
        self.assertEqual(len(old), 70)
        self.assertEqual(len(new), 71)
        self.assertEqual(len(policy), 72)
        self.assertEqual(len(deferred), 11)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'bad_policy.csv'
            records = self.r.rows(self.r.POLICY)
            def write(values):
                with p.open('w', encoding='utf-8', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=list(records[0]))
                    w.writeheader(); w.writerows(values)
            write(records[:-1])
            with patch.object(self.r, 'POLICY', p), self.assertRaisesRegex(ValueError, 'explicit review'):
                self.r.checked_policy(self.original, self.full)
            for row in records:
                if row['town_a'] == 'DELFT' and row['town_b'] == 'LEIDEN':
                    row['recommendation'] = 'RETAIN_BOTH'
            write(records)
            with patch.object(self.r, 'POLICY', p), self.assertRaisesRegex(ValueError, 'Contradictory'):
                self.r.checked_policy(self.original, self.full)

    def test_refined_terrain_categories_are_not_founding_claims(self):
        terrain = self.r.rows(self.out/'terrain_review_refined.csv')
        self.assertEqual(len(terrain), 56)
        self.assertEqual({r['name'] for r in terrain}, {r['name'] for r in self.r.rows(self.r.V7/'terrain_review.csv')})
        for r in terrain:
            category = r['category']
            if category == 'SAVED_ROAD_OCCUPANCY':
                self.assertEqual(r['v1_tile_type'], '2')
                self.assertGreater(int(r['raw_elevation']), 0)
            elif category == 'SOURCE_ZERO_OCEAN_CONNECTED':
                self.assertEqual(r['raw_elevation'], '0')
                self.assertEqual(r['source_ocean_connected'], 'True')
            elif category == 'SAVED_WATER_OVER_NONZERO_SOURCE':
                self.assertEqual(r['v1_tile_type'], '6')
                self.assertGreater(int(r['raw_elevation']), 0)
            else:
                self.fail('Unknown terrain category')
        summary = self.g.read_json(self.out/'summary.json')
        self.assertEqual(summary['in_game_tests'], 0)
        self.assertFalse(summary['reference_checks_are_raster_holdouts'])
        self.assertEqual(summary['unresolved_terrain_in_candidate'], 54)

    def test_regeneration_preserves_sources_and_matches_snapshot(self):
        assets = ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():
            self.skipTest('Source assets needed for read-only terrain review')
        before = {p: self.g.digest(assets/p) for p in self.r.HASHES}
        master_before = self.g.digest(self.g.MASTER)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'review'
            self.r.generate(assets, out)
            for p in out.iterdir():
                self.assertEqual(p.read_bytes(), (self.out/p.name).read_bytes(), p.name)
            with self.assertRaises(FileExistsError):
                self.r.generate(assets, out)
        self.assertEqual(master_before, self.g.digest(self.g.MASTER))
        self.assertEqual(before, {p: self.g.digest(assets/p) for p in before})


if __name__ == '__main__':
    unittest.main()
