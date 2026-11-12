"""The three competing Phase 4 balance variants, as exact GRF specifications.

Mechanisms used are the ones proven in game (feasibility suite, FLEET_PHASE4_CALLBACK_VALIDATION.md):
  NARS 2.52 / UKRS2: per-engine running-cost class switch to class 44 (unused by both sets) plus a
                     set-local multiplier for class 44; optionally the set-local multiplier of class 42.
                     A static factor (prop 0x0D) is NOT used: NARS ignores it in service, UKRS2 entirely.
  NARS Add-On:       per-engine running-cost factor (prop 0x0D), which the flat-rate Add-On honours.
"""
import phase4 as P4

NARS, ADDON, UKRS2 = P4.NARS, P4.ADDON, P4.UKRS2

# Add-On factor unit at its +3 exponent: 4200 * 8 / 256 = 131.25 GBP/yr.
GRASSHOPPER_FACTOR = 6      # 787 GBP/yr (from 3150); chosen from the 1850 sweep
JUDAH_FACTOR = 12           # Central Pacific T.D. Judah 1863, 126 hp: 1575 GBP/yr (from 3937)
EARLY_US = [0, 1]           # NARS Norris (1838), 4-4-0 American (1851)
EARLY_US_EXP = 3            # class 44 at +3 = 0.4286 x original: Norris 2700, American 3262 (sweep: 2700 = parity with Planet on light duty)


def spec(name):
    if name == 'original':
        return []
    if name == 'A_targeted':
        return [dict(target=NARS, tag='A', prices={44: EARLY_US_EXP}, engines=[dict(id=i, cls='electric') for i in EARLY_US]),
                dict(target=ADDON, tag='A', engines=[dict(id=116, factor=GRASSHOPPER_FACTOR), dict(id=122, factor=JUDAH_FACTOR)])]
    if name == 'B_steam':
        return [dict(target=NARS, tag='B', prices={44: 3}, engines=[dict(id=i, cls='electric') for i in P4.NARS_STEAM])]
    if name == 'C_cross':
        # NARS set-wide x1/2 (class 42 +4 -> +3: steam, diesel, electric), early outliers x0.4286 (class 44 +3);
        # UKRS2 unchanged: the era baseline shows it beside GETS / Add-On, not below them.
        return [dict(target=NARS, tag='C', prices={42: 3, 44: EARLY_US_EXP}, engines=[dict(id=i, cls='electric') for i in EARLY_US]),
                dict(target=ADDON, tag='C', engines=[dict(id=116, factor=GRASSHOPPER_FACTOR), dict(id=122, factor=JUDAH_FACTOR)])]
    raise KeyError(name)


def extras(name):
    return [P4.grf(s['target'], s['tag'], prices=s.get('prices'), engines=s.get('engines')) for s in spec(name)]


VARIANTS = ['A_targeted', 'B_steam', 'C_cross']


def changed_engines(name):
    """Runtime IDs whose running cost the variant changes (from the spec + roster)."""
    out = set()
    for sp in spec(name):
        g = sp['target']
        ids = {e['id'] for e in sp.get('engines', [])}
        if 42 in sp.get('prices', {}):   # set-wide class-42 change: every locomotive of that set
            ids |= {int(r['local_vehicle_id']) for r in P4.ROSTER if r['source_grfid'] == g and r['category'] != 'wagon'}
        out |= {P4.RID[(g, i)] for i in ids if (g, i) in P4.RID}
    return out
