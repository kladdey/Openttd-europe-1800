# Phase 7A — Readiness and handoff

**READY WITH CAVEATS.** The essential opening → paid delivery → decline/warning → real closure → replacement → save/reload sequence works in stock JGRPP 0.73.4 on both small fixtures and the actual Europe map. Natural spawning remains suppressed. This is a proven, coal-only experimental foundation; do not deploy it as a complete historical campaign lifecycle yet.

## Delivered

* Versioned Historical AXIS **0.4.0 lifecycle candidate**, GRFID KHE1, default-off scheduler parameter, source build utility and reviewable five-file patch.
* Historical Industry Lifecycle **GS v1 / schema 1**, production schedule with three source-backed opening districts and explicit finite-life proposal, persistent ledger, safe rejection, bounded placement and public warnings.
* Actual separately saved **Europe 1830 Historical AXIS 0.4.0 - Lifecycle Foundation.scn**. It starts with the same 617 towns and 542 industries, 15 NewGRFs, 96 types, 64 cargos, calendar 1830/economy 1800, seven-tile trains, maintenance enabled and inflation disabled. Other baseline settings and all initial terrain/infrastructure are preserved.
* Scoped real-engine evidence, two paid coal observations, dedicated startup smoke, actual GUI news/link proof, two multidecade runs, replay/migration/negative tests and focused validation scripts.

## Exact local candidate

Relative to repository root, the actual playable candidate is:

`newgrfs/axis-historical-lifecycle/.work/runtime/europe-editor-1793277578540923700/scenario/Europe 1830 Historical AXIS 0.4.0 - Lifecycle Foundation.scn`

SHA-256: `e73952d2ec40f0fb6ad5dce9753c9254e2df1e317c8d5cd7e25e8042f8ce03fc`.

Required GRF: `newgrfs/axis-historical-lifecycle/dist/axis-historical-europe-0.4.0-lifecycle-candidate.grf`, SHA-256 `e05de519b4695bc68bde7064c17ee0ae833edfe281579c3b92cb79532f466c52`. The isolated profile already contains it and the fourteen matching other assets, plus `game/lifecycle/{info,main,schedule}.nut`. Exact resolved engine/profile/script paths and hashes are in [delivery manifest](research/phase7a_candidate_delivery.json). The launcher verifies hashes; compiled assets and scenarios are local, deliberately excluded from Git.

Start the isolated game with:

```powershell
python scripts/lifecycle_phase7a_launch.py
# Or inspect in Scenario Editor:
python scripts/lifecycle_phase7a_launch.py --editor
```

Do not install the candidate over the existing 0.3 campaign or substitute its GRF into an ongoing save. Existing-save migration is not approved. This new candidate was created in the editor; metadata compatibility does not prove arbitrary mid-campaign replacement safe.

## Prioritized Phase 7B work

| Priority | Finding / action | Evidence, confidence and risk |
|---|---|---|
| Required before production scheduler rollout | Resolve named opening sites overlapping existing representative coal mines; select district-event versus existing-site policy | South Hetton about 8 tiles and Guido 2 tiles from existing coal. High confidence in overlap; exact production Europe openings not yet proven. Preserve historical geography and native restrictions. |
| Required before managing baseline closures | Add a separately verified per-instance arming protocol or supported native API for existing neutral/player-funded mines | Current callback deliberately closes only deity-founded managed coal. High confidence. Broadening founder checks without an identity contract risks unintended closures. |
| Required before multiplayer adoption | Three-human isolated playtest through warning, closure, reload and replacement | Dedicated server startup/ledger is proven; connected-client desync and actual competitive response are not. No claim that a localhost smoke replaces this test. |
| Required before economic policy adoption | Observe sustained service, replacement access and losses; calibrate 50% decline and +10/+15-year extension | Functional boundaries proven; service-history inputs partly injected. Two vehicles were stranded after real closures. No automatic price/recipe changes proposed. |
| Required for broader lifecycle scope | Source-backed schedules and closure/transition adapters for further industry categories | Only three coal opening districts, not all types/years. Farms/retail should not inherit finite-mine rules. Keep FOOD/GOOD coverage and chain dependencies. |
| Minor technical limitation | Replace StoryPage calendar workaround if an upstream native calendar getter becomes available | Current workaround reads actual calendar correctly; two commands/fortnight and possible Storybook churn. Wallclock intentionally unsupported. No custom engine currently required. |
| Minor operational limitation | Administrator procedure for deferred/failed closure and blocked sites | Explicit failures retain sites; there is no automatic retry of terminal failure or compensation. Logs and industry text identify required review. |

These are bounded next steps, not reasons to restart the vehicle/economy audit. No new rolling stock, prices, recipes, cargo IDs, roads, towns or train-length settings were changed for this phase.

## Human smoke test

1. Launch the isolated candidate; check 1830, 617 towns, 542 industries, 15 matching GRFs, seven-tile train limit and the GS debug window. Do not select the normal Inland Markets source as the save target.
2. Confirm calendar and economy differ as documented; no industry should open before the production schedule's 1833 eligibility. The candidate contains ordinary historical dates; short closure demos use the separately labelled accelerated Europe fixture saves referenced in the evidence.
3. In a disposable accelerated fixture session, have Kladdey, Squirrel and Toni join with identical GRFs. Observe a regional opening, deliver coal to the existing accepting consumer, and inspect vehicle income. Do not inject subsidies.
4. Read the visible decline warning and persistent industry text, follow its map link and plan alternate transport. Save, restart the dedicated server, reconnect and check the same deadline and industry signature.
5. Confirm the mine physically disappears at closure, the replacement opens elsewhere, old infrastructure remains, and no duplicate or unplanned industry appears. Check retail demand remains available. Record desyncs, cash losses and practical time to adapt.

Production warning policy gives ten years; compressed fixture deadlines are test-only. A successful short fixture is not proof that the full 1830–2025 progression or economy is balanced.

Reports: [architecture](PHASE7A_LIFECYCLE_ARCHITECTURE.md), [spawning](PHASE7A_SPAWNING_POLICY.md), [closure](PHASE7A_CLOSURE_MECHANISM.md), [validation](PHASE7A_ENGINE_VALIDATION.md). Source, documentation and evidence are committed locally only; no push or merge is authorized for this phase.
