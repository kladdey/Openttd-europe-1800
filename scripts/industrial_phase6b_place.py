"""Place real 1830 industries with engine commands on the paused 617-town copy."""
import json,re
from industrial_phase6b_runtime import ROOT,BASE,run
from transport_phase4 import squirrel


def main(additions=False,retry=False):
    plan=json.loads((BASE/('additions-plan.json' if additions else 'placement-plan.json')).read_text(encoding='utf8'))
    if retry:
        prior=json.loads((BASE/'additions-result.json').read_text())
        done={r['placement_id'] for r in prior['results'] if r['status']=='PLACED'}
        plan=[r for r in plan if r['placement_id'] not in done]
    requests=[dict(p=r['placement_id'],local_id=r['local_id'],tiles=r['candidate_tiles']) for r in plan]
    s='REQUESTS <- '+squirrel(requests)+';\n'
    s+='''class CoastalProbe extends GSController {function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
local raw=GSGameSettings.GetValue("construction.raw_industry_construction"),platform=GSGameSettings.GetValue("construction.industry_platform");
GSLog.Info("I6 BUILD_CONTEXT|raw_before="+raw+"|platform_before="+platform+"|calendar_source=1830|train_limit="+GSGameSettings.GetValue("vehicle.max_train_length"));
if(!GSGameSettings.SetValue("construction.raw_industry_construction",1) || !GSGameSettings.SetValue("construction.industry_platform",0))throw "isolated construction settings rejected";
GSCompany.ChangeBankBalance(0,100000000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
GSLog.Info("I6 CONSTRUCTION_FIXTURE_CASH|"+GSCompany.GetBankBalance(0));
local seen={};foreach(i,_ in GSIndustryList())seen[i]<-true;
{local cm=GSCompanyMode(0);
foreach(r in REQUESTS){
 local type=GSIndustryType.ResolveNewGRFID(0x4B484531,r.local_id),ok=false,attempted=0,last="no candidate";
 if(!GSIndustryType.CanBuildIndustry(type)){GSLog.Info("I6 FAILED|"+r.p+"|"+r.local_id+"|0|industry unavailable in company context");continue;}
 foreach(tile in r.tiles){
  attempted++;
  if(GSIndustryType.BuildIndustry(type,tile)){
   local id=-1;foreach(i,_ in GSIndustryList())if(!(i in seen)){id=i;seen[i]<-true;break;}
   if(id<0)throw "Successful command without a new industry";
   local actual=GSIndustry.GetLocation(id);
   GSLog.Info("I6 PLACED|"+r.p+"|"+id+"|"+r.local_id+"|"+type+"|"+actual+"|"+tile+"|"+attempted);ok=true;break;
  }
  last=GSError.GetLastErrorString();
 }
 if(!ok)GSLog.Info("I6 FAILED|"+r.p+"|"+r.local_id+"|"+attempted+"|"+last);
}
}
GSGameSettings.SetValue("construction.raw_industry_construction",raw);GSGameSettings.SetValue("construction.industry_platform",platform);
GSLog.Info("I6 RESTORED|"+GSGameSettings.GetValue("construction.raw_industry_construction")+"|"+GSGameSettings.GetValue("construction.industry_platform"));
GSLog.Info("C6 DONE industrial placement towns="+GSTownList().Count()+" industries="+GSIndustryList().Count());while(true)Sleep(365);
}}
'''
    if additions:
        migration=json.loads((BASE/'migration-0.3.json').read_text())
        source=__import__('pathlib').Path(json.loads((BASE/'additions-candidate.json').read_text())['candidate']) if retry else __import__('pathlib').Path(migration['engine_save'])
        home=run(s,'additions-retry' if retry else 'additions',12000,source=source,candidate_grf=__import__('pathlib').Path(migration['candidate_assets']))
    else:home=run(s,'placement',12000)
    log=(home/'engine.log').read_text(encoding='utf8');assert 'C6 DONE industrial placement towns=617' in log
    placements=[]
    for m in re.findall(r'I6 PLACED\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)',log):
        p,i,l,t,a,requested,n=map(int,m);placements.append(dict(placement_id=p,industry_id=i,local_id=l,game_type_id=t,tile=a,x=a%4096,y=a//4096,command_tile=requested,attempts=n,status='PLACED',evidence='VERIFIED IN GAME'))
    for m in re.findall(r'I6 FAILED\|(\d+)\|(\d+)\|(\d+)\|([^\r\n]+)',log):
        p,l,n,reason=m;placements.append(dict(placement_id=int(p),local_id=int(l),attempts=int(n),status='FAILED',reason=reason,evidence='VERIFIED IN GAME'))
    assert len(placements)==len(plan)
    result=dict(case=str(home),source_sha256=json.loads((home/'manifest.json').read_text())['source_sha256'],results=placements)
    (BASE/('additions-retry-result.json' if retry else 'additions-result.json' if additions else 'placement-result.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print('Placed',len([r for r in placements if r['status']=='PLACED']),'of',len(plan),flush=True)


if __name__=='__main__':
    import sys
    main('--additions' in sys.argv,'--retry' in sys.argv)
