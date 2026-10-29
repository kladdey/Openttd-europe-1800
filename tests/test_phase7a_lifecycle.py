"""Compiler safety and reconciliation of independently captured engine receipts.

Does not claim to run JGRPP: use the documented isolated engine drivers for that.
Local immutable-asset checks are skipped if a fresh clone lacks runtime assets.
"""
import copy,csv,datetime,hashlib,json,re,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'docs/research'
sys.path.insert(0,str(ROOT/'scripts'))
from lifecycle_phase7a_schedule import absolute_date,compile_schedule,validate

def read(name):return json.loads((DATA/name).read_text(encoding='utf-8-sig'))
def rows(name):
    with (DATA/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def observations(run):return '\n'.join(run['observations'])
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class ScheduleSafetyTests(unittest.TestCase):
    def setUp(self):self.schedule=json.loads((ROOT/'gamescripts/historical_industry_lifecycle/schedule.json').read_text())

    def test_production_dates_are_openings_not_foundations(self):
        s=validate(self.schedule)
        self.assertFalse(s['test_mode']);self.assertEqual(s['seed'],7341830)
        self.assertEqual([e['calendar_open'] for e in s['events']],['1833-08-05','1851-01-01','1860-01-01'])
        self.assertEqual([e['region'] for e in s['events']],['GB','DE','PL'])
        self.assertEqual(len({e['event_id'] for e in s['events']}),3)
        self.assertTrue(all(e['warning_years']==10 and e['local_id']==0 for e in s['events']))

    def test_date_epoch_and_leap_day(self):
        self.assertEqual(absolute_date('1830-01-01'),668394)
        self.assertEqual(absolute_date('1800-01-01'),657437)
        self.assertEqual(absolute_date('1840-03-01')-absolute_date('1840-02-28'),2)
        self.assertEqual(absolute_date('1900-03-01')-absolute_date('1900-02-28'),1)

    def test_reject_unsafe_event_properties(self):
        mutations=[('warning_years',4),('warning_years',11),('local_id',67),('max_attempts',0),('max_attempts',65),
                   ('life_years',29),('sites',[-1]),('sites',[1,1]),('sites',list(range(65))),('after_closed','missing'),('open_date',1)]
        for key,value in mutations:
            with self.subTest(key=key,value=value):
                s=copy.deepcopy(self.schedule);s['events'][0][key]=value
                with self.assertRaises(AssertionError):validate(s)

    def test_reject_duplicate_ids_and_cyclic_dependencies(self):
        s=copy.deepcopy(self.schedule);s['events'][1]['event_id']=s['events'][0]['event_id']
        with self.assertRaises(AssertionError):validate(s)
        s=copy.deepcopy(self.schedule);a,b=s['events'][:2];a['after_closed']=b['event_id'];b['after_closed']=a['event_id']
        with self.assertRaisesRegex(AssertionError,'Cyclic'):validate(s)

    def test_native_compilation_unicode_and_committed_output(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'schedule.nut';compile_schedule(self.schedule,path)
            self.assertEqual(path.read_bytes(),(ROOT/'gamescripts/historical_industry_lifecycle/schedule.nut').read_bytes())
            self.schedule['events'][0]['name']='Śląsk — coal';compile_schedule(self.schedule,path)
            text=path.read_text(encoding='utf-8-sig')
            self.assertIn('Śląsk',text);self.assertNotIn('\\u015a',text)

class EngineEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs=read('phase7a_engine_run_evidence.json');cls.events=rows('phase7a_engine_events.csv')
        cls.persistence=read('phase7a_save_reload_results.json')

    def test_availability_real_closure_and_native_constraints(self):
        probes=self.runs[:3]
        self.assertIn('AVAILABLE|false',observations(probes[0]));self.assertIn('AVAILABLE|false',observations(probes[1]))
        text=observations(probes[2]);self.assertIn('AVAILABLE|true',text)
        self.assertIn('CLOSURE|0|still_exists=false|other_exists=true',text)
        self.assertIn('BELOW_MINIMUM|result=false',text);self.assertIn('COAST_GATE|land_fishing_ground=false',text)
        for probe in probes:self.assertIn('FUTURE_GATE|can=false|built=false',observations(probe))

    def test_natural_generation_control_not_density_zero(self):
        controls=read('phase7a_natural_spawning_controls.json');self.assertEqual(len(controls),2)
        for r in controls:
            self.assertIn('NATURAL_DONE|new=0|days=1834',observations(r))
            self.assertIn('industries=47',observations(r))
        recorded=[r for r in self.runs if r['scope']=='SMALL MAP ENGINE: FIVE-YEAR NATURAL CONTROL']
        self.assertEqual([r['inputs']['industry_density'] for r in recorded],[4,4])

    def test_ordinary_dates_and_calendar_economy_separation(self):
        actual=[r for r in self.events if r['scope']=='SMALL MAP ENGINE: ORDINARY OPENING DATES' and r['event']=='opened']
        self.assertEqual([r['calendar_date'] for r in actual],['1833-08-11','1851-01-03','1860-01-13'])
        self.assertEqual([(r['x'],r['y']) for r in actual],[('150','40'),('150','150'),('214','210')])
        text='\n'.join(observations(r) for r in self.runs if r['scope']=='FULL EUROPE ENGINE: EXACT PRODUCTION SCRIPT')
        self.assertIn('calendar=668394|economy=657437',text)
        self.assertNotIn('EVENT|opened|',text)

    def test_real_ten_year_warning_and_physical_closure(self):
        data=read('phase7a_ten_year_warnings.json');self.assertEqual(len(data['records']),3)
        for r in data['records']:
            warn=datetime.date.fromisoformat(r['warning_date']);close=datetime.date.fromisoformat(r['closing_date'])
            self.assertGreaterEqual(close,warn.replace(year=warn.year+10))
            self.assertTrue(r['at_least_ten_calendar_years'])
            self.assertIn('EVENT|closed|'+r['event_id']+'|',observations(data['result']))

    def test_europe_open_close_replacement_no_duplicates(self):
        e=[r for r in self.events if r['scope']=='FULL EUROPE ENGINE: ACCELERATED REGIONAL TEST']
        opened=[r for r in e if r['event']=='opened'];closed=[r for r in e if r['event']=='closed']
        self.assertEqual(len(opened),4);self.assertEqual(len(closed),4)
        self.assertEqual({r['event_id'] for r in opened},{r['event_id'] for r in closed})
        self.assertEqual([(r['x'],r['y']) for r in opened],[('2954','1095'),('1953','1251'),('748','1495'),('2859','927')])
        first_closed=next(r for r in closed if r['event_id']=='test_gb_coalfield')
        self.assertGreaterEqual(int(opened[-1]['calendar_engine_date']),int(first_closed['calendar_engine_date']))
        self.assertGreater(e.index(opened[-1]),e.index(first_closed),'Replacement must follow physical absence, even within one polling date')
        final=observations(self.persistence['europe_vertical_slice']['result'])
        self.assertIn('baseline_preserved=542|towns=617|unplanned=0|service_vehicles_remaining=2',final)
        self.assertIn('calendar=669489',final)

    def test_actual_loaded_paid_observations_are_not_invoices(self):
        paid=rows('phase7a_paid_deliveries.csv');self.assertEqual(len(paid),2)
        self.assertEqual(sorted(int(r['sampled_net_vehicle_profit_increase']) for r in paid),[64,233])
        for r in paid:self.assertIn('not gross shipment invoice',r['evidence'])

    def test_replay_and_supported_schema_migration(self):
        replay=self.persistence['checkpoint_replay'];self.assertTrue(replay['significant_transitions_identical'])
        self.assertEqual(len(replay['runs']),2)
        migration=self.persistence['schema_migration'];self.assertEqual((migration['old_schema'],migration['new_schema']),(0,1))
        self.assertIn('EVENT|migrated|scheduler|schema=0->1',observations(migration['result']))

    def test_boundary_results_explicitly_label_injection(self):
        boundary={r['name']:r for r in self.persistence['safe_rejection_and_boundaries']}
        for name in ['longevity','closure_timeout','bounded_retry','late_warning']:
            self.assertIn('injected state',boundary[name]['scope'])
            self.assertIn('EVENT|boundary_pass|'+name+'|',observations(boundary[name]['result']))
        self.assertIn('capped at 15 years',observations(boundary['longevity']['result']))
        post=observations(boundary['europe_post_closed']['result'])
        self.assertIn('industries=542|towns=617|closed_instances_absent=4|FOOD=76|GOOD=69',post)

    def test_fail_closed_and_preserve_unknown_saved_data(self):
        boundary={r['name']:r['result'] for r in self.persistence['safe_rejection_and_boundaries']}
        self.assertIn('FATAL|Missing lifecycle ledger',observations(boundary['lost_ledger']))
        self.assertIn('FATAL|Unsupported saved lifecycle schema',observations(boundary['unknown_schema']))
        self.assertIn('UNKNOWN_SCHEMA_PRESERVED|schema=99|events=4',observations(boundary['unknown_payload_preserved']))
        reject=self.persistence['schedule_edit_rejection']
        self.assertIn('FATAL|Schedule contract changed',observations(reject));self.assertNotIn('EVENT|opened|',observations(reject))

    def test_gui_and_actual_dedicated_driver_are_distinct_proofs(self):
        gui=read('phase7a_warning_visibility.json');self.assertTrue(gui['news_window_visible'])
        self.assertTrue(gui['clicking_news_centred_wolverhampton_managed_mine'])
        server=read('phase7a_dedicated_smoke.json');self.assertTrue(server['dedicated']);self.assertFalse(server['dedicated_forced_stop'])
        command=server['command'];self.assertEqual(command[command.index('-v')+1],'dedicated')
        self.assertIn('DEDICATED|multiplayer=true',observations(server));self.assertIn('DEDICATED_SMOKE_DONE|loaded=true',observations(server))

    def test_models_compile_and_rebuild_identity(self):
        models=read('phase7a_model_validation.json');self.assertTrue(models['all_models_recipes_properties_layouts_cargo_ids_identical'])
        self.assertEqual(len(models['economies']),6);self.assertEqual(models['economies']['BASIC_TEMPERATE'],dict(industries=96,cargos=64))
        build=read('phase7a_grf_build.json');self.assertFalse(build['engine_patch']);self.assertEqual(build['default'],0)
        self.assertEqual(build['grf_version'],4);self.assertTrue(build['reproduction']['bit_identical'])
        self.assertEqual(build['sha256'],build['reproduction']['after_sha256'])

    def test_portable_initial_preservation_receipt(self):
        delivery=read('phase7a_candidate_delivery.json');p=delivery['initial_preservation']
        self.assertEqual(p['date_changed_fields'],['id'])
        self.assertEqual(p['unchanged_record_chunks'],['CITY','INDY','PATS','PSAC'])
        self.assertTrue(p['all_map_bytes_unchanged']);self.assertEqual(len(p['embedded_newgrfs']),15)
        self.assertEqual(p['candidate_date']['date'],668394)
        self.assertEqual(p['candidate_date']['economy_date'],657437)
        observation=read('phase7a_editor_observation.json');self.assertTrue(observation['editor_save_and_reload_observed'])
        self.assertEqual(observation['candidate_sha256'],delivery['candidate_sha256'])

    def test_positive_runs_have_no_hidden_fatal_and_raw_receipts_match(self):
        for r in self.runs:
            with self.subTest(case=r['case'],label=r['label']):
                if 'EXPECTED SAFE REJECTION' not in r['scope'] and 'intentional failure' not in r['scope']:
                    self.assertNotIn('P7 FATAL|',observations(r))
                self.assertNotIn('P7ERROR',observations(r))
                path=Path(r['log'])
                if path.exists():self.assertEqual(sha(path),r['log_sha256'])

    def test_local_candidate_and_original_immutable_assets(self):
        delivery=read('phase7a_candidate_delivery.json');candidate=Path(delivery['candidate'])
        if not candidate.exists():self.skipTest('Local runtime assets excluded from Git')
        from lifecycle_phase7a_runtime import SOURCE,guards
        from coastal_phase6_preservation import parts,maps
        from historical_scenario_migration import inspect
        guards();self.assertEqual(sha(candidate),delivery['candidate_sha256'])
        for key,digest in [('grf','grf_sha256'),('script','script_sha256')]:self.assertEqual(sha(Path(delivery[key])),delivery[digest])
        self.assertEqual(sha(Path(delivery['script']).parent/'schedule.nut'),delivery['schedule_sha256'])
        before,after=parts(SOURCE),parts(candidate)
        for tag in ['CITY','INDY','PATS','PSAC']:self.assertEqual(before[tag],after[tag],tag)
        self.assertEqual(maps(before),maps(after))
        a,b=inspect(SOURCE),inspect(candidate)
        self.assertEqual((b['town_records'],b['industry_records']),(617,542))
        self.assertEqual(len(b['newgrfs']),15)
        self.assertEqual([r for r in a['newgrfs'] if r['grfid']!='4B484531'],[r for r in b['newgrfs'] if r['grfid']!='4B484531'])

if __name__=='__main__':unittest.main()
