class TransportProbe extends GSController {
 function Start(){
  GSLog.Info("P3_START|"+GSDate.GetCurrentDate());
  foreach(k in ["difficulty.max_loan","difficulty.initial_interest","difficulty.vehicle_costs","difficulty.construction_cost","difficulty.vehicle_breakdowns","economy.inflation","economy.infrastructure_maintenance","economy.timekeeping_units","economy.day_length_factor","economy.cargo_aging_rate","economy.payment_algorithm","vehicle.max_train_length","economy.town_growth_rate","linkgraph.distribution_pax","linkgraph.distribution_mail","linkgraph.distribution_default","construction.raw_industry_construction"])
   GSLog.Info("P3_SETTING|"+k+"|"+GSGameSettings.GetValue(k));
  foreach(i,v in GSIndustryList()){
   local t=GSIndustry.GetIndustryType(i),xy=GSIndustry.GetLocation(i),out="",input="";
   foreach(c,z in GSIndustryType.GetProducedCargo(t))out+=c+":"+GSCargo.GetCargoLabel(c)+":"+GSIndustry.GetLastMonthProduction(i,c)+",";
   foreach(c,z in GSIndustryType.GetAcceptedCargo(t))input+=c+":"+GSCargo.GetCargoLabel(c)+",";
   GSLog.Info("P3_INDUSTRY|"+i+"|"+t+"|"+GSIndustryType.GetName(t)+"|"+GSMap.GetTileX(xy)+"|"+GSMap.GetTileY(xy)+"|"+out+"|"+input);
  }
  foreach(i,v in GSTownList()){local xy=GSTown.GetLocation(i);GSLog.Info("P3_TOWN|"+i+"|"+GSTown.GetName(i)+"|"+GSMap.GetTileX(xy)+"|"+GSMap.GetTileY(xy)+"|"+GSTown.GetPopulation(i));}
  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(2);
  {local mode=GSCompanyMode(0);
   GSLog.Info("P3_COMPANY|"+GSCompany.GetBankBalance(0)+"|"+GSCompany.GetLoanAmount()+"|"+GSCompany.GetMaxLoanAmount());
   for(local id=0;id<16000;id++){
    if(!GSEngine.IsValidEngine(id) || !GSEngine.IsBuildable(id))continue;
    local type=GSEngine.GetVehicleType(id);if(type==GSVehicle.VT_AIR)continue;
    GSLog.Info("P3_VEHICLE|"+id+"|"+type+"|"+GSEngine.GetName(id)+"|"+GSEngine.GetPrice(id)+"|"+GSEngine.GetRunningCost(id)+"|"+GSEngine.GetCapacity(id)+"|"+GSEngine.GetMaxSpeed(id));
   }
  }
  GSLog.Info("P3_DONE");while(true)Sleep(10000);
 }
}
