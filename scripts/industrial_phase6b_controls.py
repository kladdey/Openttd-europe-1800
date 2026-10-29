"""Disposable period-vehicle production controls for the 0.3.0 candidate."""
import json,os,subprocess,time,shutil
from pathlib import Path
from PIL import Image
from industrial_phase6b_runtime import ROOT,BASE,sha
from coastal_phase6_runtime import ENGINE
from transport_phase4 import generate


def builder():
    # Reuse the previously validated real route builder; replace only its
    # orchestration. There are no forced engines or price/performance changes.
    text=generate(dict(years=1,routes=[],expand=False))
    text=text[:text.index('class TransportProbe extends GSController')]
    text=text.replace('GSIndustry.HasDock(id))return', 'GSIndustry.HasDock(id) && GSIndustry.GetDockLocation(id)>=0)return')
    text='HOLD_FLEET <- false; INDUSTRIAL_STOPS <- {};\n'+text
    text=text.replace('foreach(vehicle in vehicles)if(!GSVehicle.StartStopVehicle(vehicle))', 'foreach(vehicle in vehicles)if(!HOLD_FLEET && !GSVehicle.StartStopVehicle(vehicle))')
    text=text.replace(' function Station(id,production){',' function Station(id,production){\n  if(MODE=="road" && ENDPOINTS=="industry" && (id+"_"+production) in INDUSTRIAL_STOPS)return INDUSTRIAL_STOPS[id+"_"+production];')
    text=text.replace('    if(ok)return tile;','    if(ok){if(MODE=="road" && ENDPOINTS=="industry")INDUSTRIAL_STOPS[id+"_"+production]<-tile;return tile;}')
    text=text.replace('local depot=-1,path=null;','local depot=MODE=="road" && DEPOT_TILES.len()>0?DEPOT_TILES[0]:-1,path=null;')
    text=text.replace('  if(depot<0){Fail("depot");return null;}','  if(depot<0){Fail("depot");return null;}\n  if(MODE=="road" && DEPOT_TILES.len()==0)DEPOT_TILES.append(depot);')
    start=text.index(' function Path(');end=text.index(' function Candidates(',start)
    text=text[:start]+(ROOT/'scripts/industrial_phase6b_path.nut').read_text()+text[end:]
    return text


def fresh(script,tag,ticks=60000,sea=True):
    reg=json.loads((BASE/'candidate-registration.json').read_text())
    template=Path(reg['case']);home=BASE/(tag+'-'+str(time.time_ns()));home.mkdir()
    for folder in ['newgrf','baseset']:shutil.copytree(template/folder,home/folder,copy_function=os.link)
    shutil.copytree(template/'game',home/'game')
    (home/'game/registration/main.nut').write_text(script,encoding='utf-8-sig')
    cfg=(template/'test.cfg').read_text(encoding='utf8').replace('heightmap_height = 16','heightmap_height = 1')
    cfg+='\n[vehicle]\nmax_train_length = 7\n'
    (home/'test.cfg').write_text(cfg,encoding='utf8')
    im=Image.new('L',(256,256),255)
    if sea:im.paste(0,(0,190,256,256))
    im.save(home/'flat.png')
    cmd=[str(ENGINE),'-X','-x','-c',str(home/'test.cfg'),'-g',str(home/'flat.png'),'-v',f'null:ticks={ticks}','-s','null','-m','null','-d','script=4']
    (home/'manifest.json').write_text(json.dumps(dict(kind='CONTROLLED ENGINE FIXTURE, not campaign economy',period_vehicle_policy='Only buildable existing engines, no EnableForCompany',script_sha256=sha(home/'game/registration/main.nut'),command=cmd),indent=2))
    start=time.monotonic()
    with (home/'engine.log').open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=home,stdout=f,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW,check=True)
    print(home,flush=True)
    print('\n'.join(s for s in (home/'engine.log').read_text(encoding='utf8').splitlines() if 'I6 CONTROL' in s or 'C6 DONE' in s or 'Your script made an error' in s),flush=True)
    return home


COMMON='''
 function Cargo(label){foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)==label)return c;throw "Missing cargo "+label;}
 function Build(localid,x,y){
  local type=GSIndustryType.ResolveNewGRFID(0x4B484531,localid),before={};foreach(i,_ in GSIndustryList())before[i]<-true;
  if(!GSIndustryType.CanBuildIndustry(type))throw "Historical construction blocked "+localid;
  for(local r=0;r<=14;r+=2)for(local dx=-r;dx<=r;dx+=2)for(local dy=-r;dy<=r;dy+=2){
   if(abs(dx)+abs(dy)!=r)continue;local tile=GSMap.GetTileIndex(x+dx,y+dy);
   if(GSIndustryType.BuildIndustry(type,tile)){foreach(i,_ in GSIndustryList())if(!(i in before)){GSLog.Info("I6 CONTROL_INDUSTRY|"+localid+"|"+i+"|"+GSIndustry.GetLocation(i));return i;}}
  }throw "No controlled site "+localid+" "+GSError.GetLastErrorString();
 }
 function CoastIndustry(localid,near){
  local list=[];for(local x=8;x<248;x++)for(local y=8;y<248;y++){local tile=GSMap.GetTileIndex(x,y);if(GSTile.IsCoastTile(tile))list.append(tile);}
  list.sort(function(a,b):(near){return GSMap.DistanceManhattan(a,near)-GSMap.DistanceManhattan(b,near);});
  local type=GSIndustryType.ResolveNewGRFID(0x4B484531,localid),before={};foreach(i,_ in GSIndustryList())before[i]<-true;
  foreach(t in list)for(local dx=-5;dx<=5;dx++)for(local dy=-5;dy<=5;dy++){
   if(GSIndustryType.BuildIndustry(type,GSMap.GetTileIndex(GSMap.GetTileX(t)+dx,GSMap.GetTileY(t)+dy))){foreach(i,_ in GSIndustryList())if(!(i in before)){GSLog.Info("I6 CONTROL_INDUSTRY|"+localid+"|"+i+"|"+GSIndustry.GetLocation(i));return i;}}
  }throw "No controlled coast industry "+localid+"|can="+GSIndustryType.CanBuildIndustry(type)+"|"+GSError.GetLastErrorString();
 }
 function Market(near){
  local type=GSIndustryType.ResolveNewGRFID(0x4B484531,59),before={};foreach(i,_ in GSIndustryList())before[i]<-true;
  local towns=[];foreach(t,_ in GSTownList())towns.append(t);towns.sort(function(a,b):(near){return GSMap.DistanceManhattan(GSTown.GetLocation(a),near)-GSMap.DistanceManhattan(GSTown.GetLocation(b),near);});
  foreach(t in towns){local p=GSTown.GetLocation(t),x=GSMap.GetTileX(p),y=GSMap.GetTileY(p);for(local dx=-20;dx<=20;dx++)for(local dy=-20;dy<=20;dy++){
   local tile=GSMap.GetTileIndex(x+dx,y+dy);if(!GSTile.IsHouseTile(tile))continue;
   if(GSIndustryType.BuildIndustry(type,tile)){foreach(i,_ in GSIndustryList())if(!(i in before))return i;}
  }}throw "No controlled market site";
 }
 function Engine(cargo){local best=-1,cost=1000000000;foreach(e,_ in GSEngineList(GSVehicle.VT_ROAD)){
  if(GSEngine.IsBuildable(e) && GSEngine.CanRefitCargo(e,cargo) && GSEngine.GetPrice(e)<cost){best=e;cost=GSEngine.GetPrice(e);}}
  if(best<0)throw "No period cargo engine "+cargo;GSLog.Info("I6 PERIOD_ENGINE|"+cargo+"|"+best+"|"+GSEngine.GetName(best));return best;
 }
 function Loop(rb,tile){
  local path=rb.Path(rb.Step(tile,1,0),tile,rb.Step(tile,-1,0));if(path==null)throw "No articulated-road-vehicle turning loop";
  for(local i=0;i<path.len();i++){local next=i+1<path.len()?path[i+1]:tile;
   local ok=false;
   if(GSMap.DistanceManhattan(path[i],next)>1){
    if(GSBridge.IsBridgeTile(path[i]) && GSBridge.GetOtherBridgeEnd(path[i])==next)ok=true;
    else if(GSTunnel.IsTunnelTile(path[i]) && GSTunnel.GetOtherTunnelEnd(path[i])==next)ok=true;
    else ok=GSBridge.BuildBridge(GSVehicle.VT_ROAD,0,path[i],next);
   }else ok=GSRoad.BuildRoad(path[i],next);
   if(!ok && GSError.GetLastErrorString()!="ERR_ALREADY_BUILT")throw "Loop commit failed: "+GSError.GetLastErrorString();
  }
  GSLog.Info("I6 TURNING_LOOP|"+tile+"|"+path.len());
 }
 function Service(tag,label,a,b,start){
  local c=Cargo(label),e=Engine(c);::ACTIVE={mode="road",cargo=c,a=a,b=b,engine=e,fleet=2,endpoints="industry",wagons=0,platform=2,brake=false,sep=2};
  ::MODE="road";::CARGO=c;::A=a;::B=b;::ENGINE=e;::FLEET=2;::ENDPOINTS="industry";::WAGONS=0;::PLATFORM=2;::BRAKE_VAN=false;::MIN_SEPARATION=2;::CASE=tag;
  ::HOLD_FLEET=!start;local rb=RouteBuilder();rb.CID=0;local s=rb.Build();::HOLD_FLEET=false;if(s==null)throw "Route construction blocked "+tag;
  Loop(rb,s.a);Loop(rb,s.b);

  s.label<-label;s.ever_loaded<-false;s.paid<-false;s.lastprofit<-{};s.lastyear<-GSDate.GetYear(GSDate.GetCurrentDate());
  foreach(v in s.vehicles)s.lastprofit[v]<-GSVehicle.GetProfitThisYear(v);
  GSLog.Info("I6 CONTROL_SERVICE|"+tag+"|"+a+"|"+b+"|"+s.a+"|"+s.b+"|"+s.vehicles[0]+"|"+s.vehicles[1]);return s;
 }
 function ShipService(tag,label,a,b,start){
  local c=Cargo(label),best=-1,price=1000000000;foreach(e,_ in GSEngineList(GSVehicle.VT_WATER))if(GSEngine.IsBuildable(e) && GSEngine.CanRefitCargo(e,c) && GSEngine.GetPrice(e)<price){best=e;price=GSEngine.GetPrice(e);}
  if(best<0)throw "No period ship for "+label;
  ::ACTIVE={mode="ship",cargo=c,a=a,b=b,engine=best,fleet=2,endpoints="industry",wagons=0,platform=2,brake=false,sep=2};
  ::MODE="ship";::CARGO=c;::A=a;::B=b;::ENGINE=best;::FLEET=2;::ENDPOINTS="industry";::CASE=tag;::HOLD_FLEET=!start;
  local rb=RouteBuilder();rb.CID=0;local s=rb.Build();::HOLD_FLEET=false;if(s==null)throw "Ship fixture failed "+tag;
  s.label<-label;s.ever_loaded<-false;s.paid<-false;s.lastprofit<-{};s.lastyear<-GSDate.GetYear(GSDate.GetCurrentDate());foreach(v in s.vehicles)s.lastprofit[v]<-GSVehicle.GetProfitThisYear(v);
  GSLog.Info("I6 CONTROL_SERVICE|"+tag+"|"+a+"|"+b+"|"+s.a+"|"+s.b+"|"+s.vehicles[0]+"|"+s.vehicles[1]);return s;
 }
 function Toggle(s){foreach(v in s.vehicles)GSVehicle.StartStopVehicle(v);}
 function Sample(s){
  local yr=GSDate.GetYear(GSDate.GetCurrentDate());if(yr!=s.lastyear){foreach(v in s.vehicles)s.lastprofit[v]=GSVehicle.GetProfitThisYear(v);s.lastyear=yr;}
  foreach(v in s.vehicles){local load=GSVehicle.GetCargoLoad(v,Cargo(s.label)),profit=GSVehicle.GetProfitThisYear(v),d=GSMap.DistanceManhattan(GSVehicle.GetLocation(v),s.b);
   if(load>0)s.ever_loaded=true;
   if(s.ever_loaded && d<=10 && profit>s.lastprofit[v] && !s.paid){s.paid=true;GSLog.Info("I6 CONTROL_PAID|"+s.tag+"|"+v+"|"+(profit-s.lastprofit[v])+"|"+d+"|"+GSVehicle.GetLocation(v));}
   s.lastprofit[v]=profit;
  }
 }
'''


def script(kind):
    setup='''class CoastalProbe extends GSController {
'''+COMMON+'''
 function Start(){try{
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSCompany.ChangeBankBalance(0,100000000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
GSGameSettings.SetValue("construction.industry_platform",0);
local cm=GSCompanyMode(0);GSRoad.SetCurrentRoadType(0);
'''
    if kind=='copper':
        setup+='''local ore=Build(64,25,160),coal=Build(0,50,160),quarry=Build(10,25,130),works=Build(123,70,160),customer=CoastIndustry(46,GSIndustry.GetLocation(works));
local first=Service("ore_to_copper","CORE",ore,works,true),second=Service("coal_to_copper","COAL",coal,works,false),third=Service("sand_to_copper","SAND",quarry,works,false),out=Service("copper_to_export","COPR",works,customer,false);
local phase=0,negative1=false,negative2=false,produced=false;
for(local tick=0;tick<400000;tick+=5){Sleep(5);foreach(s in [first,second,third,out])Sample(s);
 local a=GSIndustry.GetStockpiledCargo(works,Cargo("CORE")),b=GSIndustry.GetStockpiledCargo(works,Cargo("COAL")),c=GSIndustry.GetStockpiledCargo(works,Cargo("SAND")),p=GSIndustry.GetLastMonthProduction(works,Cargo("COPR"));
 if(phase==0 && a>=6){if(p!=0 || b!=0 || c!=0)throw "Copper lone-ore control failed";negative1=true;GSLog.Info("I6 CONTROL_NEGATIVE|copper_ore_only|"+a+"|"+b+"|"+c+"|"+p);Toggle(second);phase=1;}
 if(phase==1 && b>=18){if(p!=0 || c!=0)throw "Copper missing-sand control failed";negative2=true;GSLog.Info("I6 CONTROL_NEGATIVE|copper_missing_sand|"+a+"|"+b+"|"+c+"|"+p);Toggle(third);Toggle(out);phase=2;}
 if(p>0 && !produced){produced=true;GSLog.Info("I6 CONTROL_PRODUCTION|"+p);}
 if(negative1 && negative2 && produced && out.paid){GSLog.Info("I6 CONTROL_PASS|copper|production="+p+"|output_paid="+out.paid);break;}
 if(tick>=399995)GSLog.Info("I6 CONTROL_BLOCKED|copper|phase="+phase+"|production="+p+"|paid="+out.paid);
}
'''
    elif kind=='meat':
        setup+='''local raw=Build(27,25,135),salt=Build(105,25,170),works=Build(125,90,155),customer=CoastIndustry(39,GSMap.GetTileIndex(110,189));
local first=Service("salt_to_meat","SALT",salt,works,true),second=Service("livestock_to_cure","LVST",raw,works,false),out=Service("preserved_meat_to_market","FOOD",works,customer,false);
local phase=0,negative=false,produced=false;
for(local tick=0;tick<400000;tick+=5){Sleep(5);foreach(s in [first,second,out])Sample(s);
 local a=GSIndustry.GetStockpiledCargo(works,Cargo("SALT")),b=GSIndustry.GetStockpiledCargo(works,Cargo("LVST")),p=GSIndustry.GetLastMonthProduction(works,Cargo("FOOD"));
 if(phase==0 && a>=1){if(p!=0 || b!=0)throw "Salt alone incorrectly produced food";negative=true;GSLog.Info("I6 CONTROL_NEGATIVE|salt_only|"+a+"|"+b+"|"+p);Toggle(second);Toggle(out);phase=1;}
 if(p>0 && !produced){produced=true;GSLog.Info("I6 CONTROL_PRODUCTION|"+p);}
 if(negative && produced && out.paid){GSLog.Info("I6 CONTROL_PASS|meat_curing|production="+p+"|output_paid="+out.paid);break;}
 if(tick>=399995)GSLog.Info("I6 CONTROL_BLOCKED|meat|phase="+phase+"|production="+p+"|paid="+out.paid);
}
'''
    else:
        setup+='''local raw=Build(32,25,190),salt=Build(105,130,155),works=Build(124,85,184),customer=CoastIndustry(39,GSMap.GetTileIndex(160,189));
local first=Service("salt_to_fish","SALT",salt,works,true),second=ShipService("fresh_fish_to_cure","FISH",raw,works,false),out=Service("preserved_fish_to_market","FOOD",works,customer,false);
local phase=0,negative=false,produced=false;
for(local tick=0;tick<400000;tick+=5){Sleep(5);foreach(s in [first,second,out])Sample(s);
 local a=GSIndustry.GetStockpiledCargo(works,Cargo("SALT")),b=GSIndustry.GetStockpiledCargo(works,Cargo("FISH")),p=GSIndustry.GetLastMonthProduction(works,Cargo("FOOD"));
 if(phase==0 && a>=1){if(p!=0 || b!=0)throw "Salt alone incorrectly produced fish food";negative=true;GSLog.Info("I6 CONTROL_NEGATIVE|fish_salt_only|"+a+"|"+b+"|"+p);Toggle(second);Toggle(out);phase=1;}
 if(p>0 && !produced){produced=true;GSLog.Info("I6 CONTROL_PRODUCTION|"+p);}
 if(negative && produced && out.paid){GSLog.Info("I6 CONTROL_PASS|fish_curing|production="+p+"|output_paid="+out.paid);break;}
 if(tick>=399995)GSLog.Info("I6 CONTROL_BLOCKED|fish|phase="+phase+"|production="+p+"|paid="+out.paid);
}
'''
    return builder()+setup+'''GSGame.Pause();GSLog.Info("C6 DONE production control");}catch(error){GSLog.Error("I6 CONTROL_ERROR|"+error);}while(true)Sleep(365);}}
'''


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['copper','meat','fish']);a=p.parse_args()
    home=fresh(script(a.kind),'control-'+a.kind,600000)
    (BASE/('control-'+a.kind+'-case.txt')).write_text(str(home))
    log=(home/'engine.log').read_text(encoding='utf8')
    expected={'copper':'copper','meat':'meat_curing','fish':'fish_curing'}[a.kind]
    assert 'I6 CONTROL_PASS|'+expected+'|' in log, 'Loaded-output control failed; inspect '+str(home)
