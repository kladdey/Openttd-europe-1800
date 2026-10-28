# AXIS Historical Europe 0.1.0 — steelmaking milestone

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
