import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
DEPS = all(importlib.util.find_spec(n) for n in ['numpy','scipy','PIL'])


@unittest.skipUnless(DEPS, 'Install requirements-geography.txt')
class LandmarkEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import geography as g
        import validate_landmarks as v
        cls.g, cls.v = g, v
        cls.out = ROOT/'maps/calibration/geography_v9'
        cls.obs = v.rows(v.OBSERVATIONS)
        cls.coeff = g.read_json(v.MODEL)['axis_affine']['coefficients']

    def test_frozen_model_exposes_shift_instead_of_refitting(self):
        before = self.v.landmark_audit(self.obs, self.coeff)
        shifted = copy.deepcopy(self.obs)
        shifted[0]['observed_column'] = str(float(shifted[0]['observed_column'])+40)
        after = self.v.landmark_audit(shifted, self.coeff)
        self.assertEqual(before[1:], after[1:])
        self.assertEqual(before[0]['projected_column'], after[0]['projected_column'])
        self.assertAlmostEqual(before[0]['delta_column']-40, after[0]['delta_column'])
        self.assertEqual(after[0]['review_status'], 'EXCEEDS_FEATURE_ESTIMATE')

    def test_ambiguity_duplicates_and_bounds_are_not_silently_accepted(self):
        r = self.v.landmark_audit(self.obs, self.coeff)
        unresolved = [a for a in r if a['review_status']=='UNRESOLVED_IDENTIFICATION']
        self.assertEqual([a['name'] for a in unresolved], ['Cape Finisterre'])
        self.assertEqual(unresolved[0]['vector_difference_pixels'], '')
        self.assertEqual(len(r), 22)
        for field, value in [('observed_column','4096'),('observed_row','nan'),('feature_uncertainty_pixels','nan')]:
            bad=copy.deepcopy(self.obs); bad[0][field]=value
            with self.assertRaises(ValueError): self.v.landmark_audit(bad, self.coeff)
        with self.assertRaisesRegex(ValueError,'duplicate'):
            self.v.landmark_audit(self.obs+[self.obs[0]], self.coeff)

    def test_extremum_observation_uses_raster_and_explicit_box(self):
        import numpy as np
        raw=np.zeros((12,12), dtype='uint8'); raw[5:8,4:7]=20
        r=dict(name='synthetic cape',box_left='2',box_right='9',box_top='2',box_bottom='9',observation_rule='MAX_ROW')
        self.assertEqual(self.v.observe_extremum(raw,r),(5,7))
        raw[8,5]=20
        self.assertEqual(self.v.observe_extremum(raw,r),(5,8))
        raw[9,5]=20
        with self.assertRaisesRegex(ValueError,'box edge'): self.v.observe_extremum(raw,r)

    def test_catalogue_and_every_terrain_flag_remain_accounted_for(self):
        statuses=self.v.rows(self.out/'all_600_evidence_status.csv')
        self.assertEqual(len(statuses),600)
        self.assertEqual({r['name'] for r in statuses},{r['name'] for r in self.g.read_json(self.g.MASTER)})
        self.assertEqual(sum(r['evidence_status']=='DEFERRED' for r in statuses),36)
        terrain=self.v.rows(self.out/'retained_terrain_diagnostics.csv')
        self.assertEqual(len(terrain),54)
        self.assertEqual({r['name'] for r in terrain},{r['name'] for r in statuses if r['evidence_status']=='TERRAIN_REVIEW_OPEN'})
        for r in terrain:
            self.assertEqual(r['decision'],'KEEP_FLAGGED_UNMOVED')
            for radius in (5,10,16):
                for kind in ('source_land','both_saved_clear'):
                    self.assertTrue(0 <= float(r[f'r{radius}_{kind}_fraction']) <= 1)
        self.assertTrue(all(r['founding']=='UNTESTED' for r in statuses))

    def test_exact_terrain_orientation_and_regeneration(self):
        assets=ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():
            self.skipTest('Original assets required')
        from scenario_geography import source_pixel
        towns={t['name']:t for t in self.g.read_json(self.v.CANDIDATE)}
        old={r['name']:r for r in self.v.rows(self.v.V8/'terrain_review_refined.csv')}
        for r in self.v.rows(self.out/'retained_terrain_diagnostics.csv'):
            t=towns[r['name']]; actual=source_pixel(t['x'],t['y'])
            self.assertEqual(actual,(int(r['source_column']),int(r['source_row'])))
            self.assertEqual(actual,(int(old[r['name']]['source_column']),int(old[r['name']]['source_row'])))
        before={relative:self.g.digest(assets/relative) for relative in self.v.HASHES}
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'review'
            self.v.generate(assets,target)
            for p in target.iterdir():self.assertEqual(p.read_bytes(),(self.out/p.name).read_bytes(),p.name)
            with self.assertRaises(FileExistsError):self.v.generate(assets,target)
        self.assertEqual(before,{relative:self.g.digest(assets/relative) for relative in self.v.HASHES})
