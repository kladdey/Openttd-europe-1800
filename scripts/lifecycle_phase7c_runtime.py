"""Isolated Phase 7C execution. Prior candidates and normal profiles are read-only."""
import json,shutil
from pathlib import Path
import lifecycle_phase7a_runtime as prior
import lifecycle_phase7b_runtime as b
ROOT=prior.ROOT;BASE=ROOT/'newgrfs/axis-historical-expansion/.work/runtime';BASE.mkdir(parents=True,exist_ok=True)
ENGINE=prior.ENGINE;GRF=ROOT/'newgrfs/axis-historical-expansion/dist/axis-historical-europe-0.6.0-expansion-candidate.grf';sha=prior.sha
SOURCE=ROOT/'newgrfs/axis-historical-legacy/.work/runtime/legacy-editor-1793286062596721700/scenario/Europe 1830 Historical AXIS 0.5.0 - Legacy Mine Lifecycle.scn'
def guards():
    b.guards()
    assert sha(b.GRF)=='473b4ac0ebc6962959408633dbbc2cf254546fe9bc7fdd6c3531b0f0a232e534'
    assert sha(SOURCE)=='355686df5ddbc935aacdcc0b89a9bd446657d086f973df11fb794f5fbafd8e79'
def bundle():
    d=ROOT/'gamescripts/historical_industry_lifecycle'
    return b.bundle()+'\n'+(d/'expansion.nut').read_text(encoding='utf-8-sig')
def prepare(tag,script=None,policy=True,density=0):
    guards();oldbase,oldgrf=prior.BASE,prior.GRF
    try:
        prior.BASE,prior.GRF=BASE,GRF
        home=prior.prepare(tag,script if script is not None else bundle(),policy=policy,density=density)
    finally:prior.BASE,prior.GRF=oldbase,oldgrf
    d=ROOT/'gamescripts/historical_industry_lifecycle'
    if (d/'expansion_info.nut').exists():shutil.copyfile(d/'expansion_info.nut',home/'game/lifecycle/info.nut')
    return home
def execute(*args,**kwargs):
    guards();kwargs.setdefault('fail_on_fatal',True);result=prior.execute(*args,**kwargs);guards();return result
