import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_coverage_additions as c
from reverse_audit import independent_target
from scenario_geography import read_terrain
from validate_inland_features import load_frozen_model,MODEL


class CoverageAdditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads(c.CONFIG.read_bytes())
        cls.base=json.loads((ROOT/cls.config['baseline_candidate']).read_bytes())
        cls.master=json.loads((ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json').read_bytes())
        cls.old=json.loads((ROOT/'data/towns/sweden_additions_V1_TEST.json').read_bytes())
        with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as im:cls.raw=np.array(im)[:,:,0]
        cls.terrain=[read_terrain(ROOT/'source_assets/scenarios'/n) for n in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]
        cls.coefficients,_=load_frozen_model(MODEL)
        cls.results,cls.probes,cls.pairs=c.audit(cls.config,cls.base,cls.master,cls.old,cls.raw,cls.terrain,cls.coefficients)

    def test_all_sources_partition_and_populations_preserved(self):
        retained=[r for r in self.results if r['status']=='RETAIN_ADDITION_TEST']
        self.assertEqual(len(self.results),52);self.assertEqual(len(retained),31)
        self.assertEqual({r['town_id'] for r in self.results if r['region']=='Sweden'},{r['name'] for r in self.old})
        by_id={r['town_id']:r for r in self.results}
        self.assertTrue(all(by_id[t['name']]['population']==t['population'] and by_id[t['name']]['city']==t['city'] for t in self.old))
        self.assertEqual(by_id['Oskarshamn']['export_name'],'Döderhultsvik')
        self.assertEqual(by_id['PALMA']['status'],'DEFER_EXISTING_MASTER_HOLD')
        self.assertEqual(by_id['Örebro']['status'],'DEFER_MAP_EDGE_REVIEW')
        self.assertEqual(sum(r['status']=='DEFER_OUTSIDE_MAP' for r in self.results),8)

    def test_exact_export_geography_land_and_sensitivity(self):
        aa,bb,cc,dd=self.coefficients
        for r in self.results:
            self.assertAlmostEqual(r['projected_column'],aa*r['longitude']+bb,places=5)
            self.assertAlmostEqual(r['projected_row'],cc*r['latitude']+dd,places=5)
            if r['status']!='RETAIN_ADDITION_TEST':continue
            self.assertEqual(r['x'],round((cc*r['latitude']+dd)/4095,9))
            self.assertEqual(r['y'],round((aa*r['longitude']+bb)/4095,9))
            self.assertTrue(r['direct_clear_land']);self.assertEqual(r['half_pixel_probes_clear'],9)
            tx,ty=independent_target(r['x'],r['y'])
            self.assertGreater(self.raw[ty,4095-tx],0)
            self.assertTrue(all(a[ty,tx]==0 for a,h in self.terrain))
        retained={r['town_id'] for r in self.results if r['status']=='RETAIN_ADDITION_TEST'}
        self.assertTrue(all(p['direct_clear_land'] for p in self.probes if p['town_id'] in retained))

    def test_combined_spacing_and_individual_review(self):
        retained=[r for r in self.results if r['status']=='RETAIN_ADDITION_TEST']
        merged=self.base+[dict(name=r['export_name'],x=r['x'],y=r['y']) for r in retained]
        for r in retained:
            for t in merged:
                if t['name']==r['export_name']:continue
                tx,ty=independent_target(t['x'],t['y']);d=np.hypot(r['tile_x']-tx,r['tile_y']-ty)
                self.assertGreaterEqual(d,15)
                if d<=30:self.assertEqual({r['export_name'],t['name']},{'Malmö','Lund'})
        config=copy.deepcopy(self.config);config['spacing_reviews']=[]
        changed,_,_=c.audit(config,self.base,self.master,self.old,self.raw,self.terrain,self.coefficients)
        self.assertTrue(all(r['status']=='DEFER_SPACING_REVIEW' for r in changed if r['town_id'] in ('Malmö','Lund')))

    def test_duplicate_baseline_and_source_population_changes_fail(self):
        changed=copy.deepcopy(self.config);changed['records'][0]['population']+=1
        with self.assertRaisesRegex(ValueError,'population changed'):c.validate_inputs(changed,self.base,self.master,self.old)
        changed=copy.deepcopy(self.config);changed['records'][0]['export_name']=self.base[0]['name']
        with self.assertRaisesRegex(ValueError,'existing imported town'):c.validate_inputs(changed,self.base,self.master,self.old)
        changed=copy.deepcopy(self.config);changed['records'][1]['export_name']=changed['records'][0]['export_name'].upper()
        with self.assertRaisesRegex(ValueError,'Duplicate'):c.validate_inputs(changed,self.base,self.master,self.old)

    def test_regional_jsons_are_disjoint_additions_only(self):
        folder=ROOT/'maps/calibration/coverage_additions_v1'
        all_t=json.loads((folder/c.ALL).read_bytes());sw=json.loads((folder/c.SWEDEN).read_bytes());med=json.loads((folder/c.MED).read_bytes())
        self.assertEqual(len(sw),20);self.assertEqual(len(med),11)
        self.assertEqual({t['name'] for t in all_t},{t['name'] for t in sw+med})
        self.assertFalse({c.key(t['name']) for t in all_t}&{c.key(t['name']) for t in self.base})
        self.assertEqual(len(self.base)+len(all_t),568)

    def test_deterministic_reproduction_preserves_protected_inputs(self):
        paths=[ROOT/p for p in self.config['preserved_input_sha256']]
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'report';summary=c.run(out)
            self.assertEqual(summary['retained_additions'],31)
            for p in out.iterdir():self.assertEqual(p.read_bytes(),(ROOT/'maps/calibration/coverage_additions_v1'/p.name).read_bytes(),p.name)
            with self.assertRaises(FileExistsError):c.run(out)
        self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest()==sha for p,sha in before.items()))


if __name__=='__main__':unittest.main()
