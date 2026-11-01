"""7F.1: joined legal receiving station, native connectivity, one real Brig."""
import argparse,json,re
from pathlib import Path
from ports_phase7f import ROOT,BASE as PRIOR,prepare,execute,SOURCE,sha
from modern_phase7e import delivery_code
BASE=PRIOR/'connectivity';BASE.mkdir(exist_ok=True)
CANDIDATE=Path(json.loads((PRIOR/'candidate.json').read_text())['candidate'])

def code(phase):
 prefix=delivery_code().split('class FreightProbe extends GSController')[0]
 return prefix+'''class ShipProof extends GSController {
 data=null;
 function Save(){return data==null?{}:data;}
 function Load(version,saved){data=saved;}
 function Cargo(label){foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)==label)return c;throw "Missing cargo";}
 function Start(){try{GSGame.Unpause();while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
 local cm=GSCompanyMode(0),cargo=Cargo("MNSP"),rb=RouteBuilder();rb.CID=0;
 if(PHASE=="access"){
 ::MODE="ship";::CARGO=cargo;::ENDPOINTS="industry";::MIN_SEPARATION=2;::CASE="7f1_access";
 local a=rb.Station(458,true);if(a<0)throw "No loading dock";
 local b=GSMap.GetTileIndex(3349,973);if(!GSMarine.BuildDock(b,GSStation.STATION_NEW))throw "Dublin dock "+GSError.GetLastErrorString();
 local bs=GSStation.GetStationID(b),ext=GSMap.GetTileIndex(3356,966);GSRoad.SetCurrentRoadType(0);
 if(!GSTile.IsBuildable(ext)&&!GSRoad.IsRoadTile(ext))throw "Protected station extension site";
 if(!GSRoad.BuildDriveThroughRoadStation(ext,GSMap.GetTileIndex(3355,966),GSRoad.ROADVEHTYPE_TRUCK,bs))throw "Native station join "+GSError.GetLastErrorString();
 if(GSStation.GetStationID(ext)!=bs)throw "Receiving station not joined";
 local acceptance=GSTile.GetCargoAcceptance(ext,cargo,1,1,GSStation.GetCoverageRadius(GSStation.STATION_TRUCK_STOP));
 if(acceptance<8||GSIndustry.IsCargoAccepted(260,cargo)!=GSIndustry.CAS_ACCEPTED)throw "Receiving catchment does not accept MNSP";
 local aw=rb.DockWater(a),bw=rb.DockWater(b),water=rb.WaterComponent(aw,bw);
 if(!(bw in water))throw "Native approach component disconnected/bounded";
 data={phase="access",a=a,b=b,as=GSStation.GetStationID(a),bs=bs,ext=ext,aw=aw,bw=bw};
 GSLog.Info("P7 F1_ACCESS|a="+a+"|b="+b+"|station_a="+data.as+"|station_b="+bs+"|extension="+ext+"|aw="+aw+"|bw="+bw+"|acceptance="+acceptance+"|nodes="+water.len()+"|source_production="+GSIndustry.GetLastMonthProduction(458,cargo)+"|engine616_buildable="+GSEngine.IsBuildable(616)+"|refit="+GSEngine.CanRefitCargo(616,cargo));
 GSLog.Info("P7 F1_DONE|access");GSGame.Pause();
 }else{
 if(data==null||!("phase" in data))throw "Missing own disposable fixture state";
 if(PHASE=="delivery"){
 local water=rb.WaterComponent(data.aw,data.bw);if(!(data.bw in water))throw "Connection changed before purchase";
 local depot=-1;for(local r=2;r<=12&&depot<0;r++)foreach(delta in [[r,0],[-r,0],[0,r],[0,-r]]){
 local t=rb.Step(data.aw,delta[0],delta[1]),f=rb.Step(t,1,0);if(!(t in water)||!(f in water)||!GSTile.IsWaterTile(t)||!GSTile.IsWaterTile(f))continue;
 if(GSMarine.BuildWaterDepot(t,f)){depot=t;break;}}
 if(depot<0)throw "No connected depot";
 local before=GSCompany.GetBankBalance(0);local v=GSVehicle.BuildVehicleWithRefit(depot,616,cargo);
 if(!GSVehicle.IsValidVehicle(v))throw "Brig build/refit failed";
 if(!GSOrder.AppendOrder(v,data.a,GSOrder.OF_NONE)||!GSOrder.AppendOrder(v,data.b,GSOrder.OF_UNLOAD|GSOrder.OF_NO_LOAD))throw "Ship order failure";
 data.v<-v;data.depot<-depot;data.start<-GSDate.GetCurrentDate();data.maxload<-0;data.unloaded<-0;data.paid<-0;data.lastload<-0;data.lastprofit<-GSVehicle.GetProfitThisYear(v);data.lastyear<-GSDate.GetYear(GSDate.GetCurrentDate());data.phase="delivery";
 GSLog.Info("P7 F1_SHIP|vehicle="+v+"|engine=616|capacity="+GSVehicle.GetCapacity(v,cargo)+"|depot="+depot+"|capital_ship="+(before-GSCompany.GetBankBalance(0))+"|order_count="+GSOrder.GetOrderCount(v));
 GSVehicle.StartStopVehicle(v);
 }else GSLog.Info("P7 F1_RELOAD|vehicle="+data.v+"|paid="+data.paid+"|maxload="+data.maxload+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count());
 local resumed=GSDate.GetCurrentDate();
 if(PHASE=="reload"){
 GSLog.Info("P7 F1_DIAG|location="+GSVehicle.GetLocation(data.v)+"|state="+GSVehicle.GetState(data.v)+"|order="+GSOrder.ResolveOrderPosition(data.v,GSOrder.ORDER_CURRENT)+"|waiting="+GSStation.GetCargoWaiting(data.as,cargo)+"|source_production="+GSIndustry.GetLastMonthProduction(458,cargo)+"|source_level="+GSIndustry.GetProductionLevel(458)+"|source_tile_production="+GSTile.GetCargoProduction(data.a,cargo,1,1,GSStation.GetCoverageRadius(GSStation.STATION_DOCK)));
 foreach(i,_ in GSIndustryList())if(GSIndustry.GetLastMonthProduction(i,cargo)>0)GSLog.Info("P7 F1_OTHER_PRODUCER|industry="+i+"|amount="+GSIndustry.GetLastMonthProduction(i,cargo));
 }

 while(GSDate.GetCurrentDate()-(PHASE=="reload"?resumed:data.start)<(PHASE=="reload"?35:365*4)){
 local v=data.v,load=GSVehicle.GetCargoLoad(v,cargo),profit=GSVehicle.GetProfitThisYear(v),year=GSDate.GetYear(GSDate.GetCurrentDate()),distance=GSMap.DistanceManhattan(GSVehicle.GetLocation(v),data.b);
 if(year!=data.lastyear){data.lastprofit=profit;data.lastyear=year;}
 if(load>data.maxload){data.maxload=load;GSLog.Info("P7 F1_LOAD|vehicle="+v+"|load="+load+"|tile="+GSVehicle.GetLocation(v)+"|date="+GSDate.GetCurrentDate());}
 if(load<data.lastload&&distance<=10){data.unloaded+=data.lastload-load;GSLog.Info("P7 F1_UNLOAD|vehicle="+v+"|amount="+(data.lastload-load)+"|distance="+distance+"|date="+GSDate.GetCurrentDate());}
 if(data.unloaded>0&&profit>data.lastprofit&&distance<=10){data.paid+=profit-data.lastprofit;GSLog.Info("P7 F1_PAID|vehicle="+v+"|delta="+(profit-data.lastprofit)+"|date="+GSDate.GetCurrentDate()+"|unloaded="+data.unloaded);}
 data.lastload=load;data.lastprofit=profit;
 if(data.paid>0&&(PHASE!="reload"||GSDate.GetCurrentDate()-resumed>30))break;
 Sleep(1);
 }
 GSLog.Info("P7 F1_RESULT|vehicle="+data.v+"|loaded="+data.maxload+"|unloaded="+data.unloaded+"|payment="+data.paid+"|profit_current="+GSVehicle.GetProfitThisYear(data.v)+"|profit_last="+GSVehicle.GetProfitLastYear(data.v)+"|days="+(GSDate.GetCurrentDate()-data.start)+"|mill_food="+GSIndustry.GetLastMonthProduction(260,Cargo("FOOD")));
 GSLog.Info("P7 F1_DONE|"+PHASE);GSGame.Pause();
 }
 }catch(e){GSLog.Error("P7 F1_ERROR|"+e);GSGame.Pause();}while(true)Sleep(365);
 }}'''.replace('PHASE','"'+phase+'"')

def fixed_code():
 s=code('fixed')
 helper=''' function ClearDock(t){
 foreach(d in [[1,0],[-1,0],[0,1],[0,-1]]){local safe=true;
 for(local along=1;along<=5;along++)for(local across=-1;across<=1;across++){
 local q=Step(t,d[0]*along-d[1]*across,d[1]*along+d[0]*across);
 if(!GSTile.IsWaterTile(q)||GSTile.GetSlope(q)!=GSTile.SLOPE_FLAT||GSIndustry.IsValidIndustry(GSIndustry.GetIndustryID(q))||GSStation.IsValidStation(GSStation.GetStationID(q)))safe=false;
 }
 if(safe)return true;
 }
 return false;}
'''
 s=s.replace(' function Station(id,production){',helper+' function Station(id,production){')
 s=s.replace('if(!GSTile.IsCoastTile(tile))continue;','if(!GSTile.IsCoastTile(tile)||!ClearDock(tile))continue;')
 s=s.replace('if("fixed"=="access"){','if("fixed"=="access"||"fixed"=="fixed"){')
 s=s.replace('GSLog.Info("P7 F1_DONE|access");GSGame.Pause();\n }else{','if("fixed"=="access"){GSLog.Info("P7 F1_DONE|access");GSGame.Pause();}\n }\n if("fixed"!="access"){')
 s=s.replace('if("fixed"=="delivery"){','if("fixed"=="delivery"||"fixed"=="fixed"){')
 return s

def run(phase):
 h=prepare('f1-'+phase,fixed_code() if phase=='fixed' else code(phase));info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"PortsController"','"ShipProof"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 source=CANDIDATE if phase in ['access','fixed'] else Path(json.loads((BASE/('access.json' if phase=='delivery' else 'delivery.json')).read_text())['case'])/'save/autosave/exit.sav'
 before=sha(source);r=execute(h,18000 if phase=='access' else 180000,source=source);assert sha(source)==before
 r.update(source=str(source),source_sha256=before);(BASE/(phase+'.json')).write_text(json.dumps(r,indent=2))
 if any('F1_ERROR|' in s for s in r['observations']):raise RuntimeError('Fixture failed; inspect '+r['log'])
 assert any('F1_DONE|'+phase in s for s in r['observations'])
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['access','delivery','reload','fixed']);run(ap.parse_args().phase)
