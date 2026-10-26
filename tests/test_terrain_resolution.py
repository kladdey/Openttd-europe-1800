import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
DEPS=all(importlib.util.find_spec(name) for name in ('numpy','scipy','PIL'))


@unittest.skipUnless(DEPS,'Install requirements-geography.txt')
class TerrainResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import geography as g
        import resolve_terrain_flags as r
        cls.g,cls.r=g,r
        cls.out=ROOT/'maps/calibration/geography_v10'
        cls.core=g.read_json(cls.out/r.CORE)
        cls.full=g.read_json(cls.out/r.FULL)
        cls.original=g.read_json(r.V8/'Europe_1800_V8_CORRECTED_ALL_IN_BOUNDS_TEST.json')

    def test_complete_catalogue_and_metadata_preserved(self):
        master={t['name']:t for t in self.g.read_json(self.g.MASTER)}
        self.assertEqual(len(self.core),536)
        self.assertEqual(len(self.full),576)
        comparison=self.g.read_json(self.out/self.r.COMPARISON)
        self.assertEqual(len(comparison),564)
        for data in (self.core,comparison,self.full):
            self.g.validate(data)
            for t in data:
                self.assertTrue(all(t[k]==master[t['name']][k] for k in ('name','population','city')))
        records=self.r.rows(self.out/'all_600_decisions.csv')
        self.assertEqual(len(records),600)
        self.assertEqual({r['name'] for r in records},set(master))
        self.assertEqual({r['name'] for r in records if r['state']=='RETAINED_CLEAR_TARGET_CANDIDATE'},{t['name'] for t in self.core})
        deferred=self.r.rows(self.out/'deferred_towns.csv')
        self.assertEqual(len(deferred),64)
        self.assertTrue(all(r['reason'] for r in deferred))
        self.assertNotIn('MODICA/POZZALLO',{t['name'] for t in self.core})

    def test_all_old_flags_and_new_regression_have_explicit_dispositions(self):
        old={r['name'] for r in self.r.rows(self.r.V9/'retained_terrain_diagnostics.csv')}
        result=self.r.rows(self.out/'terrain_resolution.csv')
        self.assertEqual({r['name'] for r in result},old|{'ORIHUELA'})
        self.assertEqual(sum(r['terrain_flag_resolved']=='True' for r in result),27)
        self.assertEqual(sum(r['decision']=='TEMPORARILY_DEFER_TERRAIN' for r in result),28)
        self.assertTrue(all(r['founding']=='UNTESTED' for r in result))
        self.assertTrue(all(r['direct_clear_land']=='True' for r in result if r['terrain_flag_resolved']=='True'))
        self.assertTrue(all(r['reference_id'] for r in result if r['terrain_flag_resolved']=='True'))
        self.assertTrue(all(not r['reference_id'] for r in result if r['terrain_flag_resolved']=='False'))

    def test_water_or_area_only_reference_cannot_be_selected(self):
        audit=self.r.rows(self.out/'historic_reference_audit.csv')
        # CSV bools are converted deliberately; production receives real bools.
        for r in audit:r['eligible']=r['eligible']=='True'
        chosen,deferred,decisions=self.r.checked_decisions(audit)
        self.assertEqual(len(chosen),27)
        for name in ('ALICANTE','Volos'):
            bad=copy.deepcopy(decisions)
            d=next(r for r in bad if r['name']==name)
            d.update(decision='CORRECT_TO_REFERENCE',reference_id=name+' / 1')
            with patch.object(self.r,'rows',return_value=bad),self.assertRaisesRegex(ValueError,'not a clear eligible'):
                self.r.checked_decisions(audit)
        with patch.object(self.r,'rows',return_value=decisions[:-1]),self.assertRaisesRegex(ValueError,'exactly one'):
            self.r.checked_decisions(audit)

    def test_regional_registration_is_consistent_for_neighbours(self):
        rebased,changes=self.r.regional_rebase(self.original)
        self.assertEqual(len(changes),27)
        self.assertTrue({'ACIREALE','CATANIA','MURCIA','ORIHUELA','Tirana','Durrës'}<=set(changes))
        before={t['name']:t for t in self.original};after={t['name']:t for t in rebased}
        # A constant regional translation must preserve relative separations.
        for a,b in [('ACIREALE','CATANIA'),('MURCIA','ORIHUELA'),('Tirana','Durrës')]:
            self.assertAlmostEqual(self.g.distance(before[a],before[b]),self.g.distance(after[a],after[b]),places=4)
        self.assertEqual(before['LONDON'],after['LONDON'])
        actual_changes={t['name'] for t in self.full if t!=before[t['name']]}
        self.assertEqual(len(actual_changes),50)
        self.assertEqual(actual_changes,{r['name'] for r in self.r.rows(self.out/'coordinate_changes.csv')})

    def test_rejected_or_stale_models_cannot_be_applied(self):
        original=self.g.read_json(self.r.REGISTRATION)
        self.assertEqual({r['id'] for r in original['regions'] if r['accepted']},{'SE_SPAIN','SICILY','DURRES'})
        bad=copy.deepcopy(original);next(r for r in bad['regions'] if r['id']=='CADIZ')['accepted']=True
        real_read=self.g.read_json
        with patch.object(self.g,'read_json',side_effect=lambda p:bad if p==self.r.REGISTRATION else real_read(p)):
            with self.assertRaisesRegex(ValueError,'fails its evidence gates'):self.r.registered_regions()
        bad=copy.deepcopy(original);bad['input_sha256']['data/geography/coastal_regions_v10.json']='invalid'
        with patch.object(self.g,'read_json',side_effect=lambda p:bad if p==self.r.REGISTRATION else real_read(p)):
            with self.assertRaisesRegex(ValueError,'Stale'):self.r.registered_regions()

    def test_spacing_review_covers_changed_pairs_and_actual_quantization(self):
        pairs=self.r.rows(self.out/'spacing_audit.csv')
        retained=[r for r in pairs if r['both_in_clear_candidate']=='True']
        self.assertTrue(all(float(r['v10_distance_tiles'])>=15 and float(r['actual_target_distance_tiles'])>=15 for r in retained))
        new=[r for r in pairs if r['new_pair']=='True']
        self.assertEqual([(r['town_a'],r['town_b']) for r in new],[('Brzozów','Sanok')])
        self.assertEqual(new[0]['inherited_or_new_review'],'V10')
        acireale=next(r for r in pairs if r['town_a']=='ACIREALE' and r['town_b']=='CATANIA')
        self.assertGreater(float(acireale['v10_distance_tiles']),18)

    def test_every_clear_target_checked_against_both_actual_scenarios(self):
        assets=ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():self.skipTest('Original assets required')
        arrays=self.r.inputs(assets)
        self.assertTrue(all(self.r.sample(t,arrays)['direct_clear_land'] for t in self.core))
        summary=self.g.read_json(self.out/'summary.json')
        self.assertEqual(sum(not self.r.sample(t,arrays)['both_saved_flat_corners'] for t in self.core),summary['clear_candidate_nonflat_targets'])
        self.assertEqual(summary['in_game_tests'],0)
        self.assertEqual(summary['population_changes'],0)

    def test_regeneration_is_read_only_and_matches_snapshot(self):
        assets=ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():self.skipTest('Original assets required')
        before={p:self.g.digest(assets/p) for p in self.r.HASHES}
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'candidate';self.r.generate(assets,out)
            for p in out.iterdir():self.assertEqual(p.read_bytes(),(self.out/p.name).read_bytes(),p.name)
            with self.assertRaises(FileExistsError):self.r.generate(assets,out)
        self.assertEqual(before,{p:self.g.digest(assets/p) for p in self.r.HASHES})


@unittest.skipUnless(DEPS,'Install requirements-geography.txt')
class CoastalRegistrationTests(unittest.TestCase):
    def test_known_translation_recovered_without_town_inputs(self):
        import numpy as np
        from register_coastal_regions import fit_translation,CONFIG
        import geography as g
        angle=np.linspace(0,2*np.pi,300,endpoint=False)
        points=np.c_[128+60*np.cos(angle),128+60*np.sin(angle)]
        yy,xx=np.mgrid[:256,:256]
        field=np.abs(np.hypot(xx-131,yy-124)-60)
        result=fit_translation(points,field,g.read_json(CONFIG))
        self.assertTrue(result['accepted'],result)
        self.assertAlmostEqual(result['shift_column'],3,delta=.15)
        self.assertAlmostEqual(result['shift_row'],-4,delta=.15)

    def test_straight_coast_does_not_establish_both_axes(self):
        import numpy as np
        from register_coastal_regions import fit_translation,CONFIG
        import geography as g
        points=np.c_[np.full(200,120),np.linspace(10,240,200)]
        yy,xx=np.mgrid[:256,:256];field=np.abs(xx-123).astype(float)
        result=fit_translation(points,field,g.read_json(CONFIG))
        self.assertFalse(result['accepted'])
        self.assertIn('POORLY_CONSTRAINED_DIRECTION',result['rejection_reasons'])
