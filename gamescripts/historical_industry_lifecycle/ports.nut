/* GS v5, same schema 4, fresh policy contract; no automatic adoption of old saves. */
class PortsController extends ProgressionController {
 function SiteReason(tile,e){
  if(!("coastal" in e)||!e.coastal)return base.SiteReason(tile,e);
  local x=GSMap.GetTileX(tile),y=GSMap.GetTileY(tile),coast=false,water=0;
  foreach(p in e.footprint){local xx=x+p[0],yy=y+p[1];
   if(xx<2||yy<2||xx>=GSMap.GetMapSizeX()-2||yy>=GSMap.GetMapSizeY()-2)return "boundary";
   local t=GSMap.GetTileIndex(xx,yy);
   if(GSTile.IsHouseTile(t)||GSRoad.IsRoadTile(t)||GSIndustry.IsValidIndustry(GSIndustry.GetIndustryID(t)))return "protected_or_occupied";
   if(!GSTile.IsWaterTile(t)&&!GSTile.IsBuildable(t))return "protected_or_occupied";
   if(GSTile.IsCoastTile(t))coast=true;
   if(GSTile.IsWaterTile(t))water++;
  }
  if(!coast||water<2)return "no_native_shore_envelope";
  return "safe";
 }
}
