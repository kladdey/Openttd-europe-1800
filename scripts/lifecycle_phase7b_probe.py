"""Stock-engine proof: selected pre-existing neutral mine, one-shot callback."""
import json
from lifecycle_phase7b_runtime import ROOT,BASE,prepare,execute,source7a

SCRIPT='''class LifecycleController extends GSController {
function Start(){try{
GSGame.Unpause();GSLog.Info("P7 BPROBE|version="+GSNewGRF.GetVersion(0x4B484531)+"|count="+GSIndustryList().Count());
if(GSNewGRF.GetVersion(0x4B484531)!=5)throw "Wrong GRF";
local id=1,neighbour=0,initial=GSIndustryList().Count();
// A bare level-4 request is insufficient even at an allowlisted original mine.
GSIndustry.SetProductionLevel(id,4,false,null);local date=GSDate.GetCurrentDate();
while(GSDate.GetCurrentDate()-date<65)Sleep(20);
if(!GSIndustry.IsValidIndustry(id))throw "Unarmed closure occurred";
GSLog.Info("P7 BUNARMED|survives=true");
GSIndustry.SetControlFlags(id,GSIndustry.GetControlFlags(id)|GSIndustry.INDCTL_NO_CLOSURE);
if(!GSIndustry.SetProductionLevel(id,5,false,null))throw "Cannot arm";date=GSDate.GetCurrentDate();
while(GSDate.GetCurrentDate()-date<45)Sleep(20);
GSLog.Info("P7 BARM|industry=1|level="+GSIndustry.GetProductionLevel(id));
GSIndustry.SetControlFlags(id,GSIndustry.GetControlFlags(id)&~GSIndustry.INDCTL_NO_CLOSURE);
GSIndustry.SetProductionLevel(id,4,false,null);date=GSDate.GetCurrentDate();
while(GSDate.GetCurrentDate()-date<180 && GSIndustry.IsValidIndustry(id))Sleep(20);
GSLog.Info("P7 BCLOSE|selected_exists="+GSIndustry.IsValidIndustry(id)+"|same_type_neighbour="+GSIndustry.IsValidIndustry(neighbour)+"|count="+GSIndustryList().Count());
if(GSIndustry.IsValidIndustry(id)||!GSIndustry.IsValidIndustry(neighbour)||GSIndustryList().Count()!=initial-1)throw "Legacy closure failed";
GSGame.Pause();GSLog.Info("P7 BPROBE_DONE");
}catch(e){GSLog.Error("P7 BERROR|"+e);GSGame.Pause();}while(true)Sleep(365);}}
'''
if __name__=='__main__':
    home=prepare('legacy-handshake-probe',SCRIPT);(home/'scripts').mkdir();(home/'scripts/game_start.scr').write_text('unpause\n')
    r=execute(home,20000,source=source7a());assert any('BPROBE_DONE' in s for s in r['observations']),r['log']
    (BASE/'handshake-probe.json').write_text(json.dumps(r,indent=2))
