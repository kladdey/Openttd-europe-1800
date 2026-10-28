# Historical Industry Probe — unexecuted in JGRPP

Minimal source proof of concept, not an installed or validated GameScript.
Targets **JGRPP 0.73.4, API 16, AXIS 2.3.1 / Extreme Classic**. No scenario,
NewGRF or map file is opened or rewritten by this repository code.
Enabling construction DOES change the running disposable game's industries.

1. Prepare a **new disposable game/copy**, starting in **1830**, with the exact
   NewGRFs. Preserve the working scenario outside the experiment.
2. Use calendar-based timekeeping. Set industry density to **Funding only**.
   Enable AXIS **Allow industries spawning during gameplay**: deity construction
   takes that callback path, even though density prevents natural openings.
3. Copy this directory to the test installation's `game/` script directory;
   select Historical Industry Probe before starting the test. Leave
   `attempt_build=0` for the first inventory-only run. No auto-install is supplied.
4. Inspect GameScript debug logs: year, type names and cargo counts. On another
   fresh test run set `attempt_build=1`. Expect one successful coal mine OR an
   explicit failure after at most 32 construction commands/256 candidate cells.
   The grid is only a technical placement probe; it has no geographic meaning.
5. Capture logs, before/after industry counts, settings and saved-game hashes.
   Test absent AXIS, AXIS spawning disabled, unsuitable terrain, wallclock mode,
   save/reload, and three-company join/rejoin. Reload must not repeat an attempt.

The GRFID and coal-mine local ID are verified in upstream 2.3.1 source. The
mapping alone cannot prove the installed version or economy; verify these in
the test game's NewGRF UI. No text-name matching or guessed map coordinate is
used. API load incompatibility can prevent the script starting at all; the
runtime catch cannot recover from a rejected API version or syntax failure.

Status: API names and registration version checked against pinned C++ headers;
**no Squirrel compilation, no in-game execution, no successful construction or
multiplayer validation claimed**. Save/Load logic is written, not runtime-tested.
No removal, production control, setting changes or full progression system.
