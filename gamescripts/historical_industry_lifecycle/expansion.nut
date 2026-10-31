/* SPDX-License-Identifier: GPL-2.0-only
 * V3 extends the SAME persistent controller. No reset, type-wide retirement,
 * terrain changes, company-dependent opening advantage or service subsidy.
 */
require("expansion_policy.nut");
class ExpansionLifecycleController extends LegacyLifecycleController {
 function ExpansionContract(){return Hash(EXPANSION_CONTRACT_TEXT);}
 function ValidateExpansion(){
  ValidateLegacy();
  if(state.schema!=3||!("expansion_contract" in state)||state.expansion_contract!=ExpansionContract())throw "Expansion policy contract mismatch";
  if(!("expansion" in state)||!("factory" in state)||!("expansion_active" in state))throw "Partial expansion ledger";
  if(state.expansion.len()!=(state.expansion_active?EXPANSION.events.len():0))throw "Partial expansion event set";
  foreach(e in EXPANSION.events)if(state.expansion_active){
   if(!(e.event_id in state.expansion))throw "Missing expansion event";
   local r=state.expansion[e.event_id];
   foreach(k in ["status","signature","attempts","batch","last_month","announced"])if(!(k in r))throw "Partial expansion row";
   local known=false;foreach(s in ["planned","announced","deferred","built","cancelled","lost"])if(s==r.status)known=true;
   if(!known||r.attempts<0||r.attempts>e.max_attempts||r.batch<0||r.batch>e.max_batches)throw "Invalid expansion status";
   if(r.signature!=null){local allowed=false;foreach(tile in e.sites)if(tile==r.signature.tile)allowed=true;
    if(!allowed||r.signature.type!=Type(e.local_id)||r.signature.born<e.open_date||r.signature.born>e.latest_date)throw "Expansion instance outside policy";
   }
   if(r.status=="built"&&r.signature==null)throw "Built event without instance";
  }
  if(state.factory!=null){
   local r=state.factory,s=EXPANSION.retirement;
   foreach(k in ["status","signature","warn_date","armed_economy","last_level","last_notice"])if(!(k in r))throw "Partial processor ledger";
   if(s==null||r.signature.id!=s.industry_id||r.signature.tile!=s.tile||r.signature.type!=Type(s.local_id)||r.signature.born!=s.born)throw "Processor identity mismatch";
   local ok=false;foreach(v in ["active","warning","arming","closing","closed","lost","failed","deferred"])if(v==r.status)ok=true;
   if(!ok)throw "Unknown processor state";
  }
 }
 function Initialize(now){
  local incoming=loaded;
  if(incoming!=null&&("schema" in incoming)&&incoming.schema==3){
   loaded=clone incoming;loaded.schema=2;
   local initialize_parent=LegacyLifecycleController.Initialize.bindenv(this);initialize_parent(now);
   state.schema=3;loaded=incoming;ValidateExpansion();Log("expansion_loaded","scheduler","schema=3");return;
  }
  if(incoming!=null&&EXPANSION.migration!="adopt_only")throw "Explicit adopt_only required for v2 migration; no reset or automatic enrollment";
  local initialize_parent=LegacyLifecycleController.Initialize.bindenv(this);initialize_parent(now);
  state.schema=3;state.expansion_contract<-ExpansionContract();state.expansion<-{};state.factory<-null;state.expansion_active<-incoming==null;
  if(incoming!=null){Log("expansion_adopted","scheduler","events=0|new_enrollment=0");ValidateExpansion();return;}
  foreach(e in EXPANSION.events){
   if(now>=e.open_date)throw "Missing expansion ledger after first opening";
   state.expansion[e.event_id]<-{status="planned",signature=null,attempts=0,batch=0,last_month=-1,announced=false};
  }
  if(EXPANSION.retirement!=null){local s=EXPANSION.retirement;
   if(now!=668394||GSTownList().Count()!=617||GSIndustryList().Count()!=542||!LegacyMatch(s))throw "Processor enrollment requires intact 1830 baseline";
   state.factory={status="active",signature=Signature(s.industry_id),warn_date=-1,armed_economy=-1,last_level=16,last_notice=-1};
   Log("processor_enrolled",s.site_id,"industry="+s.industry_id+"|snapshot="+s.original_record_sha256);
  }
  ValidateExpansion();
 }
 function ExpansionSafe(tile,e){
  if(!GSMap.IsValidTile(tile))return false;
  local x=GSMap.GetTileX(tile),y=GSMap.GetTileY(tile),h=GSTile.GetMinHeight(tile);
  if(x<2||y<2||x+e.width>=GSMap.GetMapSizeX()-2||y+e.height>=GSMap.GetMapSizeY()-2)return false;
  for(local dx=0;dx<e.width;dx++)for(local dy=0;dy<e.height;dy++){
   local t=GSMap.GetTileIndex(x+dx,y+dy);
   if(!GSTile.IsBuildable(t)||GSTile.IsWaterTile(t)||GSRoad.IsRoadTile(t)||GSTile.GetMinHeight(t)!=h||GSTile.GetMaxHeight(t)!=h)return false;
  }
return true;
 }
 function ChainReady(e){
  foreach(dep in e.dependencies)if(!(dep in state.expansion)||state.expansion[dep].status!="built"||!Matches(state.expansion[dep].signature.id,state.expansion[dep].signature))return false;
  foreach(label in e.required_producers){local present=false;foreach(i,_ in GSIndustryList())foreach(c,_ in GSIndustryType.GetProducedCargo(GSIndustry.GetIndustryType(i)))if(GSCargo.GetCargoLabel(c)==label)present=true;if(!present)return false;}
  foreach(label in e.required_consumers){local present=false;foreach(i,_ in GSIndustryList())foreach(c,_ in GSIndustryType.GetAcceptedCargo(GSIndustry.GetIndustryType(i)))if(GSCargo.GetCargoLabel(c)==label)present=true;if(!present)return false;}
  return true;
 }
 function ExpansionOpen(e,r,now,month){
  if(r.status=="built"){
   if(!Matches(r.signature.id,r.signature)){r.status="lost";Log("expansion_lost",e.event_id,"No rebuild or command to reused ID");}
return;
  }
  if(r.status=="cancelled"||r.status=="lost")return;
  if(!r.announced&&now>=e.announce_date){r.announced=true;r.status="announced";News(e.event_id,e.name+" planned in "+e.region+" from "+GSDate.GetYear(e.open_date)+"; no company reservation or subsidy.",e.sites[0]);}
  if(now<e.open_date||r.last_month==month)return;
  r.last_month=month;
  if(now>e.latest_date||r.attempts>=e.max_attempts||r.batch>=e.max_batches){r.status="cancelled";Log("expansion_cancelled",e.event_id,"Date/search budget exhausted; no terraforming");return;}
  if(!ChainReady(e)){r.status="deferred";Log("expansion_deferred",e.event_id,"Dependency or registered cargo endpoint missing");return;}
  if(!GSIndustryType.CanBuildIndustry(Type(e.local_id))){r.status="deferred";r.batch++;Log("expansion_deferred",e.event_id,"Type unavailable");return;}
  r.batch++;local existing={};foreach(i,_ in GSIndustryList())existing[i]<-true;
  local last="No clear level footprint";
  foreach(tile in e.sites){
   if(r.attempts>=e.max_attempts)break;
   if(!ExpansionSafe(tile,e))continue;
   r.attempts++;
   if(GSIndustryType.BuildIndustry(Type(e.local_id),tile)){
    local ids=[];foreach(i,_ in GSIndustryList())if(!(i in existing))ids.append(i);
    if(ids.len()!=1)throw "Expansion construction identity ambiguity";
    r.signature=Signature(ids[0]);r.status="built";
    if(!GSIndustry.SetControlFlags(ids[0],GSIndustry.GetControlFlags(ids[0])|GSIndustry.INDCTL_NO_CLOSURE))throw "Cannot protect new processor";
    GSIndustry.SetText(ids[0],e.name+": regional historical proxy; event "+e.event_id+". No automatic service bonus or closure.");
    Log("expansion_opened",e.event_id,"local_id="+e.local_id+"|industry="+ids[0]+"|tile="+r.signature.tile+"|born="+r.signature.born+"|calendar="+now);
    News(e.event_id,e.name+" opens in "+e.region+". New industrial transport opportunity.",r.signature.tile);return;
   }
last=GSError.GetLastErrorString();
  }
  r.status="deferred";Log("expansion_deferred",e.event_id,"attempts="+r.attempts+"|batch="+r.batch+"|"+last);
 }
 function SuccessorReady(s){
  if(!(s.successor in state.expansion))return false;
  local r=state.expansion[s.successor];
  if(r.status!="built"||r.signature==null||!Matches(r.signature.id,r.signature)||r.signature.type!=Type(s.local_id)||GSMap.DistanceManhattan(s.tile,r.signature.tile)>s.radius)return false;
  foreach(label in ["GRAI","FOOD"]){local found=false;foreach(i,_ in GSIndustryList())if(i!=s.industry_id){
   if(GSMap.DistanceManhattan(GSIndustry.GetLocation(i),r.signature.tile)>160)continue;
   local list=label=="GRAI"?GSIndustryType.GetProducedCargo(GSIndustry.GetIndustryType(i)):GSIndustryType.GetAcceptedCargo(GSIndustry.GetIndustryType(i));
   foreach(c,_ in list)if(GSCargo.GetCargoLabel(c)==label)found=true;
  }
if(!found)return false;}
  return true;
 }
 function ProcessorTick(now){
  if(state.factory==null)return;
  local r=state.factory,s=EXPANSION.retirement;
  if(r.status=="closed"||r.status=="lost"||r.status=="failed")return;
  if(!LegacyMatch(s)){
   if(r.status=="closing"){r.status="closed";Log("processor_closed",s.site_id,"calendar="+now+"|industry="+s.industry_id);News(s.site_id,"Old mill physically closed; nearby successor remains available. Transport infrastructure retained.",s.tile);}
   else{r.status="lost";Log("processor_lost",s.site_id,"No commands to replacement instance");}
return;
  }
  local econ=GSDate.GetCurrentDate();
  if(r.status=="closing"){
   if(econ-r.armed_economy>180){GSIndustry.SetControlFlags(s.industry_id,GSIndustry.GetControlFlags(s.industry_id)|GSIndustry.INDCTL_NO_CLOSURE);GSIndustry.SetProductionLevel(s.industry_id,8,false,null);r.status="failed";Log("processor_failed",s.site_id,"Physical closure timed out; reprotected");}
return;
  }
  if(r.status=="arming"){
   if(econ-r.armed_economy<40)return;
   if(econ-r.armed_economy>65||!SuccessorReady(s)){r.status="failed";GSIndustry.SetProductionLevel(s.industry_id,8,false,null);return;}
   GSIndustry.SetControlFlags(s.industry_id,GSIndustry.GetControlFlags(s.industry_id)&~GSIndustry.INDCTL_NO_CLOSURE);
   if(!GSIndustry.SetProductionLevel(s.industry_id,4,false,null))throw "Processor closure commit refused";
   r.status="closing";Log("processor_commit",s.site_id,"calendar="+now);return;
  }
  if(now<s.warning_date)return;
  if(r.warn_date<0){r.warn_date=now;r.status="warning";News(s.site_id,"Old mill modernization: at least "+s.warning_years+" calendar years before possible retirement. Nearby successor and supply chain required. No pickup-based survival bonus.",s.tile);Log("processor_warning",s.site_id,"calendar="+now+"|minimum_years="+s.warning_years);}
  local stage=min(3,max(0,((now-s.warning_date)*4/max(1,s.close_date-s.warning_date)).tointeger())),level=14-stage*2;
  if(level!=r.last_level){GSIndustry.SetControlFlags(s.industry_id,GSIndustry.GetControlFlags(s.industry_id)|GSIndustry.INDCTL_NO_CLOSURE);if(!GSIndustry.SetProductionLevel(s.industry_id,level,false,null))throw "Processor capacity change refused";r.last_level=level;Log("processor_decline",s.site_id,"calendar="+now+"|level="+level);}
  if(now<s.close_date||now<AddYears(r.warn_date,s.warning_years))return;
  if(!SuccessorReady(s)||now>s.latest_close){
   r.status="deferred";if(r.last_notice<0||now-r.last_notice>365){r.last_notice=now;News(s.site_id,"Mill retirement deferred: replacement or local cargo endpoints unavailable, or reviewed date window expired. Old mill remains open.",s.tile);Log("processor_deferred",s.site_id,"calendar="+now);}
return;
  }
  GSIndustry.SetControlFlags(s.industry_id,GSIndustry.GetControlFlags(s.industry_id)|GSIndustry.INDCTL_NO_CLOSURE);
  if(!GSIndustry.SetProductionLevel(s.industry_id,11,false,null))throw "Processor authorization refused";
  r.status="arming";r.armed_economy=econ;Log("processor_arm",s.site_id,"calendar="+now+"|token="+s.token);
 }
 function Tick(now){ValidateExpansion();local parent_tick=LegacyLifecycleController.Tick.bindenv(this);parent_tick(now);
  local month=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
  if(state.expansion_active)foreach(e in EXPANSION.events)ExpansionOpen(e,state.expansion[e.event_id],now,month);
  ProcessorTick(now);
 }
 function Start(){try{
  if(GSNewGRF.GetVersion(0x4B484531)!=6)throw "Expansion requires separate AXIS 0.6";
  if(!GSIndustryType.CanBuildIndustry(Type(0)))throw "Lifecycle opt-in disabled";
  if(GSGameSettings.GetValue("economy.timekeeping_units")!=0)throw "Wallclock unsupported";
  Initialize(Calendar());while(true){Tick(Calendar());Sleep(74*14);}
 }catch(e){GSLog.Error("P7 FATAL|"+e);while(true)Sleep(365);}}
}
