class VehicleAuditProbe extends GSController {
 function Start() {
  GSLog.Info("AUDIT_BEGIN|" + GSDate.GetCurrentDate());
  local count=0;
  for(local id=0;id<16000;id++) {
   if(!GSEngine.IsValidEngine(id)) continue;
   local type=GSEngine.GetVehicleType(id);
   if(type != GSVehicle.VT_RAIL && type != GSVehicle.VT_WATER) continue;
   local cargos="";
   for(local c=0;c<64;c++) if(GSCargo.IsValidCargo(c) && GSEngine.CanRefitCargo(id,c)) cargos+=c+":"+GSCargo.GetCargoLabel(c)+",";
   local power=-1,weight=-1,te=-1,wagon=false;
   if(type==GSVehicle.VT_RAIL) { wagon=GSEngine.IsWagon(id); power=GSEngine.GetPower(id); weight=GSEngine.GetWeight(id);te=GSEngine.GetMaxTractiveEffort(id); }
   GSLog.Info("AUDIT_ROW|"+id+"|"+type+"|"+GSEngine.GetName(id)+"|"+GSEngine.GetDesignDate(id)+"|"+GSEngine.GetPrice(id)+"|"+GSEngine.GetRunningCost(id)+"|"+GSEngine.GetMaxSpeed(id)+"|"+power+"|"+weight+"|"+te+"|"+GSEngine.GetCapacity(id)+"|"+GSEngine.GetReliability(id)+"|"+wagon+"|"+cargos);
   count++;
  }
  GSLog.Info("AUDIT_DONE|"+count);
  {
   local mode=GSCompanyMode(0);
   foreach(id in [1534,2038]) GSLog.Info("AUDIT_COMPANY|"+id+"|"+GSEngine.IsValidEngine(id)+"|"+GSEngine.GetPrice(id)+"|"+GSEngine.GetRunningCost(id));
  }
  while(true) Sleep(10000);
 }
}
