# AXIS Historical Europe 0.2.0 — Phase 5

**PARTIALLY READY.** Compiled, loaded and tested with the campaign's other 14
GRFs in fresh worlds. No certified conversion of the existing Europe scenario.
Do not install over stock AXIS or hot-swap a working save.

Current identity: **KHE1 / 4B484531**, numeric version **2**, minimum compatible
**1** within this fork identity. All original 91 industry IDs/recipes/layouts
and 64 cargo slots are preserved; reused steelworks ID 2 makes **92** types.
The manifest now explicitly governs all types. Historical parameter 10 defaults
on, applies only to Classic and does not close existing industries. Draft dates
and modern-cargo proxies are explicitly experimental. Year zero means no added
pre-1830 date gate. No cargo IDs or vehicle properties are changed.

**Current output:** ignored `dist/axis-historical-europe-0.2.0.grf`, **7,842,417
bytes**, SHA256 `0728a246327826ae2dccdcbb13578631ea401d088b56e1e954b917eb2f7af8a7`.
The complete matching source ZIP rebuilds identically. Compiler emitted 546
warnings, no errors; see `.work/logs/compile.log`.

Use the pinned build commands below with the current scripts: they now select
0.2.0 from the manifest. Build dependencies remain Python 3.12.14, NML 0.9.0,
Chameleon 4.6.0 and Pillow 13.0.0. For gameplay tests also install NumPy 2.3.5
using `requirements-test.txt`. `extend_policy.py` is a policy-review generator,
not an automatic build step; do not rerun it to erase manual date refinements.
`package.py --verify-rebuild` packages full licensed corresponding source and
checks an identical rebuild. No binaries or third-party assets are committed.

Current runtime entry points:

```powershell
python newgrfs/axis-historical-europe/integration_test.py
python newgrfs/axis-historical-europe/progression_test.py
python newgrfs/axis-historical-europe/production_phase5.py
python newgrfs/axis-historical-europe/gameplay_test.py --controlled --case coal_rail
python newgrfs/axis-historical-europe/gameplay_test.py --controlled --case grain_horse
python newgrfs/axis-historical-europe/gameplay_test.py --controlled --case timber_rail
python newgrfs/axis-historical-europe/gameplay_test.py --case passenger_horse
python newgrfs/axis-historical-europe/gameplay_test.py --case passenger_ship
python newgrfs/axis-historical-europe/summarize_phase5.py
python -m unittest discover -s tests -p test_axis_historical_phase5.py -v
```

Use the fork environment with `requirements-test.txt`, or the available bundled
Python with NumPy/Pillow for the gameplay runner. Repeat the three controlled
freight commands with `--stock` for stock-AXIS controls. `runtime_test.py` reruns
16 steel construction/parameter cases on the current artifact; use the engine
argument below. `production_test.py` is deliberately an archived 0.1.0 fixture;
use **production_phase5.py** for current steel tests.

Runtime prerequisites: official JGRPP 0.73.4/OpenGFX 8.0 under
`.work/runtime/engine/openttd-jgrpp-0.73.4-windows-win64/`, and the exact audited
NewGRF library/config under `.vehicle-audit-runtime/phase2/newgrf` and
`phase2-verified-1830.cfg`. These local assets are not repository dependencies
that can be redistributed with this fork. In a fresh checkout, recreate the
isolated library from the user's installed files and the recorded 15 identities;
do not substitute versions or install vehicles. The original scenario is read
only for its fingerprint, never loaded into a historical replacement list.

Fresh runs create unique case directories with raw logs/configs/GS source and
disposable saves beneath `.work/integration/`. Read-only hardlinks share isolated
copies only. A changed artifact requires a new integration directory, avoiding
changes to earlier linked inputs. Result JSON summaries can be regenerated;
archive them before a subsequent release audit. All engine invocations use
explicit disposable config paths and `-X -x`.

See [current implementation](../../docs/AXIS_HISTORICAL_IMPLEMENTATION.md),
[gameplay results](../../docs/AXIS_HISTORICAL_GAMEPLAY_VALIDATION.md),
[compatibility](../../docs/AXIS_HISTORICAL_COMPATIBILITY.md),
[migration](../../docs/AXIS_HISTORICAL_MIGRATION_GUIDE.md),
[release readiness](../../docs/AXIS_HISTORICAL_RELEASE_READINESS.md) and
[92-type matrix](../../docs/research/axis_historical_availability.csv).
Nothing was installed, pushed, merged or published.

## Archived 0.1.0 milestone instructions and evidence

The following version-specific outputs/counts/pending tests describe the earlier
milestone. Use the current Phase 5 reports and entry points above for new tests.

### AXIS Historical Europe 0.1.0 — steelmaking milestone

**Compiled experimental NewGRF; 16 headless JGRPP 0.73.4 construction tests passed.**
An actual truck-delivery and stockpile save/reload fixture also passed.
Human multiplayer, historical vehicle refits and campaign-scale tests remain.
Replacement for AXIS 2.3.1, not an add-on to it. Targets JGRPP 0.73.4 and
Extreme Classic. It is not a save-compatible swap for original AXIS.
No installation or scenario mutation is performed by the build scripts.
Do not run upstream `make install`: use this fork's wrapper and copy its distinct
output filename only into a disposable test installation.

* Provisional GRFID **4B484531** (`KHE1`), version **1**; unregistered project ID,
  not a claim of a globally reserved identifier.
* Classic adds **Nineteenth-century Steelworks**, reusing AXIS `steel_mill`,
  local ID **2** and its graphics/layouts. Historical mode permits new works
  from **1860**. Exact stockpile batch: **3 IRON + 1 COKE → 3 STEL + 1 SLAG**.
* EAF local ID **79**: construction from **1906**; BOF local ID **77**: from
  **1952**. Existing EAF/BOF recipes unchanged. No forced closure.
* Parameter **10**, Historical Europe steelmaking dates, defaults **on**.
  Off removes added date/route restrictions; original AXIS dates and permissions
  still apply. The new steelworks remains available in Classic in either mode.
* All original **64 Classic cargo labels and slot assignments** preserved.
  Classic has **92** types (original 91 plus one reused dormant definition).
  Other economies retain their original enabled model data and cargo orders.
* Natural openings and deity GS placement share the **RANDOM** category.
  Independent natural/GS permission flags are unsupported. There is no reliable
  map-aware regional restriction in this milestone.

## Reproduce from the pinned source

Python 3.12.14 was used on Windows. `requirements-build.txt` pins the tested
compiler/render dependencies. GNU make/sed/zip/Graphviz are not needed for this
wrapper: it runs AXIS renderers and NML directly, skipping only HTML docs.
The wrapper fixes `PYTHONHASHSEED=0`; a one-line upstream set iteration is sorted
by industry local ID. These preserve the siting checks while making the emitted
binary reproducible with the tested toolchain. A rebuild from the complete
source ZIP produced the **identical GRF SHA256**, recorded in
`bundle-rebuild-result.json`. `package.py --verify-rebuild` repeats that check.

From repository root, using a real Python installation:

```powershell
python -m venv newgrfs/axis-historical-europe/.venv
newgrfs/axis-historical-europe/.venv/Scripts/python.exe -m pip install -r newgrfs/axis-historical-europe/requirements-build.txt
git clone https://github.com/EmperorJake/AXIS.git newgrfs/axis-historical-europe/.work/upstream
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-europe/prepare.py --upstream newgrfs/axis-historical-europe/.work/upstream
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-europe/build.py
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-europe/validate.py --upstream newgrfs/axis-historical-europe/.work/upstream
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-europe/package.py
```

If `venv` lacks ensurepip, install dependencies from a Python with pip using
`python -m pip --python PATH_TO_VENV_PYTHON install -r requirements-build.txt`.
Use `.venv/bin/python` on Unix. Run the commands with that same interpreter.
An existing trusted AXIS checkout may be passed with `--upstream`; it is read
using `git archive` at the exact manifest commit and is **never modified**.
No silent checkout of latest HEAD. `prepare.py --refresh` recreates only this
tool's derived `.work/source`; edited manifest/overlay requires prepare + build
+ validation again. Baseline validation uses its own pristine export.

Outputs:

* `dist/axis-historical-europe-0.1.0.grf` (7,786,646 bytes in the recorded build).
* `dist/axis-historical-europe-0.1.0-source.zip`: complete corresponding source
  and build instructions, produced by package.py.
* `dist/build-result.json`, `.work/logs/`, and committed `validation-result.json`.
* `runtime-result.json`: exact engine/binary hashes and the 16 headless cases.
* `production-result.json`: transported inputs, persisted stockpiles, steel/slag
  output and downstream steel delivery in a disposable 1860 world.

The binary, prepared sources, render caches and environment are deliberately
ignored to avoid committing large generated/third-party files. The small
`source-changes.patch` is generated for review and can also be checked/applied
against a pristine export. `prepare.py` is the authoritative reproducible patcher.

See [attribution](ATTRIBUTION.md), [implementation](../../docs/AXIS_HISTORICAL_IMPLEMENTATION.md),
[cargo validation](../../docs/AXIS_HISTORICAL_CARGO_VALIDATION.md) and
[manual JGRPP test plan](../../docs/AXIS_HISTORICAL_TEST_PLAN.md).
See also [production verification](../../docs/AXIS_HISTORICAL_PRODUCTION_VERIFICATION.md).

For the optional Windows runtime harness, extract the official
[JGRPP 0.73.4 win64 ZIP](https://github.com/JGRennison/OpenTTD-patches/releases/tag/jgrpp-0.73.4)
into `.work/runtime/engine/` and the official
[OpenGFX 8.0 ZIP](https://www.openttd.org/downloads/opengfx-releases/latest)
into that disposable engine's `baseset/`. The tested OpenGFX archive SHA256 is
`43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`.
Run `python runtime_test.py --engine-directory ABSOLUTE_PATH_TO_THAT_ENGINE`
using the fork's environment. It accepts only an engine beneath `.work`, starts
fresh 256² worlds, binds localhost and terminates its own processes. It installs
test-only GS/AI scripts into that disposable installation. No engine or base-set
binaries are committed or included in the source bundle.
