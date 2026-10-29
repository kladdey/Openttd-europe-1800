/* SPDX-License-Identifier: GPL-2.0-only
 * Version 1, schema 1. Stock JGRPP 0.73.4 + opt-in Historical AXIS 0.4.
 * No save-byte edits, engine patches, subsidies or unmanaged-site closures.
 */
require("schedule.nut");

class LifecycleController extends GSController {
 state=null; loaded=null; last_month=-1;

 function Save(){return state!=null?state:loaded;}
 function Load(version,data){loaded=data;}
 function Log(event,id,detail){GSLog.Info("P7 EVENT|"+event+"|"+id+"|"+detail);}
 function Hash(text){local h=SCHEDULE.seed;for(local i=0;i<text.len();i++)h=((h*33)^text[i])&0x7fffffff;return h;}
 function Contract(){
  local text=SCHEDULE.id+"|"+SCHEDULE.seed+"|"+SCHEDULE.test_mode;
  foreach(e in SCHEDULE.events){text+="|"+e.event_id+"|"+e.local_id+"|"+e.open_date+"|"+e.life_years+"|"+e.life_jitter_years+"|"+e.warning_years+"|"+e.max_attempts;
   if("after_closed" in e)text+="|after="+e.after_closed;
   if(SCHEDULE.test_mode)text+="|"+e.test_life_days+"|"+e.test_warning_days+"|"+e.test_service_bonus_days;
   foreach(tile in e.sites)text+="|"+tile;
  }
  return Hash(text);
 }
 function AddYears(date,years){local month=GSDate.GetMonth(date),day=GSDate.GetDayOfMonth(date);if(month==2)day=min(day,28);return GSDate.GetDate(GSDate.GetYear(date)+years,month,day);}
 function Calendar(){
  /* GSDate is economy time. A new StoryPage is stamped with actual CalTime
   * by CmdCreateStoryPage; read it and immediately remove this unshown probe.
   * Gregorian decoding is valid only for the required timekeeping mode 0. */
  local p=GSStoryPage.New(GSCompany.COMPANY_INVALID,"Historical lifecycle clock");
  if(!GSStoryPage.IsValidStoryPage(p))throw "Cannot read calendar clock safely";
  local date=GSStoryPage.GetDate(p);if(!GSStoryPage.Remove(p))throw "Cannot remove calendar probe";return date;
 }
 function News(id,text,tile){
  local ok=GSNews.Create(GSNews.NT_ECONOMY,text,GSCompany.COMPANY_INVALID,GSNews.NR_TILE,tile);
  Log("news",id,"ok="+ok+"|"+text);if(!ok)throw "Lifecycle news failed";
 }
 function Type(local_id){return GSIndustryType.ResolveNewGRFID(0x4B484531,local_id);}
 function Signature(i){return {id=i,type=GSIndustry.GetIndustryType(i),tile=GSIndustry.GetLocation(i),born=GSIndustry.GetConstructionDate(i)};}
 function Matches(i,s){return GSIndustry.IsValidIndustry(i) && GSIndustry.GetIndustryType(i)==s.type && GSIndustry.GetLocation(i)==s.tile && GSIndustry.GetConstructionDate(i)==s.born;}
 function Reconcile(r){
  if(r.signature==null)return false;
  if(Matches(r.signature.id,r.signature))return true;
  local matches=[];foreach(i,_ in GSIndustryList())if(Matches(i,r.signature))matches.append(i);
  if(matches.len()==1){r.signature.id=matches[0];return true;}
  if(matches.len()>1)throw "Ambiguous industry identity";return false;
 }
 function EligibleTile(tile){
  if(!GSMap.IsValidTile(tile))return false;
  /* Check the union bounding box of every coal layout. Do not level ground,
   * demolish houses/roads/industry, or remove protected infrastructure. */
  local x=GSMap.GetTileX(tile),y=GSMap.GetTileY(tile);if(x<2||y<2||x+6>=GSMap.GetMapSizeX()||y+6>=GSMap.GetMapSizeY())return false;
  local height=GSTile.GetMinHeight(tile);
  for(local dx=0;dx<5;dx++)for(local dy=0;dy<5;dy++){
   local t=GSMap.GetTileIndex(x+dx,y+dy);
   if(!GSTile.IsBuildable(t)||GSRoad.IsRoadTile(t)||GSTile.IsWaterTile(t)||GSTile.GetMinHeight(t)!=height||GSTile.GetMaxHeight(t)!=height)return false;
  }
  return true;
 }
 function Initialize(now){
  if(loaded!=null){
   if(("schema" in loaded) && loaded.schema==0){
    foreach(id,r in loaded.events){if(!("signature" in r))throw "Unsafe legacy ledger";
     if(!("batches" in r))r.batches<-0;if(!("last_observation_month" in r))r.last_observation_month<-GSDate.GetYear(now)*12+GSDate.GetMonth(now);}
    loaded.schema=1;Log("migrated","scheduler","schema=0->1");
   }
   if(!("schema" in loaded)||loaded.schema!=1)throw "Unsupported saved lifecycle schema; refusing reset";
   if(loaded.schedule_id!=SCHEDULE.id || loaded.seed!=SCHEDULE.seed)throw "Schedule/seed mismatch; explicit migration required";
   if("schedule_contract" in loaded){if(loaded.schedule_contract!=Contract())throw "Schedule contract changed; explicit migration required";}
   else{loaded.schedule_contract<-Contract();Log("legacy_contract","scheduler","Adopted contract for pinned pre-release schema; arbitrary legacy schedules are not supported");}
   state=loaded;Log("loaded","scheduler","schema=1|events="+state.events.len());return;
  }
  local earliest=2147483647;foreach(e in SCHEDULE.events)earliest=min(earliest,e.open_date);
  /* If state was lost after the first event, do not reopen closed/old events.
   * A normal restart uses Save/Load; destructive restart fails closed. */
  if(now>=earliest)throw "Missing lifecycle ledger after schedule start; refusing duplicate bootstrap";
  state={schema=1,schedule_id=SCHEDULE.id,schedule_contract=Contract(),seed=SCHEDULE.seed,events={},baseline=[],last_calendar=now};
  foreach(i,_ in GSIndustryList())state.baseline.append(Signature(i));
  foreach(e in SCHEDULE.events)state.events[e.event_id]<-{status="planned",signature=null,attempts=0,batches=0,last_attempt_month=-1,service_months=0,bonus=0,warn_date=-1,reminded=false,close_date=-1,last_observation_month=-1};
  Log("initialized","scheduler","baseline="+state.baseline.len()+"|calendar="+now+"|economy="+GSDate.GetCurrentDate());
 }
 function Open(e,r,now,month){
  if(now<e.open_date)return;
  if("after_closed" in e && state.events[e.after_closed].status!="closed")return;
  if(r.last_attempt_month==month)return;
  if(r.batches>=3){r.status="failed";Log("failed",e.event_id,"Three bounded monthly search batches exhausted");return;}
  r.batches++;
  r.last_attempt_month=month;r.status="eligible";
  Log("construction_context",e.event_id,"deity="+GSCompanyMode.IsDeity()+"|multiple_per_town="+GSGameSettings.GetValue("economy.multiple_industry_per_town"));
  local type=Type(e.local_id);
  if(!GSIndustryType.IsValidIndustryType(type)){r.status="failed";Log("failed",e.event_id,"Unregistered industry type");return;}
  if(!GSIndustryType.CanBuildIndustry(type)){
   r.attempts++;Log("deferred",e.event_id,"Availability rejected; attempt="+r.attempts);
   if(r.attempts>=e.max_attempts)r.status="failed";return;
  }
  local existing={};foreach(i,_ in GSIndustryList())existing[i]<-true;
  r.status="opening";local last="No safe tile";
  foreach(tile in e.sites){
   if(r.attempts>=e.max_attempts)break;
   if(!EligibleTile(tile))continue;
   r.attempts++;
   if(GSIndustryType.BuildIndustry(type,tile)){
    local ids=[];foreach(i,_ in GSIndustryList())if(!(i in existing))ids.append(i);
    if(ids.len()!=1)throw "Construction identity mismatch";
    local id=ids[0];r.signature=Signature(id);r.status="operating";
    local life=e.life_years+(Hash(e.event_id)%(e.life_jitter_years+1));
    r.close_date=SCHEDULE.test_mode?now+e.test_life_days:AddYears(r.signature.born,life);
    if(!GSIndustry.SetControlFlags(id,GSIndustry.GetControlFlags(id)|GSIndustry.INDCTL_NO_CLOSURE))throw "Cannot protect managed mine";
    if(!GSIndustry.SetText(id,"Lifecycle event "+e.event_id+"; managed finite mine; advance warnings enabled"))throw "Cannot label managed mine";
    Log("opened",e.event_id,"industry="+id+"|type="+e.local_id+"|tile="+r.signature.tile+"|calendar="+now+"|born="+r.signature.born);
    News(e.event_id,e.name+" opens in "+e.region+". New coal transport opportunity.",r.signature.tile);return;
   }
   last=GSError.GetLastErrorString();
  }
  r.status=r.attempts>=e.max_attempts?"failed":"deferred";Log(r.status,e.event_id,"attempts="+r.attempts+"|"+last);
 }
 function Operate(e,r,now,month){
  if(!Reconcile(r)){
   if(r.status=="closing"){
    r.status="closed";Log("closed",e.event_id,"calendar="+now+"|old_industry="+r.signature.id);
    News(e.event_id,e.name+" has closed. Redirect services to announced alternatives.",r.signature.tile);
   }else{r.status="failed";Log("lost",e.event_id,"Managed industry disappeared unexpectedly");}
   return;
  }
  local i=r.signature.id;
  if(r.status=="closing"){
   if(!("close_requested_economy" in r))r.close_requested_economy<-GSDate.GetCurrentDate();
   if(GSDate.GetCurrentDate()-r.close_requested_economy>120){
    GSIndustry.SetControlFlags(i,GSIndustry.GetControlFlags(i)|GSIndustry.INDCTL_NO_CLOSURE);
    GSIndustry.SetProductionLevel(i,8,false,null);r.status="failed_closure";
    GSIndustry.SetText(i,e.name+": closure could not be applied; site remains open. Administrator review required.");
    Log("failed_closure",e.event_id,"Still exists after four economy months; remains open");
    News(e.event_id,e.name+": planned closure could not be applied; site remains open. Administrator review required.",r.signature.tile);
   }
  return;
  }
  if(r.last_observation_month!=month){
   r.last_observation_month=month;local percent=0,production=0;
   foreach(c,_ in GSIndustryType.GetProducedCargo(Type(e.local_id))){percent=max(percent,GSIndustry.GetLastMonthTransportedPercentage(i,c));production+=GSIndustry.GetLastMonthProduction(i,c);}
   Log("production",e.event_id,"level="+GSIndustry.GetProductionLevel(i)+"|output="+production+"|transport_percent="+percent);
   if(percent>=40)r.service_months++;
   local bonus=r.service_months>=60?15:(r.service_months>=12?10:0);
   if(bonus>r.bonus){
    local extra=SCHEDULE.test_mode?(e.test_service_bonus_days*(bonus-r.bonus)/10).tointeger():(AddYears(r.close_date,bonus-r.bonus)-r.close_date);
    r.close_date+=extra;r.bonus=bonus;Log("longevity",e.event_id,"served_months="+r.service_months+"|close_date="+r.close_date);
    if(r.status=="warned"){
     GSIndustry.SetText(i,e.name+": warned decline; earliest closure year "+GSDate.GetYear(r.close_date)+". Sustained service extended the closure window.");
     News(e.event_id,e.name+": sustained service extends the announced closure window to calendar year "+GSDate.GetYear(r.close_date)+".",r.signature.tile);
    }
   }
  }
  local warning_date=SCHEDULE.test_mode?r.close_date-e.test_warning_days:AddYears(r.close_date,-e.warning_years);
  local protected_until=SCHEDULE.test_mode?now+e.test_warning_days:AddYears(now,e.warning_years);
  if(r.status=="operating" && now>=warning_date){
   r.status="warned";r.warn_date=now;
   /* At least the configured lead from the actual warning, even after a late
    * load or an accelerated calendar. No silent instant catch-up closure. */
   r.close_date=max(r.close_date,protected_until);
   News(e.event_id,e.name+" enters decline: finite workings. Earliest closure calendar year "+GSDate.GetYear(r.close_date)+". Plan replacement routes.",r.signature.tile);
   if(!GSIndustry.SetText(i,e.name+": finite workings in warned decline. Earliest planned closure year "+GSDate.GetYear(r.close_date)+"; sustained service may extend this. Plan replacement routes."))throw "Cannot persist warning text";
   if(!GSIndustry.SetProductionLevel(i,8,true,"Managed mine enters warned decline"))throw "Decline command rejected";
   Log("decline",e.event_id,"level="+GSIndustry.GetProductionLevel(i)+"|warn="+now+"|close="+r.close_date);
  }
  if(r.status=="warned" && !r.reminded && now>=(SCHEDULE.test_mode?r.close_date-60:AddYears(r.close_date,-2))){
   r.reminded=true;News(e.event_id,e.name+": closure window approaching. Check replacement coal services.",r.signature.tile);
  }
  if(r.status=="warned" && now>=r.close_date){
   if(e.local_id!=0)throw "Closure adapter supports managed coal mines only";
   /* Retain engine last-instance protection; never claim success from state. */
   local count=0;foreach(j,_ in GSIndustryList())if(GSIndustry.GetIndustryType(j)==Type(0))count++;
   foreach(other_id,row in state.events)if(row.status=="closing" && row.signature!=null && Matches(row.signature.id,row.signature))count--;
   if(count<=1){
    r.status="deferred_closure";Log("deferred_closure",e.event_id,"Last-instance protection");
    GSIndustry.SetText(i,e.name+": closure deferred to protect the last operating coal producer; remains open.");
    News(e.event_id,e.name+": closure deferred to protect the last operating coal producer.",r.signature.tile);return;
   }
   local flags=GSIndustry.GetControlFlags(i)&~GSIndustry.INDCTL_NO_CLOSURE;
   if(!GSIndustry.SetControlFlags(i,flags)||!GSIndustry.SetProductionLevel(i,4,true,"Managed mine closure requested"))throw "Closure adapter rejected";
   r.close_requested_economy<-GSDate.GetCurrentDate();r.status="closing";Log("closing",e.event_id,"industry="+i+"|calendar="+now+"|warned_since="+r.warn_date);
  }
 }
 function Tick(now){
  if(now<state.last_calendar)throw "Calendar moved backwards; refusing historical replay";
  local month=GSDate.GetYear(now)*12+GSDate.GetMonth(now);state.last_calendar=now;
  foreach(e in SCHEDULE.events){
   local r=state.events[e.event_id];
   if(r.status=="planned"||r.status=="eligible"||r.status=="deferred")Open(e,r,now,month);
   else if(r.status=="operating"||r.status=="warned"||r.status=="closing")Operate(e,r,now,month);
  }
  Log("status","scheduler","calendar="+now+"|economy="+GSDate.GetCurrentDate()+"|industries="+GSIndustryList().Count());
 }
 function Start(){try{
  if(GSGameSettings.GetValue("economy.timekeeping_units")!=0)throw "Unsupported wallclock decoding; fail closed";
  if(GSNewGRF.GetVersion(0x4B484531)!=4)throw "Requires opt-in Historical AXIS 0.4 lifecycle candidate";
  local now=Calendar();Initialize(now);
  while(true){now=Calendar();Tick(now);Sleep(74*14);}
 }catch(e){GSLog.Error("P7 FATAL|"+e);while(true)Sleep(365);}}
}
