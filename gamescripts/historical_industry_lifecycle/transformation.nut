/* GS v7/schema6: two additive, signature-guarded regional transformations. */
require("transformation_policy.nut");
class TransformationController extends CyclesController {
 transformation_loading=false;
 function Save(){
  if(state!=null){local saved=clone state;saved.schema=6;return saved;}
  if(loaded!=null&&transformation_loading){local saved=clone loaded;saved.schema=6;return saved;}
  return loaded;
 }
 function Initialize(now){
  if(loaded!=null){
   if(!("schema" in loaded)||loaded.schema!=6||!("transformation_contract" in loaded)||loaded.transformation_contract!=Hash(TRANSFORMATION_TEXT))throw "Fresh transformation candidate or exact schema6 contract required; no migration";
   loaded=clone loaded;loaded.schema=5;transformation_loading=true;
  }
  local initialize_parent=CyclesController.Initialize.bindenv(this);initialize_parent(now);state.schema=6;
  if(!("transformation" in state)){
   state.transformation_contract<-Hash(TRANSFORMATION_TEXT);state.transformation<-{};
   foreach(e in TRANSFORMATION.events)state.transformation[e.id]<-{status="planned",stage="planned",signature=null,attempts=0,batches=0,last_month=-1,base_flags=0,base_level=16,changed=-1,closing_economy=-1};
  }
  if(state.transformation_contract!=Hash(TRANSFORMATION_TEXT)||state.transformation.len()!=2)throw "Transformation contract/ledger mismatch";
 }
 function TransformationReady(e){
  foreach(pair in [[e.producer,true],[e.consumer,false]]){
   local found=false;
   foreach(i,_ in GSIndustryList()){
    local radius=pair[1]?e.producer_radius:160;
    if(radius>0&&GSMap.DistanceManhattan(GSIndustry.GetLocation(i),e.sites[0])>radius)continue;
    local cargos=pair[1]?GSIndustryType.GetProducedCargo(GSIndustry.GetIndustryType(i)):GSIndustryType.GetAcceptedCargo(GSIndustry.GetIndustryType(i));
    foreach(c,_ in cargos){if(GSCargo.GetCargoLabel(c)==pair[0])found=true;}
   }
   if(!found)return false;
  }
  return true;
 }
 function TransformationTarget(r){
  if(r.signature==null||!Matches(r.signature.id,r.signature))return false;
  foreach(sig in state.baseline){if(Matches(r.signature.id,sig))throw "Original industry control forbidden";}
  return true;
 }
 function TransformationLevel(r,level){
  if(!TransformationTarget(r))throw "Transformation identity changed";
  if(!GSIndustry.SetProductionLevel(r.signature.id,level,false,null))throw "Native production command refused";
 }
 function TransformationTick(now){
  local month=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
  foreach(e in TRANSFORMATION.events){
   local r=state.transformation[e.id];
   if(r.status=="ended"||r.status=="cancelled")continue;
   if(r.stage=="closing"){
    if(!Matches(r.signature.id,r.signature)){r.status="ended";r.stage="retired";Log("h_retired",e.id,"industry="+r.signature.id+"|calendar="+now);continue;}
    if(GSDate.GetCurrentDate()-r.closing_economy>180){TransformationLevel(r,r.base_level);GSIndustry.SetControlFlags(r.signature.id,r.base_flags);r.status="cancelled";r.stage="closure_failed";Log("h_cancelled",e.id,"Native retirement timed out; capacity/control restored");}
    continue;
   }
   if(r.signature!=null&&!TransformationTarget(r)){r.status="cancelled";r.stage="lost";continue;}
   if(r.last_month==month)continue;r.last_month=month;
   if(r.signature==null){
    if(now<e.open_date)continue;
    if(now>e.latest_open||r.batches>=6||r.attempts>=96){r.status="cancelled";continue;}
    if(!TransformationReady(e)||!GSIndustryType.CanBuildIndustry(Type(e.local_id)))continue;
    r.batches++;local before={};foreach(i,_ in GSIndustryList())before[i]<-true;
    foreach(t in e.sites){
     if(!ExpansionSafe(t,e))continue;if(r.attempts>=96)break;r.attempts++;
     if(GSIndustryType.BuildIndustry(Type(e.local_id),t)){
      foreach(i,_ in GSIndustryList()){
       if(i in before)continue;
       r.signature=Signature(i);r.base_flags=GSIndustry.GetControlFlags(i);r.base_level=GSIndustry.GetProductionLevel(i);r.status="active";r.stage="operating";r.changed=now;
       if(e.kind=="retire"){GSIndustry.SetControlFlags(i,r.base_flags|GSIndustry.INDCTL_NO_CLOSURE);TransformationLevel(r,r.base_level);}
       Log("h_opened",e.id,"industry="+i+"|local_id="+e.local_id+"|tile="+r.signature.tile+"|calendar="+now);
       foreach(c,_ in GSIndustryType.GetAcceptedCargo(Type(e.local_id)))Log("h_accepts",e.id,"cargo="+GSCargo.GetCargoLabel(c)+"|accepted="+(GSIndustry.IsCargoAccepted(i,c)==GSIndustry.CAS_ACCEPTED));
       foreach(c,_ in GSIndustryType.GetProducedCargo(Type(e.local_id)))Log("h_outputs",e.id,"cargo="+GSCargo.GetCargoLabel(c));
       News(e.id,e.region+": a new neutral "+e.industry+" freight opportunity is available to all companies.",r.signature.tile);
       if(e.kind=="open"){r.status="ended";r.stage="opened";}
       break;
      }
     }
     if(r.signature!=null)break;
    }
   }
   if(r.signature==null||e.kind!="retire")continue;
   if(now>=e.retire_date){
    GSIndustry.SetControlFlags(r.signature.id,GSIndustry.GetControlFlags(r.signature.id)&~GSIndustry.INDCTL_NO_CLOSURE);TransformationLevel(r,4);r.stage="closing";r.changed=now;r.closing_economy=GSDate.GetCurrentDate();
    Log("h_retire_command",e.id,"industry="+r.signature.id+"|calendar="+now+"|level=4");News(e.id,"Silesian pilot mine retirement begins after the announced decline; original mines are unaffected.",r.signature.tile);continue;
   }
   if(now>=e.decline_date&&r.stage!="declining"){
    TransformationLevel(r,8);r.stage="declining";r.changed=now;Log("h_decline",e.id,"industry="+r.signature.id+"|calendar="+now+"|level=8");News(e.id,"Silesian pilot capacity declines; planned retirement follows. No company receives compensation or reservation.",r.signature.tile);
   }
  }
 }
 function Tick(now){local tick_parent=CyclesController.Tick.bindenv(this);tick_parent(now);TransformationTick(now);}
}
