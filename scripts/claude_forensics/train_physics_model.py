"""Simplified re-implementation of JGRPP 0.73.4 realistic train acceleration
(src/ground_vehicle.cpp GetAcceleration / CargoChanged / CalculatePower, src/train.h).

MODEL, NOT A GAME MEASUREMENT. Reproduces the force/resistance terms:
  power_W = hp*746 ; tractive force = min(max_TE, power_W*18/(5*v))   (v in km-ish/h, v>0)
  resistance = 10*W (axle) + W*15*(512+v)/512 (rolling) + 14*air*v^2/1000 + slope
  air = a + 3*a*parts/20, a = max(2048/vmax_display,1)   (air_drag property assumed 0 = default)
  slope = 3% * 100 * weight of parts on an upward slope (train_slope_steepness = 3)
  speed integrates accel=(F-R)/(4*m) per tick in 1/256 km-ish/h units -> dv/tick=(F-R)/(1024 m)
  distance: ticks per tile = 2048 / v  (movement clock used in the prior audit; approximation)
Excluded: per-part slope occupancy on short hills, curves, breakdowns, station approach braking,
realistic-braking (disabled in campaign), loading time. Loco data from committed API snapshots.
Usage: python3 -I scripts/claude_forensics/train_physics_model.py <repo_root>
"""
import sys, os

LOCOS = {  # name: (hp, max TE N, weight t, vmax km-ish/h)  -- vehicle_economy_snapshots.csv, 1850
    'Planet (UKRS2 1830)': (120, 11000, 14, 48),
    'Grasshopper (Add-on 1830)': (63, 11000, 8, 38),
    'Norris (NARS 1837/38)': (200, 19000, 20, 56),
    'Coppernob (UKRS2 1844)': (250, 43000, 37, 64),
    'Crampton (UKRS2 1847)': (350, 21000, 47, 88),
    'American 4-4-0 (NARS 1850)': (450, 31000, 41, 80),
}
HOPPER = (12, 20, 64)   # NARS Single Hopper id 101: empty t, coal capacity (1 t/unit assumed), speed limit

def run_leg(loco, n_wag, loaded, tiles, grade_tiles=0):
    hp, te, lw, lv = loco
    ew, cap, wv = HOPPER
    W = lw + n_wag * (ew + (cap if loaded else 0))
    vmax = min(lv, wv) if n_wag else lv
    parts = 1 + n_wag
    a = max(2048 // vmax, 1); air = a + 3 * a * parts // 20
    P = hp * 746
    v = 0.0; x = 0.0; t = 0; stalled = False
    while x < tiles:
        on_grade = x >= tiles - grade_tiles      # grade on the final section, whole train on it
        R = 10 * W + W * 15 * (512 + v) / 512 + 14 * air * v * v / 1000 + (W * 300 if on_grade else 0)
        F = min(te, P * 18 / (5 * v)) if v > 0 else max(min(te, P), W * 8 + R)
        v = min(vmax, max(0.0, v + (F - R) / (1024 * W)))
        if v <= 0.0 and t > 10:
            stalled = True; break
        x += v / 2048; t += 1
        if t > 2_000_000: stalled = True; break
    return t, v, stalled, W

def terminal_speed(loco, n_wag, loaded, grade):
    hp, te, lw, lv = loco
    ew, cap, wv = HOPPER
    W = lw + n_wag * (ew + (cap if loaded else 0)); vmax = min(lv, wv) if n_wag else lv
    a = max(2048 // vmax, 1); air = a + 3 * a * (1 + n_wag) // 20
    best = 0
    for v10 in range(1, vmax * 10 + 1):
        v = v10 / 10
        R = 10 * W + W * 15 * (512 + v) / 512 + 14 * air * v * v / 1000 + (W * 300 if grade else 0)
        F = min(te, hp * 746 * 18 / (5 * v))
        if F >= R: best = v
    return best

lines = []
def p(s=''): print(s); lines.append(s)
p('## Terminal (power/TE-limited) speed, km-ish/h, 12 NARS single hoppers (wagon limit 64)')
p('loco | empty flat | loaded flat (W t) | loaded, whole train on 3% grade | max total train t on 3% (TE/325 N/t)')
for n, l in LOCOS.items():
    W = l[2] + 12 * 32
    p(f'{n} | {terminal_speed(l,12,False,False)} | {terminal_speed(l,12,True,False)} ({W}) | {terminal_speed(l,12,True,True) or "STALL"} | {l[1]/325:.0f}')
p('\n## 32-tile flat route, 12 hoppers loaded out / empty back, running time only (no loading/dwell)')
p('loco | loaded leg days | empty leg days | round-trip running days | max trips/yr if never waiting for cargo | max t/yr')
for n, l in LOCOS.items():
    t1, *_ = run_leg(l, 12, True, 32); t2, *_ = run_leg(l, 12, False, 32)
    days = (t1 + t2) / 74
    p(f'{n} | {t1/74:.1f} | {t2/74:.1f} | {days:.1f} | {365/days:.1f} | {365/days*240:,.0f}')
p('\n## Same route with a sustained 4-tile 3% climb at the end of the loaded leg')
for n, l in LOCOS.items():
    t1, v, stalled, W = run_leg(l, 12, True, 32, grade_tiles=4)
    p(f'{n} | {"STALLS on the grade" if stalled else f"{t1/74:.1f} days loaded leg"}')
p('\n## Largest number of loaded NARS hoppers that can climb a sustained 3% grade at all')
for n, l in LOCOS.items():
    k = 0
    while k < 30 and terminal_speed(l, k + 1, True, True) > 0: k += 1
    p(f'{n} | {k} hoppers ({k*20} t coal)')
od = os.path.join(sys.argv[1] if len(sys.argv) > 1 else '.', 'docs', 'research', 'claude_forensics')
os.makedirs(od, exist_ok=True)
open(os.path.join(od, 'train_physics_model.txt'), 'w').write('\n'.join(lines) + '\n')
