/* SPDX-License-Identifier: GPL-2.0-only
 * V2 extends the same controller and scheduled-event ledger; no second GS.
 * Baseline enrollment and the GRF's independent snapshot guard are both required.
 */
require("legacy_policy.nut");
class LegacyLifecycleController extends LifecycleController {
 function PolicyContract(){return Hash(LEGACY_POLICY.id+"|"+::LEGACY_CONTRACT_TEXT);}
 function LegacyMatch(s){return GSIndustry.IsValidIndustry(s.industry_id)&&GSIndustry.GetIndustryType(s.industry_id)==s.engine_type&&GSIndustry.GetLocation(s.industry_id)==s.tile&&GSIndustry.GetConstructionDate(s.industry_id)==s.born;}
 function ValidateLegacy(){
  if(!("legacy" in state)||!("policy_contract" in state)||state.policy_contract!=PolicyContract())throw "Legacy policy contract mismatch; no reset";
  if(!("events" in state)||state.events.len()!=SCHEDULE.events.len())throw "Partial scheduled-event ledger";
  foreach(e in SCHEDULE.events){
   if(!(e.event_id in state.events))throw "Missing scheduled event";
   local row=state.events[e.event_id];
   if(!("signature" in row)||!("status" in row))throw "Partial scheduled-event row";
   if(row.signature!=null){
    local sig=row.signature,site_ok=false;foreach(tile in e.sites)if(tile==sig.tile)site_ok=true;
    if(!site_ok||sig.type!=Type(e.local_id)||sig.born<e.open_date||sig.id<0)throw "Scheduled instance fingerprint outside event";
    if(!("close_date" in row)||row.close_date<sig.born)throw "Invalid scheduled deadline";
    if(row.status=="warned"||row.status=="closing"){
     if(!("warn_date" in row)||row.warn_date<sig.born)throw "Missing scheduled warning";
     local minimum=SCHEDULE.test_mode?row.warn_date+e.test_warning_days:AddYears(row.warn_date,e.warning_years);
     if(row.close_date<minimum)throw "Scheduled warning lead invalid";
    }
   }
  }
  if(LEGACY_POLICY.enroll_legacy && LEGACY_POLICY.migration!="adopt_only" && state.legacy.len()!=LEGACY_POLICY.sites.len())throw "Partial legacy enrollment; refusing commands";
  foreach(id,r in state.legacy){
   foreach(key in ["status","signature","samples","last_econmonth","forecast","warn_date","extension","last_level","armed_economy","reminded"])if(!(key in r))throw "Partial legacy row; refusing commands";
   if(r.signature==null||r.signature.id<0||r.samples.len()>36||r.extension<0)throw "Invalid legacy state";
   local known=false;foreach(s in LEGACY_POLICY.sites)if(s.site_id==id&&s.industry_id==r.signature.id&&s.tile==r.signature.tile&&s.born==r.signature.born&&s.engine_type==r.signature.type){
    if(r.forecast<s.earliest_close||r.forecast>s.latest_close||r.extension>s.extension_years)throw "Legacy forecast outside authorized window";
    known=true;
   }
   if(!known)throw "Legacy saved identity mismatch";
   local status_ok=false;foreach(value in ["active","declining","warning","arming","closing","closed","lost","failed_closure","deferred_closure"])if(r.status==value)status_ok=true;
   if(!status_ok)throw "Unknown legacy state";
  }
 }
 function Initialize(now){
  if(loaded!=null && ("schema" in loaded) && loaded.schema==2){
   state=loaded;if(state.schedule_id!=SCHEDULE.id||state.seed!=SCHEDULE.seed||state.schedule_contract!=Contract())throw "Scheduled-event contract mismatch";
   ValidateLegacy();Log("legacy_loaded","scheduler","schema=2|sites="+state.legacy.len());return;
  }
  local migration=loaded!=null;
  if(migration && LEGACY_POLICY.migration!="adopt_only")throw "Phase 7A migration requires explicit adopt_only policy; no automatic enrollment";
  local initialize_parent=LifecycleController.Initialize.bindenv(this);initialize_parent(now);state.schema=2;state.policy_contract<-PolicyContract();state.legacy<-{};
  if(migration){Log("legacy_migrated","scheduler","schema=1->2|enrolled=0|explicit_adopt_only=true");return;}
  if(LEGACY_POLICY.enroll_legacy){
   if(now!=668394||GSTownList().Count()!=617||GSIndustryList().Count()!=542)throw "Legacy enrollment requires intact original 1830 baseline";
   foreach(s in LEGACY_POLICY.sites)if(!LegacyMatch(s))throw "Original pilot instance mismatch; no enrollment";
   foreach(s in LEGACY_POLICY.sites){
    state.legacy[s.site_id]<-{status="active",signature=Signature(s.industry_id),samples=[],last_econmonth=-1,forecast=s.earliest_close,warn_date=-1,extension=0,last_level=16,armed_economy=-1,reminded=false};
    Log("legacy_enrolled",s.site_id,"industry="+s.industry_id+"|tile="+s.tile+"|born="+s.born+"|snapshot="+s.original_record_sha256);
   }
  }
  ValidateLegacy();
 }
 function LegacyNews(s,text){News(s.site_id,s.name+" ("+s.region+", "+s.cargo_labels[0]+"): "+text,s.tile);}
 function LegacyObserve(s,r,now){
  local economy=GSDate.GetCurrentDate(),month=GSDate.GetYear(economy)*12+GSDate.GetMonth(economy);
  if(month==r.last_econmonth)return;r.last_econmonth=month;
  local produced=0,transported=0;foreach(c,_ in GSIndustryType.GetProducedCargo(s.engine_type)){produced+=GSIndustry.GetLastMonthProduction(s.industry_id,c);transported+=GSIndustry.GetLastMonthTransported(s.industry_id,c);}
  r.samples.append({date=now,produced=produced,transported=transported});while(r.samples.len()>s.rolling_months)r.samples.remove(0);
  local total_p=0,total_t=0;foreach(sample in r.samples){total_p+=sample.produced;total_t+=sample.transported;}
  local percent=total_p>0?(100*total_t/total_p).tointeger():0;
  local full=r.samples.len()>=s.rolling_months && now-r.samples[0].date>=365*2;
  Log("legacy_sample",s.site_id,"calendar="+now+"|economy="+economy+"|production="+produced+"|transported="+transported+"|rolling_months="+r.samples.len()+"|rolling_produced="+total_p+"|rolling_transported="+total_t+"|service_percent="+percent+"|forecast="+r.forecast+"|level="+GSIndustry.GetProductionLevel(s.industry_id));
  if(full && percent>=s.minimum_percent && total_t>=s.minimum_transport && r.extension==0){
   local forecast=min(s.latest_close,AddYears(s.earliest_close,s.extension_years));
   if(forecast>r.forecast){r.forecast=forecast;r.extension=s.extension_years;LegacyNews(s,"sustained multi-year deliveries extend the exhaustion forecast to "+GSDate.GetYear(r.forecast)+"; finite hard limit "+GSDate.GetYear(s.latest_close)+".");Log("legacy_extended",s.site_id,"calendar="+now+"|forecast="+r.forecast+"|rolling_transported="+total_t+"|service_percent="+percent);}
  }
 }
 function LegacyTick(s,r,now){
  if(r.status=="closed"||r.status=="lost"||r.status=="failed_closure"||r.status=="deferred_closure")return;
  if(!LegacyMatch(s)){
   if(r.status=="closing"){r.status="closed";Log("legacy_closed",s.site_id,"calendar="+now+"|industry="+s.industry_id+"|tile="+s.tile);LegacyNews(s,"workings physically closed. Redirect services to replacement resources.");}
   else{r.status="lost";Log("legacy_identity_lost",s.site_id,"No commands issued to replacement or reused ID");}
   return;
  }
  if(r.status=="closing"){
   if(GSDate.GetCurrentDate()-r.armed_economy>180){GSIndustry.SetControlFlags(s.industry_id,GSIndustry.GetControlFlags(s.industry_id)|GSIndustry.INDCTL_NO_CLOSURE);GSIndustry.SetProductionLevel(s.industry_id,8,false,null);r.status="failed_closure";LegacyNews(s,"closure failed; site remains protected and open; administrator review required.");}
   return;
  }
  if(r.status=="arming"){
   if(GSDate.GetCurrentDate()-r.armed_economy<40)return;
   if(GSDate.GetCurrentDate()-r.armed_economy>65){r.status="failed_closure";LegacyNews(s,"closure authorization expired before commit; remains open.");return;}
   if(!LegacyMatch(s))throw "Identity changed before closure commit";
   GSIndustry.SetControlFlags(s.industry_id,GSIndustry.GetControlFlags(s.industry_id)&~GSIndustry.INDCTL_NO_CLOSURE);
   if(!GSIndustry.SetProductionLevel(s.industry_id,4,false,null))throw "Closure commit rejected";
   r.status="closing";Log("legacy_authorization",s.site_id,"action=commit|calendar="+now+"|industry="+s.industry_id+"|token="+s.token);return;
  }
  LegacyObserve(s,r,now);
  local warning=AddYears(r.forecast,-s.warning_years);
  if(r.status=="active" && now>=s.decline_date){r.status="declining";LegacyNews(s,"mature workings enter gradual decline; expected exhaustion window "+GSDate.GetYear(s.earliest_close)+"–"+GSDate.GetYear(s.latest_close)+". Sustained service can extend survival within that limit.");}
  if(r.warn_date<0 && now>=warning){
   r.warn_date=now;r.forecast=max(r.forecast,AddYears(now,s.warning_years));
   if(r.forecast>s.latest_close){r.status="deferred_closure";LegacyNews(s,"late warning would violate the historical cap; closure deferred for administrator review.");return;}
   r.status="warning";LegacyNews(s,"advance exhaustion warning: earliest closure year "+GSDate.GetYear(r.forecast)+", hard limit "+GSDate.GetYear(s.latest_close)+". Plan alternate supplies.");
   Log("legacy_warning",s.site_id,"calendar="+now+"|forecast="+r.forecast+"|minimum_years="+s.warning_years);
  }
  if(r.warn_date>=0 && !r.reminded && now>=AddYears(r.forecast,-5)){
   r.reminded=true;LegacyNews(s,"five-year closure window reminder; check replacement resources and reroute investment.");
  }
  if(now>=s.decline_date){
   local span=max(1,s.earliest_close-s.decline_date),progress=max(0,now-s.decline_date);
   local stage=min(4,(progress*5/span).tointeger()),level=16-2*(stage+1);level=max(8,level);
   if("decline_levels" in s){local levels=s.decline_levels;level=levels[min(levels.len()-1,(progress*levels.len()/span).tointeger())];}
   if(level!=r.last_level){if(!GSIndustry.SetProductionLevel(s.industry_id,level,false,null))throw "Gradual production control rejected";r.last_level=level;Log("legacy_decline",s.site_id,"calendar="+now+"|level="+level);}
   GSIndustry.SetText(s.industry_id,s.name+": managed finite working; estimated closure year "+GSDate.GetYear(r.forecast)+", hard cap "+GSDate.GetYear(s.latest_close)+". Rolling multi-year loaded transport determines bounded extension.");
  }
  if(r.warn_date>=0 && now>=r.forecast){
   if(now<AddYears(r.warn_date,s.warning_years))throw "Insufficient actual calendar warning; closure refused";
   local count=0;foreach(i,_ in GSIndustryList())if(GSIndustry.GetIndustryType(i)==s.engine_type)count++;
   foreach(id,other in state.legacy)if((other.status=="arming"||other.status=="closing")&&other.signature.type==s.engine_type)count--;
   if(count<=1){r.status="deferred_closure";LegacyNews(s,"last-producer protection defers closure.");return;}
   if(!LegacyMatch(s))throw "Identity changed before authorization";
   GSIndustry.SetControlFlags(s.industry_id,GSIndustry.GetControlFlags(s.industry_id)|GSIndustry.INDCTL_NO_CLOSURE);
   if(!GSIndustry.SetProductionLevel(s.industry_id,s.arm_level,false,null))throw "Instance authorization command failed";
   r.status="arming";r.armed_economy=GSDate.GetCurrentDate();
   Log("legacy_authorization",s.site_id,"action=arm|calendar="+now+"|economy="+r.armed_economy+"|industry="+s.industry_id+"|token="+s.token);
  }
 }
 function Tick(now){
  ValidateLegacy();local tick_parent=LifecycleController.Tick.bindenv(this);tick_parent(now);
  foreach(s in LEGACY_POLICY.sites)if(s.site_id in state.legacy)LegacyTick(s,state.legacy[s.site_id],now);
 }
 function Start(){try{
  if(GSNewGRF.GetVersion(0x4B484531)!=5)throw "Legacy controller requires separate AXIS 0.5";
  if(!GSIndustryType.CanBuildIndustry(Type(0)))throw "Lifecycle disabled or incompatible availability policy; no legacy commands";
  if(GSGameSettings.GetValue("economy.timekeeping_units")!=0)throw "Wallclock unsupported";
  local now=Calendar();Initialize(now);
  while(true){now=Calendar();Tick(now);Sleep(74*14);}
 }catch(e){GSLog.Error("P7 FATAL|"+e);while(true)Sleep(365);}}
}
