import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import reverse_audit as reverse
import validate_inland_features as inland
import river_bank_diagnostics as bank


class ReverseAuditTests(unittest.TestCase):
    def fixture(self):
        towns=[dict(name='Alpha',population=100,city=False,x=.2,y=.2),dict(name='Beta',population=200,city=True,x=.8,y=.8)]
        raw=np.ones((64,64),dtype='uint8'); terrain=[(np.zeros_like(raw),np.zeros_like(raw)) for _ in range(2)]
        decisions=[]
        for town in towns:
            tx,ty=reverse.independent_target(town['x'],town['y'],64)
            decisions.append(dict(name=town['name'],population=str(town['population']),city=str(town['city']),state='RETAINED_CLEAR_TARGET_CANDIDATE',reason='test',x=str(town['x']),y=str(town['y']),source_column=str(63-tx),source_row=str(ty),tile_x=str(tx),tile_y=str(ty),raw_elevation='1',v1_tile_type='0',industries_tile_type='0',direct_clear_land='True',both_saved_flat_corners='True'))
        claim=dict(catalogue_entries=2,clear_target_candidate=2,total_deferred=0,clear_candidate_nonflat_targets=0,minimum_spacing_tiles=round(64*np.hypot(.6,.6),6),deferred_categories={})
        return towns,copy.deepcopy(towns),decisions,raw,terrain,[],claim

    def test_clean_fixture_and_independent_importer_arithmetic(self):
        result,_,_=reverse.audit_candidate(*self.fixture(),size=64)
        self.assertEqual(result['errors'],[])
        # Binary-exact fractions make expected arithmetic independent of numpy/helpers.
        self.assertEqual(reverse.independent_target(.25,.5,4096),(2047,1023))
        for bad in (float('nan'),True,0,1,1-1e-12):
            with self.assertRaises(ValueError):reverse.independent_target(.5,bad)

    def test_metadata_membership_and_coordinate_mutations_are_detected(self):
        for mutation,expected in [('population','metadata changed'),('membership','membership'),('coordinate','Invalid export coordinate')]:
            values=list(self.fixture())
            if mutation=='population':values[1][0]['population']+=1
            elif mutation=='membership':values[1].pop()
            else:values[1][0]['x']=float('nan')
            result,_,_=reverse.audit_candidate(*values,size=64)
            self.assertTrue(any(expected in error for error in result['errors']),result)

    def test_stale_report_occupied_target_and_false_summary_are_detected(self):
        for mutation,expected in [('stale','Stale decision'),('water','not source land'),('summary','Summary claim')]:
            values=list(self.fixture());tx,ty=reverse.independent_target(.2,.2,64)
            if mutation=='stale':values[2][0]['source_column']='0'
            elif mutation=='water':values[4][1][0][ty,tx]=6
            else:values[6]['clear_target_candidate']=42
            result,_,_=reverse.audit_candidate(*values,size=64)
            self.assertTrue(any(expected in error for error in result['errors']),result)

    def test_duplicate_names_and_unreviewed_close_pairs_are_detected(self):
        values=list(self.fixture());values[1][1]['name']='ALPHA'
        result,_,_=reverse.audit_candidate(*values,size=64)
        self.assertTrue(any('duplicate' in error for error in result['errors']))
        values=list(self.fixture());values[1][1].update(x=.3,y=.3)
        result,_,_=reverse.audit_candidate(*values,size=64)
        self.assertTrue(any('Unreviewed close pair' in error for error in result['errors']))
        self.assertTrue(any('Sub-15 retained' in error for error in result['errors']))


    def test_comparison_exports_are_checked_beyond_counts(self):
        master,candidate,decisions,*_=self.fixture()
        self.assertEqual(reverse.audit_comparison(master,candidate,decisions,set()),[])
        candidate[0]['population']+=1
        self.assertTrue(any('metadata' in e for e in reverse.audit_comparison(master,candidate,decisions,set())))
        candidate[1]['x']+=.01
        self.assertTrue(any('coordinate' in e for e in reverse.audit_comparison(master,candidate,decisions,set())))

    def test_frozen_model_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'model.json'; model=json.loads(inland.MODEL.read_bytes());model['axis_affine']['coefficients'][1]+=1
            path.write_text(json.dumps(model))
            with self.assertRaisesRegex(ValueError,'Frozen V6 model hash mismatch'):inland.load_frozen_model(path)

    def test_stale_bank_target_and_duplicate_references_are_rejected(self):
        config=json.loads((ROOT/'data/geography/river_bank_observations_v1.json').read_bytes())
        case=config['cases'][0]
        refs=bank.unique_index(bank.read_rows(ROOT/'data/geography/historic_centre_references_v11.csv'),'reference_id')
        audit=bank.unique_index(bank.read_rows(ROOT/'maps/calibration/geography_v11/historic_reference_audit.csv'),'reference_id')
        a=dict(audit[case['reference_id']]);ref=refs[case['reference_id']]
        raw=np.full((4096,4096),24,dtype='uint8');terrain=[np.zeros_like(raw),np.zeros_like(raw)]
        a['source_column']=str(int(a['source_column'])+1)
        coefficients,_=inland.load_frozen_model(inland.MODEL)
        with self.assertRaisesRegex(ValueError,'Stale bank target source_column'):bank.verify_held_target(case,ref,a,coefficients,raw,terrain)
        with self.assertRaisesRegex(ValueError,'duplicate'):bank.unique_index([ref,ref],'reference_id')

    def test_real_candidate_reproduces_reverse_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'audit';report=reverse.run(out)
            self.assertEqual(report['errors'],[])
            self.assertEqual(report['candidate_towns_checked'],537)
            self.assertEqual(report['nonflat_targets'],132)
            for name in ('candidate_summary.json','candidate_reverse_audit.csv','candidate_close_pairs.csv'):
                self.assertEqual((out/name).read_bytes(),(ROOT/'maps/calibration/reverse_audit_v1'/name).read_bytes())


if __name__=='__main__':unittest.main()
