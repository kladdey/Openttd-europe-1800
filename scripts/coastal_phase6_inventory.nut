// Read-only town and real dock-command tests on a paused measurement copy.
class CoastalProbe extends GSController {
 function Start(){
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
  local passengers=-1,mail=-1,radius=GSStation.GetCoverageRadius(GSStation.STATION_DOCK); GSLog.Info("C6 RADIUS|"+radius);
  foreach(c,_ in GSCargoList()){if(GSCargo.GetCargoLabel(c)=="PASS")passengers=c;if(GSCargo.GetCargoLabel(c)=="MAIL")mail=c;}
  foreach(town,_ in GSTownList()){
   local center=GSTown.GetLocation(town),x=GSMap.GetTileX(center),y=GSMap.GetTileY(center);
   GSLog.Info("C6 TOWN|"+town+"|"+GSTown.GetName(town)+"|"+x+"|"+y+"|"+GSTown.GetPopulation(town));
   local attempted=0,legal=0,best=-1,bestdist=10000,passprod=0,mailprod=0;
   {local cm=GSCompanyMode(0);
    for(local dx=-32;dx<=32;dx++)for(local dy=-32;dy<=32;dy++){
     if(abs(dx)+abs(dy)>40 || x+dx<2 || y+dy<2 || x+dx>=4094 || y+dy>=4094)continue;
     local tile=GSMap.GetTileIndex(x+dx,y+dy);
     if(!GSTile.IsCoastTile(tile))continue;
     attempted++;
     local tm=GSTestMode(),ok=GSMarine.BuildDock(tile,GSStation.STATION_NEW);tm=null;
     if(!ok)continue;
     legal++;
     local pa=GSTile.GetCargoAcceptance(tile,passengers,1,1,radius),pp=GSTile.GetCargoProduction(tile,passengers,1,1,radius);
     local ma=GSTile.GetCargoAcceptance(tile,mail,1,1,radius),mp=GSTile.GetCargoProduction(tile,mail,1,1,radius);
     local d=abs(dx)+abs(dy);
     if(pa>=8 && pp>0 && ma>=8 && mp>0 && d<bestdist){best=tile;bestdist=d;passprod=pp;mailprod=mp;}
    }
   }
   GSLog.Info("C6 DOCK|"+town+"|"+attempted+"|"+legal+"|"+best+"|"+bestdist+"|"+passprod+"|"+mailprod);
  }
  GSLog.Info("C6 DONE towns="+GSTownList().Count()+" industries="+GSIndustryList().Count());while(true)Sleep(365);
 }
}
