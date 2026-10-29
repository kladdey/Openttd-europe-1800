# Historical AXIS 0.5.0 legacy candidate

Separately versioned prototype built from the immutable prepared 0.4 source. GRFID `4B484531`, version 5, minimum compatible 4. Existing parameter 11 remains default off. No engine patch, model/recipe change, cargo reassignment or rolling stock change.

New GPL-2.0-only code adds a guarded one-shot closure handshake for four exact original coal/copper instances. Inherited AXIS/FIRS code/assets retain their licenses and attribution. `.work` and `dist` are excluded from Git; compiled graphics/assets are not redistributed.

From repository root, with the existing Phase 7A source tree and pinned environment present:

```powershell
python scripts/lifecycle_phase7b_inventory.py
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-legacy/build_candidate.py
python scripts/lifecycle_phase7b_policy.py
```

The builder refuses an existing prepared tree unless `--rebuild` is explicitly supplied; then archives it inside this folder's `.work`. It verifies the 0.4 artifact hash, copies its source, changes three templates/language files, renders and compiles with the pinned NML environment. Missing prerequisites fail explicitly. The resulting SHA-256 is recorded in `dist/build-result.json`. [Zero-context source diff](source-changes.patch) is a review receipt; the build utility is the reproducible transformation.

The tested v2 GS package combines the retained base `main.nut` with `legacy.nut`; `legacy_info.nut` becomes its `info.nut`, alongside `schedule.nut` and `legacy_policy.nut`. It uses the same GS identity and one controller. `lifecycle_phase7b_candidate.py --stage-editor` packages this into an isolated profile and opens a source **copy**; save a new scenario in the editor, then run the utility without flags to verify and name it. The delivered candidate already exists; use `python scripts/lifecycle_phase7b_launch.py`.

Do not substitute this GRF into the normal 0.3/0.4 campaign in place. Read [migration/safety](../../docs/PHASE_7B_MIGRATION_AND_SAFETY.md) and [engine validation](../../docs/PHASE_7B_ENGINE_VALIDATION.md) before testing an existing save. Native monthly removal timing, blocked old-tile siting, finite public-counter service policy and multiplayer limits are documented there.
