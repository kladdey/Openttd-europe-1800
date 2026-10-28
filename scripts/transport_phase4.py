"""Targeted actual-scenario gameplay suite. Isolated files only; no campaign edits."""
import argparse,hashlib,json,os,re,subprocess,time
from pathlib import Path
import transport_phase3 as previous
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.vehicle-audit-runtime/phase4';DATA=ROOT/'docs/research'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest():
    p=DATA/'transport_phase4_inputs.json'
    if not p.exists():
        files=[f for f in (ROOT/'docs').rglob('*') if f.is_file() and 'phase4' not in f.name.lower() and f.name not in ('horse_transport_tests.csv','maritime_profitability_tests.csv','three_company_simulation.csv','competition_tests.csv','MULTIPLAYER_ECONOMY_READINESS.md','FINAL_ECONOMY_ACTION_PLAN.md')]
        p.write_text(json.dumps({'branch':'audit/local-vehicle-economy','prior_research_sha256':{str(f.relative_to(ROOT)):digest(f) for f in files}},indent=2))
def route(mode,cargo,a,b,engine,fleet=1,**kw):
    return dict(mode=mode,cargo=cargo,a=a,b=b,engine=engine,fleet=fleet,endpoints=kw.pop('endpoints','town'),wagons=kw.pop('wagons',4),platform=kw.pop('platform',2),brake=kw.pop('brake',False),sep=kw.pop('sep',2),**kw)
CASES={
 'three_strategies':dict(years=20,routes=[route('ship',0,458,315,616),route('rail',14,438,456,1534,endpoints='industry',wagons=12,platform=4,brake=True),route('road',28,260,286,402,8,endpoints='industry')],expand=True),
 'three_strategies_credit':dict(years=20,routes=[route('ship',0,458,315,616),route('rail',14,438,456,1534,endpoints='industry',wagons=12,platform=4,brake=True),route('road',28,260,286,402,8,endpoints='industry')],expand=True,expand_credit=True),
 'shared_coast':dict(years=5,routes=[route('ship',0,458,315,616) for i in range(3)]),
 'shared_coast_reverse':dict(years=5,order=[2,1,0],routes=[route('ship',0,458,315,616) for i in range(3)]),
 'shared_coast_spaced':dict(years=5,dock_spacing=4,routes=[route('ship',0,458,315,616) for i in range(3)]),
 'shared_coast_clear':dict(years=5,dock_spacing=4,depot_spacing=4,routes=[route('ship',0,458,315,616) for i in range(3)]),
 'shared_coast_navigable':dict(years=5,dock_spacing=4,depot_spacing=4,clear_approaches=True,routes=[route('ship',0,458,315,616) for i in range(2)]),
 'shared_coast_navigable_reverse':dict(years=5,order=[1,0],dock_spacing=4,depot_spacing=4,clear_approaches=True,routes=[route('ship',0,458,315,616) for i in range(2)]),
 'shared_coal':dict(years=5,routes=[route('road',14,438,456,402,8,endpoints='industry') for i in range(3)]),
 'horse_local_cheap':dict(years=5,routes=[route('road',0,191,191,147,2,sep=4)]),
 'horse_local_fast':dict(years=5,routes=[route('road',0,191,191,151,2,sep=4)]),
 'horse_mail_local':dict(years=5,routes=[route('road',2,191,191,181,2,sep=4)]),
 'horse_regional':dict(years=5,routes=[route('road',0,189,96,149,2)]),
 'horse_farm_small':dict(years=5,routes=[route('road',28,260,286,402,2,endpoints='industry')]),
 'horse_farm_fleet':dict(years=5,routes=[route('road',28,260,286,402,8,endpoints='industry')]),
 'horse_fruit':dict(years=5,routes=[route('road',26,130,525,430,4,endpoints='industry')]),
 'horse_coal_control':dict(years=3,routes=[route('road',14,438,456,402,8,endpoints='industry')]),
 'horse_straight_pass':dict(years=3,routes=[route('road',0,191,191,147,2,sep=4,straight_local=True)]),
 'horse_straight_mail':dict(years=3,routes=[route('road',2,191,191,181,2,sep=4,straight_local=True)]),
 'ship_medium':dict(years=5,routes=[route('ship',0,458,463,616)]),
 'ship_long':dict(years=5,routes=[route('ship',0,324,16,616)]),
 'ship_mail':dict(years=5,routes=[route('ship',2,324,315,616)]),
 'ship_mail_open_coast':dict(years=5,routes=[route('ship',2,207,309,616)]),
 'ship_fish':dict(years=5,routes=[route('ship',25,1289,1303,616,endpoints='industry')]),
 'ship_fleet':dict(years=5,routes=[route('ship',0,458,315,616,3)]),
 'ship_low_demand':dict(years=5,routes=[route('ship',0,463,461,615)]),
}
def squirrel(v):
    if isinstance(v,bool):return 'true' if v else 'false'
    if isinstance(v,(int,float)):return str(v)
    if isinstance(v,str):return json.dumps(v)
    if isinstance(v,list):return '['+','.join(squirrel(x) for x in v)+']'
    return '{'+','.join(k+'='+squirrel(x) for k,x in v.items())+'}'
def generate(config):
    if config.get('expand_credit') and (BASE/'three-final/game/p3/main.nut').exists():
        frozen=(BASE/'three-final/game/p3/main.nut').read_text(encoding='utf8')
        marker='     if(GSCompany.GetBankBalance(2)>=16000)'
        assert frozen.count(marker)==1
        credit='''     if(GSCompany.GetBankBalance(2)<20000 && GSCompany.GetLoanAmount()+10000<=GSCompany.GetMaxLoanAmount()){
      GSCompany.SetLoanAmount(GSCompany.GetLoanAmount()+10000);
      GSLog.Info("P4_EXPANSION_FINANCE|"+GSCompany.GetBankBalance(2)+"|"+GSCompany.GetLoanAmount());
     }
'''
        return frozen.replace('expand=true};','expand=true,expand_credit=true};').replace(marker,credit+marker)
    old=(ROOT/'scripts/transport_phase3_services.nut').read_text()
    prefix,body=old.split(' function Start(){',1)
    build=body.split('  local oldyear=',1)[0]
    prefix=prefix.replace('class TransportProbe extends GSController {','class RouteBuilder extends GSController {\n CID=0;')
    # Goal-directed water flood; larger bound only in this disposable harness.
    prefix=prefix.replace('pos<100000','pos<350000').replace('>200','>700')
    prefix=prefix.replace('local t=queue[pos++];','local t=queue[pos++];if(t==goal)break;')
    prefix=prefix.replace('   if(MODE=="ship"){','   if(MODE=="ship"){\n    if(ENDPOINTS=="industry" && GSIndustry.HasDock(id))return GSIndustry.GetDockLocation(id);')
    prefix=prefix.replace('MODE=="ship"?4:3','MODE=="ship"?5:3')
    prefix=prefix.replace('  foreach(tile in Candidates(id,production)){','  foreach(tile in Candidates(id,production)){\n   if("straight_local" in ACTIVE && ACTIVE.straight_local){\n    if(production){local lane=true;for(local dx=0;dx<=MIN_SEPARATION+1;dx++)if(!GSRoad.IsRoadTile(Step(tile,-dx,0)))lane=false;if(!lane)continue;}\n    else if(GSMap.GetTileY(tile)!=GSMap.GetTileY(origin_tile) || GSMap.GetTileX(tile)!=GSMap.GetTileX(origin_tile)-MIN_SEPARATION)continue;\n   }')
    prefix=prefix.replace('    if(MODE=="rail"){','    if(MODE=="road" && !GSTile.IsBuildable(Step(tile,1,0)) && !GSRoad.IsRoadTile(Step(tile,1,0)))continue;\n    if(MODE=="rail"){',1)
    prefix=prefix.replace('if(!GSTile.IsCoastTile(tile))continue;', 'if(!GSTile.IsCoastTile(tile))continue;\n    local near=false;if("dock_spacing" in CONFIG)foreach(t in DOCK_TILES)if(GSMap.DistanceManhattan(t,tile)<CONFIG.dock_spacing)near=true;\n    if("clear_approaches" in CONFIG)foreach(t in DEPOT_TILES)if(GSMap.DistanceManhattan(t,tile)<5)near=true;\n    if(near)continue;')
    prefix=prefix.replace('if(ok && GSMarine.BuildDock(tile,GSStation.STATION_NEW))return tile;','if(ok && GSMarine.BuildDock(tile,GSStation.STATION_NEW)){DOCK_TILES.append(tile);return tile;}')
    prefix=prefix.replace('}return t;}','}for(local r=1;r<=4;r++)foreach(d in [[r,0],[-r,0],[0,r],[0,-r]]){local n=Step(t,d[0],d[1]);if(GSTile.IsWaterTile(n))return n;}return t;}')
    build=build.replace('    if(t in water && f in water && GSTile.IsWaterTile(t) && GSTile.IsWaterTile(f)){','    local crowded=false;if("depot_spacing" in CONFIG)foreach(old in DEPOT_TILES)if(GSMap.DistanceManhattan(t,old)<CONFIG.depot_spacing)crowded=true;\n    if("clear_approaches" in CONFIG)foreach(old in DOCK_TILES)if(GSMap.DistanceManhattan(t,old)<5)crowded=true;\n    if(!crowded && t in water && f in water && GSTile.IsWaterTile(t) && GSTile.IsWaterTile(f)){')
    build=build.replace('if(ok && GSMarine.BuildWaterDepot(t,f))depot=t;','if(ok && GSMarine.BuildWaterDepot(t,f)){depot=t;DEPOT_TILES.append(t);}')
    build=build.replace('    foreach(t in path){','    foreach(t in path){\n     if(GSStation.IsValidStation(GSStation.GetStationID(t)))continue;')
    build=build.replace('if(ok && GSRoad.BuildRoadDepot(d,t)){depot=d;GSRoad.BuildRoad(t,d);}','if(ok){local check=GSTestMode();ok=GSRoad.BuildRoad(t,d);check=null;}\n      if(ok && GSRoad.BuildRoadDepot(d,t)){\n       if(!GSRoad.BuildRoad(t,d) && GSError.GetLastErrorString()!="ERR_ALREADY_BUILT"){Fail("road depot connection");return null;}\n       depot=d;\n      }')
    fallback='''
  if(depot<0 && MODE=="road"){
   for(local radius=1;radius<=16 && depot<0;radius++)foreach(delta in [[radius,0],[-radius,0],[0,radius],[0,-radius]]){
    if(depot>=0)break;
    local d=Step(a,delta[0],delta[1]),front=Step(d,-1,0);
    if(!GSTile.IsBuildable(d) || (!GSTile.IsBuildable(front) && !GSRoad.IsRoadTile(front)))continue;
    local tm=GSTestMode(),ok=GSRoad.BuildRoadDepot(d,front);tm=null;
    if(!ok)continue;
    local branch=Path(Step(a,-1,0),a,front);if(branch==null)continue;
    if(!GSRoad.BuildRoadDepot(d,front))continue;
    depot=d;
    for(local i=0;i<branch.len();i++){
     local next=i+1<branch.len()?branch[i+1]:d;
     if(GSMap.DistanceManhattan(branch[i],next)>1){
      if(!GSBridge.IsBridgeTile(branch[i]))GSRoad.BuildRoad(branch[i],next);
     }else GSRoad.BuildRoad(branch[i],next);
    }
    GSLog.Info("P4_DEPOT_SPUR|"+CASE+"|"+branch.len());
   }
  }
'''
    build=build.replace('  if(depot<0){Fail("depot");return;}',fallback+'  if(depot<0){Fail("depot");return;}')
    build=build.replace('   if(MODE=="road")GSRoad.BuildRoad(a,Step(a,-1,0));','   if(MODE=="road"){\n    GSRoad.BuildRoad(a,Step(a,-1,0));\n    GSRoad.BuildRoad(a,Step(a,1,0));\n    GSRoad.BuildRoad(b,Step(b,1,0));\n   }')
    build=build.replace('return;','return null;')
    build=build.replace('P3_','P4_').replace('GSCompanyMode(0)','GSCompanyMode(CID)').replace('ResolveCompanyID(0)','ResolveCompanyID(CID)').replace('GetBankBalance(0)','GetBankBalance(CID)')
    build='  local before=Ledger(CID);\n'+build
    build+='''
  local after=Ledger(CID);
  local state={cid=CID,tag=CASE,config=ACTIVE,vehicles=vehicles,a=a,b=b,capacity=GSVehicle.GetCapacity(v,CARGO),infra=after[0]-before[0],fleet=after[1]-before[1],samples=0,loaded=0,loadsum=0,cap_sum=0,broken=0,running=0,at_station=0,speed_sum=0,loads=0,arrivals=0,prior_state=-1};
  GSLog.Info("P4_COMMISSION|"+CASE+"|"+CID+"|"+state.infra+"|"+state.fleet+"|"+state.capacity+"|"+vehicles.len()+"|"+GSDate.GetCurrentDate()+"|"+depot);
  return state;
 }
 function Ledger(cid){local out=[];for(local e=0;e<15;e++){local sum=0;for(local y=0;y<3;y++)sum+=GSCompany.GetAnnualExpenseValue(cid,y,e);out.append(sum);}return out;}
}
'''
    controller=(ROOT/'scripts/transport_phase4_controller.nut').read_text()
    globals='MODE<-"road"; CARGO<-0; A<-0; B<-0; ENGINE<-147; FLEET<-1; ENDPOINTS<-"town"; WAGONS<-4; PLATFORM<-2; BRAKE_VAN<-false; MIN_SEPARATION<-2; POLICY<-"repay_idle"; CASE<-"unset"; ACTIVE<-null; DOCK_TILES<-[]; DEPOT_TILES<-[];\n'
    return globals+'CONFIG <- '+squirrel(config)+';\n'+prefix+' function Build(){'+build+controller
def run(case,tag,ticks=None,years=None):
    manifest();conf=json.loads(json.dumps(CASES[case]));home=BASE/tag
    if years:conf['years']=years
    if home.exists():raise SystemExit('Refusing to overwrite '+str(home))
    previous.RUN=home
    previous.prepare('scripts/transport_phase3_probe.nut','')
    main=generate(conf);(home/'game/p3/main.nut').write_text(main,encoding='utf8')
    n=len(conf['routes']);(home/'scripts/game_start.scr').write_text('start_ai EconomyBootstrap\n'*n)
    # Keep the same measurement GS identity already attached to the disposable copy.
    args=[r'C:\Users\Kladd\Downloads\OpenTTD\openttd.exe','-c','test.cfg','-x','-v',f'null:ticks={ticks or (conf["years"]+2)*30000}','-s','null','-m','null','-d','script=4','-g',str(home/'scenario-test.scn')]
    (home/'manifest.json').write_text(json.dumps({'case':case,'tag':tag,'configuration':conf,'script_sha256':digest(home/'game/p3/main.nut'),'scenario_sha256':digest(home/'scenario-test.scn'),'exe_sha256':digest(Path(args[0])),'arguments':args},indent=2))
    log=home/'game.log'
    with log.open('wb') as f:
        p=subprocess.Popen(args,cwd=home,stdout=f,stderr=f);print('PID',p.pid,case,flush=True);start=time.monotonic()
        while p.poll() is None:
            time.sleep(1);raw=log.read_text(errors='replace')
            if any(s in raw for s in ['P4_DONE','The script died unexpectedly.']) or time.monotonic()-start>1800:p.kill();p.wait();break
    print('Finished',case,log,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=CASES);p.add_argument('--tag');p.add_argument('--ticks',type=int);p.add_argument('--years',type=int);a=p.parse_args();run(a.case,a.tag or a.case,a.ticks,a.years)
