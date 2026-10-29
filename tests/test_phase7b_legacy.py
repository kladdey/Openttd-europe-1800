"""Policy rejection and independent engine-receipt reconciliation, not mocks."""
import collections,copy,csv,datetime,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'docs/research'
sys.path.insert(0,str(ROOT/'scripts'))
from lifecycle_phase7b_policy import validate,compile_policy
def read(name):return json.loads((DATA/name).read_text(encoding='utf-8-sig'))
def rows(name):
    with (DATA/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def text(run):return '\n'.join(run['observations'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class PolicyTests(unittest.TestCase):
    def setUp(self):self.policy=json.loads((ROOT/'gamescripts/historical_industry_lifecycle/legacy_policy.json').read_text())
    def test_production_uses_genuine_original_mines_and_normal_dates(self):
        p=validate(self.policy);self.assertFalse(p['test_mode']);self.assertEqual(p['migration'],'reject')
        self.assertEqual([s['industry_id'] for s in p['sites']],[1,11,12,438])
        inv={r['industry_id']:r for r in read('phase7b_extractive_inventory.json')}
        for s in p['sites']:
            self.assertEqual(s['born'],668394);self.assertEqual(s['original_record_sha256'],inv[s['industry_id']]['record_sha256'])
            self.assertGreaterEqual(datetime.date.fromordinal(s['decline_date']-365).year,1860)
            self.assertEqual(s['warning_years'],10)
    def test_resource_curves_never_arm_closure(self):
        coal,copper=self.policy['sites'][0],self.policy['sites'][-1]
        self.assertNotEqual(coal['decline_levels'],copper['decline_levels'])
        for s in self.policy['sites']:self.assertFalse(set(s['decline_levels'])&{4,5,6,7,9})
    def test_reject_unsafe_policy_values(self):
        changes=[('warning_years',4),('rolling_months',1),('minimum_transport',1),('minimum_percent',1),('arm_level',8),('born',1),('local_id',45),('earliest_close',1),('decline_levels',[14,9,8])]
        for key,value in changes:
            with self.subTest(key=key):
                p=copy.deepcopy(self.policy);p['sites'][0][key]=value
                with self.assertRaises(AssertionError):validate(p)
    def test_compilation_matches_packaged_policy(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'legacy_policy.nut';compile_policy(self.policy,path)
            self.assertEqual(path.read_bytes(),(ROOT/'gamescripts/historical_industry_lifecycle/legacy_policy.nut').read_bytes())
            self.assertIn('LEGACY_CONTRACT_TEXT',path.read_text(encoding='utf-8-sig'))

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.receipts=read('phase7b_engine_receipts.json');cls.runs=cls.receipts['runs']
    def test_inventory_complete_and_soda_sites_preserved(self):
        baseline=read('phase7b_baseline_fingerprints.json')['industries'];inv=read('phase7b_extractive_inventory.json')
        self.assertEqual(len(baseline),542);self.assertEqual([r['industry_id'] for r in baseline],list(range(542)))
        self.assertEqual(len(inv),44)
        self.assertEqual(collections.Counter(r['industry'] for r in inv),{'coal_mine':14,'iron_ore_mine':7,'copper_mine':2,'salt_mine':2,'quarry':8,'clay_pit':7,'soda_ash_mine':4})
        soda=[r for r in inv if r['industry']=='soda_ash_mine'];self.assertEqual({r['industry_id'] for r in soda},{196,197,198,199})
        self.assertTrue(all('UNRESOLVED' in r['provenance_flag'] for r in soda))
    def test_bare_command_does_not_close_original_mine(self):
        probe=next(r for r in self.runs if 'one-shot closure' in r['scope'])
        self.assertIn('BUNARMED|survives=true',text(probe))
        self.assertIn('BCLOSE|selected_exists=false|same_type_neighbour=true|count=541',text(probe))
    def test_actual_paid_service_changes_survival_within_cap(self):
        outcome={(r['mode'],r['site_id']):r for r in rows('phase7b_survival_comparison.csv')}
        a=outcome['control','legacy_1'];b=outcome['served','legacy_1']
        self.assertEqual(a['physical_closure_date'],'1837-04-07');self.assertEqual(b['physical_closure_date'],'1839-04-14')
        delta=datetime.date.fromisoformat(b['physical_closure_date'])-datetime.date.fromisoformat(a['physical_closure_date'])
        self.assertEqual(delta.days,737);self.assertEqual(b['forecast_after_extension'],'1839-01-01')
        self.assertEqual(int(b['rolling_transport_at_extension']),2060);self.assertEqual(int(b['service_percent_at_extension']),38)
        for site in ['legacy_11','legacy_12','legacy_438']:self.assertEqual(outcome['served',site]['extended'],'False')
        paid=rows('phase7b_paid_deliveries.csv');self.assertEqual(len(paid),1);self.assertEqual(int(paid[0]['sampled_net_vehicle_income_increase']),91)
        self.assertIn('not gross invoice',paid[0]['evidence'])
    def test_real_calendar_notice_and_gradual_production(self):
        for row in rows('phase7b_survival_comparison.csv'):
            warning=datetime.date.fromisoformat(row['warning_date']);closed=datetime.date.fromisoformat(row['physical_closure_date'])
            self.assertGreaterEqual(closed,warning.replace(year=warning.year+5))
        ledger=rows('phase7b_production_service_ledger.csv')
        self.assertEqual({int(r['level']) for r in ledger if r['scope'].startswith('FULL EUROPE ENGINE: control comparison')},{16,14,12,10,8})
        self.assertTrue(any(int(r['transported'])>0 for r in ledger if r['scope'].startswith('FULL EUROPE ENGINE: served comparison')))
    def test_four_stage_save_reload_and_replay(self):
        for mode,p in self.receipts['comparisons'].items():
            self.assertEqual(len(p['runs']),4)
            for r in p['runs'][1:]:self.assertIn('legacy_loaded|scheduler|schema=2|sites=4',text(r))
            self.assertIn('unmanaged_intact=538|towns=617',text(p['runs'][-1]))
        replay=self.receipts['validations']['replay']['runs'];self.assertEqual(len(replay),2)
        self.assertIn('post_closed|scheduler|industries=538|legacy=4',text(replay[-1]))
        significant=lambda run:[line.split('P7 EVENT|',1)[1] for line in run['observations'] if any('EVENT|'+k+'|' in line for k in ['legacy_authorization','legacy_closed','comparison_final','opened','closed'])]
        self.assertEqual(significant(replay[0]),significant(self.receipts['comparisons']['control']['runs'][3]))
    def test_actual_corrupt_state_refusals(self):
        safety=self.receipts['safety'];self.assertEqual(len(safety),9)
        for r in safety[:-1]:
            self.assertIn('P7 FATAL|',text(r['result']));self.assertNotIn('legacy_authorization|',text(r['result']))
        reused=text(safety[-1]['result']);self.assertIn('old_id=1|new_id=1',reused);self.assertIn('stale_ledger_rejected=true|replacement_via_scheduler=true',reused)
        self.assertIn('exact_tile=false|exact_tile_error=ERR_SITE_UNSUITABLE',reused)
    def test_off_missing_script_wrong_version_and_expired_token(self):
        controls=self.receipts['validations']['controls']['runs'];self.assertEqual(len(controls),7)
        self.assertIn('FATAL|Lifecycle disabled',text(controls[0]));self.assertIn('no_enrollment|scheduler|sites=0',text(controls[1]))
        self.assertIn('FATAL|Legacy controller requires separate AXIS 0.5',text(controls[2]))
        for r,mode in zip(controls[3:5],['off','expired']):self.assertIn('SAFETY_NATIVE|'+mode+'|selected_exists=true|unregistered_exists=true|different_type_exists=true|count=542',text(r))
        self.assertEqual(controls[5]['observations'],[])
        missing=next(r for r in self.runs if r['case']==controls[5]['case'])['saved_engine_observation']
        self.assertGreaterEqual(missing['elapsed_calendar_days'],120);self.assertEqual(missing['industry_count'],542);self.assertTrue(missing['registered_info_file_absent'])
        self.assertIn('NATURAL_DONE|new=0|days=1834',text(controls[6]))
        density=next(r for r in self.runs if r['case']==controls[6]['case'])['inputs']['industry_density'];self.assertEqual(density,4)
    def test_original_scheduled_lifecycle_regression(self):
        r=self.receipts['validations']['soak']['runs'][0];s=text(r)
        self.assertEqual(s.count('EVENT|opened|'),4);self.assertEqual(s.count('EVENT|closed|'),4)
        self.assertIn('regression_done|fixture|calendar=679728|industries=1',s)
    def test_explicit_inactive_migration(self):
        r=self.receipts['validations']['migration']['runs'];self.assertEqual(len(r),3)
        self.assertIn('FATAL|Phase 7A migration requires explicit adopt_only',text(r[0]))
        self.assertIn('legacy_migrated|scheduler|schema=1->2|enrolled=0',text(r[1]))
        self.assertIn('legacy_loaded|scheduler|schema=2|sites=0',text(r[2]))
        self.assertIn('migration_verified|scheduler|events=3|legacy=0',text(r[2]))
    def test_dedicated_ledger_and_public_news(self):
        r=self.receipts['validations']['dedicated']['runs'][0]
        self.assertTrue(r['dedicated']);self.assertFalse(r['dedicated_forced_stop'])
        self.assertEqual(r['command'][r['command'].index('-v')+1],'dedicated')
        self.assertIn('DEDICATED|multiplayer=true',text(r));self.assertIn('EVENT|news|legacy_1|ok=true',text(r));self.assertIn('DEDICATED_SMOKE_DONE|legacy=4',text(r))
    def test_unmanaged_production_flags_and_retail_coverage(self):
        r=next(r for r in self.runs if 'unchanged unmanaged production' in r['scope'])
        self.assertIn('industries=538|towns=617|unmanaged=538|unmanaged_level_changes=0|unmanaged_flag_changes=0|FOOD=76|GOOD=69',text(r))
    def test_initial_preservation_and_models(self):
        p=read('phase7b_preservation_diff.json');self.assertTrue(p['all_map_bytes_unchanged']);self.assertEqual(p['date_changed_fields'],['id'])
        self.assertEqual(p['unchanged_chunks'],['CITY','INDY','PATS','PSAC'])
        m=read('phase7b_candidate_delivery.json');self.assertEqual(len(m['embedded_newgrfs']),15);self.assertFalse(m['test_dates'])
        self.assertEqual(len(m['required_asset_files']),15);self.assertTrue(any(r['format']=='archive' for r in m['required_asset_files']))
        build=read('phase7b_grf_build.json');self.assertTrue(build['models_equal_in_all_six_economies']);self.assertEqual(len(build['economies']),6)
        self.assertEqual(build['economies']['BASIC_TEMPERATE'],dict(industries=96,cargos=64));self.assertFalse(build['engine_patch'])
        self.assertEqual((build['grf_version'],build['min_compatible_version']),(5,4))
        for r in self.receipts['validations']['roundtrip']['runs']:self.assertIn('calendar=668394|economy=657437|types=96|cargos=64',text(r))
    def test_committed_raw_logs_are_exact_and_no_hidden_engine_errors(self):
        for r in self.runs:
            with self.subTest(case=r['case']):
                self.assertEqual(sha(ROOT/r['committed_log']),r['log_sha256'])
                self.assertNotIn('The script died unexpectedly', (ROOT/r['committed_log']).read_text(encoding='utf8'))
                if 'P7 FATAL|' in text(r):self.assertTrue(any(k in r['scope'] for k in ['safe rejection','controls','migration']))
        for r in self.receipts['archived_runs']:self.assertEqual(sha(ROOT/r['committed_log']),r['log_sha256'])
    def test_local_candidate_assets_and_original_guards(self):
        m=read('phase7b_candidate_delivery.json')
        if not Path(m['candidate']).exists():self.skipTest('Local assets excluded from Git')
        from lifecycle_phase7b_runtime import guards
        guards()
        for key in ['candidate','engine','grf','script']:self.assertEqual(sha(Path(m[key])),m[key+'_sha256'])
        for filename,key in [('legacy_policy.nut','policy_sha256'),('schedule.nut','schedule_sha256'),('info.nut','info_sha256')]:self.assertEqual(sha(Path(m['script']).with_name(filename)),m[key])
        self.assertTrue(read('phase7b_editor_observation.json')['named_candidate_reopened'])

if __name__=='__main__':unittest.main()
