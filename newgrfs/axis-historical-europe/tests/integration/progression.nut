// GPL-2.0-only. One persistent world; no date cheat, reconstruction or closure command.
class HistoricalSteelRuntimeTest extends GSController {
 state=null;
 function Save(){return state;}
 function Load(version,data){state=data;}
 function Start(){
  if(state==null){state={next=0,initial={}};foreach(i,_ in GSIndustryList())state.initial[i]<-GSIndustry.GetIndustryType(i);}
  else GSLog.Info("AHE5P RELOADED year="+GSDate.GetYear(GSDate.GetCurrentDate())+" next="+state.next);
  local milestones=[1830,1850,1870,1900,1925,1950,1975,2000,2025];
  while(state.next<milestones.len()){
   local year=GSDate.GetYear(GSDate.GetCurrentDate());
   if(year>=milestones[state.next]){
    local failures=0,alive=0;
    foreach(i,t in state.initial)if(GSIndustry.IsValidIndustry(i) && GSIndustry.GetIndustryType(i)==t)alive++;
    foreach(target in TARGETS){
     local type=GSIndustryType.ResolveNewGRFID(0x4B484531,target.id);
     local expected=target.allow && year>=target.year;
     if(GSIndustryType.CanBuildIndustry(type)!=expected)failures++;
     if(!expected)foreach(i,_ in GSIndustryList())if(GSIndustry.GetIndustryType(i)==type)failures++;
    }
    GSLog.Info("AHE5P MILESTONE year="+year+" industries="+GSIndustryList().Count()+" original_id_type_matches="+alive+" failures="+failures);
    state.next++;
   }
   this.Sleep(74);
  }
  GSLog.Info("AHE5P DONE");while(true)this.Sleep(1000);
 }
}
