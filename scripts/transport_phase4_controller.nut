class TransportProbe extends GSController {
 function Apply(cfg,cid,tag){
  ::ACTIVE=cfg;::MODE=cfg.mode;::CARGO=cfg.cargo;::A=cfg.a;::B=cfg.b;::ENGINE=cfg.engine;::FLEET=cfg.fleet;::ENDPOINTS=cfg.endpoints;::WAGONS=cfg.wagons;::PLATFORM=cfg.platform;::BRAKE_VAN=cfg.brake;::MIN_SEPARATION=cfg.sep;::CASE=tag;
  local builder=RouteBuilder();builder.CID=cid;return builder.Build();
 }
 function Sample(s){
  foreach(v in s.vehicles){
   if(!GSVehicle.IsValidVehicle(v))continue;
   local load=GSVehicle.GetCargoLoad(v,s.config.cargo),state=GSVehicle.GetState(v),speed=GSVehicle.GetCurrentSpeed(v);
   s.samples++;if(load>0)s.loaded++;s.loadsum+=load;s.cap_sum+=GSVehicle.GetCapacity(v,s.config.cargo);
   if(state==GSVehicle.VS_BROKEN)s.broken++;
   if(state==GSVehicle.VS_AT_STATION)s.at_station++;
   if(speed>0)s.running++;
   if(load>0){s.speed_sum+=speed;s.loads++;}
  }
 }
 function Start(){
  local count=CONFIG.routes.len(),services=[],expanded=false;
  while(GSCompany.ResolveCompanyID(count-1)==GSCompany.COMPANY_INVALID)Sleep(2);
  for(local c=0;c<count;c++){
   local mode=GSCompanyMode(c);
   GSLog.Info("P4_START|"+c+"|"+GSCompany.GetBankBalance(c)+"|"+GSCompany.GetLoanAmount()+"|"+GSCompany.GetMaxLoanAmount()+"|"+GSGameSettings.GetValue("economy.infrastructure_maintenance")+"|"+GSGameSettings.GetValue("vehicle.max_train_length"));
   foreach(id in [147,149,150,151,181,402,430,612,614,615,616,617,1534,2038])GSLog.Info("P4_OPENING|"+c+"|"+id+"|"+GSEngine.IsBuildable(id)+"|"+GSEngine.GetName(id)+"|"+GSEngine.GetDesignDate(id));
  }
  local order=[];if("order" in CONFIG)order=CONFIG.order;else for(local c=0;c<count;c++)order.append(c);
  foreach(c in order){
   local s=Apply(CONFIG.routes[c],c,"company_"+c);if(s!=null)services.append(s);
  }
  if(services.len()==0){GSLog.Info("P4_NO_SERVICE");GSLog.Info("P4_DONE");while(true)Sleep(10000);}
  local year=GSDate.GetYear(GSDate.GetCurrentDate()),end=1800+CONFIG.years,month=-1;
  while(year<end){
   foreach(s in services){local mode=GSCompanyMode(s.cid);Sample(s);}
   if(GSDate.GetMonth(GSDate.GetCurrentDate())!=month){
    month=GSDate.GetMonth(GSDate.GetCurrentDate());
    foreach(s in services){local mode=GSCompanyMode(s.cid);
     GSLog.Info("P4_MONTH|"+s.cid+"|"+GSDate.GetCurrentDate()+"|"+GSCompany.GetBankBalance(s.cid)+"|"+GSStation.GetCargoRating(GSStation.GetStationID(s.a),s.config.cargo)+"|"+GSStation.GetCargoWaiting(GSStation.GetStationID(s.a),s.config.cargo));
     foreach(v in s.vehicles)if(GSVehicle.IsValidVehicle(v))GSLog.Info("P4_POSITION|"+s.cid+"|"+v+"|"+GSVehicle.GetLocation(v)+"|"+GSVehicle.GetCurrentSpeed(v)+"|"+GSVehicle.GetCargoLoad(v,s.config.cargo)+"|"+GSVehicle.GetState(v));
    }
   }
   if(GSDate.GetYear(GSDate.GetCurrentDate())!=year){
    Sleep(74);
    for(local c=0;c<count;c++){
     local mode=GSCompanyMode(c),ledger="",delivered=0,profit=0,fleet=0;
     for(local e=0;e<15;e++)ledger+=GSCompany.GetAnnualExpenseValue(c,1,e)+",";
     for(local q=1;q<=4;q++)delivered+=GSCompany.GetQuarterlyCargoDelivered(c,q);
     foreach(s in services)if(s.cid==c)foreach(v in s.vehicles)if(GSVehicle.IsValidVehicle(v)){fleet++;profit+=GSVehicle.GetProfitLastYear(v);}
     GSLog.Info("P4_YEAR|"+c+"|"+year+"|"+GSCompany.GetBankBalance(c)+"|"+GSCompany.GetLoanAmount()+"|"+GSCompany.GetQuarterlyCompanyValue(c,0)+"|"+delivered+"|"+fleet+"|"+profit+"|"+ledger);
    }
    foreach(s in services){
     GSLog.Info("P4_DUTY|"+s.cid+"|"+year+"|"+s.tag+"|"+s.samples+"|"+s.loaded+"|"+s.loadsum+"|"+s.cap_sum+"|"+s.broken+"|"+s.running+"|"+s.at_station+"|"+s.speed_sum+"|"+s.loads);
     s.samples=0;s.loaded=0;s.loadsum=0;s.cap_sum=0;s.broken=0;s.running=0;s.at_station=0;s.speed_sum=0;s.loads=0;
    }
    year=GSDate.GetYear(GSDate.GetCurrentDate());
    if("expand" in CONFIG && CONFIG.expand && !expanded && year>=1810){
     expanded=true;
     local cfg={mode="rail",cargo=0,a=189,b=96,engine=1534,fleet=1,endpoints="town",wagons=4,platform=2,brake=false,sep=2};
     local mode=GSCompanyMode(2);GSLog.Info("P4_EXPANSION|"+GSCompany.GetBankBalance(2)+"|"+GSCompany.GetLoanAmount());
     if("expand_credit" in CONFIG && CONFIG.expand_credit && GSCompany.GetBankBalance(2)<20000 && GSCompany.GetLoanAmount()+10000<=GSCompany.GetMaxLoanAmount()){
      GSCompany.SetLoanAmount(GSCompany.GetLoanAmount()+10000);
      GSLog.Info("P4_EXPANSION_FINANCE|"+GSCompany.GetBankBalance(2)+"|"+GSCompany.GetLoanAmount());
     }
     if(GSCompany.GetBankBalance(2)>=16000){local s=Apply(cfg,2,"road_to_rail");if(s!=null)services.append(s);}
    }
   }
   Sleep(5);
  }
  GSLog.Info("P4_DONE");while(true)Sleep(10000);
 }
}
