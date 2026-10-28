// All services operate solely on a disposable copy of the Europe scenario.
class TransportProbe extends GSController {
 origin_tile=-1;
 function Tile(x,y){return GSMap.GetTileIndex(x,y);}
 function Fail(s){GSLog.Info("P3_BLOCKED|"+CASE+"|"+s+"|"+GSError.GetLastErrorString());}
 function Step(t,dx,dy){return Tile(GSMap.GetTileX(t)+dx,GSMap.GetTileY(t)+dy);}
 function DockWater(t){foreach(d in [[1,0],[-1,0],[0,1],[0,-1]]){local n=Step(t,d[0],d[1]);if(GSMarine.IsDockTile(n))return Step(n,d[0],d[1]);}return t;}
 function WaterComponent(start,goal){
  local queue=[start],seen={},pos=0;seen[start]<-true;
  while(pos<queue.len() && pos<100000){local t=queue[pos++];
   foreach(d in [[1,0],[-1,0],[0,1],[0,-1]]){local n=Step(t,d[0],d[1]);if(n in seen || GSMap.DistanceManhattan(start,n)>200)continue;
    if(GSMarine.AreWaterTilesConnected(t,n)){seen[n]<-true;queue.append(n);}
   }
  }
  GSLog.Info("P3_WATER|"+start+"|"+goal+"|"+seen.len()+"|"+(goal in seen));return seen;
 }
 function Link(prev,cur,next){
  if(MODE=="road" && (GSMap.DistanceManhattan(cur,next)>1 || GSMap.DistanceManhattan(prev,cur)>1)){
   local px=GSMap.GetTileX(prev)-GSMap.GetTileX(cur),py=GSMap.GetTileY(prev)-GSMap.GetTileY(cur),nx=GSMap.GetTileX(next)-GSMap.GetTileX(cur),ny=GSMap.GetTileY(next)-GSMap.GetTileY(cur);
   if(px*ny!=py*nx || px*nx+py*ny>=0)return false;
  }
  if(MODE=="road" && GSMap.DistanceManhattan(cur,next)>1){
   if(GSBridge.IsBridgeTile(cur) && GSBridge.GetOtherBridgeEnd(cur)==next)return true;
   if(GSTunnel.IsTunnelTile(cur) && GSTunnel.GetOtherTunnelEnd(cur)==next)return true;
   local test=GSTestMode(),ok=GSBridge.BuildBridge(GSVehicle.VT_ROAD,0,cur,next);test=null;return ok;
  }
  if(MODE=="road" && GSTile.GetSlope(cur)!=GSTile.SLOPE_FLAT && (GSMap.GetTileX(prev)+GSMap.GetTileX(next)!=2*GSMap.GetTileX(cur) || GSMap.GetTileY(prev)+GSMap.GetTileY(next)!=2*GSMap.GetTileY(cur)))return false;
  local test=GSTestMode();
  local ok=MODE=="rail"?GSRail.BuildRail(prev,cur,next):GSRoad.BuildRoad(cur,next);
  if(!ok && GSError.GetLastErrorString()=="ERR_ALREADY_BUILT")ok=true;
  test=null;return ok;
 }
 function Path(start,previous,goal){
  local nodes=[{tile=start,prev=previous,backidx=-1}],seen={},pos=0;
  seen[previous+"_"+start]<-true;
  local xmin=min(GSMap.GetTileX(start),GSMap.GetTileX(goal))-14,xmax=max(GSMap.GetTileX(start),GSMap.GetTileX(goal))+14;
  local ymin=min(GSMap.GetTileY(start),GSMap.GetTileY(goal))-14,ymax=max(GSMap.GetTileY(start),GSMap.GetTileY(goal))+14;
  while(pos<nodes.len() && pos<30000){
   local node=nodes[pos];
   if(node.tile==goal && Link(node.prev,goal,Step(goal,MODE=="rail"?-1:1,0))){local path=[];local i=pos;while(i>=0){path.insert(0,nodes[i].tile);i=nodes[i].backidx;}return path;}
   local adjacent=[];
   foreach(delta in [[1,0],[-1,0],[0,1],[0,-1]]){
    local n=Step(node.tile,delta[0],delta[1]);adjacent.append(n);
    if(MODE=="road" && GSTile.IsWaterTile(n))for(local length=2;length<=12;length++){
     local end=Step(node.tile,delta[0]*length,delta[1]*length);
     if(!GSTile.IsWaterTile(end)){adjacent.append(end);break;}
    }
   }
   if(MODE=="road" && GSRoad.HasRoadType(node.tile,GSRoad.GetCurrentRoadType())){
    if(GSBridge.IsBridgeTile(node.tile))adjacent.append(GSBridge.GetOtherBridgeEnd(node.tile));
    if(GSTunnel.IsTunnelTile(node.tile))adjacent.append(GSTunnel.GetOtherTunnelEnd(node.tile));
   }
   foreach(next in adjacent){
    local x=GSMap.GetTileX(next),y=GSMap.GetTileY(next);
    if(x<xmin || x>xmax || y<ymin || y>ymax || x<1 || y<1)continue;
    local key=node.tile+"_"+next;
    if(MODE=="rail" && GSRail.IsRailStationTile(next))continue;
    if(next==node.prev || key in seen)continue;
    local ancestor=pos,repeated=false;
    while(ancestor>=0){
     if(nodes[ancestor].tile==next){repeated=true;break;}
     ancestor=nodes[ancestor].backidx;
    }
    if(repeated)continue;
    seen[key]<-true;
    if(!Link(node.prev,node.tile,next))continue;
    nodes.append({tile=next,prev=node.tile,backidx=pos});
   }
   pos++;
  }
  GSLog.Info("P3_PATH_FAILURE|"+pos+"|"+nodes.len());return null;
 }
 function Candidates(id,production){
  local list=[];
  if(ENDPOINTS=="industry"){
   local tiles=production?GSTileList_IndustryProducing(id,MODE=="road"?3:4):GSTileList_IndustryAccepting(id,MODE=="road"?3:4);
   foreach(tile,v in tiles)list.append(tile);
  }else{
   local t=GSTown.GetLocation(id),x=GSMap.GetTileX(t),y=GSMap.GetTileY(t);
   for(local dx=-14;dx<=14;dx++)for(local dy=-14;dy<=14;dy++){
    local tile=Tile(x+dx,y+dy);
    if(GSTile.GetCargoAcceptance(tile,CARGO,1,1,MODE=="ship"?4:3)>=8 && GSTile.GetCargoProduction(tile,CARGO,1,1,MODE=="ship"?4:3)>0)list.append(tile);
   }
  }
  local center=ENDPOINTS=="industry"?GSIndustry.GetLocation(id):GSTown.GetLocation(id);
  list.sort(function(a,b):(center){return GSMap.DistanceManhattan(a,center)-GSMap.DistanceManhattan(b,center);});
  return list;
 }
 function Station(id,production){
  foreach(tile in Candidates(id,production)){
   if(!production && origin_tile>=0 && GSMap.DistanceManhattan(tile,origin_tile)<MIN_SEPARATION)continue;
   if(MODE=="ship"){
    if(!GSTile.IsCoastTile(tile))continue;
    local tm=GSTestMode(),ok=GSMarine.BuildDock(tile,GSStation.STATION_NEW);tm=null;
    if(ok && GSMarine.BuildDock(tile,GSStation.STATION_NEW))return tile;
   }else{
    if(!GSTile.IsBuildable(tile) && !(MODE=="road" && GSRoad.IsRoadTile(tile)))continue;
    if(MODE=="road" && !GSTile.IsBuildable(Step(tile,-1,0)) && !GSRoad.IsRoadTile(Step(tile,-1,0)))continue;
    if(MODE=="rail"){
     local clear=true;for(local dx=-2;dx<=PLATFORM+1;dx++)if(!GSTile.IsBuildable(Step(tile,dx,0)))clear=false;
     if(!clear)continue;
    }
    local front=Step(tile,-1,0),tm=GSTestMode();
    local ok=MODE=="rail"?GSRail.BuildRailStation(tile,GSRail.RAILTRACK_NE_SW,1,PLATFORM,GSStation.STATION_NEW):GSRoad.BuildDriveThroughRoadStation(tile,front,CARGO==0?GSRoad.ROADVEHTYPE_BUS:GSRoad.ROADVEHTYPE_TRUCK,GSStation.STATION_NEW);
    tm=null;
    if(!ok)continue;
    if(!production && origin_tile>=0){
     local trial=Path(Step(origin_tile,-1,0),origin_tile,Step(tile,MODE=="rail"?PLATFORM:-1,0));
     if(trial==null)continue;
    }
    ok=MODE=="rail"?GSRail.BuildRailStation(tile,GSRail.RAILTRACK_NE_SW,1,PLATFORM,GSStation.STATION_NEW):GSRoad.BuildDriveThroughRoadStation(tile,front,CARGO==0?GSRoad.ROADVEHTYPE_BUS:GSRoad.ROADVEHTYPE_TRUCK,GSStation.STATION_NEW);
    if(ok)return tile;
   }
  }
  return -1;
 }
 function Start(){
  GSLog.Info("P3_CASE|"+CASE+"|"+MODE+"|"+CARGO+"|"+A+"|"+B+"|"+GSDate.GetCurrentDate());
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(2);
  local mode=GSCompanyMode(0),account=GSAccounting(),initialcash=GSCompany.GetBankBalance(0);
  GSLog.Info("P3_INITIAL|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount()+"|"+GSCompany.GetMaxLoanAmount()+"|"+GSGameSettings.GetValue("economy.infrastructure_maintenance")+"|"+GSGameSettings.GetValue("vehicle.max_train_length"));
  if(MODE=="rail")GSRail.SetCurrentRailType(GSEngine.GetRailType(ENGINE));
  if(MODE=="road")GSRoad.SetCurrentRoadType(GSEngine.GetRoadType(ENGINE));
  local a=Station(A,true);if(a<0){Fail("origin station");return;}
  origin_tile=a;
  local aftera=GSCompany.GetBankBalance(0);GSLog.Info("P3_CAPITAL|"+CASE+"|origin_station|"+(initialcash-aftera));
  local b=Station(B,false);if(b<0){Fail("destination station");return;}
  local afterb=GSCompany.GetBankBalance(0);GSLog.Info("P3_CAPITAL|"+CASE+"|destination_station|"+(aftera-afterb));
  local depot=-1,path=null;
  if(MODE=="ship"){
   local water=WaterComponent(DockWater(a),DockWater(b));if(!(DockWater(b) in water)){Fail("docks not connected within 200-tile water search");return;}
   local x=GSMap.GetTileX(a),y=GSMap.GetTileY(a);
   for(local dx=-14;dx<=14 && depot<0;dx++)for(local dy=-14;dy<=14 && depot<0;dy++){
    local t=Tile(x+dx,y+dy),f=Step(t,1,0);
    if(t in water && f in water && GSTile.IsWaterTile(t) && GSTile.IsWaterTile(f)){
     local tm=GSTestMode(),ok=GSMarine.BuildWaterDepot(t,f);tm=null;
     if(ok && GSMarine.BuildWaterDepot(t,f))depot=t;
    }
   }
  }else{
   local start=Step(a,-1,0),previous=a,goal=MODE=="rail"?Step(b,PLATFORM,0):Step(b,-1,0);
   path=Path(start,previous,goal);if(path==null){Fail("no legal contiguous route");return;}
   local prev=previous;
   for(local i=0;i<path.len();i++){
    local next=i+1<path.len()?path[i+1]:(MODE=="rail"?Step(b,PLATFORM-1,0):b);
    local ok=false;
    if(MODE=="rail")ok=GSRail.BuildRail(prev,path[i],next);
    else if(GSMap.DistanceManhattan(path[i],next)>1){
     if(GSBridge.IsBridgeTile(path[i]) && GSBridge.GetOtherBridgeEnd(path[i])==next)ok=true;
     else if(GSTunnel.IsTunnelTile(path[i]) && GSTunnel.GetOtherTunnelEnd(path[i])==next)ok=true;
     else ok=GSBridge.BuildBridge(GSVehicle.VT_ROAD,0,path[i],next);
    }else ok=GSRoad.BuildRoad(path[i],next);
    if(!ok && GSError.GetLastErrorString()!="ERR_ALREADY_BUILT"){GSLog.Info("P3_COMMIT_FAILURE|"+i+"|"+prev+"|"+path[i]+"|"+next);Fail("commit path");return;}
    prev=path[i];
   }
   if(MODE=="road")GSRoad.BuildRoad(a,Step(a,-1,0));
   if(MODE=="rail"){
    depot=Step(a,PLATFORM+1,0);local f=Step(a,PLATFORM,0);
    if(!GSRail.BuildRailDepot(depot,f) || !GSRail.BuildRailTrack(f,GSRail.RAILTRACK_NE_SW)){Fail("rail depot connection");return;}
   }else{
    foreach(t in path){
     foreach(delta in [[0,1],[0,-1],[1,0],[-1,0]]){
      if(depot>=0)break;
      local d=Step(t,delta[0],delta[1]);if(!GSTile.IsBuildable(d))continue;
      local tm=GSTestMode(),ok=GSRoad.BuildRoadDepot(d,t);tm=null;
      if(ok && GSRoad.BuildRoadDepot(d,t)){depot=d;GSRoad.BuildRoad(t,d);}
     }
     if(depot>=0)break;
    }
   }
  }
  if(depot<0){Fail("depot");return;}
  GSLog.Info("P3_CAPITAL|"+CASE+"|way_and_depot|"+(afterb-GSCompany.GetBankBalance(0)));
  local infra=initialcash-GSCompany.GetBankBalance(0),prefleet=GSCompany.GetBankBalance(0);account.ResetCosts();
  local v=(MODE=="rail"?GSVehicle.BuildVehicle(depot,ENGINE):GSVehicle.BuildVehicleWithRefit(depot,ENGINE,CARGO));
  if(!GSVehicle.IsValidVehicle(v)){Fail("vehicle/refit");return;}
  if(MODE=="rail")for(local i=0;i<WAGONS;i++){
   local w=GSVehicle.BuildVehicleWithRefit(depot,CARGO==0 || CARGO==2?1462:1430,CARGO);
   if(!GSVehicle.IsValidVehicle(w) || !GSVehicle.MoveWagon(w,0,v,GSVehicle.GetNumWagons(v)-1)){Fail("wagons");return;}
  }
  if(MODE=="rail" && BRAKE_VAN){
   local van=GSVehicle.BuildVehicle(depot,1459);
   if(!GSVehicle.IsValidVehicle(van) || !GSVehicle.MoveWagon(van,0,v,GSVehicle.GetNumWagons(v)-1)){Fail("brake van");return;}
  }
  local fleet=prefleet-GSCompany.GetBankBalance(0);
  if(MODE=="rail")GSLog.Info("P3_TRAIN_LENGTH|"+CASE+"|"+WAGONS+"|"+GSVehicle.GetLength(v)+"|"+PLATFORM+"|"+GSGameSettings.GetValue("vehicle.max_train_length"));
  GSLog.Info("P3_STATIONS|"+a+"|"+b+"|"+GSStation.GetStationID(a)+"|"+GSStation.GetStationID(b)+"|"+v+"|"+GSVehicle.GetVehicleType(v));
  if(!GSOrder.AppendOrder(v,a,GSOrder.OF_NONE)){Fail("origin order");return;}
  if(!GSOrder.AppendOrder(v,b,ENDPOINTS=="industry"?GSOrder.OF_UNLOAD|GSOrder.OF_NO_LOAD:GSOrder.OF_NONE)){Fail("destination order");return;}
  local vehicles=[v];
  for(local i=1;i<FLEET;i++){
   local copyv=GSVehicle.CloneVehicle(depot,v,true);
   if(!GSVehicle.IsValidVehicle(copyv)){Fail("clone fleet");return;}
   vehicles.append(copyv);
  }
  fleet=prefleet-GSCompany.GetBankBalance(0);
  GSLog.Info("P3_FLEET|"+CASE+"|"+vehicles.len());
  if(POLICY=="repay_idle"){
   local target=max(0,((GSCompany.GetLoanAmount()-GSCompany.GetBankBalance(0)+10000+9999)/10000).tointeger()*10000);
   if(target<GSCompany.GetLoanAmount())GSCompany.SetLoanAmount(target);
  }
  GSLog.Info("P3_BUILT|"+CASE+"|"+ENGINE+"|"+GSEngine.GetName(ENGINE)+"|"+infra+"|"+fleet+"|"+GSVehicle.GetCapacity(v,CARGO)+"|"+GSMap.GetTileX(a)+"|"+GSMap.GetTileY(a)+"|"+GSMap.GetTileX(b)+"|"+GSMap.GetTileY(b)+"|"+(path==null?-1:path.len())+"|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount()+"|"+GSDate.GetCurrentDate());
  foreach(vehicle in vehicles)if(!GSVehicle.StartStopVehicle(vehicle)){Fail("start");return;}
  local oldyear=GSDate.GetYear(GSDate.GetCurrentDate()),maxload=0,positive=0,samples=0,prevload=0,unloads=0,prevlocation=-1,visitsa=0,visitsb=0;
  local endyear=oldyear+YEARS,oldmonth=-1;
  while(GSVehicle.IsValidVehicle(v)){
   local load=GSVehicle.GetCargoLoad(v,CARGO),loc=GSVehicle.GetLocation(v);
   maxload=max(maxload,load);if(load>0)positive++;samples++;
   if(load<prevload)unloads+=prevload-load;
   if(loc!=prevlocation){if(GSStation.GetStationID(loc)==GSStation.GetStationID(a))visitsa++;if(GSStation.GetStationID(loc)==GSStation.GetStationID(b))visitsb++;}
   prevload=load;prevlocation=loc;
   if(GSDate.GetMonth(GSDate.GetCurrentDate())!=oldmonth){oldmonth=GSDate.GetMonth(GSDate.GetCurrentDate());GSLog.Info("P3_MONTH|"+CASE+"|"+GSDate.GetCurrentDate()+"|"+loc+"|"+load+"|"+GSVehicle.GetCurrentSpeed(v)+"|"+GSVehicle.GetProfitThisYear(v));}
   if(GSDate.GetYear(GSDate.GetCurrentDate())!=oldyear){
    Sleep(74); // Let the first-day company finance/quarter rollover finish.
    local ledger="";for(local e=0;e<15;e++)ledger+=GSCompany.GetAnnualExpenseValue(0,1,e)+",";
    GSLog.Info("P3_LEDGER|"+CASE+"|"+oldyear+"|"+ledger);
    local income=0,expenses=0,delivered=0;for(local q=1;q<=4;q++){income+=GSCompany.GetQuarterlyIncome(0,q);expenses+=GSCompany.GetQuarterlyExpenses(0,q);delivered+=GSCompany.GetQuarterlyCargoDelivered(0,q);}
    local monthly=0;foreach(inf in [GSInfrastructure.INFRASTRUCTURE_RAIL,GSInfrastructure.INFRASTRUCTURE_ROAD,GSInfrastructure.INFRASTRUCTURE_CANAL,GSInfrastructure.INFRASTRUCTURE_STATION])monthly+=GSInfrastructure.GetMonthlyInfrastructureCosts(0,inf);
    GSLog.Info("P3_YEAR|"+CASE+"|"+oldyear+"|"+income+"|"+expenses+"|"+GSVehicle.GetProfitLastYear(v)+"|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount()+"|"+monthly+"|"+maxload+"|"+positive+"|"+samples+"|"+unloads+"|"+visitsa+"|"+visitsb+"|"+GSVehicle.GetAge(v)+"|"+GSVehicle.GetReliability(v)+"|"+delivered);
    oldyear=GSDate.GetYear(GSDate.GetCurrentDate());if(oldyear>=endyear)break;maxload=0;positive=0;samples=0;unloads=0;visitsa=0;visitsb=0;
   }
   Sleep(5);
  }
  if(EXPAND){
   GSLog.Info("P3_EXPANSION_BEGIN|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount()+"|"+GSDate.GetCurrentDate());
   ::CASE="horse_then_rail";
   ::MODE="rail";
   ::CARGO=0;
   ::A=189;
   ::B=96;
   ::ENGINE=1534;
   ::FLEET=1;
   ::YEARS=5;
   ::POLICY="keep";
   ::ENDPOINTS="town";
   ::EXPAND=false;
   local nextstage=TransportProbe();nextstage.Start();return;
  }
  GSLog.Info("P3_SERVICE_DONE|"+CASE);while(true)Sleep(10000);
 }
}
