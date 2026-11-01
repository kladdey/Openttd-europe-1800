"""Reuse 7E's safe route-builder and sampler; specialize early intermodal freight."""
import json,re
from ports_phase7f import *
from modern_phase7e import delivery_code
from industrial_phase6b_controls import COMMON

def code():
 s=delivery_code();s=s[:s.index('function Start(){try{')]
 a=s.index(' function Engine(');b=s.index(' function Loop(',a);orig=COMMON[COMMON.index(' function Engine('):COMMON.index(' function Loop(')]
 s=s[:a]+orig+s[b:]
 # The feeder must join the ship's station, then TRANSFER instead of selling there.
 s=s.replace('GSRoad.ROADVEHTYPE_TRUCK,GSStation.STATION_NEW)','GSRoad.ROADVEHTYPE_TRUCK,(id==150&&!production?JOIN_DOCK:GSStation.STATION_NEW))')
 # delivery_code includes COMMON ShipService already.
 s='JOIN_DOCK <- -1;\n'+s
 s+='''
function Start(){try{GSGame.Unpause();while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
local services=[],ship=null,start=GSDate.GetCurrentDate();
{local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];
GSLog.Info("P7 F_FINANCE_START|cash="+GSCompany.GetBankBalance(0)+"|loan="+GSCompany.GetLoanAmount());
ship=ShipService("irish_sea_food","FOOD",150,542,false);::JOIN_DOCK=GSStation.GetStationID(ship.a);
::DEPOT_TILES=[];GSRoad.SetCurrentRoadType(0);
local grain=Service("irish_grain","GRAI",50,260,false),food=Service("food_feeder","FOOD",260,150,false);
foreach(v in food.vehicles)if(!GSOrder.SetOrderFlags(v,1,GSOrder.OF_TRANSFER|GSOrder.OF_NO_LOAD))throw "Transfer flags failed";
if(GSStation.GetStationID(food.b)!=JOIN_DOCK)throw "Feeder and ship stations did not join";
services=[grain,food,ship];
foreach(r in services){r.lastload<-{};r.unloaded<-false;r.peak<-0;r.income<-0;foreach(v in r.vehicles)r.lastload[v]<-0;
GSLog.Info("P7 F_ROUTE|tag="+r.tag+"|a="+r.a+"|b="+r.b+"|station_a="+GSStation.GetStationID(r.a)+"|station_b="+GSStation.GetStationID(r.b));
foreach(v in r.vehicles)GSLog.Info("P7 F_VEHICLE|tag="+r.tag+"|id="+v+"|engine="+GSVehicle.GetEngineType(v)+"|capacity="+GSVehicle.GetCapacity(v,Cargo(r.label)));
Toggle(r);}
GSLog.Info("P7 F_COMMISSION|cash="+GSCompany.GetBankBalance(0)+"|loan="+GSCompany.GetLoanAmount()+"|date="+GSDate.GetCurrentDate());}
local month=-1;
while(GSDate.GetCurrentDate()-start<365*5){
{local cm=GSCompanyMode(0);foreach(r in services)Sample(r);}
local now=GSDate.GetCurrentDate(),m=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
if(m!=month){month=m;GSLog.Info("P7 F_FLOW|date="+now+"|mill_food="+GSIndustry.GetLastMonthProduction(260,Cargo("FOOD"))+"|dock_food="+GSStation.GetCargoWaiting(JOIN_DOCK,Cargo("FOOD")));}
if(ship.paid)break;
Sleep(2);
}
{local cm=GSCompanyMode(0);local profit=0;foreach(v in ship.vehicles)profit+=GSVehicle.GetProfitThisYear(v)+GSVehicle.GetProfitLastYear(v);
GSLog.Info("P7 F_SHIP_RESULT|loaded="+ship.ever_loaded+"|unloaded="+ship.unloaded+"|paid="+ship.paid+"|peak="+ship.peak+"|sample_income="+ship.income+"|current_last_year_vehicle_profit="+profit+"|days="+(GSDate.GetCurrentDate()-start)+"|cash="+GSCompany.GetBankBalance(0));}
GSLog.Info("P7 F_FREIGHT_DONE");GSGame.Pause();
}catch(e){GSLog.Error("P7 F_ERROR|"+e);}while(true)Sleep(365);}}
'''
 return re.sub(r'}(?=(?:return|if\(|Sleep|local|GSLog|Toggle))','}\n',s)

def direct_code():
 s=code();s=s[:s.index('function Start(){try{')]
 s=s.replace('class FreightProbe extends GSController {function Save(){return {};}', 'class FreightProbe extends PortsController {')
 s=bundle()+'\n'+s
 s+='''function Start(){try{GSGame.Unpause();Initialize(Calendar());local start=GSDate.GetCurrentDate(),month=-1,ship=null;
{local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];
GSLog.Info("P7 F_FINANCE_START|cash="+GSCompany.GetBankBalance(0)+"|loan="+GSCompany.GetLoanAmount());
ship=ShipService("liverpool_greenock_supplies","MNSP",458,410,false);ship.lastload<-{};ship.unloaded<-false;ship.peak<-0;ship.income<-0;
foreach(v in ship.vehicles){ship.lastload[v]<-0;GSLog.Info("P7 F_VEHICLE|tag="+ship.tag+"|id="+v+"|engine="+GSVehicle.GetEngineType(v)+"|capacity="+GSVehicle.GetCapacity(v,Cargo(ship.label)));}
GSLog.Info("P7 F_ROUTE|tag="+ship.tag+"|a="+ship.a+"|b="+ship.b+"|station_a="+GSStation.GetStationID(ship.a)+"|station_b="+GSStation.GetStationID(ship.b));Toggle(ship);
}
while(GSDate.GetCurrentDate()-start<365*5){local now=Calendar(),m=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
if(m!=month){month=m;Tick(now);GSLog.Info("P7 F_STATE|calendar="+now+"|economy="+GSDate.GetCurrentDate()+"|schema="+state.schema+"|events="+state.expansion.len()+"|towns="+GSTownList().Count());}
{local cm=GSCompanyMode(0);Sample(ship);}
if(ship.paid&&GSDate.GetCurrentDate()-start>=366)break;Sleep(2);
}
{local cm=GSCompanyMode(0);local profit=0;foreach(v in ship.vehicles)profit+=GSVehicle.GetProfitThisYear(v)+GSVehicle.GetProfitLastYear(v);
GSLog.Info("P7 F_SHIP_RESULT|loaded="+ship.ever_loaded+"|unloaded="+ship.unloaded+"|paid="+ship.paid+"|peak="+ship.peak+"|sample_income="+ship.income+"|current_last_year_vehicle_profit="+profit+"|days="+(GSDate.GetCurrentDate()-start)+"|cash="+GSCompany.GetBankBalance(0));}
local kept=0;foreach(sig in state.baseline)if(Matches(sig.id,sig))kept++;
GSLog.Info("P7 F_SAFETY|baseline_intact="+kept+"|schema="+Save().schema+"|events="+state.expansion.len());
GSLog.Info("P7 F_FREIGHT_DONE");GSGame.Pause();
}catch(e){GSLog.Error("P7 F_ERROR|"+e);}while(true)Sleep(365);}}
'''
 return re.sub(r'}(?=(?:return|if\(|Sleep|local|GSLog|Toggle))','}\n',s)

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--direct',action='store_true');a=ap.parse_args()
 h=prepare('coastal-acceptor-freight' if a.direct else 'early-paid-freight',direct_code() if a.direct else code());info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"PortsController"','"FreightProbe"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 src=Path(json.loads((BASE/'candidate.json').read_text())['candidate']) if a.direct else Path(json.loads((BASE/'probe.json').read_text())['case'])/'save/autosave/exit.sav'
 r=execute(h,230000,source=src);(BASE/('direct.json' if a.direct else 'freight.json')).write_text(json.dumps(r,indent=2))
