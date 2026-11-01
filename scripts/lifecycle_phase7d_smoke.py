"""One focused native construction probe; no terrain/house/road demolition."""
import json
from lifecycle_phase7d_runtime import *
from lifecycle_phase7d_policy import production,setup,squirrel
PROBE='''
class DProbe extends ProgressionController {
 function Find(e,x,y){
  local reasons={},commands=0;for(local radius=0;radius<=40;radius++)for(local dx=-radius;dx<=radius;dx++)for(local dy=-radius;dy<=radius;dy++){
   if(abs(dx)+abs(dy)!=radius)continue;
   local xx=x+dx,yy=y+dy;if(xx<2||yy<2||xx>=GSMap.GetMapSizeX()-10||yy>=GSMap.GetMapSizeY()-10)continue;
   local tile=GSMap.GetTileIndex(xx,yy),reason=SiteReason(tile,e);
   if(!(reason in reasons))reasons[reason]<-0;reasons[reason]++;
   if(reason!="safe")continue;
   local before={};foreach(i,_ in GSIndustryList())before[i]<-true;
   commands++;
   if(GSIndustryType.BuildIndustry(Type(e.local_id),tile)){
    foreach(i,_ in GSIndustryList())if(!(i in before)){
     GSLog.Info("P7 D_BUILT|local="+e.local_id+"|industry="+i+"|tile="+GSIndustry.GetLocation(i)+"|native_attempts="+commands);
     foreach(k,v in reasons)GSLog.Info("P7 D_SITE_COUNTS|local="+e.local_id+"|"+k+"="+v);
     return i;
    }
   }
   GSLog.Info("P7 D_NATIVE_REJECT|local="+e.local_id+"|tile="+tile+"|"+GSError.GetLastErrorString());
   if(commands>=64){foreach(k,v in reasons)GSLog.Info("P7 D_SITE_COUNTS|local="+e.local_id+"|"+k+"="+v);return -1;}
  }
  foreach(k,v in reasons)GSLog.Info("P7 D_SITE_COUNTS|local="+e.local_id+"|"+k+"="+v);
  return -1;
 }
 function Start(){try{
 GSGame.Unpause();local town=-1;foreach(t,_ in GSTownList())if(town<0||GSTown.GetPopulation(t)>GSTown.GetPopulation(town))town=t;
 local at=GSTown.GetLocation(town),x=GSMap.GetTileX(at),y=GSMap.GetTileY(at);
 GSLog.Info("P7 D_TOWN|id="+town+"|population="+GSTown.GetPopulation(town)+"|tile="+at);
 local made=[];
 foreach(local_id in [24,25,23,18]){
  local e=null;foreach(candidate in EXPANSION.events)if(candidate.local_id==local_id){e=candidate;break;}
  local i=Find(e,x,y);if(i<0)throw "Native construction exhausted type "+local_id;
  made.append(i);if(local_id==25){at=GSIndustry.GetLocation(i);x=GSMap.GetTileX(at)+10;y=GSMap.GetTileY(at);}
  foreach(c,_ in GSIndustryType.GetAcceptedCargo(Type(local_id)))GSLog.Info("P7 D_ACCEPTS|"+local_id+"|"+GSCargo.GetCargoLabel(c));
  foreach(c,_ in GSIndustryType.GetProducedCargo(Type(local_id)))GSLog.Info("P7 D_OUTPUT|"+local_id+"|"+GSCargo.GetCargoLabel(c));
 }
 local start=GSDate.GetCurrentDate();while(GSDate.GetCurrentDate()-start<65)Sleep(74);
 foreach(c,_ in GSIndustryType.GetProducedCargo(Type(24)))GSLog.Info("P7 D_COLLECTION_PRODUCTION|cargo="+GSCargo.GetCargoLabel(c)+"|last_month="+GSIndustry.GetLastMonthProduction(made[0],c));
 GSLog.Info("P7 D_SMOKE_DONE|constructed=4|houses_removed=0|industries="+GSIndustryList().Count());GSGame.Pause();
 }catch(e){GSLog.Error("P7 D_BLOCKED|"+e);GSGame.Pause();}
 while(true)Sleep(365);
 }
}
'''
if __name__=='__main__':
 h=prepare('modern-construction',bundle()+'\n'+PROBE,year=1985);setup(h)
 info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"ProgressionController"','"DProbe"'))
 r=execute(h,150000,timeout=300);(BASE/'modern-smoke.json').write_text(json.dumps(r,indent=2))
 print('PASS' if any('D_SMOKE_DONE|' in s for s in r['observations']) else 'BLOCKED')
