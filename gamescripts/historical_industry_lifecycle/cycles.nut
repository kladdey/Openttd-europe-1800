/* GS v6/schema5. Direct production control only for one newly created neutral site. */
require("cycles_policy.nut");
class CyclesController extends PortsController {
 cycle_loading=false;
 function SiteReason(tile,e){
  if(("coastal" in e)&&e.coastal){local coast=PortsController.SiteReason.bindenv(this);return coast(tile,e);}
  local land=ProgressionController.SiteReason.bindenv(this);return land(tile,e);
 }
 function Save(){if(state!=null){local out=clone state;out.schema=5;return out;}
 if(loaded!=null&&cycle_loading){local out=clone loaded;out.schema=5;return out;}
return loaded;}
 function Initialize(now){
  if(loaded!=null){if(!("schema" in loaded)||loaded.schema!=5||!("cycle_contract" in loaded)||loaded.cycle_contract!=Hash(CYCLE_CONTRACT_TEXT))throw "Cycles require fresh candidate or exact schema5 policy; no migration";
   loaded=clone loaded;loaded.schema=4;cycle_loading=true;}
  local initialize_parent=PortsController.Initialize.bindenv(this);initialize_parent(now);state.schema=5;
  if(!("cycles" in state)){state.cycle_contract<-Hash(CYCLE_CONTRACT_TEXT);state.cycles<-{boom="planned",downturn="planned",stage="planned",signature=null,attempts=0,batches=0,last_month=-1,base_flags=0,base_level=16,boosted=false};}
  if(state.cycle_contract!=Hash(CYCLE_CONTRACT_TEXT))throw "Cycle policy contract mismatch";
 }
 function CycleConsumer(){
  foreach(i,_ in GSIndustryList()){
   if(GSMap.DistanceManhattan(GSIndustry.GetLocation(i),CYCLE.site.sites[0])>160)continue;
   foreach(c,_ in GSIndustryType.GetAcceptedCargo(GSIndustry.GetIndustryType(i))){
    if(GSCargo.GetCargoLabel(c)=="COAL")return true;
   }
  }
  return false;
 }
 function CycleLevel(level,tag){local r=state.cycles;
  if(r.signature==null||!Matches(r.signature.id,r.signature))throw "Cycle target identity lost; refusing reused ID";
  foreach(s in state.baseline)if(s.id==r.signature.id)throw "Cycle cannot control original industry";
  local i=r.signature.id;
  GSIndustry.SetControlFlags(i,GSIndustry.GetControlFlags(i)|GSIndustry.INDCTL_NO_CLOSURE);
  if(!GSIndustry.SetProductionLevel(i,level,false,null))throw "Native cycle production refused";
  r.last_change<-Calendar();
  Log("cycle_level",tag,"industry="+i+"|level="+GSIndustry.GetProductionLevel(i)+"|calendar="+Calendar());
 }
 function CycleTick(now){local r=state.cycles,month=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
  if(r.stage=="cancelled"||r.stage=="ended")return;
  if(r.signature!=null&&!Matches(r.signature.id,r.signature)){r.boom="cancelled";r.downturn="cancelled";r.stage="cancelled";Log("cycle_cancelled","identity","No reconstruction or reassignment");return;}
  if(r.signature==null){
   if(now<CYCLE.open_date||r.last_month==month)return;r.last_month=month;
   if(now>CYCLE.latest_open||r.batches>=6||r.attempts>=96){r.boom="cancelled";r.downturn="cancelled";r.stage="cancelled";return;}
   if(!CycleConsumer()||!GSIndustryType.CanBuildIndustry(Type(0)))return;
   r.batches++;local before={};foreach(i,_ in GSIndustryList())before[i]<-true;
   foreach(t in CYCLE.site.sites){if(!ExpansionSafe(t,CYCLE.site))continue;if(r.attempts>=96)break;r.attempts++;
    if(GSIndustryType.BuildIndustry(Type(0),t)){foreach(i,_ in GSIndustryList())if(!(i in before)){r.signature=Signature(i);r.base_flags=GSIndustry.GetControlFlags(i);r.base_level=GSIndustry.GetProductionLevel(i);r.stage="baseline";r.boom="active";CycleLevel(r.base_level,"baseline");News("ruhr_boom","Ruhr expansion: a new neutral coal opportunity; later capacity changes are scenario policy, available to every company.",GSIndustry.GetLocation(i));Log("cycle_opened","ruhr","industry="+i+"|tile="+r.signature.tile+"|calendar="+now);break;}
    }
    if(r.signature!=null)break;
   }
  }
  if(r.signature==null)return;
  if(now>=CYCLE.end_date){CycleLevel(r.base_level,"restored");local i=r.signature.id,mask=GSIndustry.INDCTL_NO_CLOSURE|GSIndustry.INDCTL_EXTERNAL_PROD_LEVEL;
   GSIndustry.SetControlFlags(i,(GSIndustry.GetControlFlags(i)&~mask)|(r.base_flags&mask));r.boom="ended";r.downturn="ended";r.stage="ended";
   News("ruhr_recovery","Ruhr cycle ended: the pilot mine returns to normal native production control. No company preference or guaranteed profit.",r.signature.tile);return;}
  if(now>=CYCLE.down_date&&r.stage!="downturn"){CycleLevel(CYCLE.down_level,"downturn");r.boom="ended";r.downturn="active";r.stage="downturn";News("ruhr_downturn","Ruhr downturn: temporary capacity reduction at the pilot mine; original mines are unaffected.",r.signature.tile);return;}
  if(now>=CYCLE.boost_date&&!r.boosted&&now<CYCLE.down_date){CycleLevel(CYCLE.boom_level,"boom");r.boosted=true;r.stage="boom";News("ruhr_boost","Ruhr pilot mine capacity expands; freight opportunities are public, with no company reservation.",r.signature.tile);}
 }
 function Tick(now){local tick_parent=PortsController.Tick.bindenv(this);tick_parent(now);CycleTick(now);}
}
