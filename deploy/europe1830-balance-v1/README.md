# Europe 1830 Balance v1: deployment package

Variant C of the Phase 4 fleet rebalance. It changes **running costs only**. Purchase
prices, physics, introduction dates, capacities, graphics, UKRS2, GETS, PTS and PRSP are
unchanged.

| Locomotives | Running cost per year |
| --- | --- |
| All 71 NARS 2.52 locomotives (steam, diesel, electric) | ×½ |
| Norris (NARS) | £6,300 → £2,700 |
| 4-4-0 American (NARS) | £7,612 → £3,262 |
| Grasshopper (NARS Add-On) | £3,150 → £787 |
| Central Pacific T.D. Judah (NARS Add-On) | £3,937 → £1,575 |

Evidence and reasoning: `docs/FLEET_PHASE4_FINAL_RECOMMENDATION.md` on branch
`claude/europe-1830-fleet-phase4`. Permission from the NARS author was reported by the
project owner on 2026-11-12.

## Contents

| File | Purpose |
| --- | --- |
| `newgrf/europe1830_balance_v1_nars.grf` | GRFID `52560010`; must load **directly after** NARS 2.52 (`44440302`) |
| `newgrf/europe1830_balance_v1_nars_addon.grf` | GRFID `52560011`; must load **directly after** the NARS Add-On Set 2cc (`4E4D0518`) |
| `campaign_<date>_balance-v1.sav` | The newest campaign save with the two GRFs added to its NewGRF list. The GameScript and its state are untouched. Not in git; local package only |
| `apply_balance.py`, `balance_grfs.json` | Adds the GRFs to, or removes them from, any later campaign save (standard-library Python) |
| `verification.json` | Native JGRPP checks run on this exact package |
| `SHA256SUMS.txt` | Checksums of every file |

## Install

Everyone must use the **same two files**: server and all clients. A client without them is
refused when joining (tested).

1. Check the files: `certutil -hashfile <file> SHA256` must match `SHA256SUMS.txt`.
2. **Every player and the server:** copy both `.grf` files into
   `Documents\OpenTTD\newgrf\`. They are not on the online content service, so share them
   directly.
3. **Server, existing campaign:**
   1. Stop the server and keep a copy of the current save and of `openttd.cfg`.
   2. If the save to continue is newer than the one in this package, convert it yourself
      instead of using the packaged save:

      ```bash
      python apply_balance.py apply "<current save>.sav" "<current save> balance-v1.sav"
      python apply_balance.py check "<current save> balance-v1.sav"
      ```

      The tool needs an LZMA save. If it reports a different header, set
      `savegame_format = lzma` in `[misc]` of `openttd.cfg`, load and save once, and
      retry. It never overwrites its input.
   3. Start the server with the balanced save.
4. **New games (optional):** in the NewGRF settings, add the two GRFs directly after their
   targets: Balance-NARS after NARS 2.52, Balance-Add-On after the NARS Add-On.
5. On the first session, confirm in the game that, for example, the Norris shows £2,700/yr
   in the purchase list.

## Rollback

1. On the server:

   ```bash
   python apply_balance.py rollback "<balanced save>.sav" "<save> original.sav"
   ```

   This was verified to give content identical to the save before balancing.
2. Start the server with the rolled-back save. Clients may keep the GRF files (unused) or
   delete them.
3. Costs return immediately: OpenTTD stores no running cost per vehicle.

## Known limits

- Multiplayer sync was verified with one windowed client for 2 × 4 minutes (about 180
  sync checks). Sessions with several clients or longer play are untested: watch the
  first one.
- The tool supports the JGRPP 0.73.4 save layout used here. It aborts rather than guess
  on anything unexpected.
