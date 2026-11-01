# Historical AXIS 0.6.0 expansion candidate

Separate local candidate; GRFID `4B484531`, native version 6, minimum compatible version 5. Lifecycle parameter 11 stays default-off. The supplied isolated scenario/profile explicitly opts in.

`build_candidate.py` copies the pinned local 0.5 prepared source and applies only the version/name and original-mill adapter changes. It refuses a changed 0.5 GRF. Rebuilding requires explicit `--rebuild` and archives the preceding source/binary rather than deleting it. The Phase 7B primary template and all industry model definitions remain unchanged. Build tools/dependencies/upstream preparation are documented in the prior candidate folders; a fresh clone must reproduce those licensed inputs first.

```powershell
& newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-expansion/build_candidate.py
```

Only build/patch source is committed here; ignored `.work` and `dist` hold local source/assets/binaries. No upstream graphics or rolling stock are redistributed. The code changes follow the upstream GPL-2.0-only licence.

See [implementation](../../docs/PHASE_7C_IMPLEMENTATION.md), [actual engine validation](../../docs/PHASE_7C_ENGINE_VALIDATION.md) and [readiness / launcher](../../docs/PHASE_7C_READINESS.md). Never substitute this GRF into an ongoing game in place. The tested supported path is the separate initial scenario and isolated profile.
