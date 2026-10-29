// GPL-2.0-only. Tests actual enabled specs, generation and funding callbacks.
class HistoricalSteelRuntimeTest extends GSController {
 function Start() {
  this.Sleep(1);
  local year=GSDate.GetYear(GSDate.GetCurrentDate()), failures=0;
  local cargos=GSCargoList(), types=GSIndustryTypeList();
  GSLog.Info("AHE5 INVENTORY year="+year+" cargos="+cargos.Count()+" types="+types.Count());
  if(cargos.Count()!=64 || types.Count()!=92)failures++;
  foreach(target in TARGETS){
   local type=GSIndustryType.ResolveNewGRFID(0x4B484531,target.id);
   local expected=target.allow && year>=target.year;
   local valid=GSIndustryType.IsValidIndustryType(type);
   local available=valid && GSIndustryType.CanBuildIndustry(type);
   local count=0;
   foreach(industry,_ in GSIndustryList())if(GSIndustry.GetIndustryType(industry)==type)count++;
   if(available!=expected || (!expected && count>0))failures++;
   if(!expected && GSIndustryType.BuildIndustry(type,GSMap.GetTileIndex(10,10)))failures++;
   GSLog.Info("AHE5 DEITY id="+target.id+" available="+available+" expected="+expected+" generated="+count);
  }
  for(local n=0;n<100 && GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID;n++)this.Sleep(1);
  if(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID){GSLog.Error("AHE5 NO COMPANY");failures++;}
  else{
   local company=GSCompanyMode(0);
   foreach(target in TARGETS){
    local type=GSIndustryType.ResolveNewGRFID(0x4B484531,target.id);
    local expected=target.allow && year>=target.year;
    local available=GSIndustryType.CanBuildIndustry(type);
    if(available!=expected)failures++;
    if(!expected && GSIndustryType.BuildIndustry(type,GSMap.GetTileIndex(10,10)))failures++;
    GSLog.Info("AHE5 FUND id="+target.id+" available="+available+" expected="+expected);
   }
  }
  GSLog.Info("AHE5 DONE failures="+failures);
  while(true)this.Sleep(365);
 }
}
