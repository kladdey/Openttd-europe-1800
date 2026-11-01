"""Lean real-Europe port construction, vessel capability and paid cargo fixtures."""
import argparse,json
from ports_phase7f import *
PROBE='''
class PortProbe extends PortsController {
 function Start(){try{GSGame.Unpause();
 GSLog.Info("P7 F_BASE|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|economy_date="+GSDate.GetCurrentDate()+"|calendar="+Calendar());
 foreach(e in EXPANSION.events)if(e.event_id=="liverpool_1831"||e.event_id=="hamburg_1831"){
 local tries=0,made=false;
 foreach(t in e.sites){if(SiteReason(t,e)!="safe")continue;if(tries++>=96)break;
 local before={};foreach(i,_ in GSIndustryList())before[i]<-true;
 if(GSIndustryType.BuildIndustry(Type(e.local_id),t)){foreach(i,_ in GSIndustryList())if(!(i in before)){GSLog.Info("P7 F_PORT|event="+e.event_id+"|id="+i+"|tile="+GSIndustry.GetLocation(i)+"|dock="+GSIndustry.GetDockLocation(i)+"|attempts="+tries);made=true;}\nbreak;}
 }
 if(!made)GSLog.Info("P7 F_DEFERRED|event="+e.event_id+"|attempts="+tries+"|error="+GSError.GetLastErrorString());
 }
 foreach(i,_ in GSIndustryList())if(GSIndustry.HasDock(i))GSLog.Info("P7 F_DOCK|industry="+i+"|tile="+GSIndustry.GetLocation(i)+"|dock="+GSIndustry.GetDockLocation(i));
 foreach(e,_ in GSEngineList(GSVehicle.VT_WATER))if(GSEngine.IsBuildable(e)){
 local c="";foreach(k,_ in GSCargoList())if(GSEngine.CanRefitCargo(e,k))c+=GSCargo.GetCargoLabel(k)+",";
 GSLog.Info("P7 F_SHIP|engine="+e+"|name="+GSEngine.GetName(e)+"|price="+GSEngine.GetPrice(e)+"|running="+GSEngine.GetRunningCost(e)+"|cargos="+c);}
 GSLog.Info("P7 F_PROBE_DONE");GSGame.Pause();
 }catch(e){GSLog.Error("P7 F_ERROR|"+e);}while(true)Sleep(365);}
}
'''
def probe():
 h=prepare('native-port-probe',bundle()+PROBE);info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"PortsController"','"PortProbe"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 r=execute(h,12000);(BASE/'probe.json').write_text(json.dumps(r,indent=2))
if __name__=='__main__':probe()
