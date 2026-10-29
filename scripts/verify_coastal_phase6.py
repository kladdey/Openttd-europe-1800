"""Read-only verification of delivered Phase 6A candidate against its source.

Run: python -X utf8 scripts/verify_coastal_phase6.py
Requires NumPy and the original local scenario files. No engine is launched.
"""
import json
from pathlib import Path
import numpy as np
from coastal_phase6_runtime import ROOT,SOURCE,EXPECTED,sha
from coastal_phase6_preservation import parts,differences
from historical_scenario_migration import inspect


def main():
    if not __debug__:raise SystemExit('Safety assertions required; do not run with Python -O')
    report=json.loads((ROOT/'docs/research/coastal_scenario_delivery.json').read_text(encoding='utf8'))
    target=Path(report['output']);assert sha(SOURCE)==EXPECTED and sha(target)==report['output_sha256']
    a,b,changed,guards=differences(SOURCE,target)
    assert guards==report['guards']
    assert guards['height_changes']==guards['water_type_changes']==guards['existing_infrastructure_changes']==0
    p,q=parts(SOURCE),parts(target)
    assert p['CITY'][1]==q['CITY'][1][:614]
    assert len(q['CITY'][1])==614+report['added_towns']
    assert all(p[t]==q[t] for t in p if t not in set(a)|{'CITY'})
    ids=np.flatnonzero(changed);at=np.frombuffer(a['MAPT'],dtype='u1')>>4;bt=np.frombuffer(b['MAPT'],dtype='u1')>>4
    assert np.all(np.isin(at[ids],[0,4])) and np.all(np.isin(bt[ids],[0,2,3,4]))
    # All water bytes (including coast/river metadata) remain identical.
    water=np.flatnonzero(at==6);n=4096**2
    for t in a:
        stride=len(a[t])//n
        assert np.array_equal(np.frombuffer(a[t],dtype='u1').reshape(n,stride)[water],np.frombuffer(b[t],dtype='u1').reshape(n,stride)[water]),t
    original=inspect(SOURCE);candidate=inspect(target)
    assert candidate['newgrfs']==original['newgrfs'] and len(candidate['newgrfs'])==15
    assert candidate['industry_records']==candidate['industry_tiles']==0
    assert candidate['town_records']==report['final_towns']
    print(f"PASS: {report['final_towns']} towns; original 613 bit-identical; {guards['changed_tiles']} logged tiles; zero height/water/infrastructure changes; all 15 NewGRFs unchanged.")


if __name__=='__main__':main()
