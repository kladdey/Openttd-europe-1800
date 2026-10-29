"""Reject edited production schedules even if their label and seed are retained."""
import datetime,json
from pathlib import Path
from lifecycle_phase7a_runtime import ROOT,BASE,prepare,execute
from lifecycle_phase7a_schedule import historical,compile_schedule

if __name__=='__main__':
    manifest=json.loads((BASE/'candidate-delivery.json').read_text())
    source=Path(manifest['actual_production_script_gameplay_save_reload'][0]['case'])/'production-start.sav'
    s=historical();e=s['events'][0];e['open_date']+=1;e['calendar_open']=(datetime.date.fromisoformat(e['calendar_open'])+datetime.timedelta(days=1)).isoformat()
    home=prepare('edited-schedule-rejection',(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text());compile_schedule(s,home/'game/lifecycle/schedule.nut')
    result=execute(home,2000,source=source)
    assert any('P7 FATAL|Schedule contract changed; explicit migration required' in line for line in result['observations'])
    assert not any('EVENT|opened|' in line for line in result['observations'])
    (BASE/'schedule-contract-rejection.json').write_text(json.dumps(result,indent=2))
