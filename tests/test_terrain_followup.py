import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
DEPS=all(importlib.util.find_spec(n) for n in ('numpy','scipy','PIL'))


@unittest.skipUnless(DEPS,'Install requirements-geography.txt')
class TerrainFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import geography as g
        import resolve_terrain_flags as r
        import review_remaining_terrain as f
        cls.g,cls.r,cls.f=g,r,f
        cls.out=ROOT/'maps/calibration/geography_v11'
        cls.settings=r.load_profile(f.PROFILE)

    def test_profile_schema_version_and_paths_are_checked(self):
        data=self.g.read_json(self.f.PROFILE)
        mutations=[dict(data,version='../V11'),dict(data,schema_version=True),dict(data,unexpected='value'),
                   dict(data,references='../outside.csv'),dict(data,references='/tmp/outside.csv'),dict(data,references=None)]
        for bad in mutations:
            with patch.object(self.g,'read_json',return_value=bad),self.assertRaises(ValueError):
                self.r.load_profile(self.f.PROFILE)
        self.assertEqual(self.r.load_profile()['version'],'V10')

    def test_a_clear_pixel_does_not_override_a_bank_review_hold(self):
        audit=self.r.rows(self.out/'historic_reference_audit.csv')
        for a in audit:a['eligible']=a['eligible']=='True'
        for name in ('ALENCON','ARLES'):
            ref=next(a for a in audit if a['reference_id']==name+' / V11_SITE')
            self.assertEqual(ref['direct_clear_land'],'True')
            self.assertFalse(ref['eligible'])
            self.assertEqual(ref['placement_review'],'HOLD_BANK_ALIGNMENT')
            decisions=self.r.rows(self.settings['decisions'])
            row=next(a for a in decisions if a['name']==name)
            row.update(decision='CORRECT_TO_REFERENCE',reference_id=ref['reference_id'])
            with patch.object(self.r,'rows',return_value=decisions),self.assertRaisesRegex(ValueError,'not a clear eligible'):
                self.r.checked_decisions(audit,self.settings['decisions'])

    def test_only_namur_changes_and_the_existing_candidate_is_preserved(self):
        before={t['name']:t for t in self.g.read_json(self.f.V10/self.r.FULL)}
        after={t['name']:t for t in self.g.read_json(self.out/self.settings['full'])}
        self.assertEqual(set(before),set(after))
        self.assertEqual({n for n in before if before[n]!=after[n]},{'NAMUR'})
        core=self.g.read_json(self.out/self.settings['core'])
        self.g.validate(core)
        old={t['name'] for t in self.g.read_json(self.f.V10/self.r.CORE)}
        self.assertEqual({t['name'] for t in core}-old,{'NAMUR'})
        self.assertEqual(len(core),537)
        master={t['name']:t for t in self.g.read_json(self.g.MASTER)}
        for t in after.values():self.assertTrue(all(t[k]==master[t['name']][k] for k in ('name','population','city')))
        refs=self.r.rows(self.out/'historic_reference_audit.csv')
        namur=next(a for a in refs if a['reference_id']=='NAMUR / V11_SITE')
        self.assertEqual((after['NAMUR']['x'],after['NAMUR']['y']),(float(namur['x']),float(namur['y'])))

    def test_all_pending_cases_and_rejected_sources_are_accounted_for(self):
        cases=self.r.rows(self.out/'remaining_case_review.csv')
        self.assertEqual(len(cases),28)
        self.assertEqual(sum(int(a['new_references']) for a in cases),25)
        self.assertEqual(sum(int(a['held_clear_references']) for a in cases),2)
        self.assertEqual(sum(a['remains_deferred']=='True' for a in cases),27)
        self.assertEqual(sum(a['new_references']!='0' and a['distinct_new_import_pixels']=='0' for a in cases),9)
        excluded=self.r.rows(self.out/'source_exclusions.csv')
        self.assertEqual(len(excluded),9)
        self.assertTrue({'NICE','MODENA','Dubrovnik','Volos','Dębica'}<={a['name'] for a in excluded})
        self.assertTrue(all(a['source'] and a['reason'] for a in excluded))
        all_rows=self.r.rows(self.out/'all_600_decisions.csv')
        self.assertEqual(len(all_rows),600)
        self.assertEqual(sum(a['state'].startswith('DEFERRED') for a in all_rows),63)

    def test_unknown_review_states_cannot_silently_approve_references(self):
        assets=ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():self.skipTest('Original assets required')
        arrays=self.r.inputs(assets)
        bad=self.r.rows(self.settings['references'])
        bad[0]['placement_review']='APPROVED_BY_TYPO'
        real=self.r.rows
        with patch.object(self.r,'rows',side_effect=lambda p:bad if p==self.settings['references'] else real(p)):
            with self.assertRaisesRegex(ValueError,'Unknown historic placement'):
                self.r.reference_audit(arrays,self.settings['references'])

    def test_land_spacing_and_flatness_remain_distinct(self):
        assets=ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():self.skipTest('Original assets required')
        arrays=self.r.inputs(assets)
        core=self.g.read_json(self.out/self.settings['core'])
        self.assertTrue(all(self.r.sample(t,arrays)['direct_clear_land'] for t in core))
        namur=self.r.sample(next(t for t in core if t['name']=='NAMUR'),arrays)
        self.assertFalse(namur['both_saved_flat_corners'])
        summary=self.g.read_json(self.out/'summary.json')
        self.assertEqual(summary['clear_candidate_nonflat_targets'],132)
        self.assertEqual(summary['original_flags_resolved'],28)
        self.assertEqual(summary['in_game_tests'],0)
        for p in self.r.rows(self.out/'spacing_audit.csv'):
            if p['both_in_clear_candidate']=='True':
                self.assertGreaterEqual(float(p['v11_distance_tiles']),15)
                self.assertGreaterEqual(float(p['actual_target_distance_tiles']),15)

    def test_regeneration_preserves_source_assets_and_matches_snapshot(self):
        assets=ROOT/'source_assets'
        if not (assets/'heightmaps/Europe_heightmap_original.png').exists():self.skipTest('Original assets required')
        before={p:self.g.digest(assets/p) for p in self.r.HASHES}
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'followup';self.f.generate(assets,out)
            for p in out.iterdir():self.assertEqual(p.read_bytes(),(self.out/p.name).read_bytes(),p.name)
            with self.assertRaises(FileExistsError):self.f.generate(assets,out)
        self.assertEqual(before,{p:self.g.digest(assets/p) for p in self.r.HASHES})
