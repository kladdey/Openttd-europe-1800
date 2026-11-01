"""Historical-year Europe snapshot and small-map multi-era construction tests.

The small map deliberately removes cargo-endpoint gates to test native date,
layout and persistent scheduling only. It is NOT proof of a working economy.
"""
import argparse,copy,json,shutil
from pathlib import Path
from lifecycle_phase7c_runtime import *
from lifecycle_phase7c_policy import production,setup,absolute_date
from lifecycle_phase7b_policy import production as bp
from lifecycle_phase7a_schedule import historical
def parked():
    s=historical();s['id']='phase7c-fixture-parked-mine-events'
    for e in s['events']:e.update(open_date=absolute_date('2100-01-01'),calendar_open='2100-01-01')
    return s
def code(end):
    return bundle().replace('Initialize(Calendar());while(true)', 'GSGame.Unpause();Initialize(Calendar());while(true)').replace('Tick(Calendar());Sleep(74*14);',f'''local now=Calendar();Tick(now);if(GSDate.GetYear(now)>={end}){{
foreach(e in EXPANSION.events)Log("c_wave_final",e.event_id,"state="+state.expansion[e.event_id].status+"|attempts="+state.expansion[e.event_id].attempts);
Log("c_wave_done","fixture","calendar="+now+"|industries="+GSIndustryList().Count());GSGame.Pause();while(true)Sleep(365);
}}
Sleep(74*14);''')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['europe','mini']);a=ap.parse_args()
    p=production();legacy=bp();legacy.update(enroll_legacy=False,sites=[]);p['retirement']=None
    if a.case=='europe':
        p['id']='phase7c-1864-EDITOR-SNAPSHOT-normal-1865-openings';p['events']=p['events'][1:3]
        source=Path(json.loads((BASE/'future-fixture.json').read_text())['source']);assert source.exists()
        h=prepare('Europe-real-1865-wave',code(1867));setup(h,p,legacy,parked());(h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
        r=execute(h,120000,source=source,timeout=600)
    else:
        p['id']='phase7c-small-map-HISTORICAL-YEARS-construction-only';p['test_mode']=True
        # Sites are intentionally abstract; candidate dates/native rules retained.
        for index,e in enumerate(p['events']):
            e['required_producers']=[];e['required_consumers']=[]
            x,y=[(70,60),(125,70),(150,70),(40,75),(145,110),(170,110),(164,139),(160,150),(188,150),(180,180)][index]
            e['sites']=[(y+dy)*256+x+dx for radius in range(0,25,2) for dx in range(-radius,radius+1,2) for dy in range(-radius,radius+1,2) if abs(dx)+abs(dy)==radius]
        # Slag mill requires a blast furnace, not merely the steelworks type.
        # Town-producer tests use native house-adjacent sites around a real town.
        s=code(2026)
        seed='''GSGame.Unpause();if(loaded==null){
if(!GSIndustryType.BuildIndustry(Type(26),GSMap.GetTileIndex(55,55)))throw "Mini farm seed rejected";
if(!GSIndustryType.BuildIndustry(Type(7),GSMap.GetTileIndex(150,135)))throw "Mini blast-furnace seed rejected";
Log("c_mini_fixture","scope","Cargo gates omitted; not an economic validation; normal historical years retained");
}
Initialize(Calendar());while(true)'''
        s=s.replace('GSGame.Unpause();Initialize(Calendar());while(true)',seed)
        h=prepare('mini-196-historical-years',s);setup(h,p,legacy,parked());cfg=h/'test.cfg';cfg.write_text(cfg.read_text().replace('custom_town_number = 3','custom_town_number = 18'))
        r=execute(h,5500000,timeout=600)
    assert any('c_wave_done|' in line for line in r['observations']),r['log']
    (BASE/('waves-'+a.case+'.json')).write_text(json.dumps(dict(policy=p,scope=a.case,run=r),indent=2))
if __name__=='__main__':main()
