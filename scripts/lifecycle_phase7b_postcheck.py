"""Post-closure engine checks: markets and every unmanaged native instance."""
import json
from pathlib import Path
from lifecycle_phase7b_runtime import ROOT,BASE,prepare,execute,bundle
from lifecycle_phase7b_validate import setup

if __name__=='__main__':
    p=json.loads((BASE/'comparison-control.json').read_text());source=Path(p['case'])/'checkpoint-3.sav'
    expected=json.loads((ROOT/'docs/research/phase7b_baseline_fingerprints.json').read_text())['industries']
    # Baseline IDs are the verified dense 0..541 range; arrays avoid identifier
    # ambiguities and no runtime evaluation of generated Python/JSON is used.
    prefix='ORIGINAL_LEVELS <- ['+','.join(str(r['prod_level']) for r in expected)+'];\nORIGINAL_FLAGS <- ['+','.join(str(r['ctlflags']) for r in expected)+'];\n'
    body='''
local food=0,goods=0,intact=0,levelchanges=0,flagchanges=0;
foreach(i,_ in GSIndustryList()){
 local managed=false;foreach(s in LEGACY_POLICY.sites)if(s.industry_id==i)managed=true;
 if(!managed){intact++;if(GSIndustry.GetProductionLevel(i)!=ORIGINAL_LEVELS[i])levelchanges++;if(GSIndustry.GetControlFlags(i)!=ORIGINAL_FLAGS[i])flagchanges++;}
 foreach(c,_ in GSCargoList()){local label=GSCargo.GetCargoLabel(c);if(label=="FOOD"&&GSIndustry.IsCargoAccepted(i,c)==GSIndustry.CAS_ACCEPTED)food++;if(label=="GOOD"&&GSIndustry.IsCargoAccepted(i,c)==GSIndustry.CAS_ACCEPTED)goods++;}
}
Log("postcheck","europe","industries="+GSIndustryList().Count()+"|towns="+GSTownList().Count()+"|unmanaged="+intact+"|unmanaged_level_changes="+levelchanges+"|unmanaged_flag_changes="+flagchanges+"|FOOD="+food+"|GOOD="+goods);
if(intact!=538||levelchanges!=0||flagchanges!=0||food!=76||goods!=69)throw "Unmanaged industry or market coverage mismatch";
GSGame.Pause();while(true)Sleep(365);
'''
    home=prepare('post-closure-markets',prefix+bundle().replace('Initialize(now);','Initialize(now);'+body));setup(home,p['policy'])
    r=execute(home,2500,source=source);assert any('postcheck|europe|' in line for line in r['observations'])
    (BASE/'postcheck.json').write_text(json.dumps(r,indent=2))
