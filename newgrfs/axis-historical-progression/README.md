# Phase 7D isolated development profile

No new GRF binary is built here. This candidate deliberately retains the pinned Historical AXIS 0.6.0 artifact and fifteen existing GRF references, with a separate **GS v4/schema 4** package and scenario. `.work` contains disposable profiles, native logs and save fixtures and is ignored.

Use `scripts/lifecycle_phase7d_candidate.py --stage-editor`, save a separate scenario through the stock editor, then finalize with the same script. Never modify a prior candidate or a live save in place. The packaged controller is v1 + v2 + v3 + `progression.nut`; use `progression_info.nut`, the new compiled policy under the profile's `expansion_policy.nut`, and unchanged legacy/scheduled policies.

See [Phase 7D implementation](../../docs/PHASE_7D_IMPLEMENTATION.md) and [readiness/launcher](../../docs/PHASE_7D_READINESS.md). Raw logs remain local and only compact evidence is committed. No graphics, rolling stock, engine or scenario binaries are redistributed.
