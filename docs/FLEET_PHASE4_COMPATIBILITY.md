# Fleet Phase 4: implementation feasibility and compatibility

What can actually implement a selective rebalance, what it preserves, and what is still
unverified. RUNTIME = measured in JGRPP 0.73.4; SOURCE = read from code, GRF bytes or
licence files.

## 1. Mechanisms compared

| # | Mechanism | Feasible here? | Evidence |
| --- | --- | --- | --- |
| 1 | Per-vehicle property override (Action 0 prop 0x0D running-cost factor) from a separate GRF via the engine-allocation override | **Add-On only.** NARS: catalogue-only trap (no in-service effect). UKRS2: no effect | RUNTIME, feasibility suite |
| 2 | Callback-aware adjustment: move an engine to another running-cost class (prop 0x0E) and set that class's set-local multiplier, so the set's own callback 0x36 still supplies its state factors | **Yes, for NARS and UKRS2** (class 44 is unused by both). Coarse: ×0.857 × 2^k steps | RUNTIME: state ratios preserved, 33/33 engines |
| 3 | Steam-only cost-base change | **Yes, via #2.** Proven to change exactly the 21 NARS steam engines and no diesel or electric (Variant B) | RUNTIME, catalogue integrity |
| 4 | Minimal source patch (fork the GRF) | NARS 2.52: **not permitted** (copyright notice, no licence granted). UKRS2: **prohibited** ("Distribution or modification without permission prohibited"). Add-On: permitted (GPL v2), but unnecessary because #1 works | SOURCE: `license.txt` in each package |
| 5 | A dedicated "Europe 1830 balance" GRF | **Yes, as built**: one tiny GRF per target set (one override target per GRFID). It contains only Action 8 and Action 0; no code, graphics or data of the original sets | RUNTIME, all suites |
| — | JGRPP engine/source patch | Not justified: the cost path behaves as coded, and the stationary-cost settings act on every set | Phase 3 |

**Most maintainable: #5, implemented with #1 for the Add-On and #2 for NARS.** The balance
GRF is about 260 bytes in total and is rebuilt deterministically from `variants.py` by
`build_balance_grfs.py`. Its build is byte-identical to the GRFs that were tested
(`test_phase4.py`).

## 2. What the balance GRFs preserve

| Property | Status | Evidence |
| --- | --- | --- |
| Vehicle identities (engine IDs, local IDs, GRFIDs of the original sets) | Preserved | The GRFs define no vehicles. On the cloned save all 176 trains keep owner, unit number, engine, wagon count and length (RUNTIME) |
| Purchase prices | Preserved | 2,854 engines × 3 dates × 3 variants: zero price changes (RUNTIME) |
| Graphics, sounds, refits | Preserved | No Action 1/2/3/4 in the GRFs (SOURCE). Cargo capacities unchanged (RUNTIME) |
| Cargo compatibility | Preserved | No cargo or rail-type translation table is defined. `GetCurrentGRFOverride()` copies translation tables to the target, so defining none is required. Capacities and refits are unchanged (RUNTIME) |
| Articulated vehicle definitions | Preserved | No articulation properties or callbacks touched. The Mallet, Big Boy and Yellowstone build, run and climb identically (RUNTIME: tonnage equal across variants) |
| Introduction dates | Preserved | Design dates unchanged in every catalogue (RUNTIME) |
| Physics (power, TE, weight, speed) | Preserved | Unchanged in every catalogue. Delivered tonnage identical across cost levels on every duty (RUNTIME) |
| Multiplayer determinism | **Verified for the tested sessions** | 180 control runs reproduce exactly (single-player, RUNTIME). A windowed client passed about 180 network sync checks over two 4-minute sessions on the Variant C campaign clone, with no desync (see §4). Longer sessions with several human clients are not tested |

Unchanged GRFIDs are **not** treated as proof of compatibility. Each row above was tested.

## 3. Savegame safety (cloned saves only)

Source: the latest campaign save, `… 1893-06-04.sav`. The clone and every derivative lived
in `runs\_saves\`. SHA-256 of the source and the production save-folder listing were
identical before and after (RUNTIME, `savetest_*.json`).

| Test | Variant B | Variant C |
| --- | --- | --- |
| Load existing campaign save with balance GRFs added (NGRF rewrite) | ✔ 176 trains | ✔ 176 trains |
| Vehicle identity preserved | ✔ | ✔ |
| Correct costs after load | ✔ NARS 4-4-0 Express £9,450 → £4,050 (×0.4286); 13 other engine types unchanged | ✔ Express £9,450 → £4,725 (×0.5); others unchanged |
| Consist integrity | ✔ (parts and length per train unchanged) | ✔ |
| Game-written save with the GRFs | ✔ autosave written in the test directory | ✔ |
| Rollback: that save with the GRFs removed | ✔ all costs back to original, identities intact | ✔ |
| Autoreplace onto and away from modified engines | ✔ (new-game fixture, Variant A engines) | — (same mechanism) |

**Important:** OpenTTD does not let a player add a GRF to a running game, outside
developer tools. Here the GRF list of a clone was edited at chunk level. A production
roll-out would need the campaign save's GRF list changed the same way, by an
administrator, with every client updated. Rollback works by the same edit.

## 4. Multiplayer (localhost only, cloned save)

A dedicated JGRPP server was bound to 127.0.0.1:3989, not advertised, running the
Variant C clone. The client was a second JGRPP instance with null video, run from its own
test directory (RUNTIME, `mptest_C_cross.json`, `mp_logs/`).

| Check | Result |
| --- | --- |
| Server starts with the balance GRFs and the cloned save | ✔ |
| Client with the balance GRFs joins | ✔ `Client #2 … joined` |
| Client leaves and rejoins | ✔ `Client #3 … joined` |
| Client **without** the balance GRFs | ✔ **Refused**: "NewGRF 52560010 not found". It cannot join a modified server, which protects the campaign from silent mismatches |
| Desync, headless client | None reported, but the null-video client logged "Missed frame for sync-test" for all 25 sync points, so no states were compared there |
| **Desync, windowed client** (`mptest.py --gui`, `mptest_C_cross_gui.json`) | **None.** A normal windowed JGRPP client joined, played 240 s, left, rejoined (at server frame 9,147) and played another 240 s. **0 missed sync frames**, no sync error, and the connection was never lost (it closed only when the test ended it). Default `sync_freq` is 100 frames, so this is about 90 state comparisons per session (DERIVED from the frame counter). **Network determinism verified for this session length** |
| Production multiplayer environment | Never touched. No production server was started, and nothing was advertised |

The first Variant B attempts failed because a null-video client does nothing without a
`client_name`. That setting lives in `private.cfg`, which is now written into the test
directory. Those attempts are recorded in `mptest_B_steam.json`.

## 5. Source availability and redistribution

| Set | Licence (from the package) | Consequence |
| --- | --- | --- |
| NARS 2.52 (PikkaBird) | "Copyright 2021 David Dallaston (PikkaBird)", with no licence grant | No fork or redistribution of a modified NARS. An independent override GRF does not modify or contain NARS, but it deliberately changes NARS economics. **Permission from the author obtained** (reported by the project owner, 2026-11-12; keep the written record) |
| UKRS2 1.05 (PikkaBird) | "All rights reserved. Distribution or modification without permission prohibited." | Nothing proposed touches UKRS2 |
| NARS Add-On 2cc | GPL v2 | A fork would be allowed, but the override is simpler and keeps the original binary |

The balance GRFs are project-authored data. They contain no third-party code or graphics.

## 6. Rollback instructions (for any future trial)

1. Keep the original GRF files unchanged. The balance GRFs never modify them.
2. For a **new game**: remove the balance GRF(s) from the NewGRF list before starting.
   Costs revert immediately because nothing is stored per vehicle.
3. For an **existing save**: remove the balance GRF records from the save's GRF list
   (`save_tools.rewrite(..., remove={'52560010','52560011'})`, the same operation tested
   above) on a copy, load it, and verify costs against `cat-original-*`.
4. Multiplayer: every client must remove the GRF at the same time as the server. A
   mismatched client is refused, as tested.
5. To verify: `python -B test_phase4.py` must pass.
