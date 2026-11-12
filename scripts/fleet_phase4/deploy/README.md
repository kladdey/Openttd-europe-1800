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

## Ledger year fix (optional, separate from the balance)

The campaign's economy date, which labels the finances window and drives the GameScript's
timers, still runs 30 years behind the calendar (1863 vs 1893), an offset inherited from the
1800 scenario. JGRPP's change-date cheat resynchronises it, moving vehicle and link-graph dates
with it and staying in calendar mode throughout.

**Do not** switch *Timekeeping units* to wallclock and back to fix this. That also resyncs the
date, but the campaign GameScript stops immediately (`Pinned AXIS/calendar time required`).

| | Calendar | Economy / finances |
| --- | --- | --- |
| Before | 1893-06-05 | 1863-06-06 |
| After | 1893-06-05 | 1893-06-05 |

The package contains `campaign_<date>_balance-v1_datesynced.sav`: the balanced save with this
fix already applied. To apply it to a later save yourself:

1. Stop the server and keep a copy of the save.
2. Open the save in **single-player** with the same OpenTTD (JGRPP 0.73.4) and NewGRFs. The
   cheat is disabled in multiplayer.
3. Pause the game.
4. Press **Ctrl+Alt+C** to open *Sandbox Options*. On **Change date**, click the left arrow
   once (one year back), then the right arrow once (back to the current year).
5. Open the console (the key below Esc) and run `getfulldate`. *Calendar Date* and *Economy
   Date* must now be equal.
6. Save under a new name and host that save. If the server starts paused, type `unpause` in
   the server console.

What changes:

- The finances window shows real years: 1891 / 1892 / 1893 instead of 1861 / 1862 / 1863.
  The amounts are untouched.
- The save records that the change-date cheat was used. This is shown only in the cheats window.
- The GameScript sees the economy date jump forward 30 years once. A GameScript industry
  closure that is in progress at that moment is cancelled safely: the industry stays open
  and a news item asks for administrator review. In the tested save no closure was in
  progress, and the GameScript produced exactly the same events as without the fix.

Rollback: host the save kept from step 1.

## Known limits

- Multiplayer sync was verified with one windowed client for 2 × 4 minutes (about 180
  sync checks). Sessions with several clients or longer play are untested: watch the
  first one.
- The tool supports the JGRPP 0.73.4 save layout used here. It aborts rather than guess
  on anything unexpected.
