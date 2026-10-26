import json
import unittest
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_gap_additions import ROOT, CONFIG, BASELINE, ADDITIONS, FULL
from build_coverage_additions import key, source_sample
from build_full_import import check_spacing, read_rows
from geography import validate
from scenario_geography import read_terrain

class GapAdditionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=ROOT/'maps/calibration/geography_v13'
        cls.add=json.loads((cls.out/ADDITIONS).read_bytes())
        cls.full=json.loads((cls.out/FULL).read_bytes())

    def test_composition_and_identity(self):
        base=json.loads(BASELINE.read_bytes())
        self.assertEqual(self.full,base+self.add)
        validate(self.full)
        self.assertEqual(len(self.full),len({key(t['name']) for t in self.full}))

    def test_every_research_lead_accounted_for(self):
        cfg=json.loads(CONFIG.read_bytes())
        research=json.loads((ROOT/'data/geography/coverage_gap_research_v1.json').read_bytes())
        rows=read_rows(self.out/'all_candidate_decisions.csv')
        self.assertEqual({r['id'] for r in research['candidates']},{r['town_id'] for r in rows})
        self.assertEqual(len(rows),62)
        self.assertEqual({r['export_name'] for r in rows if r['status']=='RETAIN_ADDITION_TEST'},{t['name'] for t in self.add})
        self.assertTrue(all(r['historical_basis'] and r['history_source'] for r in cfg['records']))

    def test_actual_land_and_probes(self):
        with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as image:raw=np.array(image)[:,:,0]
        terrains=[read_terrain(ROOT/'source_assets/scenarios'/n) for n in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]
        for t in self.add:
            for dx in (-.5,0,.5):
                for dy in (-.5,0,.5):
                    s=source_sample(t['x']+dy/4095,t['y']+dx/4095,raw,terrains)
                    self.assertTrue(s['direct_clear_land'],t['name'])
                    self.assertGreaterEqual(s['edge_margin_tiles'],8)

    def test_all_close_pairs_reviewed(self):
        paths=[ROOT/'maps/calibration/geography_v11/spacing_audit.csv',ROOT/'maps/calibration/coverage_additions_v1/spacing_review.csv',self.out/'new_spacing_review.csv']
        self.assertEqual(len(check_spacing(self.full,[r for p in paths for r in read_rows(p)])),len(read_rows(self.out/'combined_spacing_audit.csv')))

    def test_prior_holds_not_restored(self):
        self.assertFalse({key(t['name']) for t in self.add}&{key(n) for n in ('Cagliari','Napoli','Oran','Annaba','Visby','Ibiza')})
