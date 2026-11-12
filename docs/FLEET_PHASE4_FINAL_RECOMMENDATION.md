# Fleet Phase 4: final recommendation

**Status: experimental, test-backed, NOT approved, NOT deployed.** No production GRF,
save, scenario or multiplayer configuration was changed. Evidence base: 2,191 native JGRPP
0.73.4 runs on Historical AXIS 0.6.0, with 5 seeds for every priority comparison, plus
cloned-save and localhost-multiplayer tests. All operating profits are DERIVED from
RUNTIME ledgers.

## The recommended change: Variant C ("Europe 1830 balance", 2 GRFs, 258 bytes)

| GRF (load directly after) | Content | Effect (RUNTIME catalogue) |
| --- | --- | --- |
| `europe1830_balance_C_cross_44440302.grf`, GRFID `52560010` (after NARS 2.52) | Engine-allocation override → NARS. NARS-local price 42 (steam running base, used by **all** NARS locomotives) +4 → **+3**. Norris (local 0) and 4-4-0 American (local 1) running-cost class → 44, with NARS-local price 44 = **+3** | All 71 NARS 2.52 locomotives ×0.5 (steam, diesel and electric). Norris £6,300 → **£2,700**. American £7,612 → **£3,262** |
| `europe1830_balance_C_cross_4e4d0518.grf`, GRFID `52560011` (after NARS Add-On) | Engine-allocation override → Add-On. Grasshopper (local 116) running-cost factor 24 → **6**. T.D. Judah (local 122) 30 → **12** | Grasshopper £3,150 → **£787**. Judah £3,937 → **£1,575** |

Not changed: purchase prices, physics, dates, capacities, graphics, UKRS2, GETS, PTS,
PRSP, and every other Add-On engine. Exact per-engine values are in
[`fleet_phase4_proposed_values.csv`](fleet_phase4_proposed_values.csv). Binaries and
SHA-256 are in `research/fleet_phase4/grf_build/`, built by
`scripts/fleet_phase4/build_balance_grfs.py`.

## Direct answers

**1. Which balancing approach performed best?**
**C: cross-set normalisation.** It is NARS set-wide ×½ plus individual fixes for the two
early American outliers and the Add-On's Grasshopper. Under C the tested NARS engines
reach 0.87–1.00 of the era-best on their own duties from 1878 to 2025, from 0.63–0.89
originally, and no NARS engine exceeds the best other engine by more than 6%. A (targeted
only) fixes 1850 and leaves NARS 11–37% behind later. B (steam only) works technically
but leaves NARS diesels 11–23% behind from 1955 to 2025.

**2. What should Norris cost?** **£2,700/yr catalogue** (was £6,300), which bills about
£3,000/yr in service with 12 hoppers. At this value Norris (1838):
- earns 1.6× Planet on heavy 12-hopper trains (£14.3k vs £8.75k);
- is at parity on light trains (£8.6k vs £8.2k);
- earns 1.35× on full passenger trains;
- climbs a 3% grade with one loaded hopper where Planet cannot;
- never beats Coppernob or Crampton.

£1,350 makes it beat Planet on every flat duty, so it was rejected. The original £6,300
leaves it barely viable on light work (£5.2k against Planet's £8.2k).

**3. What should Grasshopper cost?** **£787/yr** (factor 6, −75%). The proposed −50%
(£1,575) is insufficient: 62% of Planet's profit against 71%, and £77k against £93k
twenty-year cash. Its weakness is mainly throughput: 63 hp, 21% less tonnage, slower.
So it stays below Planet even at Planet's own cost. That is the intended "budget
curiosity", not a trap. Adding a standstill discount is not technically possible without
replacing its graphics, and would be worth only about £190/yr because it moves 89–93% of
the time.

**4. Should UKRS2 costs be increased?** **No.** The era baseline places UKRS2 beside GETS
and the Add-On in every era. Its grade weakness is physics, and its ageing steps already
impose obsolescence. No measured case requires an increase.

**5. Should NARS steam be adjusted globally or individually?** **Globally for the whole
NARS 2.52 set (steam *and* diesel/electric, ×½), plus individually for Norris and the
American.** A steam-only change (B) is possible but leaves NARS diesels uncompetitive. The
NARS fixed-cost curve over-penalises the two smallest early engines, which need the
extra ×0.86.

**6. Which American locomotives are currently (original) uncompetitive?**
The share of the era-best on the engine's own duty:

| Engine | Duty | Share |
| --- | --- | --- |
| Norris | 1850 passenger | 0.66 |
| NARS 4-4-0 American | 1860 freight | 0.56 |
| Grasshopper | 1850 passenger | 0.30 |
| Grasshopper | 1850 freight vs Planet | 0.42 |
| T.D. Judah | 1866 light passenger / full trains | 0.70 / 0.59 (0.22–0.30 on coal) |
| Mallet | 1945 flat / grade | 0.63 / 0.63 |
| Santa Fe | 1925–45 flat | 0.71–0.79 |
| NARS Express | 1890 passenger | 0.81 |
| Hudson / NARS Jubilee | 1940 passenger | 0.81–0.82 |
| GP9 / RS3 | 1955 | 0.89 |
| SD40-2 / GP38-2 | 1977 | 0.85–0.87 |
| F40PH | 1980 passenger | 0.80 |
| SD70MAC / C44-9W / GE Evolution | 2000–2025 | 0.77–0.85 |

The **Add-On** engines (Big Boy, Yellowstone, RSD7, SD40, SD80MAC, SD70ACe, D16, Angus)
are already competitive and are unchanged.

**7. Which vehicles would become overpowered under the proposed changes?**
None beyond a 6% lead in any tested era or duty. Watch list:
- NARS Consolidation 1878 (1.04 against UKRS2 Goods, flat);
- Santa Fe on 3% grades in 1925 (1.06 against Angus);
- SD40-2 on grades in 1977 (1.01).

Norris's 1.6× lead over Planet on heavy trains is a deliberate 1838–44 specialisation
that ends when Coppernob arrives. Rejected as overpowered: Norris at £1,350 or below, and
Grasshopper at or below Planet's £525.

**8. How do the modifications affect heavy freight and gradients?** Physics is untouched,
so delivered tonnage is identical. On a sustained 3% grade at the 7-tile limit the
American heavy engines remain the only profitable performers. The Mallet improves from
£23.6k to £36.4k on the grade (0.98 of the Big Boy) and the Santa Fe from £26.1k to £35.8k.
The UKRS2 8F and Mineral, NARS GP9 and GP38-2, Brush Type 4 and Class 58 still stall or
break even on the grade. On flat supply-limited duty the British 8F still out-earns every
American heavy engine. Specialisation is preserved and sharpened.

**9. Are the experimental GRFs technically suitable for the existing multiplayer campaign?**
**Technically yes, with conditions; not yet approved.** Tested on cloned campaign saves:
- loading with the GRFs keeps all 176 trains' identities;
- costs after load are correct;
- game-written saves work;
- rollback restores every cost;
- autoreplace works.

Localhost multiplayer: join and rejoin work, and a client without the GRFs is refused. A
normal windowed client played two 4-minute sessions on the Variant C campaign clone with
0 missed sync frames and no desync, which is about 180 network sync checks.

Conditions:
- **(a)** Determinism is verified only for those short single-client sessions. Watch the
  first real session with several clients.
- **(b)** Adding a GRF to the running campaign needs an administrator GRF-list edit of
  the save. It is not a normal in-game operation.
- **(c)** Every client must install the GRF.
- **(d)** ~~Ask PikkaBird before distributing a NARS rebalance.~~ **Resolved 2026-11-12:**
  the project owner reports that permission was obtained from the NARS author. Keep the
  written permission with the project records (not verified by me).

**10. Exact changes to approve for production.**

1. **Approve Variant C's NARS GRF** (`52560010`): NARS-local price 42 → +3; NARS-local
   price 44 → +3; Norris (L0) and American (L1) running-cost class → 44. *Confidence:
   high* (5 seeds; 1850–2025; catalogue integrity, state ratios, ageing, save and rollback
   all verified).
2. **Approve the Grasshopper part of the Add-On GRF** (`52560011`, L116 factor 6 =
   £787). *Confidence: high.*
3. **Approve the T.D. Judah change** (L122 factor 12 = £1,575). *Confidence:
   medium-high.* It was tested in its passenger role (suite `judah`: 1866, 5 seeds, RUNTIME
   ledgers, profit DERIVED).
   - **48-tile, 4-coach route:** £9.8k → £12.2k (0.70 → 0.86 of the best, the UKRS2 Lady
     at £14.2k). It still trails Coppernob (£12.9k) and Crampton (£13.5k), and stays the
     cheapest to buy, with a 1.0-year payback.
   - **96-tile, full 7-tile train:** £21.3k → £23.7k (0.66). At 126 hp it can't move full
     trains quickly (27.8 km-ish/h), so it stays a light-train engine.

   It becomes a sensible budget light-passenger engine and is not overpowered. In the same
   test, the NARS American under C reaches 0.87 on the short route and parity on the long
   one (£35.7k against the Lady's £36.0k), up from 0.59 and 0.88.
4. **No change** to UKRS2, GETS, the Polish sets, purchase prices, or the Add-On's
   set-wide parameter.
5. **Before deployment:**
   - ~~author permission (NARS)~~: obtained (reported by the project owner, 2026-11-12);
   - an administrator GRF-list update of the campaign save, done on a copy and verified
     with `test_phase4.py`;
   - simultaneous client distribution;
   - keep the original GRF list for rollback (procedure in
     [compatibility](FLEET_PHASE4_COMPATIBILITY.md) §6).

## What is measured, estimated and unverified

| Measured (RUNTIME) | Estimated (DERIVED / ANALYTIC) | Unverified |
| --- | --- | --- |
| Ledger revenue, train running, property; delivered tonnes; speeds; per-state running rates; catalogue values; ageing; autoreplace; save load, autosave and rollback; client join, rejoin and refusal; about 180 network sync checks with a windowed client; Judah in 1866 passenger service | Operating profit (revenue − running − property); payback; 10- and 20-year cash flow from 5-year means (the 20-year cash for the priority engines is measured); cost per tonne-tile; the £190/yr value of a hypothetical Grasshopper standstill discount | Multi-client and long multiplayer sessions (two 4-minute single-client sessions passed); NARS electric locomotives on electrified routes; GETS/Polish standstill behaviour; long (96-tile) routes with the original Coke Oven (AXIS refuses it, so a fallback acceptor was used); 1830 calendar date for Norris (tested in 1850) |

## Deployment package (prepared 2026-11-12, not deployed)

Location: [`deploy/europe1830-balance-v1/`](../deploy/europe1830-balance-v1/) in git. The
local package, which also contains the balanced campaign save, is in
`C:\Users\Kladd\OTTD-runtime-validation\deploy\europe1830-balance-v1\` and `.zip`.
Install and rollback steps are in its `README.md`. The package GRFs carry production names
(*Europe 1830 Balance v1*); their content is otherwise Variant C.

Native JGRPP checks on the exact package (`verification.json`, RUNTIME):

- **Catalogue:** identical to the tested Variant C GRFs for all 2,854 engines at 1850,
  1925 and 2000.
- **Balanced campaign save:** all 176 trains keep their identity. The 14 engine types in
  use have exactly the tested Variant C costs, and no purchase price changes.
- **Campaign GameScript:** the save loads and runs with the campaign's own "Historical
  Industry Lifecycle" GameScript (240 s, no script errors, no missing GRFs).
- **Rollback:** `apply_balance.py rollback` output is content-identical to the original
  save.

The source save was only read; its SHA-256 was unchanged afterwards.
