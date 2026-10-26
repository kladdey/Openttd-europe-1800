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
import audit_coverage_gaps as gap


class CoverageGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads(gap.CONFIG.read_bytes())
        cls.towns=json.loads((ROOT/cls.config['input_import']).read_bytes())
        cls.coefficients,_=gap.load_frozen_model(gap.MODEL)
        with Image.open(ROOT/'source_assets/heightmaps/Europe_heightmap_original.png') as im:cls.raw=np.array(im)[:,:,0]
        cls.terrain=[gap.read_terrain(ROOT/'source_assets/scenarios'/name)[0] for name in ('Europe_1800_V1.scn','Europe_1800_Industries_Original.scn')]

    def test_nearest_distance_and_nonzero_source_mask(self):
        raw=np.ones((5,5),dtype='uint8');raw[1,1]=0
        xx,yy,mask,distance=gap.distance_samples(raw,np.array([[0,0],[4,0]]),1)
        self.assertEqual(distance[0,2],2)
        self.assertEqual(distance[4,0],4)
        self.assertFalse(mask[1,1])
        self.assertAlmostEqual(distance[4,2],np.sqrt(20))
        with self.assertRaises(ValueError):gap.distance_samples(raw,np.empty((0,2)))

    def test_existing_name_at_another_place_is_not_mistaken_for_present(self):
        points=gap.target_points(self.towns);a,b,c,d=self.coefficients
        item=copy.deepcopy(self.config['candidates'][0])
        item.update(name=self.towns[0]['name'],longitude=(points[0,0]-b)/a,latitude=(points[0,1]-d)/c)
        r=gap.candidate_audit([item],self.towns,self.raw,self.terrain,self.coefficients)[0]
        self.assertEqual(r['stage'],'ALREADY_PRESENT')
        item.update(longitude=(points[-1,0]-b)/a,latitude=(points[-1,1]-d)/c)
        r=gap.candidate_audit([item],self.towns,self.raw,self.terrain,self.coefficients)[0]
        self.assertEqual(r['stage'],'NAME_COLLISION_REQUIRES_IDENTITY_REVIEW')
        item['name']='New name at an already occupied place'
        r=gap.candidate_audit([item],self.towns,self.raw,self.terrain,self.coefficients)[0]
        self.assertEqual(r['stage'],'SUB_15_IMPORTANCE_EXCEPTION_REVIEW')

    def test_known_deferrals_are_not_new_candidates_or_double_counted(self):
        held=gap.deferred_audit(self.towns)
        self.assertEqual(len(held),83)
        self.assertEqual(sum(r['name']=='PALMA' for r in held),1)
        self.assertTrue({'CAGLIARI','NAPOLI','Oran','Visby'}<={r['name'] for r in held})
        names={gap.key(r['name']) for r in held}
        self.assertFalse(names&{gap.key(r['name']) for r in self.config['candidates']})

    def test_proposals_are_research_only_and_close_pairs_are_flagged(self):
        audited=gap.candidate_audit(self.config['candidates'],self.towns,self.raw,self.terrain,self.coefficients)
        self.assertEqual(len(audited),62)
        helsingor=next(r for r in audited if r['name']=='Helsingør')
        self.assertEqual(helsingor['stage'],'SUB_15_IMPORTANCE_EXCEPTION_REVIEW')
        brest=next(r for r in audited if r['name']=='Brest (Belarus)')
        self.assertTrue(brest['requires_qualified_name'])
        self.assertTrue(all(r['research_only'] and 'population' not in r and 'city' not in r for r in audited))
        bad=copy.deepcopy(self.config['candidates'][0]);bad['latitude']=float('nan')
        with self.assertRaisesRegex(ValueError,'Invalid geographic'):gap.candidate_audit([bad],self.towns,self.raw,self.terrain,self.coefficients)

    def test_reproduction_preserves_inputs_and_generates_no_import(self):
        paths=[ROOT/self.config['input_import'],gap.CONFIG,gap.MODEL,ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json']
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'report';summary=gap.run(out)
            self.assertEqual((summary['current_towns'],summary['research_candidates'],summary['known_deferrals']),(568,62,83))
            self.assertEqual((summary['new_imports_generated'],summary['town_coordinate_changes']),(0,0))
            for p in out.iterdir():self.assertEqual(p.read_bytes(),(ROOT/'maps/calibration/coverage_gap_audit_v1'/p.name).read_bytes(),p.name)
            self.assertFalse(any(p.name.endswith('_TEST.json') for p in out.iterdir()))
        self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest()==sha for p,sha in before.items()))


if __name__=='__main__':unittest.main()
