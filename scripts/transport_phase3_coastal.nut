class TransportProbe extends GSController {
 function Start(){
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(2);
  local company=GSCompanyMode(0);
  foreach(i,v in GSIndustryList()){
   local type=GSIndustry.GetIndustryType(i),produces=false,accepts=false;
   foreach(c,z in GSIndustryType.GetProducedCargo(type))if(c==14 && GSIndustry.GetLastMonthProduction(i,c)>0)produces=true;
   foreach(c,z in GSIndustryType.GetAcceptedCargo(type))if(c==14)accepts=true;
   if(!produces && !accepts)continue;
   local count=0,example=-1,tiles=produces?GSTileList_IndustryProducing(i,5):GSTileList_IndustryAccepting(i,5);
   foreach(tile,z in tiles){
    if(!GSTile.IsCoastTile(tile))continue;
    local test=GSTestMode(),ok=GSMarine.BuildDock(tile,GSStation.STATION_NEW);test=null;
    if(ok){count++;example=tile;}
   }
   GSLog.Info("P3_COAST|"+i+"|"+GSIndustryType.GetName(type)+"|"+produces+"|"+accepts+"|"+GSIndustry.HasDock(i)+"|"+count+"|"+example);
  }
  GSLog.Info("P3_DONE");while(true)Sleep(10000);
 }
}
