"""Validated policy data; historical windows are explicit game approximations."""
import json,datetime,hashlib
from lifecycle_phase7b_runtime import ROOT,BASE
from lifecycle_phase7a_schedule import absolute_date,squirrel

def production():
    built=json.loads((ROOT/'newgrfs/axis-historical-legacy/.work/enrollment-build.json').read_text())
    dates={1:(1880,1900,1920,'Regional Coalbrookdale workings; proposed exhaustion window, not an identified shaft closure','https://www.ironbridge.org.uk/'),
        11:(1860,1882,1892,'Nachtigall district proxy; 1892 historical closure is a hard cap','https://zeche-nachtigall.lwl.org/de/geschichte/'),
        12:(1950,1978,1998,'Queen Louise district proxy; proposed exhaustion window bounded by documented terminal year','https://www.metropolia.slaskie.travel/culturalheritage/1703/sztolnia-krolowa-luiza-strefa-carnall'),
        438:(1890,1911,1920,'Dolcoath copper working proxy; copper still recorded in 1910; no conversion to tin cargo','https://www.dmm.org.uk/colliery/d241.htm')}
    sites=[]
    for r in built:
        decline,earliest,latest,basis,url=dates[r['industry_id']]
        sites.append(dict(site_id=r['site_id'],name=r['historical_locality'],region=r['region'],local_id=r['local_id'],engine_type=r['type'],
            industry_id=r['industry_id'],tile=r['tile'],born=r['construction_date'],founder=r['founder'],layout=r['selected_layout'],random=r['random'],
            original_record_sha256=r['record_sha256'],snapshot_sha256='afcab50864e87f56a7260c62d87bd37560fa3d7676713afb14c480c555d0bc06',
            arm_level=r['arm_level'],token=r['token'],decline_date=absolute_date(f'{decline}-01-01'),earliest_close=absolute_date(f'{earliest}-01-01'),
            latest_close=absolute_date(f'{latest}-01-01'),warning_years=10,extension_years=min(latest-earliest,10),
            rolling_months=36,minimum_transport=1200,minimum_percent=25,cargo_labels=r['cargo_outputs'],basis=basis,source=url,
            decline_levels=[14,12,10,8] if r['local_id']==0 else [12,10,8],maturity='Mature pre-1830 regional working; native scenario construction date is not historical founding date',
            reserves='UNVERIFIED; no numerical reserves claimed'))
    return validate(dict(id='phase7b-legacy-pilot-v1',schema=2,enroll_legacy=True,migration='reject',test_mode=False,sites=sites))

def validate(p):
    assert __debug__ and p['schema']==2 and p['migration'] in ['reject','adopt_only']
    assert len({s['site_id'] for s in p['sites']})==len(p['sites'])
    assert len({s['industry_id'] for s in p['sites']})==len(p['sites'])
    for s in p['sites']:
        assert s['local_id'] in [0,64] and s['arm_level'] in [5,6,7,9]
        assert s['decline_date']<s['earliest_close']<=s['latest_close'] and 5<=s['warning_years']<=10
        assert s['rolling_months']>=24 and s['minimum_transport']>=1200 and s['minimum_percent']>=25
        assert s['born']==668394 and len(s['original_record_sha256'])==64 and s['token']>0
        if 'decline_levels' in s:assert all(8<=level<16 and level not in [5,6,7,9] for level in s['decline_levels']) and s['decline_levels']==sorted(s['decline_levels'],reverse=True)
    return p

def fixture(served=False):
    p=production();p.update(id='phase7b-real-europe-comparison-v1',test_mode=True)
    for s in p['sites']:
        s.update(decline_date=absolute_date('1831-01-01'),earliest_close=absolute_date('1837-01-01'),latest_close=absolute_date('1839-01-01'),warning_years=5,extension_years=2)
        s.pop('decline_levels',None) # Retain the initially validated accelerated comparison curve.
    return validate(p)

def compile_policy(p,path):
    validate(p);contract=json.dumps(p,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    path.write_text('/* Validated policy: production dates are separate from fixtures. */\nLEGACY_CONTRACT_TEXT <- '+squirrel(contract)+';\nLEGACY_POLICY <- '+squirrel(p)+';\n',encoding='utf-8-sig')

if __name__=='__main__':
    p=production();directory=ROOT/'gamescripts/historical_industry_lifecycle'
    (directory/'legacy_policy.json').write_text(json.dumps(p,indent=2));compile_policy(p,directory/'legacy_policy.nut')
    from industrial_phase6b_plan import write_csv
    write_csv(ROOT/'docs/research/phase7b_managed_pilot.csv',p['sites']);print([(s['site_id'],s['name']) for s in p['sites']])
