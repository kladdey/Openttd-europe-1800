"""Actual chained deliveries and normal-budget finance on disposable Europe copies."""
import argparse,json,re
from pathlib import Path
from inland_phase6c_runtime import ROOT,BASE,run,sha
from industrial_phase6b_controls import builder,COMMON
from transport_phase4 import squirrel


def distance(a,b):return abs(a['x']-b['x'])+abs(a['y']-b['y'])


def plan_case(name,rank=0):
    g=json.loads((ROOT/'docs/research/industry_chain_graph.json').read_text())['industries'];g={int(k):v|dict(industry_id=int(k)) for k,v in g.items()}
    markets=[r for r in json.loads((BASE/'placement.json').read_text())['results'] if r['status']=='PLACED']
    def leg(label,a,b,mode='road'):return dict(label=label,a=a['industry_id'],b=b['industry_id'],mode=mode,manhattan=distance(a,b),a_tile=a['y']*4096+a['x'],b_tile=b['y']*4096+b['x'])
    if name=='coastal_goods_water':
        # Existing British coastal fibre source, textile mill and export wharf.
        # Selected after two road fixtures were blocked; actual water access
        # and cargo refits remain subject to engine validation below.
        return [leg('FICR',g[176],g[358],'ship'),leg('GOOD',g[358],g[458],'ship')]
    if name=='farm_fruit':
        options=[(distance(p,m),p,m) for p in g.values() if p['local_id']==47 for m in markets if m['local_id']==59 and 15<=distance(p,m)<=100]
        _,raw,customer=min(options,key=lambda x:x[0]);return [leg('FRUT',raw,customer)]
    if name=='copper_regression':
        works=next(v for v in g.values() if v['local_id']==123);ore=next(v for v in g.values() if v['local_id']==64 and v['y']<1100)
        coal=min([v for v in g.values() if v['local_id']==0],key=lambda x:distance(x,works));sand=min([v for v in g.values() if v['local_id']==10],key=lambda x:distance(x,works));customer=min([v for v in g.values() if v['local_id']==46],key=lambda x:distance(x,works))
        return [leg('CORE',ore,works),leg('COAL',coal,works),leg('SAND',sand,works),leg('COPR',works,customer)]
    if name=='salt_regression':
        works=min([v for v in g.values() if v['local_id']==125 and v['region']=='PL'],key=lambda x:min(distance(x,m) for m in markets if 'FOOD' in m['accepted_labels']))
        salt=min([v for v in g.values() if v['local_id']==105],key=lambda x:distance(x,works));raw=min([v for v in g.values() if v['local_id'] in [27,48]],key=lambda x:distance(x,works));customer=min([v for v in markets if 'FOOD' in v['accepted_labels']],key=lambda x:distance(x,works))
        return [leg('SALT',salt,works),leg('LVST',raw,works),leg('FOOD',works,customer)]
    if name=='coastal_food':
        candidates=[]
        for works in [v for v in g.values() if v['local_id']==90]:
            raw=min([v for v in g.values() if v['local_id']==32],key=lambda x:distance(x,works))
            for customer in [v for v in g.values() if v['local_id']==39 and 20<=distance(v,works)<=140]:candidates.append((distance(raw,works)+distance(works,customer),raw,works,customer))
        _,raw,works,customer=min(candidates,key=lambda x:x[0]);return [leg('FISH',raw,works,'ship'),leg('FOOD',works,customer,'ship')]
    food=name in ['local_food','regional_food','rail_food']
    label='FOOD' if food else 'GOOD';stype=34 if food else 42;rtype=26 if food else 48;input_='GRAI' if food else 'FICR'
    region={'local_food':'PL','regional_food':'GB','rail_food':'PL','local_goods':'CE','long_goods':'FR'}.get(name)
    candidates=[]
    for works in [v for v in g.values() if v['local_id']==stype and (region is None or v['region']==region)]:
        raw=min([v for v in g.values() if v['local_id']==rtype],key=lambda x:distance(x,works));d=distance(raw,works)
        if d>80:continue
        customers=[v for v in g.values() if v['local_id']==46] if name=='coastal_goods' else [m for m in markets if label in m['accepted_labels']]
        for customer in customers:
            out=distance(works,customer)
            if name=='long_goods' and not 100<=out<=220:continue
            if name=='coastal_goods' and not 10<=out<=180:continue
            if out<6:continue
            candidates.append((out+d,raw,works,customer))
    _,raw,works,customer=sorted(candidates,key=lambda x:x[0])[rank];return [leg(input_,raw,works,'rail' if name=='rail_food' else 'road'),leg(label,works,customer)]


EXTRA='''
 function RailService(tag,label,a,b){
  local c=Cargo(label),engine=-1,price=-1;foreach(e,_ in GSEngineList(GSVehicle.VT_RAIL))if(GSEngine.IsBuildable(e) && !GSEngine.IsWagon(e) && GSEngine.GetPower(e)>price){engine=e;price=GSEngine.GetPower(e);}
  if(engine<0)throw "No available 1830 locomotive";
  local wagon=-1,wp=1000000000;foreach(e,_ in GSEngineList(GSVehicle.VT_RAIL))if(GSEngine.IsBuildable(e) && GSEngine.IsWagon(e) && GSEngine.GetCapacity(e)>0 && GSEngine.CanRefitCargo(e,c) && GSEngine.GetRailType(e)==GSEngine.GetRailType(engine) && GSEngine.GetPrice(e)<wp){wagon=e;wp=GSEngine.GetPrice(e);}
  if(GSEngine.IsBuildable(1430) && GSEngine.CanRefitCargo(1430,c) && GSEngine.GetRailType(1430)==GSEngine.GetRailType(engine))wagon=1430;
  if(wagon<0)throw "No period compatible refittable wagon";
  ::RAIL_WAGON= wagon;::ACTIVE={mode="rail",cargo=c,a=a,b=b,engine=engine,fleet=1,endpoints="industry",wagons=12,platform=4,brake=true,sep=2};
  ::MODE="rail";::CARGO=c;::A=a;::B=b;::ENGINE=engine;::FLEET=1;::ENDPOINTS="industry";::WAGONS=12;::PLATFORM=4;::BRAKE_VAN=true;::CASE=tag;
  local rb=RouteBuilder();rb.CID=0;local s=rb.Build();if(s==null)throw "Rail construction failed";
  foreach(v in s.vehicles)if(GSVehicle.GetLength(v)>112)throw "Seven-tile safeguard failed";
  s.label<-label;s.ever_loaded<-false;s.paid<-false;s.lastprofit<-{};s.lastyear<-GSDate.GetYear(GSDate.GetCurrentDate());foreach(v in s.vehicles)s.lastprofit[v]<-GSVehicle.GetProfitThisYear(v);
  GSLog.Info("M6 TRAIN|"+engine+"|"+GSEngine.GetName(engine)+"|"+wagon+"|"+GSEngine.GetName(wagon)+"|"+GSVehicle.GetLength(s.vehicles[0])+"|"+GSVehicle.GetCapacity(s.vehicles[0],c));return s;
 }
 function FinancialYear(year){local row="";for(local e=0;e<15;e++)row+=GSCompany.GetAnnualExpenseValue(0,1,e)+",";
  GSLog.Info("M6 FINANCE|"+year+"|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount()+"|"+GSCompany.GetQuarterlyCompanyValue(0,0)+"|"+row);
 }
'''


def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['local_food','regional_food','rail_food','local_goods','long_goods','coastal_food','coastal_goods','coastal_goods_water','salt_regression','copper_regression','farm_fruit']);ap.add_argument('--years',type=int,default=5);ap.add_argument('--grant',action='store_true');ap.add_argument('--policy',choices=['cheapest','four_horse'],default='cheapest');ap.add_argument('--fleet',type=int,default=2);ap.add_argument('--partial-load',action='store_true');args=ap.parse_args()
    legs=plan_case(args.case,int(__import__('os').environ.get('INLAND_ROUTE_RANK','0')))
    prefix=builder().replace('CARGO==0 || CARGO==2?1462:1430','CARGO==0 || CARGO==2?1462:RAIL_WAGON')
    if not args.partial_load:
        prefix=prefix.replace('GSOrder.AppendOrder(v,a,GSOrder.OF_NONE)', 'GSOrder.AppendOrder(v,a,GSOrder.OF_FULL_LOAD_ANY)')
    prefix=prefix.replace('  return state;', '  state.path <- path;return state;')
    # Legal rail pieces can still form operationally forbidden adjacent bends.
    # Require a straight terminal approach and a straight tile between bends.
    prefix=prefix.replace('node.tile==goal && Link(', 'node.tile==goal && (MODE!="rail" || node.prev==Step(goal,1,0)) && Link(')
    guard='''    if(MODE=="rail" && node.backidx>=0){
     local grand=nodes[node.backidx].prev;
     local previous_turn=GSMap.GetTileX(grand)+GSMap.GetTileX(node.tile)!=2*GSMap.GetTileX(node.prev) || GSMap.GetTileY(grand)+GSMap.GetTileY(node.tile)!=2*GSMap.GetTileY(node.prev);
     local this_turn=GSMap.GetTileX(node.prev)+GSMap.GetTileX(next)!=2*GSMap.GetTileX(node.tile) || GSMap.GetTileY(node.prev)+GSMap.GetTileY(next)!=2*GSMap.GetTileY(node.tile);
     if(previous_turn && this_turn)continue;
    }
'''
    prefix=prefix.replace('    if(!Link(node.prev,node.tile,next))continue;',guard+'    if(!Link(node.prev,node.tile,next))continue;')

    common=COMMON
    start_road=common.index(' function Service(');end_road=common.index(' function ShipService(')
    road=common[start_road:end_road].replace('fleet=2','fleet='+str(args.fleet)).replace('::FLEET=2','::FLEET='+str(args.fleet))
    common=common[:start_road]+road+common[end_road:]
    if args.policy=='four_horse':
        common=common.replace('if(GSEngine.IsBuildable(e) && GSEngine.CanRefitCargo(e,cargo) && GSEngine.GetPrice(e)<cost)', 'if(GSEngine.IsBuildable(e) && GSEngine.GetRoadType(e)==0 && GSEngine.GetName(e).find("4 Horse")!=null && GSEngine.CanRefitCargo(e,cargo) && GSEngine.GetPrice(e)<cost)')
    if args.policy=='cheapest':
        common=common.replace('if(GSEngine.IsBuildable(e) && GSEngine.CanRefitCargo(e,cargo) && GSEngine.GetPrice(e)<cost)', 'if(GSEngine.IsBuildable(e) && GSEngine.GetRoadType(e)==0 && GSEngine.CanRefitCargo(e,cargo) && GSEngine.GetPrice(e)<cost)')
    script='LEGS <- '+squirrel(legs)+'; YEARS <- '+str(args.years)+'; GRANT <- '+('true' if args.grant else 'false')+'; RAIL_WAGON <- 1430;\n'+prefix+'class CoastalProbe extends GSController {\n'+common+EXTRA+'''function Start(){try{
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
if(GRANT && !GSCompany.ChangeBankBalance(0,1000000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID))throw "Technical grant failed";
local cm=GSCompanyMode(0);::POLICY="keep";GSRoad.SetCurrentRoadType(0);
GSLog.Info("M6 INITIAL|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount()+"|"+GSCompany.GetMaxLoanAmount()+"|grant="+GRANT+"|maintenance="+GSGameSettings.GetValue("economy.infrastructure_maintenance")+"|train_limit="+GSGameSettings.GetValue("vehicle.max_train_length"));
local services=[],rb=RouteBuilder(),before=rb.Ledger(0),start=GSDate.GetCurrentDate();
foreach(l in LEGS){::DEPOT_TILES=[];local tag=l.label+"_"+l.a+"_"+l.b;
 local s=l.mode=="rail"?RailService(tag,l.label,l.a,l.b):(l.mode=="ship"?ShipService(tag,l.label,l.a,l.b,true):Service(tag,l.label,l.a,l.b,true));services.append(s);
}
foreach(s in services)if(s.config.mode=="rail"){
 local prev=s.a;for(local i=0;i<s.path.len();i++){local cur=s.path[i],next=i+1<s.path.len()?s.path[i+1]:cur+s.config.platform-1;
  if(i+1==s.path.len())next=s.b+s.config.platform-1;
  GSLog.Info("M6 RAIL_LINK|"+i+"|"+prev+"|"+cur+"|"+next+"|"+GSRail.AreTilesConnected(prev,cur,next));prev=cur;
 }
}
local after=rb.Ledger(0),capital=(after[0]-before[0])+(after[1]-before[1]);
GSLog.Info("M6 CAPITAL|"+(after[0]-before[0])+"|"+(after[1]-before[1])+"|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount());
if(!GRANT){local target=max(0,((GSCompany.GetLoanAmount()-GSCompany.GetBankBalance(0)+10000+9999)/10000).tointeger()*10000);if(target<GSCompany.GetLoanAmount())GSCompany.SetLoanAmount(target);}
local year=GSDate.GetYear(GSDate.GetCurrentDate()),end=year+YEARS,allpaid=false;
while(GSDate.GetYear(GSDate.GetCurrentDate())<end){
 foreach(s in services)Sample(s);
 if(!allpaid){local count=0;foreach(s in services)if(s.paid)count++;if(count==services.len()){allpaid=true;GSLog.Info("M6 CHAIN_PAID|"+(GSDate.GetCurrentDate()-start)+"|legs="+count);}}
 if(!GRANT && GSCompany.GetBankBalance(0)<5000 && GSCompany.GetLoanAmount()+10000<=GSCompany.GetMaxLoanAmount()){
  GSCompany.SetLoanAmount(GSCompany.GetLoanAmount()+10000);GSLog.Info("M6 BORROW|"+GSDate.GetCurrentDate()+"|"+GSCompany.GetLoanAmount());
 }
 if(GSDate.GetYear(GSDate.GetCurrentDate())!=year){Sleep(74);FinancialYear(year);year=GSDate.GetYear(GSDate.GetCurrentDate());}
 Sleep(10);
}
Sleep(74);FinancialYear(GSDate.GetYear(GSDate.GetCurrentDate())-1);
GSLog.Info("M6 COMPLETE|all_paid="+allpaid+"|cash="+GSCompany.GetBankBalance(0)+"|loan="+GSCompany.GetLoanAmount()+"|elapsed="+(GSDate.GetCurrentDate()-start));
GSGame.Pause();GSLog.Info("C6 DONE inland service");}catch(e){GSLog.Error("M6 SERVICE_ERROR|"+e);GSGame.Pause();GSLog.Info("C6 DONE inland service blocked");}while(true)Sleep(365);}}'''
    candidate=Path(json.loads((BASE/'candidate.json').read_text())['candidate'])
    home=run(script,'service-'+args.case+'-'+args.policy+'-fleet'+str(args.fleet),(args.years+1)*30000,source=candidate,unpaused=True)
    log=(home/'engine.log').read_text(encoding='utf8');result=dict(case=args.case,vehicle_policy=args.policy,road_fleet_per_leg=args.fleet,origin_load_policy='partial/empty departures allowed' if args.partial_load else 'full load any',rail_wagon_policy='UKRS2 Open Wagon 1430 preferred, refit verified',engine_case=str(home),scenario_sha256=sha(candidate),script_sha256=sha(home/'game/coastal/main.nut'),grant=args.grant,years_requested=args.years,legs=legs,status='VERIFIED IN GAME' if 'M6 COMPLETE|all_paid=true' in log else 'BLOCKED / NO COMPLETE PAID CHAIN',events=[l.split(' M6 ',1)[1] for l in log.splitlines() if ' M6 ' in l],paid_events=[l.split(' I6 CONTROL_PAID|',1)[1] for l in log.splitlines() if ' I6 CONTROL_PAID|' in l],currency='GBP: JGRPP currency.cpp GBP rate=1; script values used without scaling')
    output=BASE/('service-'+args.case+'-'+args.policy+'-fleet'+str(args.fleet)+'.json')
    if output.exists():
        previous=json.loads(output.read_text());previous_path=BASE/('archived-'+args.case+'-'+Path(previous['engine_case']).name+'.json');previous_path.write_text(json.dumps(previous,indent=2))
    output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
