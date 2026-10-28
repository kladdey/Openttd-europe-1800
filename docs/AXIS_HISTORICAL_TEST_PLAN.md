# AXIS Historical Europe — reproducible test plan

2026-10-28. Binary 0.1.0, GRFID `4B484531`, numeric version 1.
**16 headless JGRPP 0.73.4 construction cases have passed.** Human multiplayer,
editor and actual transported-cargo production tests below remain pending.

## Installation and isolation

1. Preserve the working campaign and original AXIS. Prepare a separate portable
   JGRPP **0.73.4** installation and a fresh disposable **1830** game. Do not
   load or resave the working scenario. Use 256² for a quick technical test,
   then a separately prepared 4096² Europe candidate for geographic/performance tests.
2. Copy `newgrfs/axis-historical-europe/dist/axis-historical-europe-0.1.0.grf`
   into the **test** installation's `newgrf/`. Keep its matching source ZIP and
   attribution alongside any binary redistribution. Build from the directory
   README if the ignored local artifact is unavailable in a fresh Git checkout.
3. In NewGRF selection, choose **AXIS Historical Europe 0.1.0** and remove
   original AXIS. Never enable both. Confirm ID `4B484531`, version 1, and
   **Extreme Classic** (first economy selection; internal `BASIC_TEMPERATE`).
4. Enable **Historical Europe steelmaking dates (Classic only)**, parameter 10.
   Enable AXIS **Allow industries spawning during gameplay**, parameter 2 bit 2.
   For GS-only openings choose engine density **Funding only**. For natural
   generation tests choose a normal/high density in a new game instead.
5. Use calendar-based timekeeping initially. Install transport NewGRFs from
   their original sources, not from this fork's source bundle. Test their refits
   only after the industry-only smoke test passes.

For configuration-file tests the tested parameter vector is:

```ini
[newgrf]
axis-historical-europe-0.1.0.grf = 0 0 4 0 0 0 16 150 80 300 1
```

Positions are raw parameter indices: economy 0, parameter 2 value 4 means its
bit 2 is enabled, and parameter 10 value 1 enables history. Do not confuse raw
parameter 2 value 1 with enabling bit 2. Unrestricted test mode changes only the
last value to 0. Turning random/deity spawning off changes raw parameter 2 to 0.
The configuration UI is preferred for manual setup.

## Automated checks already executed

Run `prepare.py`, `build.py` and `validate.py` using the fork README. The static
validator checks source model equality, all 64 cargo slots, 320 emitted binary
cargo-label records, GRF identity/version, generated callback truth tables,
optional final-year/permission fields, batch expressions and cargo reachability.
The small generated patch also passed `git apply --check` against a pristine
source export. The original AXIS checkout stayed clean.
The complete corresponding-source ZIP was extracted to another directory and
its documented build commands produced the identical GRF SHA256. Run
`package.py --verify-rebuild` to repeat this check; it fixes Python's hash seed
and retains the deterministic ordering patch.

The optional Windows [runtime harness](../newgrfs/axis-historical-europe/runtime_test.py)
uses the separately extracted JGRPP engine and OpenGFX 8.0 under `.work/`.
It creates fresh 256² worlds, logs version/hash and inventory, starts a test-only
idle AI company, and exercises industry construction in deity and company modes.
It binds only localhost and terminates its own processes. It has no download or
campaign save-loading step. Run from repository root:

```powershell
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-europe/runtime_test.py --engine-directory ABSOLUTE_PATH_TO_DISPOSABLE_ENGINE
```

The exact passed report is
[runtime-result.json](../newgrfs/axis-historical-europe/runtime-result.json).
Company-mode GS executes the engine's funded-company route with an idle AI
identity; it is not a test of the human funding-window GUI. Deity mode executes
RANDOM, the shared natural-gameplay/GS category. Natural map generation was
tested independently at 1830 and 2000. A long run of autonomous gameplay openings
was **not** performed.

## Year expectations

Create a **fresh** test game for each year; do not change NewGRFs in an existing
save. With history on, these are permissions, not a guarantee of a suitable tile.
AXIS terrain/keystone restrictions still apply. Deity BOF construction needs a
nearby blast furnace; the automated harness supplies one.

| Year | Historical steelworks | EAF | BOF | Executed headless result |
|---|---|---|---|---|
| 1830 | Reject | Reject | Reject | PASS; early blast furnace builds; 64 cargoes, 92 types |
| 1850 | Reject | Reject | Reject | PASS |
| 1859 | Reject | Reject | Reject | PASS, steelworks lower boundary |
| 1860 | Allow | Reject | Reject | PASS, steelworks built |
| 1900 | Allow | Reject | Reject | PASS; EAF gameplay date is 1906 |
| 1905 | Allow | Reject | Reject | PASS, EAF lower boundary |
| 1906 | Allow | Allow | Reject | PASS, EAF built |
| 1950 | Allow | Allow | Reject | PASS |
| 1951 | Allow | Allow | Reject | PASS, BOF lower boundary |
| 1952 | Allow | Allow | Allow | PASS, BOF built |
| 1955 | Allow | Allow | Allow | PASS |
| 2000 | Allow | Allow | Allow | PASS |

Each of these 12 cases exercised both deity and funded-company construction.
Four additional passed cases:

* Unrestricted 1830: all three build through both routes.
* AXIS spawning off, 2000: deity construction rejects all three, while funded
  construction succeeds. This demonstrates the shared RANDOM permission.
* Natural map generation, 1830: zero instances of all three gated types.
* Natural map generation, 2000: the fixed-seed test map initially contains one
  of each; additional deity and funded builds succeed.

## Pending manual/runtime acceptance tests

**Funding-window and editor UI:** repeat the year table using the human funding
window and editor placement, recording rejection messages and tile coordinates.
At eligible years distinguish a historical veto from an unsuitable site. Try
original AXIS alongside the fork in an isolated new-game configuration and
confirm the incompatible-set error; never test it by changing the campaign save.
Check custom steelworks name, batch explanation and unrestricted-mode text.

**Actual steel production:** in a disposable 1860 game build a blast furnace,
coke oven and historical steelworks. Confirm `IRON`/`COKE` acceptance and
`STEL`/`SLAG` output using a vehicle set with verified refits. Deliver one input
alone: it must remain stockpiled with no output. Deliver the second: complete
3:1 batches should produce 3 steel + 1 slag, with remainders retained. Test small
loads, reverse delivery order, repeated callbacks, concurrent unloading, and
save/reload with partial stockpiles. Transport steel to an existing customer;
do not infer commercial viability from an output label in source.

**Persistence and construction expiry:** all current final-year fields are null,
so existing works should keep producing in 1906, 1952 and 2000. Verify across a
save/reload and date progression. To test the optional final-year feature, use
a separately versioned throwaway build with the steelworks final year 1900:
new construction must work through 1900 and fail in 1901, while a previously
built works continues its production callbacks. Do not force-close it or replace
the NewGRF in an existing campaign. The optional final-year guard has automated
synthetic expression tests, not this engine persistence test.

**Multiplayer and scale:** on a separately curated 4096² 1830 Europe candidate,
three humans join/rejoin, share matching GRF hashes, fund eligible works and
transport inputs/output. Record latency, server CPU, save size and industry
counts. Verify saved-game load and all listed transport refits. Run later-year
checks on new disposable candidates, and test a representative long campaign
before adoption. The headless 256² tests do not prove 4096² performance or
compatibility with the complete campaign vehicle stack.

Stop adoption if the custom batch duplicates/loses cargo, if the intended GRF
identity differs, if a before-date company build succeeds, or if save/reload
changes availability. Keep logs and the isolated failing save; leave the working
campaign unchanged.
