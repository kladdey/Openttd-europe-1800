import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import research_river_banks as research


class HistoricBankResearchTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(research.MANIFEST.read_bytes())

    def test_arles_crossing_gap_and_boundary_years(self):
        bridge=next(r for r in self.data['timeline'] if r['id']=='ARLES_BOAT_GAP')
        self.assertEqual(research.timeline_context(bridge,1800),'ABSENT_DURING_RECORDED_INTERRUPTION')
        for year in (1792,1805):
            self.assertEqual(research.timeline_context(bridge,year),'TRANSITION_YEAR_REQUIRES_EXACT_DATE')
        self.assertEqual(research.timeline_context(bridge,1780),'OUTSIDE_DOCUMENTED_GAP_CONTINUITY_UNKNOWN')

    def test_later_name_and_fabric_do_not_erase_older_sites(self):
        for record in self.data['timeline']:
            if record['kind']=='LATER_NAME_OR_FABRIC':
                self.assertEqual(research.timeline_context(record,1800),'OLDER_SITE_LATER_NAME_OR_FABRIC')
        bridge=next(r for r in self.data['timeline'] if r['id']=='ALENCON_PONT_NEUF')
        self.assertEqual(research.timeline_context(bridge,1770),'NOT_OPENED_YET')
        self.assertEqual(research.timeline_context(bridge,1800),'OPENED_BEFORE_START_CONTINUITY_NOT_PROVEN')

    def test_locators_cardinal_banks_and_unmeasured_registration_are_rejected(self):
        research.validate_research(self.data)
        for change,expected in [('locator','locator-only'),('compass','downstream'),('measurement','registration')]:
            data=copy.deepcopy(self.data)
            if change=='locator':data['cases'][0]['bank_source_ids']=['ALENCON_BNF_PLAN']
            elif change=='compass':data['cases'][0]['historic_bank']='NORTH'
            else:data['cases'][0]['registration_error_bound_pixels']=.1
            with self.assertRaisesRegex(ValueError,expected):research.validate_research(data)

    def test_unsupported_chronology_cannot_enter_report(self):
        self.data['timeline'][0]['start_1800_context']='PRESENT'
        with self.assertRaisesRegex(ValueError,'Chronology'):research.validate_research(self.data)

    def test_reproduction_and_half_pixel_fragility_preserve_inputs(self):
        import csv
        paths=[ROOT/'source_assets'/name for name in research.HASHES]
        paths += [ROOT/'data/towns/europe_1800_import_AUDIT_FIXED_TEST.json',ROOT/'maps/calibration/geography_v11/Europe_1800_V11_CLEAR_TARGET_CANDIDATE_TEST.json']
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'report';summary=research.run(out)
            self.assertEqual((summary['holds_lifted'],summary['town_coordinate_changes'],summary['historic_maps_georeferenced']),(0,0,0))
            self.assertEqual((summary['candidate_towns'],summary['terrain_cases_unresolved']),(537,27))
            with (out/'bank_case_review.csv').open() as stream:cases=list(csv.DictReader(stream))
            self.assertEqual({r['name']:int(r['probes_hitting_saved_water']) for r in cases},{'ALENCON':3,'ARLES':2})
            with (out/'half_pixel_sensitivity.csv').open() as stream:samples=list(csv.DictReader(stream))
            for sample in samples:
                if float(sample['offset_column_pixels'])==float(sample['offset_row_pixels'])==0:
                    self.assertEqual(sample['direct_clear_land'],'True')
            for p in out.iterdir():self.assertEqual(p.read_bytes(),(ROOT/'maps/calibration/river_bank_research_v1'/p.name).read_bytes(),p.name)
        self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest()==sha for p,sha in before.items()))


if __name__=='__main__':unittest.main()
