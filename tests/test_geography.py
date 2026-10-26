import copy
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/geography.py'
spec = importlib.util.spec_from_file_location('geography', SCRIPT)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.towns = g.read_json(g.V4)

    def test_existing_datasets_and_anchors(self):
        for path, count in [(g.MASTER, 600), (g.V4, 40), (g.V2, 5)]:
            towns = g.read_json(path)
            g.validate(towns)
            self.assertEqual(len(towns), count)
        indexed = {t['name']: t for t in self.towns}
        for t in g.read_json(g.V2):
            self.assertEqual(t, indexed[t['name']])

    def test_bounds_and_types(self):
        for bad in [-0.001, 1.001, float('nan'), float('inf'), True, '0.3', None]:
            towns = copy.deepcopy(self.towns)
            towns[0]['x'] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                g.validate(towns)

    def test_unicode_duplicate_names(self):
        towns = copy.deepcopy(self.towns)
        towns[1]['name'] = '  london '
        with self.assertRaises(ValueError):
            g.validate(towns)

    def test_spacing_policy_boundaries(self):
        self.assertEqual(g.band(14.999), 'under_15_review_importance')
        for d in (15, 30):
            self.assertEqual(g.band(d), '15_to_30_individual_review')
        self.assertEqual(g.band(30.001), 'over_30_generally_coexist')
        a, b = dict(x=0, y=0), dict(x=3/4096, y=4/4096)
        self.assertEqual(g.distance(a, b), 5)
        self.assertGreater(min(r['distance_tiles'] for r in g.spacing(self.towns)), 30)

    def test_reproducible_audit_preserves_inputs(self):
        paths = (g.MASTER, g.V4, g.V2, g.INVENTORY)
        before = [g.digest(p) for p in paths]
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td)/'a', Path(td)/'b'
            summary = g.audit(a)
            g.audit(b)
            self.assertEqual(summary['geographically_validated'], 0)
            self.assertEqual(summary['existing_v4_metadata_discrepancies'], 3)
            for file in a.iterdir():
                self.assertEqual(file.read_bytes(), (b/file.name).read_bytes())
            with (a/'catalogue_review.csv').open() as f:
                self.assertEqual(len(list(csv.DictReader(f))), 600)
            with self.assertRaises(FileExistsError):
                g.audit(a)
        self.assertEqual(before, [g.digest(p) for p in paths])


class MappingTests(unittest.TestCase):
    def test_explicit_axis_and_flip_mapping(self):
        self.assertEqual(g.game_to_pixel(.25, .75, 101, 201, [[1, 0, 0], [0, 1, 0]]), (25, 150))
        self.assertEqual(g.game_to_pixel(.25, .75, 101, 201, [[0, 1, 0], [-1, 0, 1]]), (75, 150))
        self.assertEqual(g.game_to_pixel(1, 0, 4096, 4096, [[1, 0, 0], [0, 1, 0]]), (4095, 0))
        with self.assertRaises(ValueError):
            g.game_to_pixel(.3, .4, 101, 201, [[0, 0, 0], [0, 0, 0]])

    @unittest.skipUnless(importlib.util.find_spec('PIL'), 'Pillow optional')
    def test_raster_sampling_and_hash_gate(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            im = Image.new('L', (3, 3), 100)
            im.putpixel((0, 2), 0)
            im.save(p/'raster.png')
            towns = [dict(name='low', x=0, y=1, population=300, city=False),
                     dict(name='high', x=1, y=0, population=300, city=False)]
            (p/'towns.json').write_text(json.dumps(towns))
            m = dict(mapping_evidence='Synthetic fixture only', raster_sha256=g.digest(p/'raster.png'),
                     raster_dimensions=[3, 3], game_to_raster_matrix=[[1, 0, 0], [0, 1, 0]],
                     pixel_convention='normalized_endpoints_nearest', zero_elevation_threshold=0)
            (p/'mapping.json').write_text(json.dumps(m))
            result = g.terrain(p/'towns.json', p/'raster.png', p/'mapping.json', p/'terrain.csv')
            self.assertEqual(result, dict(sampled=2, land_validated=0))
            with (p/'terrain.csv').open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]['raster_status'], 'ZERO_OR_LOW_REVIEW')
            self.assertEqual(rows[1]['raster_status'], 'NONZERO_REVIEW')
            self.assertTrue(all(r['land_status'] == 'UNVERIFIED_IN_GAME' for r in rows))
            m['raster_sha256'] = 'wrong'
            (p/'mapping.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                g.terrain(p/'towns.json', p/'raster.png', p/'mapping.json', p/'bad.csv')
            self.assertFalse((p/'bad.csv').exists())


@unittest.skipUnless(importlib.util.find_spec('numpy'), 'NumPy optional')
class CalibrationTests(unittest.TestCase):
    def test_independent_holdout_detects_wrong_control(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'controls.csv'
            fields = ['name', 'longitude', 'latitude', 'column', 'row', 'role', 'evidence']
            rows = []
            for i, (lon, lat) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2)]):
                rows.append(dict(name=str(i), longitude=lon, latitude=lat, column=10+2*lon,
                                 row=20+3*lat, role='fit' if i < 3 else 'holdout', evidence='synthetic'))
            def write():
                with p.open('w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()
                    w.writerows(rows)
            write()
            self.assertTrue(g.fit_controls(p, 1)['holdout_threshold_passed'])
            rows[-1]['column'] += 20
            write()
            result = g.fit_controls(p, 1)
            self.assertFalse(result['holdout_threshold_passed'])
            self.assertFalse(result['release_validated'])
            rows[-1]['longitude'], rows[-1]['latitude'] = 0, 0
            write()
            with self.assertRaisesRegex(ValueError, 'reused'):
                g.fit_controls(p, 1)


if __name__ == '__main__':
    unittest.main()
