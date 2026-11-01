/* SPDX-License-Identifier: GPL-2.0-only. V4 retains the v1-v3 lifecycle.
 * No GRF, recipe, closure-adapter or original-mine policy changes.
 */
class ProgressionController extends ExpansionLifecycleController {
 progression_contract=null;
 site_counts=null;
 function Save(){
  /* Parent validation temporarily views the root as v3. An autosave must
   * always serialize this controller's own active root as schema 4. Refused
   * older loaded data is preserved verbatim while state is still null. */
  if(state!=null){local saved=clone state;saved.schema=4;return saved;}
  return loaded!=null?loaded:{};
 }
 function Log(event,id,detail){if(event!="status"&&event!="legacy_sample"&&event!="production")GSLog.Info("P7 EVENT|"+event+"|"+id+"|"+detail);}
 function ExpansionContract(){if(progression_contract==null)progression_contract=Hash(EXPANSION_CONTRACT_TEXT);return progression_contract;}
 function ValidateExpansion(){
  local schema=state.schema;state.schema=3;
  try{local validate_parent=ExpansionLifecycleController.ValidateExpansion.bindenv(this);validate_parent();}
  catch(e){state.schema=schema;throw e;}
  state.schema=schema;
 }
 function Initialize(now){
  if(loaded!=null){
   if(!("schema" in loaded)||loaded.schema!=4)throw "Phase 7D requires a fresh candidate or its own schema-4 save; no automatic migration";
   loaded=clone loaded;loaded.schema=3;
  }
  local initialize_parent=ExpansionLifecycleController.Initialize.bindenv(this);initialize_parent(now);state.schema=4;
  ValidateExpansion();
 }
 function HousesNear(tile){
  local x=GSMap.GetTileX(tile),y=GSMap.GetTileY(tile);
  for(local dx=-7;dx<=7;dx++)for(local dy=-7;dy<=7;dy++){
   local xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=GSMap.GetMapSizeX()||yy>=GSMap.GetMapSizeY())continue;
   if(GSTile.IsHouseTile(GSMap.GetTileIndex(xx,yy)))return true;
  }
return false;
 }
 function SiteReason(tile,e){
  if(!GSMap.IsValidTile(tile))return "invalid";
  local x=GSMap.GetTileX(tile),y=GSMap.GetTileY(tile),h=GSTile.GetMinHeight(tile);
  if(x<2||y<2||x+e.width>=GSMap.GetMapSizeX()-2||y+e.height>=GSMap.GetMapSizeY()-2)return "boundary";
  foreach(p in e.footprint){local t=GSMap.GetTileIndex(x+p[0],y+p[1]);
   if(GSTile.IsHouseTile(t))return "house_preserved";
   if(GSTile.IsWaterTile(t)||GSRoad.IsRoadTile(t)||!GSTile.IsBuildable(t))return "protected_or_occupied";
   if(GSTile.GetMinHeight(t)!=h||GSTile.GetMaxHeight(t)!=h)return "not_level";
  }
  if(e.houses_nearby)foreach(p in e.footprint)if(!HousesNear(GSMap.GetTileIndex(x+p[0],y+p[1])))return "no_houses_within_seven";
  if(e.minimum_population>0){local town=GSTile.GetClosestTown(tile);if(!GSTown.IsValidTown(town)||GSTown.GetPopulation(town)<e.minimum_population)return "town_population";}
  if(e.keystone_local_ids.len()>0){local found=false;foreach(i,_ in GSIndustryList()){
   foreach(local_id in e.keystone_local_ids)if(GSIndustry.GetIndustryType(i)==Type(local_id)&&GSMap.DistanceManhattan(tile,GSIndustry.GetLocation(i))<=e.keystone_distance)found=true;
  }
if(!found)return "missing_nearby_keystone";}
  return "safe";
 }
 function ExpansionSafe(tile,e){local reason=SiteReason(tile,e);if(site_counts!=null){if(!(reason in site_counts))site_counts[reason]<-0;site_counts[reason]++;}
 return reason=="safe";}
 function ExpansionOpen(e,r,now,month){
  local batch=r.batch;site_counts={};local open_parent=ExpansionLifecycleController.ExpansionOpen.bindenv(this);open_parent(e,r,now,month);
  if(r.batch!=batch)foreach(reason,count in site_counts)Log("siting",e.event_id,"reason="+reason+"|count="+count+"|native_attempts="+r.attempts);
  site_counts=null;
 }
}
