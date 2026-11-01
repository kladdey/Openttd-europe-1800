"""Loaded old-mill capacity fixture; finite batches, unchanged native recipe."""
import json,re
from lifecycle_phase7c_runtime import *
from industrial_phase6b_controls import builder,COMMON
def main():
    text='''class ExpansionLifecycleController extends GSController {
'''+COMMON.replace('fleet=2','fleet=8').replace('::FLEET=2','::FLEET=8')+'''
function Start(){GSGame.Unpause();while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
local services=[];{local cm=GSCompanyMode(0);::POLICY="keep";::DEPOT_TILES=[];GSRoad.SetCurrentRoadType(0);
services.append(Service("old_mill_grain","GRAI",66,275,true));services.append(Service("old_mill_food","FOOD",275,474,true));}
local start=GSDate.GetCurrentDate(),month=-1;
GSIndustry.SetControlFlags(275,GSIndustry.GetControlFlags(275)|GSIndustry.INDCTL_NO_CLOSURE);
while(GSDate.GetCurrentDate()-start<365*4){
local elapsed=GSDate.GetCurrentDate()-start;
if(elapsed>=365*2&&GSIndustry.GetProductionLevel(275)!=8)GSIndustry.SetProductionLevel(275,8,false,null);
local current=GSDate.GetYear(GSDate.GetCurrentDate())*12+GSDate.GetMonth(GSDate.GetCurrentDate());
if(current!=month){month=current;GSLog.Info("P7 C_CAPACITY|elapsed="+elapsed+"|level="+GSIndustry.GetProductionLevel(275)+"|grain_stock="+GSIndustry.GetStockpiledCargo(275,Cargo("GRAI"))+"|food_produced="+GSIndustry.GetLastMonthProduction(275,Cargo("FOOD")));}
{local cm=GSCompanyMode(0);foreach(s in services)Sample(s);}
Sleep(10);
}
GSLog.Info("P7 C_CAPACITY_DONE|old_exists="+GSIndustry.IsValidIndustry(275)+"|grain_paid="+services[0].paid+"|food_paid="+services[1].paid);GSGame.Pause();while(true)Sleep(365);
}}
'''
    text=re.sub(r'}(?=(?:return|if\(|Sleep|local|GSLog))','}\n',builder()+text)
    h=prepare('old-mill-loaded-capacity',text);(h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
    r=execute(h,140000,source=SOURCE,timeout=600);assert any('C_CAPACITY_DONE|' in s for s in r['observations']);(BASE/'capacity.json').write_text(json.dumps(r,indent=2))
if __name__=='__main__':main()
