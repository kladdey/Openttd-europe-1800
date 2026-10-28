require("cases.nut");
class Phase2Probe extends GSController {
 function Error(){return GSError.GetLastErrorString();}
 function MoveEmpty(v){
  local peak=-1,speed=-1;
  if(!GSVehicle.StartStopVehicle(v)){GSLog.Info("P2_MOTION_ERROR|"+v+"|"+Error());return [-1,-1,GSVehicle.IsStoppedInDepot(v)];}
  for(local i=0;i<100;i++){
   Sleep(4);
   if(GSVehicle.GetCurrentSpeed(v)>0){speed=max(speed,GSVehicle.GetCurrentSpeed(v));peak=max(peak,GSVehicle.GetRunningCost(v));}
  }
  GSVehicle.SendVehicleToDepot(v);
  for(local i=0;i<500 && !GSVehicle.IsStoppedInDepot(v);i++)Sleep(4);
  return [peak,speed,GSVehicle.IsStoppedInDepot(v)];
 }
 function Start(){
  GSLog.Info("P2_BEGIN|"+GSDate.GetCurrentDate());
  foreach(key in ["difficulty.vehicle_costs","difficulty.construction_cost","economy.inflation","economy.day_length_factor","economy.timekeeping_units","vehicle.freight_trains","vehicle.train_slope_steepness","economy.infrastructure_maintenance"])
   GSLog.Info("P2_SETTING|"+key+"|"+GSGameSettings.GetValue(key));
  local ids=[];
  for(local id=0;id<16000;id++){
   if(!GSEngine.IsValidEngine(id))continue;
   local t=GSEngine.GetVehicleType(id);
   if(t!=GSVehicle.VT_RAIL && t!=GSVehicle.VT_WATER)continue;
   ids.append(id);
   local rail=-1,art=false;
   if(t==GSVehicle.VT_RAIL){rail=GSEngine.GetRailType(id);art=GSEngine.IsArticulated(id);}
   local hp=-1,te=-1,weight=-1;
   if(t==GSVehicle.VT_RAIL){hp=GSEngine.GetPower(id);te=GSEngine.GetMaxTractiveEffort(id);weight=GSEngine.GetWeight(id);}
   GSLog.Info("P2_ENGINE|"+id+"|"+GSEngine.GetPrice(id)+"|"+GSEngine.GetRunningCost(id)+"|"+GSEngine.GetMaxAge(id)+"|"+GSEngine.GetCargoType(id)+"|"+rail+"|"+art+"|"+GSEngine.GetCapacity(id)+"|"+GSEngine.GetReliability(id)+"|"+hp+"|"+te+"|"+weight+"|"+GSEngine.GetMaxSpeed(id)+"|"+GSEngine.GetDesignDate(id));
  }
  for(local c=0;c<64;c++){
   if(!GSCargo.IsValidCargo(c))continue;
   GSLog.Info("P2_CARGO|"+c+"|"+GSCargo.GetCargoLabel(c)+"|"+GSCargo.GetWeight(c,1000));
   foreach(d in [32,64,128,256,512,1024])foreach(days in [0,5,10,20,40,80,160,320,640])
    GSLog.Info("P2_PAYMENT|"+c+"|"+d+"|"+days+"|"+GSCargo.GetCargoIncome(c,d,days));
  }
  local waited=0;
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID && waited<100){Sleep(10);waited++;}
  if(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID){GSLog.Info("P2_BLOCKER|no test company");return;}
  GSCompany.ChangeBankBalance(0,100000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
  {
   local mode=GSCompanyMode(0);
   foreach(id in ids)GSLog.Info("P2_AVAILABLE|"+id+"|"+GSEngine.IsBuildable(id));
   foreach(g,group in SET_GROUPS){
    local freight=-1,express=-1,unit=-1;
    foreach(id in group){
     if(!GSEngine.IsBuildable(id) || GSEngine.IsWagon(id) || GSEngine.GetPower(id)<=1)continue;
     if(GSEngine.GetCapacity(id)>0){if(unit<0 || GSEngine.GetCapacity(id)>GSEngine.GetCapacity(unit))unit=id;}
     else{
      if(GSEngine.GetMaxSpeed(id)<=140 && (freight<0 || GSEngine.GetPower(id)>GSEngine.GetPower(freight)))freight=id;
      if(express<0 || GSEngine.GetMaxSpeed(id)>GSEngine.GetMaxSpeed(express))express=id;
     }
    }
    if(freight>=0)TEST_CASES.append({key="auto_heavy_"+g,engine=freight,wagon=-2,n=12,cargo=14});
    if(express>=0)TEST_CASES.append({key="auto_express_"+g,engine=express,wagon=-2,n=8,cargo=0});
    if(unit>=0)TEST_CASES.append({key="auto_unit_"+g,engine=unit,wagon=-1,n=0,cargo=0});
   }
   local depots={};
   foreach(test in TEST_CASES){
    local key=test.key,engine=test.engine,wagon=test.wagon,cargo=test.cargo,n=test.n;
    if(!GSEngine.IsBuildable(engine)){GSLog.Info("P2_TRAIN_BLOCKED|"+key+"|locomotive unavailable");continue;}
    if(wagon==-2 || wagon>=0 && !GSEngine.IsBuildable(wagon)){
     wagon=-2;
     foreach(w in WAGON_CANDIDATES){
      if(GSEngine.IsBuildable(w) && GSEngine.CanRefitCargo(w,cargo) && GSEngine.CanRunOnRail(w,GSEngine.GetRailType(engine))){wagon=w;break;}
     }
     if(wagon==-2){GSLog.Info("P2_TRAIN_BLOCKED|"+key+"|no available compatible cargo wagon");continue;}
    }
    local rail=GSEngine.GetRailType(engine),depot=-1;
    if(rail in depots)depot=depots[rail];
    else{
     GSRail.SetCurrentRailType(rail);
     for(local x=4;x<120 && depot<0;x+=3)for(local y=4;y<120 && depot<0;y+=3){
      local tile=GSMap.GetTileIndex(x,y),front=GSMap.GetTileIndex(x+1,y);
      if(!GSTile.IsBuildable(tile) || GSTile.GetSlope(tile)!=GSTile.SLOPE_FLAT)continue;
      if(GSRail.BuildRailDepot(tile,front))depot=tile;
     }
     if(depot>=0){
      depots[rail]<-depot;
      local acc=GSAccounting(),x=GSMap.GetTileX(depot),y=GSMap.GetTileY(depot);
      for(local dx=1;dx<=32;dx++){
       local tile=GSMap.GetTileIndex(x+dx,y);
       if(GSTile.IsBuildable(tile))GSRail.BuildRailTrack(tile,GSRail.RAILTRACK_NE_SW);
      }
      GSLog.Info("P2_TRACK|"+rail+"|"+acc.GetCosts());
     }
    }
    if(depot<0){GSLog.Info("P2_TRAIN_BLOCKED|"+key+"|no depot: "+Error());continue;}
    local accounting=GSAccounting();
    accounting.ResetCosts();
    local v=GSVehicle.BuildVehicle(depot,engine);
    if(!GSVehicle.IsValidVehicle(v)){GSLog.Info("P2_TRAIN_BLOCKED|"+key+"|engine build: "+Error());continue;}
    local parts=0,failed=false;
    for(local j=0;j<n && wagon>=0;j++){
     local wcargo=key.find("mixed")!=null ? [14,5,32,29][j%4] : cargo;
     local w=GSVehicle.BuildVehicleWithRefit(depot,wagon,wcargo);
     if(!GSVehicle.IsValidVehicle(w)){GSLog.Info("P2_TRAIN_BLOCKED|"+key+"|wagon build/refit: "+Error());failed=true;break;}
     if(!GSVehicle.MoveWagon(w,0,v,GSVehicle.GetNumWagons(v)-1)){GSLog.Info("P2_TRAIN_BLOCKED|"+key+"|attachment: "+Error());GSVehicle.SellVehicle(w);failed=true;break;}
     parts++;
    }
    if(wagon<0 && cargo>=0 && GSEngine.CanRefitCargo(engine,cargo)){
     if(!GSVehicle.RefitVehicle(v,cargo)){GSLog.Info("P2_TRAIN_BLOCKED|"+key+"|unit refit: "+Error());failed=true;}
    }
    local price=accounting.GetCosts(),capacity=GSVehicle.GetCapacity(v,cargo),running=GSVehicle.GetRunningCost(v);
    GSLog.Info("P2_TRAIN|"+key+"|"+v+"|"+engine+"|"+wagon+"|"+parts+"|"+cargo+"|"+price+"|"+running+"|"+capacity+"|"+GSVehicle.GetLength(v)+"|"+GSVehicle.GetNumWagons(v)+"|"+failed);
    for(local c=0;c<64;c++)if(GSCargo.IsValidCargo(c) && GSVehicle.GetCapacity(v,c)>0)GSLog.Info("P2_TRAIN_CAP|"+key+"|"+c+"|"+GSVehicle.GetCapacity(v,c));
    if(!failed && (key.find("auto_")==0 || key.find("_4_")!=null || key.slice(key.len()-2)=="_4" || key.slice(key.len()-3)=="_12" || key.find("mixed")!=null || wagon<0)){
     local motion=MoveEmpty(v);
     GSLog.Info("P2_TRAIN_MOTION|"+key+"|"+motion[0]+"|"+motion[1]+"|"+motion[2]);
    }
    if(GSVehicle.IsStoppedInDepot(v))GSVehicle.SellVehicle(v);
   }
   foreach(rail,depot in depots)GSLog.Info("P2_INFRA|"+rail+"|"+GSRail.GetBuildCost(rail,GSRail.BT_TRACK)+"|"+GSRail.GetBuildCost(rail,GSRail.BT_DEPOT)+"|"+GSRail.GetBuildCost(rail,GSRail.BT_STATION)+"|"+GSInfrastructure.GetMonthlyRailCosts(0,rail));
   // Solo-engine context calibration. Trains are empty; this is not a
   // loaded-route profitability test. All construction is on the test map.
   foreach(engine in CALIBRATION_ENGINES){
    if(!GSEngine.IsBuildable(engine))continue;
    local rail=GSEngine.GetRailType(engine);
    if(!(rail in depots))continue;
    local depot=depots[rail],x=GSMap.GetTileX(depot),y=GSMap.GetTileY(depot);
    GSRail.SetCurrentRailType(rail);
    local acc=GSAccounting();
    for(local dx=1;dx<=32;dx++){
     local tile=GSMap.GetTileIndex(x+dx,y);
     if(GSTile.IsBuildable(tile))GSRail.BuildRailTrack(tile,GSRail.RAILTRACK_NE_SW);
    }
    local trackcost=acc.GetCosts();
    acc.ResetCosts();local v=GSVehicle.BuildVehicle(depot,engine);
    if(!GSVehicle.IsValidVehicle(v))continue;
    local build=acc.GetCosts(),idle=GSVehicle.GetRunningCost(v),moving=-1,speed=-1;
    GSVehicle.StartStopVehicle(v);
    for(local i=0;i<100;i++){
     Sleep(4);
     if(GSVehicle.GetCurrentSpeed(v)>0){speed=max(speed,GSVehicle.GetCurrentSpeed(v));moving=max(moving,GSVehicle.GetRunningCost(v));}
     if(speed>=GSEngine.GetMaxSpeed(engine))break;
    }
    local stopped=-1;
    local outside=false;
    if(GSVehicle.GetCurrentSpeed(v)>0){
     GSVehicle.StartStopVehicle(v);
     for(local i=0;i<200 && GSVehicle.GetCurrentSpeed(v)>0;i++)Sleep(2);
     outside=GSVehicle.GetLocation(v)!=depot;
     stopped=GSVehicle.GetRunningCost(v);GSVehicle.StartStopVehicle(v);
    }
    GSVehicle.SendVehicleToDepot(v);
    for(local i=0;i<500 && !GSVehicle.IsStoppedInDepot(v);i++)Sleep(4);
    GSLog.Info("P2_CONTEXT|"+engine+"|"+build+"|"+idle+"|"+moving+"|"+stopped+"|"+speed+"|"+trackcost+"|"+GSVehicle.IsStoppedInDepot(v)+"|"+outside);
    if(GSVehicle.IsStoppedInDepot(v))GSVehicle.SellVehicle(v);
   }
   foreach(rail,depot in depots)GSLog.Info("P2_INFRA_FINAL|"+rail+"|"+GSInfrastructure.GetRailPieceCount(0,rail)+"|"+GSInfrastructure.GetMonthlyRailCosts(0,rail));
  }
  GSLog.Info("P2_DONE|"+GSDate.GetCurrentDate());
  while(true)Sleep(10000);
 }
}
