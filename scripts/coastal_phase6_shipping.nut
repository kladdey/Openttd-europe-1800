// Temporary infrastructure/ships ONLY in a disposable gameplay copy.
class CoastalProbe extends GSController {
 function Step(t,dx,dy){return GSMap.GetTileIndex(GSMap.GetTileX(t)+dx,GSMap.GetTileY(t)+dy);}
 function Water(dock){foreach(d in [[1,0],[-1,0],[0,1],[0,-1]]){local n=Step(dock,d[0],d[1]);if(GSMarine.IsDockTile(n))return Step(n,d[0],d[1]);}return -1;}
 function Connected(start,goal){
  local queue=[start],seen={},pos=0;seen[start]<-true;
  while(pos<queue.len() && pos<20000){local t=queue[pos++];if(t==goal)return true;
   foreach(d in [[1,0],[-1,0],[0,1],[0,-1]]){local n=Step(t,d[0],d[1]);
    if(n in seen || GSMap.DistanceManhattan(start,n)>85)continue;
    if(GSMarine.AreWaterTilesConnected(t,n)){seen[n]<-true;queue.append(n);}
   }
  }return false;
 }
 function Start(){
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
  local cm=GSCompanyMode(0);GSCompany.SetLoanAmount(GSCompany.GetMaxLoanAmount());
  local pass=-1;foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)=="PASS")pass=c;
  local docks={},services=[];
  foreach(p in PORTS){
   local ok=GSMarine.BuildDock(p.tile,GSStation.STATION_NEW);
   GSLog.Info("C6 BUILT_DOCK|"+p.name+"|"+p.tile+"|"+ok+"|"+GSError.GetLastErrorString());
   if(ok){docks[p.name]<-p.tile;
    if("witness" in p)GSLog.Info("C6 SEA_CONNECTION|"+p.name+"|"+Water(p.tile)+"|"+p.witness+"|"+Connected(Water(p.tile),p.witness));
   }
  }
  foreach(r in ROUTES){
   if(!(r.a in docks) || !(r.b in docks)){GSLog.Info("C6 SHIP_BLOCKED|"+r.name+"|dock construction");continue;}
   local a=docks[r.a],b=docks[r.b],water=Water(a),depot=-1;
   for(local radius=3;radius<=18 && depot<0;radius++)for(local dx=-radius;dx<=radius && depot<0;dx++)for(local dy=-radius;dy<=radius && depot<0;dy++){
    if(abs(dx)+abs(dy)!=radius)continue;
    local t=Step(water,dx,dy),f=Step(t,1,0);
    if(!GSTile.IsWaterTile(t) || !GSTile.IsWaterTile(f))continue;
    local tm=GSTestMode(),ok=GSMarine.BuildWaterDepot(t,f);tm=null;
    if(ok && GSMarine.BuildWaterDepot(t,f))depot=t;
   }
   if(depot<0){GSLog.Info("C6 SHIP_BLOCKED|"+r.name+"|depot construction");continue;}
   local ship=GSVehicle.BuildVehicleWithRefit(depot,616,pass);
   if(!GSVehicle.IsValidVehicle(ship)){GSLog.Info("C6 SHIP_BLOCKED|"+r.name+"|ship build|"+GSError.GetLastErrorString());continue;}
   GSOrder.AppendOrder(ship,a,GSOrder.OF_NONE);GSOrder.AppendOrder(ship,b,GSOrder.OF_NONE);
   GSVehicle.StartStopVehicle(ship);
   services.append({name=r.name,v=ship,a=a,b=b,start=GSVehicle.GetLocation(ship),moved=false,arrived=false,min_distance=100000,loaded=false,lastorder=0});
   GSLog.Info("C6 SHIP_START|"+r.name+"|"+ship+"|"+a+"|"+b+"|"+GSEngine.GetName(616));
  }
  for(local tick=0;tick<100000;tick+=5){
   Sleep(5);local all=true;
   foreach(s in services){
    local t=GSVehicle.GetLocation(s.v),d=GSMap.DistanceManhattan(t,s.b);
    s.min_distance=min(s.min_distance,d);
    if(GSMap.DistanceManhattan(t,s.start)>10)s.moved=true;
    if(GSVehicle.GetCargoLoad(s.v,pass)>0)s.loaded=true;
    local order=GSOrder.ResolveOrderPosition(s.v,GSOrder.ORDER_CURRENT);
    if(d<=4 && (GSVehicle.GetState(s.v)==GSVehicle.VS_AT_STATION || (s.lastorder==1 && order==0)) && !s.arrived){s.arrived=true;GSLog.Info("C6 SHIP_ARRIVED|"+s.name+"|"+t+"|"+order+"|"+GSVehicle.GetCargoLoad(s.v,pass)+"|"+GSVehicle.GetState(s.v));}
    s.lastorder=order;
    if(!s.arrived)all=false;
   }
   if(all && services.len()>0)break;
  }
  foreach(s in services)GSLog.Info("C6 SHIP_RESULT|"+s.name+"|"+s.moved+"|"+s.arrived+"|"+s.min_distance+"|"+s.loaded+"|"+GSVehicle.GetLocation(s.v));
  GSGame.Pause();GSLog.Info("C6 DONE shipping");while(true)Sleep(365);
 }
}
