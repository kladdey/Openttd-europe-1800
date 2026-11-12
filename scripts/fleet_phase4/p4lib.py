"""Shared parsing helpers for Phase 4 evidence (wraps runtime_validation/analyze.py)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'runtime_validation'))
import analyze as A   # noqa: E402
A.RUNS = A.DATA.parents[0] / 'fleet_phase4' / 'runs'
OUT = A.DATA.parents[0] / 'fleet_phase4'


def catalogue(tag, sample='start'):
    return A.catalogue(tag).get(sample, {})


def cat_diff(base, test):
    b, t = catalogue(base), catalogue(test)
    return [(i, b[i]['name'], b[i]['price'], t[i]['price'], b[i]['running'], t[i]['running']) for i in b
            if i in t and (b[i]['price'] != t[i]['price'] or b[i]['running'] != t[i]['running'])]
