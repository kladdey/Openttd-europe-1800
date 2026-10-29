"""Observe five years of unassisted town regrowth, with original growth settings."""
import json,re
from pathlib import Path
import numpy as np
from inland_phase6c_runtime import ROOT,BASE,run,sha
from coastal_phase6_preservation import parts,maps
from industrial_phase6b_plan import write_csv
from transport_phase4 import squirrel


def main():
    towns=json.loads((BASE/'towns.json').read_text(encoding='utf8'))
    selected=[t for t in towns if t['name'] in ['LONDON','PRAHA','KRAKOW']]
    assert len(selected)==3
    ids=[t['town_id'] for t in selected]
    script='TOWNS <- '+squirrel(ids)+';\n'+'''class CoastalProbe extends GSController {
function Snapshot(){foreach(t in TOWNS)GSLog.Info("M6 GROWTH|"+GSDate.GetCurrentDate()+"|"+t+"|"+GSTown.GetPopulation(t)+"|"+GSTown.GetHouseCount(t)+"|"+GSTown.GetGrowthRate(t));GSLog.Info("M6 GROWTH_INDUSTRIES|"+GSIndustryList().Count());}
function Start(){while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);Snapshot();local year=GSDate.GetYear(GSDate.GetCurrentDate()),end=year+5;
while(GSDate.GetYear(GSDate.GetCurrentDate())<end){if(GSDate.GetYear(GSDate.GetCurrentDate())!=year){Snapshot();year=GSDate.GetYear(GSDate.GetCurrentDate());}
Sleep(74);}
Snapshot();GSGame.Pause();GSLog.Info("C6 DONE unassisted regrowth");while(true)Sleep(365);}}'''
    source=Path(json.loads((BASE/'candidate.json').read_text())['candidate']);home=run(script,'regrowth',160000,source=source,unpaused=True)
    log=(home/'engine.log').read_text(encoding='utf8');assert 'C6 DONE unassisted regrowth' in log
    rows=[dict(economy_date=int(d),economy_year=1800+(int(d)-657437)//365,town_id=int(t),town_name=next(x['name'] for x in selected if x['town_id']==int(t)),population=int(p),house_count=int(h),growth_rate_days=int(g),evidence='VERIFIED IN GAME',service_condition='No added passenger, mail or freight service; normal town growth settings',engine_case=str(home)) for d,t,p,h,g in re.findall(r'M6 GROWTH\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)',log)]
    before=maps(parts(source));after=maps(parts(home/'save/autosave/exit.sav'))
    at=np.frombuffer(before['MAPT'],dtype='u1')>>4;bt=np.frombuffer(after['MAPT'],dtype='u1')>>4
    road_removed=int(np.count_nonzero((at==2)&(bt!=2)))
    write_csv(ROOT/'docs/research/inland_town_regrowth.csv',rows)
    (ROOT/'docs/research/inland_regrowth_validation.json').write_text(json.dumps(dict(case=str(home),source_sha256=sha(source),source_road_tiles_no_longer_road=road_removed,industry_counts=list(map(int,re.findall(r'M6 GROWTH_INDUSTRIES\|(\d+)',log))),no_growth_rate_or_economy_setting_changes=True,observations=rows),indent=2))
    print('Regrowth rows',len(rows),'source road tiles lost',road_removed)


if __name__=='__main__':main()
