"""Supported HOUSE replacement, with aggregate per-town population limits."""
import json,re
from inland_phase6c_runtime import ROOT,BASE,run
from transport_phase4 import squirrel


def main():
    import sys
    fruit="--fruit" in sys.argv
    extend="--extend" in sys.argv or fruit
    plan=json.loads((BASE/('market-fruit-plan.json' if fruit else 'market-extension-plan.json' if extend else 'market-plan.json')).read_text(encoding='utf8'))
    requests=[{k:r[k] for k in ['request_id','town_id','population','population_budget','local_id','sites']} for r in plan['requests']]
    script='REQUESTS <- '+squirrel(requests)+';\n'+'''class CoastalProbe extends GSController {function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
local platform=GSGameSettings.GetValue("construction.industry_platform");GSGameSettings.SetValue("construction.industry_platform",0);
GSCompany.ChangeBankBalance(0,1000000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
local seen={};foreach(i,_ in GSIndustryList())seen[i]<-true;
foreach(t,_ in GSTownList())GSLog.Info("M6 BEFORE_TOWN|"+t+"|"+GSTown.GetName(t)+"|"+GSTown.GetLocation(t)+"|"+GSTown.GetPopulation(t));
{local cm=GSCompanyMode(0);
foreach(r in REQUESTS){local ok=false,attempts=0,last="No safeguarded site",type=GSIndustryType.ResolveNewGRFID(0x4B484531,r.local_id);
 foreach(s in r.sites){
  if(!GSTile.IsHouseTile(s.tile))continue;
  local before=GSTown.GetPopulation(r.town_id),loss=r.population-before;
  if(loss+s.estimated_population_loss>r.population_budget)continue;
  attempts++;if(!GSIndustryType.BuildIndustry(type,s.tile)){last=GSError.GetLastErrorString();continue;}
  local id=-1;foreach(i,_ in GSIndustryList())if(!(i in seen)){id=i;seen[i]<-true;break;}
  local after=GSTown.GetPopulation(r.town_id);if(id<467 || before-after!=s.estimated_population_loss || r.population-after>r.population_budget)throw "Demolition safeguard mismatch; discard this test copy";
  local ac="";foreach(c,_ in GSIndustryType.GetAcceptedCargo(type)){if(GSIndustry.IsCargoAccepted(id,c)!=GSIndustry.CAS_ACCEPTED)throw "Market rejected declared cargo";ac+=GSCargo.GetCargoLabel(c)+",";}
  GSLog.Info("M6 MARKET|"+r.request_id+"|"+id+"|"+r.local_id+"|"+r.town_id+"|"+s.tile+"|"+s.house_id+"|"+before+"|"+after+"|"+attempts+"|"+ac);ok=true;break;
 }
 if(!ok)GSLog.Info("M6 FAILED|"+r.request_id+"|"+attempts+"|"+last);
}}
GSGameSettings.SetValue("construction.industry_platform",platform);
foreach(t,_ in GSTownList())GSLog.Info("M6 AFTER_TOWN|"+t+"|"+GSTown.GetName(t)+"|"+GSTown.GetLocation(t)+"|"+GSTown.GetPopulation(t));
GSLog.Info("C6 DONE markets towns="+GSTownList().Count()+" industries="+GSIndustryList().Count());while(true)Sleep(365);}}'''
    source=None
    if extend:source=__import__('pathlib').Path(json.loads((BASE/'candidate.json').read_text())['candidate'])
    home=run(script,'placement-extension' if extend else 'placement',12000,source=source);log=(home/'engine.log').read_text(encoding='utf8')
    assert 'C6 DONE markets towns=617' in log,log[-3000:]
    good=[]
    for row in re.findall(r'M6 MARKET\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|([^\r\n]+)',log):
        p,i,l,t,tile,h,b,a,n=map(int,row[:9]);good.append(dict(request_id=p,industry_id=i,local_id=l,town_id=t,tile=tile,x=tile%4096,y=tile//4096,house_id=h,population_before=b,population_after=a,population_loss=b-a,house_tiles_replaced=1,attempts=n,accepted_labels=row[9],status='PLACED',evidence='VERIFIED IN GAME'))
    bad=[dict(request_id=int(i),attempts=int(n),reason=e,status='FAILED',evidence='VERIFIED IN GAME') for i,n,e in re.findall(r'M6 FAILED\|(\d+)\|(\d+)\|([^\r\n]+)',log)]
    assert len(good)+len(bad)==len(plan['requests'])
    for r in good+bad:r['engine_case']=str(home)
    if extend:
        prior=json.loads((BASE/'placement.json').read_text());(BASE/('placement-before-fruit.json' if fruit else 'placement-initial.json')).write_text(json.dumps(prior,indent=2))
        good=prior['results']+good
    result=dict(case=str(home),results=good+bad,settings_restored=True)
    (BASE/'placement.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('Markets placed',len(good),'failed',len(bad))


if __name__=='__main__':main()
