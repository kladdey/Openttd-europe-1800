"""Reconcile independent engine receipts, finance, coverage and actual artifacts."""
import collections,csv,hashlib,json,re,sys,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'docs/research'
sys.path.insert(0,str(ROOT/'scripts'))


def rows(name):
    with (DATA/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))


def read(name):return json.loads((DATA/name).read_text(encoding='utf-8-sig'))


class InlandEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery=read('inland_scenario_delivery.json');cls.markets=rows('inland_market_placements.csv')
        cls.population=rows('inland_town_population_changes.csv');cls.evidence=read('inland_gameplay_evidence.json')

    def test_final_industry_and_town_accounting(self):
        self.assertEqual(len(self.markets),75);self.assertEqual(len({r['tile'] for r in self.markets}),75)
        self.assertEqual({int(r['industry_id']) for r in self.markets},set(range(467,542)))
        self.assertEqual(collections.Counter(int(r['local_id']) for r in self.markets),{61:45,59:18,57:12})
        self.assertEqual(len({r['town_id'] for r in self.markets}),61)
        self.assertEqual(len(self.population),617);self.assertEqual(len({r['town_id'] for r in self.population}),617)

    def test_every_market_has_matching_actual_command_receipt(self):
        receipts={r['industry_id']:r for r in read('inland_market_engine_receipts.json')}
        self.assertEqual(len(receipts),75)
        for r in self.markets:
            receipt=receipts[int(r['industry_id'])]
            prefix='M6 MARKET|'+'|'.join(r[k] for k in ['request_id','industry_id','local_id','town_id','tile','house_id','population_before','population_after'])+'|'
            self.assertIn(prefix,receipt['measurement']);self.assertEqual(receipt['case'],r['engine_case'])
            self.assertIn(r['accepted_labels'],receipt['measurement'])

    def test_demolition_is_ordinary_one_tile_and_population_reconciles(self):
        specs=read('inland_house_specifications.json')['houses']
        losses=collections.Counter();counts=collections.Counter()
        for r in self.markets:
            s=specs[r['house_id']];self.assertTrue(s['ordinary'] and s['one_tile'])
            self.assertNotIn('PARK',s['building_name']);self.assertEqual(int(r['house_tiles_replaced']),1)
            self.assertEqual(int(r['population_loss']),s['population'])
            self.assertEqual(int(r['population_before'])-int(r['population_after']),int(r['population_loss']))
            losses[r['town_id']]+=int(r['population_loss']);counts[r['town_id']]+=1
        for r in self.population:
            loss=int(r['population_before'])-int(r['population_after'])
            self.assertEqual(loss,losses[r['town_id']]);self.assertEqual(int(r['new_markets']),counts[r['town_id']])
            self.assertGreaterEqual(loss,0);self.assertLessEqual(loss,int(r['population_before'])*.05)
        self.assertEqual(sum(losses.values()),900)

    def test_all_declared_cargos_are_correct_for_market_type(self):
        expected={61:{'FOOD','GOOD','BEER'},59:{'FRUT','FOOD','BEER'},57:{'BDMT','GOOD'}}
        for r in self.markets:self.assertEqual(set(r['accepted_labels'].strip(',').split(',')),expected[int(r['local_id'])])

    def test_coverage_totals_reconcile_with_placement_acceptance(self):
        details=rows('inland_producer_market_distances.csv');summary=rows('inland_market_coverage_summary.csv')
        for cargo,n,before in [('FOOD',92,13),('GOOD',56,12)]:
            group=[r for r in details if r['cargo_label']==cargo];self.assertEqual(len(group),n)
            self.assertEqual(len({r['producer_id'] for r in group}),n)
            self.assertTrue(all(int(r['after_distance'])<=int(r['before_distance']) for r in group))
            out=next(r for r in summary if r['cargo_label']==cargo and r['phase']=='after')
            self.assertEqual(int(out['consumers']),before+sum(cargo in r['accepted_labels'].split(',') for r in self.markets))
            for threshold in [160,300]:self.assertEqual(int(out[f'over_{threshold}_tiles']),sum(int(r['after_distance'])>threshold for r in group))

    def test_finance_rows_match_raw_engine_ledgers(self):
        annual=rows('inland_route_finances.csv');self.assertEqual(len(annual),33)
        for case in self.evidence:
            subset=[r for r in annual if r['test_id']==Path(case['engine_case']).name]
            self.assertEqual(len(subset),len({r['economy_year'] for r in subset}))
            for r in subset:
                raw=next(e for e in case['events'] if e.startswith('FINANCE|'+r['economy_year']+'|'))
                a=list(map(int,raw.split('|')[-1].strip(',').split(',')))
                revenue=-sum(a[7:11]);cost=sum(a[2:7])+sum(a[11:])
                self.assertEqual(int(r['revenue_gbp']),revenue);self.assertEqual(int(r['operating_profit_gbp']),revenue-cost)
                self.assertEqual(int(r['calendar_year']),int(r['economy_year'])+30)

    def test_normal_budget_comparison_excludes_grants_and_tram_trial(self):
        result=rows('inland_route_results.csv')
        for r in result:
            if r['comparison_scope']!='Normal starting-finance comparison':continue
            self.assertEqual(r['grant_requested'],'False')
            self.assertIn('INITIAL|100000|100000|300000|grant=false|maintenance=1|train_limit=7',r['initial_state'])
            self.assertNotIn('315:',r['engines'])
        fruit_fleet=next(r for r in result if r['case']=='farm_fruit' and r['road_fleet_per_leg']=='8')
        self.assertIn('430: 1 Horse Ice Box Carriage',fruit_fleet['engines'])

    def test_paid_chain_claims_have_all_actual_load_and_payment_events(self):
        deliveries=rows('inland_paid_deliveries.csv');self.assertEqual(len(deliveries),17)
        for case in self.evidence:
            paid=[r for r in deliveries if r['test_id']==Path(case['engine_case']).name]
            for r in paid:
                self.assertEqual(r['load_observed'],'True');self.assertGreater(int(r['observed_profit_increase_gbp']),0)
                self.assertLessEqual(int(r['distance_to_destination']),10)
            if case['status']=='VERIFIED IN GAME':self.assertEqual(len(paid),len(case['legs']))
            else:self.assertFalse(any(e.startswith('COMPLETE|all_paid=true') for e in case['events']))

    def test_rail_financial_and_length_conclusion_is_supported(self):
        result=next(r for r in rows('inland_route_results.csv') if r['case']=='rail_food')
        self.assertEqual(int(result['operating_profit_sum_gbp']),16498)
        self.assertEqual(int(result['infrastructure_capital_gbp'])+int(result['vehicle_capital_gbp']),23573)
        self.assertEqual(result['capital_recovery'],'NOT OBSERVED')
        evidence=next(r for r in self.evidence if r['case']=='rail_food')
        train=next(e for e in evidence['events'] if e.startswith('TRAIN|')).split('|')
        self.assertEqual(int(train[-1]),72);self.assertLessEqual(int(train[-2]),7*16)

    def test_coastal_food_recovers_capital_but_horse_examples_do_not(self):
        result=rows('inland_route_results.csv');coast=next(r for r in result if r['case']=='coastal_food')
        self.assertEqual(int(coast['operating_profit_sum_gbp']),23934)
        self.assertIn('after 3 years',coast['capital_recovery'])
        for name in ['local_food','local_goods','regional_food','long_goods']:
            r=next(r for r in result if r['case']==name);self.assertLess(int(r['operating_profit_sum_gbp']),0)

    def test_regressions_are_not_conflated_with_europe_profitability(self):
        salt=next(r for r in self.evidence if r['case']=='salt_regression')
        self.assertEqual(salt['status'],'VERIFIED IN GAME');self.assertEqual(len(salt['paid_events']),3)
        copper=read('inland_copper_regression.json');self.assertIn('not Europe route profitability',copper['scope'])
        self.assertTrue(any('CONTROL_NEGATIVE|copper_ore_only|' in e for e in copper['events']))
        self.assertTrue(any('CONTROL_NEGATIVE|copper_missing_sand|' in e for e in copper['events']))
        self.assertTrue(any('CONTROL_PAID|copper_to_export|' in e for e in copper['events']))
        europe=next(r for r in self.evidence if r['case']=='copper_regression')
        self.assertNotEqual(europe['status'],'VERIFIED IN GAME')

    def test_regrowth_uses_final_candidate_and_original_growth_policy(self):
        j=read('inland_regrowth_validation.json');self.assertEqual(j['source_sha256'],self.delivery['delivered_sha256'])
        self.assertTrue(j['no_growth_rate_or_economy_setting_changes']);self.assertEqual(set(j['industry_counts']),{542})
        for name in ['LONDON','PRAHA','KRAKOW']:
            obs=sorted([r for r in j['observations'] if r['town_name']==name],key=lambda r:r['economy_date'])
            self.assertEqual(len(obs),6);self.assertGreater(obs[-1]['population'],obs[0]['population'])
        self.assertEqual(j['source_road_tiles_no_longer_road'],len(j['road_change_details']))

    def test_editor_and_gameplay_roundtrips_and_settings(self):
        reload=read('inland_reload_validation.json');self.assertEqual(len(reload['tests']),2)
        self.assertTrue(all(r['town_industry_newgrf_rows_and_maps_identical'] for r in reload['tests']))
        self.assertEqual(len(reload['newgrfs']),15)
        for row in ['vehicle.max_train_length|7','economy.infrastructure_maintenance|1','economy.inflation|0']:
            self.assertIn(row,reload['settings'])
        editor=read('inland_editor_validation.json');self.assertTrue(editor['editor_reload_visually_verified'])
        self.assertTrue(editor['editor_roundtrip_maps_towns_industries_settings_identical'])
        self.assertEqual(set(editor['date_editor_changes']),{'id'})

    def test_live_delivered_artifact_preserves_source_and_only_authorized_tiles(self):
        source=Path(self.delivery['source']);dest=Path(self.delivery['delivered']);grf=Path(self.delivery['newgrf_path'])
        if not all(p.exists() for p in [source,dest,grf]):self.skipTest('Local game artifacts unavailable; portable evidence tests still apply')
        for path,key in [(source,'source_sha256'),(dest,'delivered_sha256'),(grf,'newgrf_sha256')]:
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),self.delivery[key])
        from coastal_phase6_preservation import parts,differences
        a,b=parts(source),parts(dest)
        self.assertEqual(a['INDY'][1],b['INDY'][1][:len(a['INDY'][1])])
        self.assertEqual(a['PSAC'][1],b['PSAC'][1][:len(a['PSAC'][1])])
        for tag in ['NGRF','PATS','DATE','GSDT','ANIT','STNN']:self.assertEqual(a[tag],b[tag],tag)
        _,_,changed,guard=differences(source,dest)
        self.assertEqual(set(changed.nonzero()[0]),{int(r['tile']) for r in self.markets})
        for key in ['height_changes','water_type_changes','existing_infrastructure_changes']:self.assertEqual(guard[key],0)

    def test_retained_engine_log_hashes_match_portable_receipts(self):
        cases={r['case']:r['engine_log_sha256'] for r in read('inland_market_engine_receipts.json')}
        cases.update({r['engine_case']:r['engine_log_sha256'] for r in self.evidence})
        found=0
        for path,expected in cases.items():
            file=Path(path)/'engine.log'
            if not file.exists():continue
            found+=1;self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),expected)
        if not found:self.skipTest('Raw local engine logs unavailable')

    def test_all_617_towns_reconcile_with_real_reload_observations(self):
        path=Path(read('inland_reload_validation.json')['tests'][0]['case'])/'engine.log'
        if not path.exists():self.skipTest('Local engine log unavailable')
        actual={int(i):(name,int(tile),int(pop)) for i,name,tile,pop,houses in re.findall(r'M6 TOWN\|(\d+)\|([^|]+)\|(\d+)\|(\d+)\|(\d+)',path.read_text(encoding='utf8'))}
        expected={int(r['town_id']):(r['town_name'],int(r['y'])*4096+int(r['x']),int(r['population_after'])) for r in self.population}
        self.assertEqual(actual,expected)


if __name__=='__main__':unittest.main()
