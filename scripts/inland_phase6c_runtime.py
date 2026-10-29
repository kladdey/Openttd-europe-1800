"""Isolated Phase 6C harness. The delivered Phase 6B scenario/GRF are immutable."""
import json
from pathlib import Path
import coastal_phase6_runtime as runtime

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'newgrfs/axis-historical-europe/.work/inland6c'
SOURCE=Path(r'C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.3.0 Candidate - Industrialized.scn')
EXPECTED='b05ef51a3bd17eb453d6b5e4af544c0745fee372a6195f5354ab8bd927ce6e75'
GRF=SOURCE.parent.parent/'newgrf/axis-historical-europe-0.3.0-candidate.grf'
GRF_HASH='f0da622873c91107fa4d2b768d88cd95d5db009c2b2975bdb6d7ab6caaed3c33'
sha=runtime.sha


def run(script,tag,ticks=6000,source=None,unpaused=False):
    assert sha(SOURCE)==EXPECTED and sha(GRF)==GRF_HASH
    runtime.BASE=BASE;runtime.SOURCE=SOURCE;runtime.EXPECTED=EXPECTED
    registration=json.loads((ROOT/'newgrfs/axis-historical-europe/.work/industrial6b/candidate-registration.json').read_text())
    runtime.ASSETS=Path(registration['case'])
    return runtime.run(script,tag,ticks,source=source or SOURCE,unpaused=unpaused,stop_on_script_error=True)
