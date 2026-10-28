// A single real AXIS coal-delivery fixture on a disposable generated map.
class RouteProbe extends GSController {
 function Fail(s){GSLog.Info("ROUTE_BLOCKED|"+s+"|"+GSError.GetLastErrorString());}
 function Start(){
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(5);
  GSCompany.ChangeBankBalance(0,100000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
  local origin=GSMap.GetTileIndex(24,24),goal=GSMap.GetTileIndex(56,24);
  {
   local mode=GSCompanyMode(0);
   GSCompany.SetLoanAmount(0);
   if(!GSTile.LevelTiles(GSMap.GetTileIndex(20,20),GSMap.GetTileIndex(72,34))){Fail("flat fixture terraform");return;}
   mode=null;
  }
  GSLog.Info("ROUTE_MODE|"+GSCompanyMode.IsDeity());
  GSLog.Info("ROUTE_DENSITY|"+GSGameSettings.GetValue("difficulty.industry_density"));
  local producers=GSIndustryTypeList(),producer=-1,consumer=-1;
  foreach(t,v in producers){
   local output=GSIndustryType.GetProducedCargo(t);
   if(output.HasItem(14))GSLog.Info("ROUTE_COAL_TYPE|"+t+"|"+GSIndustryType.GetName(t)+"|"+GSIndustryType.CanBuildIndustry(t));
   if(!GSIndustryType.CanBuildIndustry(t))continue;
   if(producer<0 && output.HasItem(14) && GSIndustryType.BuildIndustry(t,origin)){producer=t;GSLog.Info("ROUTE_PRODUCER|"+t+"|"+GSIndustryType.GetName(t));}
  }
  if(producer<0){Fail("no AXIS coal producer could be constructed at fixture origin");return;}
  foreach(t,v in producers){
   if(!GSIndustryType.CanBuildIndustry(t))continue;
   local input=GSIndustryType.GetAcceptedCargo(t);
   if(consumer<0 && input.HasItem(14) && GSIndustryType.BuildIndustry(t,goal)){consumer=t;GSLog.Info("ROUTE_CONSUMER|"+t+"|"+GSIndustryType.GetName(t));}
  }
  if(consumer<0){Fail("no AXIS coal-accepting industry could be constructed at destination");return;}
  {
   local mode=GSCompanyMode(0),acc=GSAccounting();
   GSRail.SetCurrentRailType(GSEngine.GetRailType(ROUTE_ENGINE));
   local a=GSMap.GetTileIndex(25,30),b=GSMap.GetTileIndex(57,30),depot=GSMap.GetTileIndex(22,30);
   if(!GSRail.BuildRailStation(a,GSRail.RAILTRACK_NE_SW,1,2,GSStation.STATION_NEW)){Fail("origin station");return;}
   if(!GSRail.BuildRailStation(b,GSRail.RAILTRACK_NE_SW,1,2,GSStation.STATION_NEW)){Fail("destination station");return;}
   if(!GSRail.BuildRailDepot(depot,GSMap.GetTileIndex(23,30))){Fail("route depot");return;}
   for(local x=23;x<=59;x++){
    if(x==25 || x==26 || x==57 || x==58)continue;
    if(!GSRail.BuildRailTrack(GSMap.GetTileIndex(x,30),GSRail.RAILTRACK_NE_SW)){Fail("route track at x="+x);return;}
   }
   local v=GSVehicle.BuildVehicle(depot,ROUTE_ENGINE);
   if(!GSVehicle.IsValidVehicle(v)){Fail("locomotive");return;}
   local wagon=1430;
   if(!GSEngine.IsBuildable(wagon)){
    wagon=-1;for(local i=0;i<16000;i++)if(wagon<0 && GSEngine.IsValidEngine(i) && GSEngine.GetVehicleType(i)==GSVehicle.VT_RAIL && GSEngine.IsWagon(i) && GSEngine.IsBuildable(i) && GSEngine.CanRefitCargo(i,14))wagon=i;
   }
   if(wagon<0){Fail("no available coal wagon");return;}
   for(local j=0;j<4;j++){
    local w=GSVehicle.BuildVehicleWithRefit(depot,wagon,14);
    if(!GSVehicle.IsValidVehicle(w) || !GSVehicle.MoveWagon(w,0,v,GSVehicle.GetNumWagons(v)-1)){Fail("coal refit/attachment");return;}
   }
   if(!GSOrder.AppendOrder(v,a,GSOrder.OF_FULL_LOAD_ANY) || !GSOrder.AppendOrder(v,b,GSOrder.OF_UNLOAD|GSOrder.OF_NO_LOAD)){Fail("station orders");return;}
   local capital=acc.GetCosts(),bank=GSCompany.GetBankBalance(0),begin=GSDate.GetCurrentDate(),loaded_seen=0,max_waiting=0;
   local start_income=0;
   for(local q=0;q<4;q++)start_income+=GSCompany.GetQuarterlyIncome(0,q);
   if(!GSVehicle.StartStopVehicle(v)){Fail("train start");return;}
   while(GSDate.GetYear(GSDate.GetCurrentDate())==GSDate.GetYear(begin)){
    loaded_seen=max(loaded_seen,GSVehicle.GetCargoLoad(v,14));
    max_waiting=max(max_waiting,GSStation.GetCargoWaiting(GSStation.GetStationID(a),14));
    Sleep(20);
   }
   local revenue=0;for(local q=1;q<=4;q++)revenue+=GSCompany.GetQuarterlyIncome(0,q);
   GSLog.Info("ROUTE_OBSERVED|"+ROUTE_ENGINE+"|"+begin+"|"+GSDate.GetCurrentDate()+"|"+capital+"|"+(GSCompany.GetBankBalance(0)-bank)+"|"+GSVehicle.GetProfitLastYear(v)+"|"+revenue+"|"+GSVehicle.GetCapacity(v,14)+"|"+loaded_seen+"|"+max_waiting+"|"+GSVehicle.GetLocation(v));
  }
  while(true)Sleep(10000);
 }
}
