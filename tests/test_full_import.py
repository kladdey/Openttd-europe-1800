import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_full_import as full


class FullImportTests(unittest.TestCase):
    def test_exact_records_and_source_preservation(self):
        before={p:p.read_bytes() for p in (full.BASELINE,full.ADDITIONS)}
        baseline=json.loads(before[full.BASELINE]);additions=json.loads(before[full.ADDITIONS])
        merged=full.combine(baseline,additions)
        self.assertEqual(len(merged),568)
        self.assertEqual(merged[:537],baseline);self.assertEqual(merged[537:],additions)
        self.assertTrue(all(p.read_bytes()==b for p,b in before.items()))
        self.assertEqual(merged,json.loads((ROOT/'maps/calibration/geography_v12'/full.OUTPUT).read_bytes()))

    def test_duplicates_invalid_coordinates_and_metadata_fail(self):
        baseline=json.loads(full.BASELINE.read_bytes());additions=json.loads(full.ADDITIONS.read_bytes())
        with self.assertRaisesRegex(ValueError,'Duplicate'):full.combine(baseline,[baseline[0]])
        bad=copy.deepcopy(additions);bad[0]['x']=float('nan')
        with self.assertRaises(ValueError):full.combine(baseline,bad)
        bad=copy.deepcopy(additions);bad[0]['population']=True
        with self.assertRaises(ValueError):full.combine(baseline,bad)
        bad=copy.deepcopy(additions);bad[0]['city']='false'
        with self.assertRaises(ValueError):full.combine(baseline,bad)

    def test_reproduction_spacing_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'full';summary=full.run(out)
            self.assertEqual((summary['full_import_towns'],summary['reviewed_close_pairs']),(568,50))
            self.assertEqual(summary['minimum_actual_target_spacing'],15.620499)
            for p in out.iterdir():self.assertEqual(p.read_bytes(),(ROOT/'maps/calibration/geography_v12'/p.name).read_bytes())
            with self.assertRaises(FileExistsError):full.run(out)
        a=dict(name='a',population=100,city=False,x=.5,y=.5)
        b=dict(name='b',population=100,city=False,x=.505,y=.5)
        with self.assertRaisesRegex(ValueError,'lacks review'):full.check_spacing([a,b],[])


if __name__=='__main__':unittest.main()
