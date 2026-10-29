"""Isolated Phase 6B runner; reuse the validated save framing/runtime harness."""
from pathlib import Path
import coastal_phase6_runtime as runtime

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'newgrfs/axis-historical-europe/.work/industrial6b'
SOURCE=Path(r'C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - Coastal Towns.scn')
EXPECTED='6c7a7b8ccbf72a744102ab06df755d119d692ca435e397e1bbbac3267ee1b60d'
sha=runtime.sha


def run(script,tag,ticks=3000,source=None,unpaused=False,candidate_grf=False):
    runtime.BASE=BASE;runtime.SOURCE=SOURCE;runtime.EXPECTED=EXPECTED
    original_assets=runtime.ASSETS
    try:
        if candidate_grf:runtime.ASSETS=BASE/'candidate-assets' if candidate_grf is True else Path(candidate_grf)
        return runtime.run(script,tag,ticks,source=source or SOURCE,unpaused=unpaused)
    finally:runtime.ASSETS=original_assets
