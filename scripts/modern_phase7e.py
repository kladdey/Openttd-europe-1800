"""Phase 7E: isolated real-Europe cargo delivery fixture; never edits source saves."""
import argparse,json,re
from pathlib import Path
import lifecycle_phase7d_runtime as d
from industrial_phase6b_controls import builder,COMMON
ROOT=d.ROOT
BASE=d.BASE/'phase7e';BASE.mkdir(exist_ok=True)
def source():
 r=json.loads((d.BASE/'europe.json').read_text())['run']
 p=Path(r['case'])/'save/autosave/exit.sav'
 assert p.exists()
 return p

def run(tag,code,ticks=8000,input_save=None):
 old=d.BASE
 try:
  d.BASE=BASE;h=d.prepare(tag,code)
 finally:d.BASE=old
 info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"ProgressionController"','"FreightProbe"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 inp=Path(input_save) if input_save else source();before=d.sha(inp)
 (h/'source.json').write_text(json.dumps(dict(path=str(inp),sha256=before)))
 result=d.execute(h,ticks,source=inp,timeout=300)
 assert d.sha(inp)==before
 (BASE/(tag+'.json')).write_text(json.dumps(result,indent=2))
 if any('P7 E_ERROR|' in line for line in result['observations']):raise RuntimeError('Fixture failed; inspect '+result['log'])
 marker='E_CAPABILITY_DONE' if tag=='capability' else 'E_DELIVERY_DONE'
 if not any(marker in line for line in result['observations']):raise RuntimeError('Fixture did not complete; inspect '+result['log'])
 return result

PROBE='''class FreightProbe extends GSController {
function Save(){return {};}
function Start(){try{GSGame.Pause();
GSLog.Info("P7 E_BASE|date="+GSDate.GetCurrentDate()+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|train="+GSGameSettings.GetValue("vehicle.max_train_length"));
foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)=="RCYC"||GSCargo.GetCargoLabel(c)=="PLAS"||GSCargo.GetCargoLabel(c)=="MNSP"||GSCargo.GetCargoLabel(c)=="SCMT"||GSCargo.GetCargoLabel(c)=="MPAR"||GSCargo.GetCargoLabel(c)=="QLME"){
GSLog.Info("P7 E_CARGO|id="+c+"|label="+GSCargo.GetCargoLabel(c));
foreach(e,_ in GSEngineList(GSVehicle.VT_ROAD))if(GSEngine.IsBuildable(e)&&GSEngine.CanRefitCargo(e,c))GSLog.Info("P7 E_ENGINE|cargo="+c+"|engine="+e+"|name="+GSEngine.GetName(e)+"|price="+GSEngine.GetPrice(e)+"|running="+GSEngine.GetRunningCost(e)+"|speed="+GSEngine.GetMaxSpeed(e));
}
foreach(i,_ in GSIndustryList()){
local type=GSIndustry.GetIndustryType(i),relevant=i>=542;
foreach(c,_ in GSIndustryType.GetAcceptedCargo(type))if(GSCargo.GetCargoLabel(c)=="MNSP"||GSCargo.GetCargoLabel(c)=="SCMT")relevant=true;
if(relevant){local a="",p="";foreach(c,_ in GSIndustryType.GetAcceptedCargo(type))a+=GSCargo.GetCargoLabel(c)+",";foreach(c,_ in GSIndustryType.GetProducedCargo(type))p+=GSCargo.GetCargoLabel(c)+",";
GSLog.Info("P7 E_INDUSTRY|id="+i+"|type="+type+"|tile="+GSIndustry.GetLocation(i)+"|accept="+a+"|produce="+p);}
}
GSLog.Info("P7 E_CAPABILITY_DONE");}catch(e){GSLog.Error("P7 E_ERROR|"+e);}while(true)Sleep(365);}}
'''

def delivery_code():
 common=COMMON
 start=common.index(' function Engine(');end=common.index(' function Loop(',start)
 common=common[:start]+''' function Engine(cargo){local e=GSCargo.GetCargoLabel(cargo)=="RCYC"||GSCargo.GetCargoLabel(cargo)=="SCMT"?407:369;
 if(!GSEngine.IsBuildable(e)||!GSEngine.CanRefitCargo(e,cargo))throw "Chosen modern engine unavailable";
 GSLog.Info("P7 E_SELECTED|cargo="+cargo+"|engine="+e+"|name="+GSEngine.GetName(e)+"|price="+GSEngine.GetPrice(e)+"|running="+GSEngine.GetRunningCost(e));return e;}
'''+common[end:]
 start=common.index(' function Sample(')
 common=common[:start]+''' function Sample(s){
 local yr=GSDate.GetYear(GSDate.GetCurrentDate());if(yr!=s.lastyear){foreach(v in s.vehicles)s.lastprofit[v]=GSVehicle.GetProfitThisYear(v);s.lastyear=yr;}
 foreach(v in s.vehicles){local load=GSVehicle.GetCargoLoad(v,Cargo(s.label)),profit=GSVehicle.GetProfitThisYear(v),distance=GSMap.DistanceManhattan(GSVehicle.GetLocation(v),s.b);
 if(load>0&&!s.ever_loaded){s.ever_loaded=true;GSLog.Info("P7 E_LOADED|tag="+s.tag+"|vehicle="+v+"|load="+load+"|date="+GSDate.GetCurrentDate());}
 if(load<s.lastload[v]&&distance<=10)s.unloaded=true;
 if(s.unloaded&&distance<=10&&profit>s.lastprofit[v]){s.income+=profit-s.lastprofit[v];if(!s.paid){s.paid=true;GSLog.Info("P7 E_PAID|tag="+s.tag+"|vehicle="+v+"|delta="+(profit-s.lastprofit[v])+"|before_load="+s.lastload[v]+"|after_load="+load+"|distance="+distance+"|date="+GSDate.GetCurrentDate());}}
 s.lastprofit[v]=profit;s.lastload[v]=load;s.peak=max(s.peak,load);
 }
 }
'''
 code=builder()
 # Existing road construction commands must not automatically clear protected tiles.
 code=code.replace(' function Link(prev,cur,next){',' function Link(prev,cur,next){\n if(GSTile.IsHouseTile(cur)||GSTile.IsHouseTile(next)||GSIndustry.IsValidIndustry(GSIndustry.GetIndustryID(cur))||GSIndustry.IsValidIndustry(GSIndustry.GetIndustryID(next)))return false;')
 code=code.replace('  foreach(tile in Candidates(id,production)){','  foreach(tile in Candidates(id,production)){\n   if(MODE=="road" && Path(Step(tile,1,0),tile,Step(tile,-1,0))==null)continue;')
 code+='class FreightProbe extends GSController {function Save(){return {};}\n'+common+'''
function Start(){try{GSGame.Unpause();while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
local services=[],start=GSDate.GetCurrentDate(),initial=0;
{local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];GSRoad.SetCurrentRoadType(0);
initial=GSCompany.GetBankBalance(0);GSLog.Info("P7 E_FINANCE_BEGIN|cash="+initial+"|loan="+GSCompany.GetLoanAmount());
foreach(route in [["RCYC",547,549],["PLAS",549,550],["MNSP",550,546],["RCYC",547,548]]){
local before=GSCompany.GetBankBalance(0),s=Service(route[0]+"_"+route[1]+"_"+route[2],route[0],route[1],route[2],false);
s.lastload<-{};s.unloaded<-false;s.peak<-0;s.income<-0;
foreach(v in s.vehicles){s.lastload[v]<-0;GSLog.Info("P7 E_VEHICLE|tag="+s.tag+"|id="+v+"|engine="+GSVehicle.GetEngineType(v)+"|capacity="+GSVehicle.GetCapacity(v,Cargo(s.label)));}
GSLog.Info("P7 E_ROUTE|tag="+s.tag+"|origin="+route[1]+"|destination="+route[2]+"|a="+s.a+"|b="+s.b+"|station_a="+GSStation.GetStationID(s.a)+"|station_b="+GSStation.GetStationID(s.b)+"|capital_cash_delta="+(before-GSCompany.GetBankBalance(0))+"|acceptance="+GSTile.GetCargoAcceptance(s.b,Cargo(s.label),1,1,3));
services.append(s);
}}
{local cm=GSCompanyMode(0);foreach(s in services)Toggle(s);}
local month=-1;
while(GSDate.GetCurrentDate()-start<365*4){
{local cm=GSCompanyMode(0);foreach(s in services)Sample(s);}
local now=GSDate.GetCurrentDate(),m=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
if(m!=month){month=m;foreach(i in [547,548,549,550,546])foreach(c,_ in GSIndustryType.GetProducedCargo(GSIndustry.GetIndustryType(i)))GSLog.Info("P7 E_PRODUCTION|industry="+i+"|cargo="+GSCargo.GetCargoLabel(c)+"|last_month="+GSIndustry.GetLastMonthProduction(i,c)+"|date="+now);
foreach(i in [548,549,550,546])foreach(c,_ in GSIndustryType.GetAcceptedCargo(GSIndustry.GetIndustryType(i)))GSLog.Info("P7 E_STOCK|industry="+i+"|cargo="+GSCargo.GetCargoLabel(c)+"|stock="+GSIndustry.GetStockpiledCargo(i,c)+"|date="+now);
}
local all=true;foreach(s in services)if(!s.paid)all=false;
if(all&&now-start>365)break;
Sleep(2);
}
{local cm=GSCompanyMode(0);foreach(s in services){local profit=0;foreach(v in s.vehicles)profit+=GSVehicle.GetProfitThisYear(v)+GSVehicle.GetProfitLastYear(v);GSLog.Info("P7 E_RESULT|tag="+s.tag+"|loaded="+s.ever_loaded+"|unloaded="+s.unloaded+"|paid="+s.paid+"|peak="+s.peak+"|positive_income_samples="+s.income+"|current_plus_last_year_vehicle_profit="+profit);}
GSLog.Info("P7 E_FINANCE_END|cash="+GSCompany.GetBankBalance(0)+"|loan="+GSCompany.GetLoanAmount()+"|days="+(GSDate.GetCurrentDate()-start));}
GSLog.Info("P7 E_DELIVERY_DONE");GSGame.Pause();
}catch(e){GSLog.Error("P7 E_ERROR|"+e);}while(true)Sleep(365);}}
'''
 return re.sub(r'}(?=(?:return|if\(|Sleep|local|GSLog))','}\n',code)


def secondary_code():
 from lifecycle_phase7d_policy import enrich,squirrel
 e=enrich(dict(local_id=79,event_id='eaf_fixture'))
 code=delivery_code()
 code=code.replace('function Start(){try{GSGame.Unpause();while', 'function Start(){try{GSGame.Unpause();local eaf=Eaf();GSLog.Info("P7 E_RELOAD|towns="+GSTownList().Count()+"|industry_count="+GSIndustryList().Count()+"|original_vehicle0="+GSVehicle.IsValidVehicle(0));while')
 code=code.replace('[["RCYC",547,549],["PLAS",549,550],["MNSP",550,546],["RCYC",547,548]]','[["SCMT",548,eaf]]')
 code=code.replace('foreach(i in [547,548,549,550,546])','foreach(i in [548,eaf])').replace('foreach(i in [548,549,550,546])','foreach(i in [eaf])')
 method=''' function Eaf(){local before={};foreach(i,_ in GSIndustryList())before[i]<-true;local attempts=0;
 for(local r=0;r<=28;r+=2)for(local dx=-r;dx<=r;dx+=2)for(local dy=-r;dy<=r;dy+=2){if(abs(dx)+abs(dy)!=r)continue;
 local tile=GSMap.GetTileIndex(2440+dx,1448+dy),height=GSTile.GetMinHeight(tile),safe=true;
 foreach(p in EAF_FOOTPRINT){local t=GSMap.GetTileIndex(2440+dx+p[0],1448+dy+p[1]);if(GSTile.IsHouseTile(t)||GSTile.IsWaterTile(t)||GSRoad.IsRoadTile(t)||!GSTile.IsBuildable(t)||GSTile.GetMinHeight(t)!=height||GSTile.GetMaxHeight(t)!=height)safe=false;}
 if(!safe)continue;if(attempts++>=96)throw "EAF legal site attempts exhausted";
 if(GSIndustryType.BuildIndustry(GSIndustryType.ResolveNewGRFID(0x4B484531,79),tile)){foreach(i,_ in GSIndustryList())if(!(i in before)){GSLog.Info("P7 E_EAF_BUILT|id="+i+"|tile="+GSIndustry.GetLocation(i)+"|attempts="+attempts);return i;}}
 }
 throw "No legal bounded EAF site";}
'''
 code=code.replace('function Start(){try{GSGame.Unpause();local eaf',method+'function Start(){try{GSGame.Unpause();local eaf')
 return 'EAF_FOOTPRINT <- '+squirrel(e['footprint'])+';\n'+code

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('case',choices=['capability','delivery','secondary']);a=ap.parse_args()
 inp=None
 if a.case=='secondary':inp=Path(json.loads((BASE/'delivery.json').read_text())['case'])/'save/autosave/exit.sav'
 run(a.case,{'capability':lambda:PROBE,'delivery':delivery_code,'secondary':secondary_code}[a.case](),8000 if a.case=='capability' else 180000,input_save=inp)
