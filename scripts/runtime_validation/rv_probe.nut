// Runtime-validation measurement GameScript. Runs only on generated disposable fixtures.
// rv.py prepends:  CONFIG <- {...};
// Modes:
//   "catalogue" : log engine catalogue (price / running cost) for CONFIG.engines, then done.
//               With CONFIG.watch_months>0 keeps logging the catalogue monthly (date test).
//   "route"     : build a coal service (producer -> consumer) of CONFIG.distance tiles,
//               run CONFIG.years full years after commissioning, log ledgers, deliveries,
//               speed and GetRunningCost sampled by vehicle state.
// All output lines start with "RV_" and are pipe-separated.

class RVProbe extends GSController {
 coal = -1;
 function L(s){GSLog.Info("RV_"+s);}
 function Fail(s){L("BLOCKED|"+s+"|"+GSError.GetLastErrorString());L("DONE|blocked");while(true)Sleep(10000);}
 function Cfg(k,d){return (k in CONFIG)?CONFIG[k]:d;}

 function Catalogue(tag){
  foreach(id in CONFIG.engines){
   if(!GSEngine.IsValidEngine(id)){L("ENGINE|"+tag+"|"+id+"|invalid");continue;}
   local rail=GSEngine.GetVehicleType(id)==GSVehicle.VT_RAIL;
   L("ENGINE|"+tag+"|"+id+"|"+GSEngine.GetName(id)+"|"+GSEngine.GetPrice(id)+"|"+GSEngine.GetRunningCost(id)
     +"|"+(rail?GSEngine.GetPower(id):-1)+"|"+(rail?GSEngine.GetMaxTractiveEffort(id):-1)+"|"+(rail?GSEngine.GetWeight(id):-1)
     +"|"+GSEngine.GetMaxSpeed(id)+"|"+GSEngine.IsWagon(id)+"|"+GSEngine.GetDesignDate(id)+"|"+GSEngine.GetCapacity(id)+"|"+Buildable(id));
  }
 }

 function Buildable(id){if(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)return "nc";local m=GSCompanyMode(0);return GSEngine.IsBuildable(id);}
 function Settings(){
  foreach(key in ["difficulty.vehicle_costs","difficulty.vehicle_costs_in_depot","difficulty.vehicle_costs_when_stopped",
                  "economy.inflation","economy.timekeeping_units","economy.minutes_per_calendar_year","economy.day_length_factor",
                  "vehicle.train_acceleration_model","vehicle.train_slope_steepness","vehicle.max_train_length","vehicle.freight_trains",
                  "difficulty.vehicle_breakdowns","economy.infrastructure_maintenance","difficulty.subsidy_multiplier","difficulty.subsidy_duration"])
   L("SETTING|"+key+"|"+(GSGameSettings.IsValid(key)?GSGameSettings.GetValue(key):"n/a"));
 }

 function ResolveCoal(){
  foreach(c,v in GSCargoList())if(GSCargo.GetCargoLabel(c)=="COAL")return c;
  return -1;
 }

 function Start(){
  L("BEGIN|"+GSDate.GetCurrentDate()+"|"+GSDate.GetYear(GSDate.GetCurrentDate())+"|"+CONFIG.mode);
  Settings();
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(5);
  Catalogue("start");
  if(CONFIG.mode=="catalogue"){
   if(Cfg("income",false)){
    foreach(c,v in GSCargoList()){
     local lab=GSCargo.GetCargoLabel(c);
     if(lab!="COAL" && lab!="COKE" && lab!="PASS" && lab!="GOOD")continue;
     foreach(d in [16,26,32,64,128])foreach(days in [0,5,10,20,40,80])L("INCOME|"+lab+"|"+d+"|"+days+"|"+GSCargo.GetCargoIncome(c,d,days));
    }
   }
   local months=Cfg("watch_months",0),m=GSDate.GetMonth(GSDate.GetCurrentDate()),seen=0;
   while(seen<months){
    Sleep(20);
    local now=GSDate.GetMonth(GSDate.GetCurrentDate());
    if(now!=m){m=now;seen++;L("DATE|"+GSDate.GetCurrentDate()+"|"+GSDate.GetYear(GSDate.GetCurrentDate()));Catalogue("m"+seen);}
   }
   L("DONE|catalogue");while(true)Sleep(10000);
  }
  Route();
 }

 // Find the corridor: row y with flat (or heightmap-ramp) ground along x.
 function Clearable(t){return GSTile.IsBuildable(t)||GSTile.HasTreeOnTile(t)||GSTile.IsRockTile(t)||GSTile.IsRoughTile(t);}
 function Height(x,y){return GSTile.GetMinHeight(GSMap.GetTileIndex(x,y));}

 function Route(){
  coal=ResolveCoal();if(coal<0)Fail("no COAL cargo");
  GSCompany.ChangeBankBalance(0,200000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
  local D=CONFIG.distance,x=CONFIG.x0,y=-1,bx=x+D;
  // First row (from y0) whose corridor and industry band are entirely clear and buildable.
  for(local yy=CONFIG.y0;yy<240 && y<0;yy+=3){
   local ok=true;
   for(local xx=x-5;xx<=bx+10 && ok;xx++)for(local dy=-11;dy<=3 && ok;dy++)if(!Clearable(GSMap.GetTileIndex(xx,yy+dy)))ok=false;
   if(ok)y=yy;
  }
  if(y<0){local pr="";for(local xx=x-5;xx<=bx+10;xx++){local t=GSMap.GetTileIndex(xx,CONFIG.y0+20);pr+=Height(xx,CONFIG.y0+20)+(GSTile.IsBuildable(t)?"":"*w"+GSTile.IsWaterTile(t)+"o"+GSTile.GetOwner(t)+"tr"+GSTile.HasTreeOnTile(t)+"tn"+GSTile.IsWithinTownInfluence(t,GSTile.GetClosestTown(t))+"sl"+GSTile.GetSlope(t)+"rd"+GSRoad.IsRoadTile(t))+",";}L("PROFILE_FAIL|"+pr);Fail("no clear corridor");}
  local cleared=0;
  for(local xx=x-5;xx<=bx+10;xx++)for(local dy=-11;dy<=3;dy++){local t=GSMap.GetTileIndex(xx,y+dy);if(!GSTile.IsBuildable(t)){if(!GSTile.DemolishTile(t))Fail("clear "+xx+","+(y+dy));cleared++;}}
  L("CORRIDOR|"+x+"|"+y+"|"+bx+"|cleared "+cleared);
  local prof="";for(local xx=x-4;xx<=bx+9;xx++)prof+=Height(xx,y)+",";
  L("PROFILE|x|"+prof);
  local prof2="";for(local yy=y-4;yy<=y+D+9;yy++)prof2+=Height(x,yy)+",";
  L("PROFILE|y|"+prof2);

  // Industries (built as deity; capital outside the transport company).
  local ptype=-1,ctype=-1,crank=9;
  foreach(t,v in GSIndustryTypeList()){
   local prod=GSIndustryType.GetProducedCargo(t),acc=GSIndustryType.GetAcceptedCargo(t);
   L("INDTYPE|"+t+"|"+GSIndustryType.GetName(t)+"|"+GSIndustryType.CanBuildIndustry(t)+"|"+prod.HasItem(coal)+"|"+acc.HasItem(coal)+"|"+prod.Count());
   if(!GSIndustryType.CanBuildIndustry(t))continue;
   if(prod.HasItem(coal) && prod.Count()==1 && ptype<0)ptype=t;
   if(acc.HasItem(coal)){
    local n=GSIndustryType.GetName(t),rank=(n.find("Coke")!=null)?0:((n.find("Power")!=null)?1:2);
    if(ctype<0 || rank<crank){ctype=t;crank=rank;}
   }
  }
  if(ptype<0||ctype<0)Fail("coal industry types");
  L("INDUSTRY_TYPES|"+ptype+"|"+GSIndustryType.GetName(ptype)+"|"+ctype+"|"+GSIndustryType.GetName(ctype));
  local a=GSMap.GetTileIndex(x,y),b=GSMap.GetTileIndex(bx,y);
  BuildLine(x,y,bx,a,b);
  local built=[false,false];
  foreach(i,pair in [[ptype,x,true],[ctype,bx,false]]){
   for(local dy=-4;dy>=-9 && !built[i];dy--)for(local dx=-2;dx<=6 && !built[i];dx++){
    local t=GSMap.GetTileIndex(pair[1]+dx,y+dy);
    if(GSIndustryType.BuildIndustry(pair[0],t)){built[i]=true;L("INDUSTRY_BUILT|"+pair[0]+"|"+t+"|"+dx+"|"+dy);}
   }
  }
  if(!built[0]||!built[1])Fail("industry placement");
  local level=Cfg("production_level",16);
  foreach(i,v in GSIndustryList()){
   GSIndustry.SetControlFlags(i,GSIndustry.INDCTL_NO_PRODUCTION_INCREASE|GSIndustry.INDCTL_NO_PRODUCTION_DECREASE);
   L("PRODUCTION_LEVEL|"+i+"|"+GSIndustry.GetIndustryType(i)+"|"+GSIndustry.SetProductionLevel(i,level,false,null));
  }

  local mode=GSCompanyMode(0);
  L("AUTORENEW|"+GSCompany.GetAutoRenewStatus(0)+"|"+GSCompany.SetAutoRenewStatus(false)+"|"+GSCompany.GetAutoRenewStatus(0));
  local eng=CONFIG.engine,wag=CONFIG.wagon,depot=GSMap.GetTileIndex(x-3,y);
  local infra=GSAccounting();
  local infrastructure=line_cost;
  local prodA=GSTile.GetCargoProduction(a,coal,7,1,4),accB=GSTile.GetCargoAcceptance(b,coal,7,1,4);
  L("CATCHMENT|"+prodA+"|"+accB);
  if(prodA<1||accB<8)Fail("catchment");

  // Consist: engine + N wagons refitted to coal, or fill to the 7-tile limit when wagons<0.
  local v=BuildConsist(depot,eng,wag,CONFIG.wagons);
  local purchase=infra.GetCosts();infra.ResetCosts();
  if(!GSOrder.AppendOrder(v,a,GSOrder.OF_FULL_LOAD_ANY) || !GSOrder.AppendOrder(v,b,GSOrder.OF_UNLOAD|GSOrder.OF_NO_LOAD))Fail("orders");
  local twin=-1;
  if(Cfg("twin",false)){twin=BuildConsist(depot,eng,wag,CONFIG.wagons);infra.ResetCosts();}
  local sa=GSStation.GetStationID(a),sb=GSStation.GetStationID(b);
  L("MAX_AGE|"+GSEngine.GetMaxAge(eng)+"|"+GSVehicle.GetMaxAge(v));
  L("BUILD|"+v+"|"+purchase+"|"+infrastructure+"|"+GSVehicle.GetCapacity(v,coal)+"|"+GSVehicle.GetLength(v)+"|"+GSVehicle.GetNumWagons(v)+"|"+sa+"|"+sb+"|"+twin+"|"+GSVehicle.GetRunningCost(v));
  L("EXPENSE_IDS|"+GSCompany.EXPENSES_TRAIN_RUN+"|"+GSCompany.EXPENSES_PROPERTY+"|"+GSCompany.EXPENSES_OTHER+"|"+GSCompany.EXPENSES_NEW_VEHICLES+"|"+GSCompany.EXPENSES_CONSTRUCTION);
  for(local e=0;e<15;e++)L("LEDGER_START|"+e+"|"+GSCompany.GetAnnualExpenseValue(0,0,e));
  if(!GSVehicle.StartStopVehicle(v))Fail("start");

  local ramp0=Cfg("ramp_x0",-1),ramp1=Cfg("ramp_x1",-1);
  local year=GSDate.GetYear(GSDate.GetCurrentDate()),end=year+CONFIG.years+1,month=-1;
  local S=NewStats(),last_load=0,arrivals=0;
  while(year<end){
   local sp=GSVehicle.GetCurrentSpeed(v),load=GSVehicle.GetCargoLoad(v,coal),st=GSVehicle.GetState(v);
   local loc=GSVehicle.GetLocation(v),cost=GSVehicle.GetRunningCost(v),here=GSStation.GetStationID(loc);
   local cls="other_stopped";
   if(GSVehicle.IsInDepot(v))cls="depot";
   else if(sp>0)cls=(load>0)?"moving_loaded":"moving_empty";
   else if(st==GSVehicle.VS_AT_STATION)cls=(here==sa)?((load>0)?"platform_loading_part":"platform_loading_empty"):"platform_unloading";
   Acc(S,cls,cost,sp,load);
   if(load>0 && sp>0 && ramp0>=0){local tx=GSMap.GetTileX(loc);if(tx>=ramp0 && tx<=ramp1){S.ramp_n++;S.ramp_speed+=sp;if(sp<S.ramp_min)S.ramp_min=sp;}}
   if(here==sb && load<last_load)S.unloaded+=last_load-load;
   if(here==sb && last_load>0 && load==0)arrivals++;
   last_load=load;
   if(twin>=0){local tc=GSVehicle.GetRunningCost(twin);if(tc<S.twin_min)S.twin_min=tc;if(tc>S.twin_max)S.twin_max=tc;}
   if(GSDate.GetMonth(GSDate.GetCurrentDate())!=month){
    month=GSDate.GetMonth(GSDate.GetCurrentDate());
    local supply=0;foreach(i,vv in GSIndustryList())supply+=GSIndustry.GetLastMonthProduction(i,coal);
    L("MONTH|"+GSDate.GetCurrentDate()+"|"+supply+"|"+GSStation.GetCargoWaiting(sa,coal)+"|"+GSStation.GetCargoRating(sa,coal)+"|"+load+"|"+sp+"|"+cls+"|"+cost+"|"+GSVehicle.GetAge(v)+"|"+GSVehicle.GetReliability(v)
      +"|"+(twin>=0?GSVehicle.GetRunningCost(twin):-1)+"|"+GSEngine.GetRunningCost(eng));
   }
   if(GSDate.GetYear(GSDate.GetCurrentDate())!=year){
    Sleep(74);
    local delivered=0;for(local q=1;q<=4;q++)delivered+=GSCompany.GetQuarterlyCargoDelivered(0,q);
    local ledger="";for(local e=0;e<15;e++)ledger+=GSCompany.GetAnnualExpenseValue(0,1,e)+",";
    local subs=0;foreach(sid,vv in GSSubsidyList())if(GSSubsidy.IsAwarded(sid))subs++;
    L("SUBSIDIES_AWARDED|"+year+"|"+subs);
    L("YEAR|"+year+"|"+delivered+"|"+S.unloaded+"|"+arrivals+"|"+GSVehicle.GetProfitLastYear(v)+"|"+ledger+"|"+GSVehicle.GetAge(v)+"|"+GSVehicle.GetReliability(v)
      +"|"+S.ramp_n+"|"+S.ramp_speed+"|"+(S.ramp_min==99999?-1:S.ramp_min)+"|"+(twin>=0?S.twin_min:-1)+"|"+(twin>=0?S.twin_max:-1)+"|"+(twin>=0?GSVehicle.GetAge(twin):-1));
    foreach(k,c in S.cls)L("STATE|"+year+"|"+k+"|"+c.n+"|"+c.cost+"|"+c.cmin+"|"+c.cmax+"|"+c.speed+"|"+c.load);
    year=GSDate.GetYear(GSDate.GetCurrentDate());S=NewStats();arrivals=0;
   }
   Sleep(5);
  }
  L("DONE|finished");while(true)Sleep(10000);
 }

 line_cost = 0;
 function BuildLine(x,y,bx,a,b){
  local mode=GSCompanyMode(0);
  GSCompany.SetLoanAmount(0);
  local eng=CONFIG.engine,wag=CONFIG.wagon;
  if(!GSEngine.IsBuildable(eng))Fail("engine "+eng+" not buildable");
  if(!GSEngine.IsBuildable(wag))Fail("wagon "+wag+" not buildable");
  GSRail.SetCurrentRailType(GSEngine.GetRailType(eng));
  local depot=GSMap.GetTileIndex(x-3,y);
  local acc=GSAccounting();
  if(!GSRail.BuildRailStation(a,GSRail.RAILTRACK_NE_SW,1,7,GSStation.STATION_NEW))Fail("origin station");
  if(!GSRail.BuildRailStation(b,GSRail.RAILTRACK_NE_SW,1,7,GSStation.STATION_NEW))Fail("destination station");
  if(!GSRail.BuildRailDepot(depot,GSMap.GetTileIndex(x-2,y)))Fail("depot");
  for(local xx=x-2;xx<=bx+7;xx++){
   if(xx>=x && xx<x+7 || xx>=bx && xx<bx+7)continue;
   if(!GSRail.BuildRailTrack(GSMap.GetTileIndex(xx,y),GSRail.RAILTRACK_NE_SW))Fail("track "+xx);
  }
  line_cost=acc.GetCosts();
 }

 function BuildConsist(depot,eng,wag,n){
  local v=GSVehicle.BuildVehicle(depot,eng);
  if(!GSVehicle.IsValidVehicle(v))Fail("engine build");
  local limit=GSGameSettings.GetValue("vehicle.max_train_length")*16;
  local count=0;
  while(n<0 || count<n){
   local w=GSVehicle.BuildVehicleWithRefit(depot,wag,coal);
   if(!GSVehicle.IsValidVehicle(w))Fail("wagon build");
   if(!GSVehicle.MoveWagon(w,0,v,GSVehicle.GetNumWagons(v)-1)){GSVehicle.SellVehicle(w);if(n<0)break;Fail("wagon attach");}
   if(n<0 && GSVehicle.GetLength(v)>limit){GSVehicle.SellWagon(v,GSVehicle.GetNumWagons(v)-1);break;}
   count++;
  }
  return v;
 }
 function NewStats(){return {cls={},unloaded=0,ramp_n=0,ramp_speed=0,ramp_min=99999,twin_min=999999999,twin_max=-1};}
 function Acc(S,k,cost,sp,load){
  if(!(k in S.cls))S.cls[k]<-{n=0,cost=0,cmin=999999999,cmax=-1,speed=0,load=0};
  local c=S.cls[k];c.n++;c.cost+=cost;if(cost<c.cmin)c.cmin=cost;if(cost>c.cmax)c.cmax=cost;c.speed+=sp;c.load+=load;
 }
}
