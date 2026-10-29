# Historical AXIS 0.4.0 lifecycle candidate

Separate experimental extension of the existing Historical AXIS 0.3.0 prepared source. Uses the existing AXIS/FIRS assets and license; do not redistribute graphics or compiled assets without their licenses. This folder commits source transformations and the five-file diff, not copyrighted binaries/assets. New lifecycle code is GPL-2.0-only; inherited source/assets retain their own attribution and license.

GRFID `4B484531`; numeric version 4, minimum-compatible version 3. Parameter 11 defaults **off**. In Classic historical mode, opt-in permits deity placement while rejecting natural RandomCreation by founder, and reserves production level 4 on deity-founded coal for a monthly real-closure callback. All models, recipes, cargos and IDs remain unchanged. This is a same-GRFID version upgrade for a **separate editor-created candidate**, not permission to change a live scenario in place.

## Rebuild

Prerequisites are the existing Phase 6B/6C build environment: complete pinned AXIS virtual environment under `../axis-historical-europe/.venv`, prepared 0.3 source under `../axis-historical-copper-salt/.work/source`, and its verified original compiled GRF under `../axis-historical-copper-salt/dist`. Recreate these using those phases' documented build utilities if unavailable. The build refuses an unexpected 0.3 hash.

From repository root:

```powershell
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-lifecycle/build_candidate.py
# Explicit repeat: archives the previous prepared tree/artifact inside .work.
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-lifecycle/build_candidate.py --rebuild
newgrfs/axis-historical-europe/.venv/Scripts/python.exe scripts/lifecycle_phase7a_models.py
```

The utility copies the base tree, transforms five files, runs language/render/NML compilation and writes `dist/build-result.json`. It does not modify the base. The validated GRF SHA-256 is `e05de519b4695bc68bde7064c17ee0ae833edfe281579c3b92cb79532f466c52`; a repeat build was bit-identical. `source-changes.patch` records the resulting source diff. The model comparison covers six source economies; end-to-end engine tests cover Classic historical mode.

`.work` and `dist` are ignored. Runtime utilities make unique disposable profiles, resolve exact existing assets, guard the originals and invoke the unmodified installed engine. See [validation and reproduction](../../docs/PHASE7A_ENGINE_VALIDATION.md) for commands and scope. No ordinary arbitrary-property override, custom engine API, fake closure or save-byte mutation is involved.
