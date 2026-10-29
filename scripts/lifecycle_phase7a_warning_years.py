"""Real ten-calendar-year warnings, ordinary-year policy on a small test map."""
import datetime,json,re
from lifecycle_phase7a_runtime import ROOT,BASE,prepare,execute
from lifecycle_phase7a_schedule import historical,fixture,compile_schedule,absolute_date

def main():
    s=historical();s['id']='phase7a-ten-calendar-year-warning-test';mini=fixture()
    for i,(e,m) in enumerate(zip(s['events'],mini['events'])):
        date=f'{1831+i}-01-01';e.update(open_date=absolute_date(date),calendar_open=date,sites=m['sites'],life_years=30,life_jitter_years=0)
    replacement=dict(s['events'][0]);replacement.update(event_id='test_replacement',after_closed=s['events'][0]['event_id'],name='TEST replacement after decade warning',
        calendar_open='1861-01-01',open_date=absolute_date('1861-01-01'),sites=mini['events'][3]['sites']);s['events'].append(replacement)
    text=(ROOT/'gamescripts/historical_industry_lifecycle/main.nut').read_text().replace('Tick(now);Sleep(74*14);',
        'Tick(now);if(GSDate.GetYear(now)>=1865){Log("warning_years_done","fixture","calendar="+now);GSGame.Pause();while(true)Sleep(365);};Sleep(74*14);')
    home=prepare('ten-year-warnings',text);compile_schedule(s,home/'game/lifecycle/schedule.nut');cfg=home/'test.cfg';cfg.write_text(cfg.read_text().replace('custom_town_number = 3','custom_town_number = 12'))
    result=execute(home,980000)
    data='\n'.join(result['observations']);records=[]
    for event in s['events'][:3]:
        match=re.search(r'EVENT\|closing\|'+event['event_id']+r'\|industry=(\d+)\|calendar=(\d+)\|warned_since=(\d+)',data);assert match,event['event_id']
        i,closed,warn=map(int,match.groups());warning_date=datetime.date.fromordinal(warn-365);closure_date=datetime.date.fromordinal(closed-365)
        deadline=warning_date.replace(year=warning_date.year+10);assert closure_date>=deadline
        assert 'EVENT|closed|'+event['event_id']+'|' in data
        records.append(dict(event_id=event['event_id'],warning_date=str(warning_date),closing_date=str(closure_date),warning_days=closed-warn,at_least_ten_calendar_years=True))
    assert 'EVENT|opened|test_replacement|' in data and 'EVENT|warning_years_done|' in data
    (BASE/'ten-year-warnings.json').write_text(json.dumps(dict(evidence='SMALL MAP ENGINE TEST, shortened test lifetimes; real ten-year lead times',records=records,result=result),indent=2))

if __name__=='__main__':main()
