import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import validate_inland_features as v
from river_bank_diagnostics import source_oriented_crop


class InlandFeatureTests(unittest.TestCase):
    def feature(self, **changes):
        result = dict(name='test', ne_id=1, box=[0,0,12,12], elevation=24,
                      seeds=[[4,4]], identification='APPROXIMATE_BASIN', note='synthetic')
        result.update(changes)
        return result

    def test_explicit_components_do_not_capture_nearer_decoys(self):
        raw = np.ones((12,12), dtype=np.uint8)*30
        raw[3:6,3:6] = 24
        raw[7:10,7:10] = 24
        mask = v.observed_mask(raw, self.feature())
        self.assertEqual(int(mask.sum()), 9)
        self.assertFalse(mask[8,8])
        merged = v.observed_mask(raw, self.feature(seeds=[[4,4],[8,8]]))
        self.assertEqual(int(merged.sum()), 18)
        with self.assertRaisesRegex(ValueError, 'Duplicate component'):
            v.observed_mask(raw, self.feature(seeds=[[4,4],[5,5]]))

    def test_unresolved_wrong_elevation_and_edge_components_fail_closed(self):
        raw = np.zeros((12,12), dtype=np.uint8)
        with self.assertRaisesRegex(ValueError, 'declared elevation'):
            v.observed_mask(raw, self.feature())
        with self.assertRaisesRegex(ValueError, 'window edge'):
            v.observed_mask(raw, self.feature(elevation=0))
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            v.observed_mask(raw, self.feature(identification='UNRESOLVED_IDENTIFICATION'))
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            v.observed_mask(raw, self.feature(identification='VERIFIED'))

    def test_frozen_shape_metrics_detect_known_shift_without_refitting(self):
        a = np.zeros((30,30), dtype=bool);a[10:16,10:16] = True
        b = np.zeros_like(a);b[12:18,7:13] = True
        metrics = v.shape_metrics(a,b)
        self.assertEqual(metrics['observed_minus_predicted_column'],3)
        self.assertEqual(metrics['observed_minus_predicted_row'],-2)
        self.assertAlmostEqual(metrics['centroid_difference_pixels'],np.hypot(3,2),places=3)
        self.assertEqual(v.shape_metrics(a,a)['intersection_over_union'],1)

    def test_polygon_holes_and_window_clipping(self):
        geometry = dict(type='Polygon', coordinates=[[[2,2],[10,2],[10,10],[2,10],[2,2]],[[4,4],[6,4],[6,6],[4,6],[4,4]]])
        mask, clipped = v.projected_mask(geometry,[1,0,1,0],[0,0,12,12],(12,12))
        self.assertFalse(clipped)
        self.assertFalse(mask[5,5])
        self.assertTrue(mask[3,3])
        _, clipped = v.projected_mask(geometry,[1,-5,1,0],[0,0,12,12],(12,12))
        self.assertTrue(clipped)

    def test_partial_clipped_and_unresolved_features_cannot_produce_control_metrics(self):
        raw = np.ones((12,12), dtype=np.uint8)*30;raw[3:6,3:6]=24
        vectors={1:dict(geometry=dict(type='Polygon',coordinates=[[[2,2],[7,2],[7,7],[2,7],[2,2]]]))}
        for state in ['PARTIAL_BASIN','CLIPPED_REFERENCE','UNRESOLVED_IDENTIFICATION']:
            feature=self.feature(identification=state)
            if state=='UNRESOLVED_IDENTIFICATION':feature.update(elevation=None,seeds=[])
            rows,_=v.audit(raw,[feature],vectors,[1,0,1,0])
            self.assertFalse(rows[0]['diagnostic_comparison'])
            self.assertFalse(rows[0]['eligible_for_automatic_town_correction'])
            self.assertNotIn('centroid_difference_pixels',rows[0])

    def test_saved_terrain_crop_preserves_exact_source_orientation(self):
        game=np.arange(64).reshape(8,8)
        crop=source_oriented_crop(game,[1,2,4,5])
        for row in range(3):
            for col in range(3):self.assertEqual(crop[row,col],game[row+2,7-(col+1)])

    def test_reproduction_matches_reports_and_preserves_inputs(self):
        paths=[v.CONFIG,v.VECTOR,v.MODEL,v.SOURCE,ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json',ROOT/'data/geography/historic_centre_references_v11.csv',ROOT/'maps/calibration/geography_v11/Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json']
        before={p:p.read_bytes() for p in paths}
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'output'; summary=v.run(out)
            self.assertEqual(summary['features_reviewed'],10)
            self.assertEqual(summary['diagnostic_comparisons'],7)
            self.assertEqual(summary['river_bank_review']['cases_resolved'],0)
            self.assertEqual(summary['town_coordinate_changes'],0)
            expected=ROOT/'maps/calibration/inland_v2'
            for name in ['summary.json','inland_shape_audit.csv','river_bank_review.csv','inland_contact_sheet.png','river_bank_overlays.png']:
                self.assertEqual((out/name).read_bytes(),(expected/name).read_bytes(),name)
            with self.assertRaises(FileExistsError):v.run(out)
        self.assertTrue(all(p.read_bytes()==data for p,data in before.items()))


if __name__ == '__main__':unittest.main()
