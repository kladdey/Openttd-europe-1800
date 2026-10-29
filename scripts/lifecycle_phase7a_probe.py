"""First actual selective-construction and closure experiment, stock engine."""
from lifecycle_phase7a_runtime import prepare,execute,BASE
import json
SCRIPT='''class LifecycleController extends GSController {
 function Build(x,y){local ty=GSIndustryType.ResolveNewGRFID(0x4B484531,0);local before={};foreach(i,_ in GSIndustryList())before[i]<-true;
 for(local r=0;r<=20;r++)for(local dx=-r;dx<=r;dx++)foreach(dy in [r-abs(dx),-(r-abs(dx))]){
  if(GSIndustryType.BuildIndustry(ty,GSMap.GetTileIndex(x+dx,y+dy))){foreach(i,_ in GSIndustryList())if(!(i in before)){GSLog.Info("P7 OPEN|"+i+"|"+GSIndustry.GetLocation(i));return i;}}
 }throw "Bounded construction failed "+GSError.GetLastErrorString();}
 function Start(){try{
 local page=GSStoryPage.New(GSCompany.COMPANY_INVALID,"Lifecycle clock probe");GSLog.Info("P7 CLOCK|economy="+GSDate.GetCurrentDate()+"|calendar="+GSStoryPage.GetDate(page));GSStoryPage.Remove(page);
 local ty=GSIndustryType.ResolveNewGRFID(0x4B484531,0);GSLog.Info("P7 AVAILABLE|"+GSIndustryType.CanBuildIndustry(ty));
 local future=GSIndustryType.ResolveNewGRFID(0x4B484531,67);local early=GSIndustryType.BuildIndustry(future,GSMap.GetTileIndex(200,100));GSLog.Info("P7 FUTURE_GATE|can="+GSIndustryType.CanBuildIndustry(future)+"|built="+early+"|error="+GSError.GetLastErrorString());if(early)throw "Future industry bypassed date gate";
 if(!GSIndustryType.CanBuildIndustry(ty)){GSLog.Info("P7 REJECT|"+GSIndustryType.BuildIndustry(ty,GSMap.GetTileIndex(40,40))+"|"+GSError.GetLastErrorString());GSGame.Pause();while(true)Sleep(365);}
 local first=Build(40,40),second=Build(150,40);local below=GSIndustry.SetProductionLevel(first,3,false,null);GSLog.Info("P7 BELOW_MINIMUM|result="+below+"|error="+GSError.GetLastErrorString());if(below)throw "Illegal production minimum accepted";
 local fish=GSIndustryType.ResolveNewGRFID(0x4B484531,32);local inland=GSIndustryType.BuildIndustry(fish,GSMap.GetTileIndex(200,100));GSLog.Info("P7 COAST_GATE|land_fishing_ground="+inland+"|error="+GSError.GetLastErrorString());if(inland)throw "Invalid coastline was bypassed";
 GSLog.Info("P7 PRODUCTION_COMMAND|"+first+"|"+GSIndustry.GetProductionLevel(first)+"|"+GSIndustry.SetProductionLevel(first,8,true,"Lifecycle decline test"));
 local ok=GSNews.Create(GSNews.NT_ECONOMY,"TEST ONLY: planned closure of managed mine; production configuration uses ten years warning",GSCompany.COMPANY_INVALID,GSNews.NR_TILE,GSIndustry.GetLocation(first));GSLog.Info("P7 NEWS|"+ok);
 local start=GSDate.GetCurrentDate();while(GSDate.GetCurrentDate()-start<65)Sleep(10);
 GSLog.Info("P7 CLOSE_REQUEST|"+first+"|"+GSIndustry.SetProductionLevel(first,4,true,"TEST ONLY: closure command"));
 while(GSDate.GetCurrentDate()-start<180 && GSIndustry.IsValidIndustry(first))Sleep(10);
 GSLog.Info("P7 CLOSURE|"+first+"|still_exists="+GSIndustry.IsValidIndustry(first)+"|other_exists="+GSIndustry.IsValidIndustry(second));GSGame.Pause();GSLog.Info("P7 DONE probe");
 }catch(e){GSLog.Error("P7 ERROR|"+e);GSGame.Pause();}while(true)Sleep(365);}}
'''
if __name__=='__main__':
    result=[]
    for label,policy,old in [('stock03',False,True),('candidate_off',False,False),('candidate_on',True,False)]:
        home=prepare('probe-'+label,SCRIPT,policy=policy,old=old)
        cfg=home/'test.cfg';cfg.write_text(cfg.read_text().replace('custom_town_number = 3','custom_town_number = 12'))
        r=execute(home,18000);lines='\n'.join(r['observations'])
        assert 'P7 FUTURE_GATE|can=false|built=false|error=ERR_PRECONDITION_FAILED' in lines
        assert 'P7 ERROR|' not in lines
        if policy:
            assert 'still_exists=false|other_exists=true' in lines and 'P7 BELOW_MINIMUM|result=false|' in lines and 'P7 COAST_GATE|land_fishing_ground=false|' in lines
        else:assert 'P7 REJECT|false|ERR_PRECONDITION_FAILED' in lines
        result.append(r)
    (BASE/'probes.json').write_text(json.dumps(result,indent=2))
