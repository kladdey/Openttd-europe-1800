"""Phase 7B isolated profiles, retaining all immutable Phase 7A assets."""
import json,shutil
from pathlib import Path
import lifecycle_phase7a_runtime as prior
ROOT=prior.ROOT;BASE=ROOT/'newgrfs/axis-historical-legacy/.work/runtime';BASE.mkdir(parents=True,exist_ok=True)
GRF=ROOT/'newgrfs/axis-historical-legacy/dist/axis-historical-europe-0.5.0-legacy-candidate.grf'
SOURCE=prior.SOURCE;ENGINE=prior.ENGINE;sha=prior.sha
def guards():
    prior.guards();assert sha(prior.GRF)=='e05de519b4695bc68bde7064c17ee0ae833edfe281579c3b92cb79532f466c52'
    manifest=json.loads((ROOT/'docs/research/phase7a_candidate_delivery.json').read_text())
    assert sha(Path(manifest['candidate']))==manifest['candidate_sha256']
def prepare(tag,text,policy=True,v5=True,density=0):
    guards();oldbase,oldgrf=prior.BASE,prior.GRF
    try:
        prior.BASE=BASE
        if v5:
            assert GRF.exists(),'Missing compiled Phase 7B candidate; no implicit rebuild';prior.GRF=GRF
        home=prior.prepare(tag,text,policy=policy,density=density)
    finally:prior.BASE,prior.GRF=oldbase,oldgrf
    if v5:
        p=ROOT/'gamescripts/historical_industry_lifecycle/legacy_info.nut'
        if p.exists():shutil.copyfile(p,home/'game/lifecycle/info.nut')
    return home
def execute(*args,**kwargs):
    guards();kwargs.setdefault('fail_on_fatal',True);r=prior.execute(*args,**kwargs);guards();return r
def source7a():return Path(json.loads((ROOT/'docs/research/phase7a_candidate_delivery.json').read_text())['candidate'])
def bundle():
    folder=ROOT/'gamescripts/historical_industry_lifecycle'
    return (folder/'main.nut').read_text(encoding='utf-8-sig')+'\n'+(folder/'legacy.nut').read_text(encoding='utf-8-sig')

def registration():
    path=BASE/'registration.json'
    if path.exists():return json.loads(path.read_text())
    script='''class LifecycleController extends GSController {function Start(){
foreach(local_id in [0]){} for(local n=0;n<256;n++){local t=GSIndustryType.ResolveNewGRFID(0x4B484531,n);if(GSIndustryType.IsValidIndustryType(t))GSLog.Info("P7 BTYPE|"+n+"|"+t);}
GSGame.Pause();while(true)Sleep(365);}}'''.replace('foreach(local_id in [0]){} ','')
    home=prepare('baseline-registration',script,v5=False);r=execute(home,1500,source=source7a())
    import re
    mapping={int(t):int(n) for s in r['observations'] for n,t in re.findall(r'BTYPE\|(\d+)\|(\d+)',s)}
    assert len(mapping)==96
    result=dict(mapping=mapping,result=r);path.write_text(json.dumps(result,indent=2));return result
