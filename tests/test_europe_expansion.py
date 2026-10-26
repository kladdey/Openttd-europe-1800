import csv
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
DEPS = all(importlib.util.find_spec(n) for n in ['numpy', 'PIL', 'scipy'])


@unittest.skipUnless(DEPS, 'Install requirements-geography.txt')
class EuropeExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import geography as g
        import expand_europe_towns as e
        cls.g, cls.e = g, e
        cls.path = ROOT/'maps/calibration/geography_v7'
        cls.all = g.read_json(cls.path/e.ALL_FILE)
        cls.summary = g.read_json(cls.path/'summary.json')
        with (cls.path/'all_600_placement_audit.csv').open(encoding='utf-8') as f:
            cls.rows = list(csv.DictReader(f))

    def test_all_master_records_accounted_and_metadata_preserved(self):
        master = {t['name']: t for t in self.g.read_json(self.g.MASTER)}
        self.assertEqual({r['name'] for r in self.rows}, set(master))
        self.assertEqual(len(self.rows), 600)
        self.g.validate(self.all)
        for t in self.all:
            self.assertEqual(set(t), {'name', 'population', 'city', 'x', 'y'})
            for field in ('population', 'city'):
                self.assertEqual(t[field], master[t['name']][field])
        deferred = {r['name'] for r in self.rows if r['coverage_status'] == 'DEFERRED_OUTSIDE_MAP'}
        self.assertEqual(set(master), {t['name'] for t in self.all} | deferred)
        self.assertFalse({t['name'] for t in self.all} & deferred)
        self.assertEqual(len(self.all), self.summary['all_in_bounds_towns'])
        for r in self.rows:
            if r['name'] in deferred:
                self.assertTrue(r['reason'])
                self.assertTrue(not (0 < float(r['projected_row'])/4095 < 1) or
                                not (0 < float(r['projected_column'])/4095 < 1))

    def test_missing_companions_and_homonyms_corrected(self):
        names = {t['name'] for t in self.all}
        self.assertTrue({'Głogów', 'Łowicz', 'Sieradz', 'Rawicz', 'Písek', 'Krems'} <= names)
        rows = {r['name']: r for r in self.rows}
        self.assertLess(float(rows['BREST']['longitude']), 0)
        self.assertGreater(float(rows['MUNSTER']['longitude']), 7)
        self.assertGreater(float(rows['FREIBURG']['latitude']), 47)
        self.assertGreater(float(rows['BOULOGNE']['latitude']), 50)
        self.assertIn('Provisional', rows['BOULOGNE']['override_reason'])
        for region, lat, lon in [('France', 52.09755, 23.68775), ('Germany', 52.34333, -8.71667), ('Germany', 46.66667, 7.16667)]:
            with self.assertRaises(ValueError):
                self.e.check_region(region, lat, lon)

    def test_close_neighbours_and_water_targets_not_silently_deleted(self):
        names = {t['name'] for t in self.all}
        self.assertTrue({'LONDON', 'ROSTOCK', 'TROYES', 'GREENWICH', 'VERSAILLES', 'BOULOGNE'} <= names)
        with (self.path/'close_pairs_review.csv').open(encoding='utf-8') as f:
            pairs = list(csv.DictReader(f))
        self.assertTrue(pairs)
        self.assertTrue(all(r['town_a'] in names and r['town_b'] in names for r in pairs))
        self.assertEqual(sum(float(r['distance_tiles']) < 15 for r in pairs), self.summary['pairs_under_15'])
        self.assertTrue(all('review pending' in r['decision'] for r in pairs))

    def test_actual_land_subset_and_reproducible_export(self):
        assets = ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():
            self.skipTest('Source assets needed')
        from PIL import Image
        from scenario_geography import read_terrain, import_target, source_pixel
        import numpy as np
        land = self.g.read_json(self.path/self.e.LAND_FILE)
        self.assertEqual({t['name'] for t in land}, {r['name'] for r in self.rows if r['direct_clear_land'] == 'True'})
        with Image.open(assets/'heightmaps/Europe_heightmap_original.png') as im:
            raw = np.array(im)[:, :, 0]
        for file in ['Europe_1800_V1.scn', 'Europe_1800_Industries_Original.scn']:
            types, _ = read_terrain(assets/'scenarios'/file)
            for t in land:
                tx, ty = import_target(t['x'], t['y'])
                col, row = source_pixel(t['x'], t['y'])
                self.assertGreater(int(raw[row, col]), 0)
                self.assertEqual(int(types[ty, tx]), 0)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'export'
            self.e.export(assets, out)
            for file in out.iterdir():
                self.assertEqual(file.read_bytes(), (self.path/file.name).read_bytes(), file.name)
            with self.assertRaises(FileExistsError):
                self.e.export(assets, out)


if __name__ == '__main__':
    unittest.main()
