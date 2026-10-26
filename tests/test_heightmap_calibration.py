import csv
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
DEPS = all(importlib.util.find_spec(n) for n in ['numpy', 'scipy', 'PIL'])


@unittest.skipUnless(DEPS, 'Install requirements-geography.txt for terrain/calibration tests')
class CalibrationTerrainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import geography as g
        import scenario_geography as s
        import calibrate_heightmap as c
        cls.g, cls.s, cls.c = g, s, c
        cls.out = ROOT/'maps/calibration/geography_v6'

    def test_importer_exact_float32_rotation_and_interior_bounds(self):
        self.assertEqual(self.s.import_target(.25, .75, 'clockwise'), (1023, 3071))
        self.assertEqual(self.s.import_target(.25, .75, 'counter_clockwise'), (1023, 1023))
        self.assertEqual(self.s.source_pixel(.25, .75), (3072, 1023))
        for x, y in [(0, .5), (1, .5), (.5, 0), (.5, 1), (float('nan'), .5)]:
            with self.assertRaises(ValueError):
                self.s.import_target(x, y)

    def test_framed_chunk_parser_rejects_malformed_data(self):
        # Embedded MAPT tag is payload data, not a new chunk.
        body = b'TEST\0\0\0\x04MAPT\0\0\0\0'
        chunks = list(self.s.chunks(body))
        self.assertEqual(len(chunks), 1)
        self.assertEqual(bytes(chunks[0][2][0]), b'MAPT')
        for malformed in [b'MAPT\0\0\0\x08short', b'PATS\x03\x10short', b'TEST\x0f', b'']:
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                list(self.s.chunks(malformed))

    def test_holdouts_are_spatially_disjoint_and_model_is_diagnostic(self):
        pts, holdout = self.c.coastline_samples()
        train_cells = {(int(a//2), int(b//2)) for a, b in pts[~holdout]}
        held_cells = {(int(a//2), int(b//2)) for a, b in pts[holdout]}
        self.assertFalse(train_cells & held_cells)
        models = self.g.read_json(self.out/'coastline_models.json')
        self.assertGreater(models['axis_affine']['holdout_samples'], 900)
        self.assertLess(models['axis_affine']['holdout_p90_coast_distance_pixels'], 12)
        self.assertLess(models['axis_affine']['holdout_p90_coast_distance_pixels'],
                        models['mercator']['holdout_p90_coast_distance_pixels'])
        self.assertEqual(self.g.read_json(self.out/'summary.json')['independently_surveyed_town_positions'], 0)

    def test_candidate_preserves_master_metadata_and_spacing(self):
        candidate = self.g.read_json(self.out/'Europe_1800_V6_REGIONAL_GEOGRAPHIC_TEST.json')
        master = {t['name']: t for t in self.g.read_json(self.g.MASTER)}
        self.g.validate(candidate)
        for t in candidate:
            self.assertEqual(set(t), {'name', 'population', 'city', 'x', 'y'})
            for field in ('population', 'city'):
                self.assertEqual(t[field], master[t['name']][field])
        self.assertGreater(min(r['distance_tiles'] for r in self.g.spacing(candidate)), 30)
        self.assertEqual({t['name'] for t in candidate} & {'LONDON', 'STOCKHOLM', 'BOULOGNE'}, set())
        self.assertTrue(all(t['x'] != master[t['name']]['x'] or t['y'] != master[t['name']]['y'] for t in candidate))

    def test_all_regional_towns_accounted_for(self):
        with (self.out/'regional_validation.csv').open(encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        with (self.out/'regional_deferred.csv').open(encoding='utf-8') as f:
            deferred = list(csv.DictReader(f))
        candidate = self.g.read_json(self.out/'Europe_1800_V6_REGIONAL_GEOGRAPHIC_TEST.json')
        expected = {t['name'] for t in self.g.read_json(self.g.V4)} | {'VERSAILLES', 'BOULOGNE', 'GREENWICH'}
        self.assertEqual({r['name'] for r in rows}, expected)
        self.assertEqual({t['name'] for t in candidate} | {r['name'] for r in deferred}, expected)
        self.assertFalse({t['name'] for t in candidate} & {r['name'] for r in deferred})
        self.assertTrue(all(r['reason'] for r in deferred))
        retained_rows = [r for r in rows if r['decision'] == 'RETAINED_TEST_ONLY']
        self.assertEqual(len(retained_rows), len(candidate))
        self.assertTrue(all(r['landmass'] in ('Great Britain', 'Ireland', 'continental Europe') for r in retained_rows))
        brandenburg = next(r for r in rows if r['name'] == 'BRANDENBURG')
        self.assertEqual(float(brandenburg['longitude']), 12.533)
        self.assertEqual(float(brandenburg['latitude']), 52.417)
        with (self.out/'catalogue_projection_review.csv').open(encoding='utf-8') as f:
            self.assertEqual(len(list(csv.DictReader(f))), 600)

    def test_actual_source_assets_and_candidate_land_placement(self):
        from PIL import Image
        import numpy as np
        assets = ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():
            self.skipTest('Original source assets required for real terrain checks')
        before = {p: self.g.digest(assets/p) for p in self.c.HASHES}
        self.assertEqual(before, self.c.HASHES)
        raw = np.array(Image.open(assets/'heightmaps/Europe_heightmap_original.png'))[:, :, 0]
        candidate = self.g.read_json(self.out/'Europe_1800_V6_REGIONAL_GEOGRAPHIC_TEST.json')
        for scenario in ['Europe_1800_V1.scn', 'Europe_1800_Industries_Original.scn']:
            tile_types, heights = self.s.read_terrain(assets/'scenarios'/scenario)
            best = max(self.c.orientation(raw, tile_types, heights), key=lambda r: r['sampled_height_correlation'])
            self.assertTrue(best['flip_columns'])
            for t in candidate:
                tx, ty = self.s.import_target(t['x'], t['y'])
                col, row = self.s.source_pixel(t['x'], t['y'])
                with self.subTest(scenario=scenario, town=t['name']):
                    self.assertGreater(int(raw[row, col]), 0)
                    self.assertEqual(int(tile_types[ty, tx]), 0)
        self.assertEqual(before, {p: self.g.digest(assets/p) for p in before})


if __name__ == '__main__':
    unittest.main()
