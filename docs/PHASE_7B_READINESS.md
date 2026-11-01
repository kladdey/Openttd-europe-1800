# Phase 7B — Readiness

**READY WITH CAVEATS.** A working legacy-mine foundation and separate normal-play scenario are delivered. Real neutral baseline coal and copper mines declined, warned, physically closed and persisted across reload. Sustained actual transport on a paid route prolonged one mine's life by roughly two years while retaining finite exhaustion. This is a limited pilot, not a complete 1830–2025 resource simulation.

## Verified outcome

* Inventory: **44 extractive sites**, with full original fingerprints and compatible downstream consumers. Four soda-ash sites remain flagged and unmanaged.
* Pilot: original IDs **1/11/12/438**, British/Ruhr/Silesian coal and Dolcoath copper; never newly created substitutes.
* Control closures: **1837-04-07**. Served British mine: **1839-04-14**, after an observed 36-month window with **2,060 units / 38% transported**. All other served-case pilot mines closed on 1837-04-08.
* Actual paid delivery: **£91 positive sampled net vehicle-income increase**, following loading and unloading at an accepting consumer. No subsidy; £100,000 starting cash, £11,967 initial route/fleet investment. This does not establish annual commercial balance.
* Warnings: real five-calendar-year minimum, not economy-year arithmetic. Production level and output actually declined. Normal candidate uses ten-year notice and historically anchored production windows.
* All **617 towns and 542 industries** present initially; all map bytes and initial industry/town/settings records preserved. After pilot closures: all **538 unmanaged identities/levels/control flags** preserved, FOOD/GOOD acceptance **76/69**.
* Safe OFF/absent-script/wrong-version/corrupt-state/expired-token cases, save/reload at four lifecycle stages, deterministic saved-checkpoint replay, explicit inactive migration, original scheduled-lifecycle regression, five-year spawning control and dedicated-server notification smoke passed.

## Actual local playable candidate

Relative to this repository:

`newgrfs/axis-historical-legacy/.work/runtime/legacy-editor-1793286062596721700/scenario/Europe 1830 Historical AXIS 0.5.0 - Legacy Mine Lifecycle.scn`

SHA-256: **`355686df5ddbc935aacdcc0b89a9bd446657d086f973df11fb794f5fbafd8e79`**.

Required GRF: `newgrfs/axis-historical-legacy/dist/axis-historical-europe-0.5.0-legacy-candidate.grf`, SHA-256 **`473b4ac0ebc6962959408633dbbc2cf254546fe9bc7fdd6c3531b0f0a232e534`**. The isolated profile already contains it, the other fourteen matching active GRFs and the packaged v2 script/policy. [Delivery manifest](research/phase7b_candidate_delivery.json) gives exact Windows paths, per-file hashes, active identities/parameters and the profile's library inventory. Inactive library files are distinguished from the fifteen active references.

```powershell
python scripts/lifecycle_phase7b_launch.py
# Optional editor inspection:
python scripts/lifecycle_phase7b_launch.py --editor
```

The launcher verifies assets and uses isolated `-X -x` user data. The candidate starts in **1830**, economy **1800**, with seven-tile trains, maintenance enabled, inflation unchanged and ordinary production dates. It does not contain the accelerated 1837/1839 fixture deadlines. No source scenario, original GRF, saved campaign or normal configuration was replaced. Compiled assets/scenarios remain local and are not redistributed through Git.

## Remaining work, in priority order

| Priority | Action | Reason and confidence |
|---|---|---|
| Before production policy adoption | Review the four regional exhaustion windows, especially generic Coalbrookdale and how a copper-only proxy represents Dolcoath | Actual closure machinery is proven; exact reserves are unknown. Historical terminal years constrain proposals, not inferred geological quantities. High confidence in the distinction. |
| Before live-save conversion | Review a separate enrollment migration for that exact save | Only explicit **adopt-only, zero-enrollment** migration is tested. No silent activation on an existing campaign. |
| Multiplayer playtest | Kladdey, Squirrel and Toni test shared service, cargo dumping, closure losses, warnings and reconnects | Loopback dedicated restoration/news is proven; three connected humans and adversarial service exploits are not. |
| Before wider rollout | Design resource/industry-specific policies and replacement rules | Only four existing mines enrolled. The normal scenario does not promise an automatic replacement for every exhausted site. A test-only regional replacement through the existing scheduler passed. |
| Optional technical work | Diagnose exact old-tile rebuild restriction without changing terrain or native checks | Native `ERR_SITE_UNSUITABLE`; a nearby legal replacement and reused ID were tested. Brownfield replacement is not guaranteed. |
| Optional engine/API improvement | Native calendar accessor and stronger end-to-end delivery attribution | Current StoryPage clock is verified; public pickup counters are an imperfect payment proxy. No custom engine is required now. |

## Practical human playtest

1. Launch the isolated **normal** candidate and verify initial towns/industries, GS v2 and all fifteen exact GRFs. Keep new saves in the isolated profile.
2. For a short closure demonstration, use copies of the **accelerated comparison profile and its matching policy/script**, listed in engine receipts. Do not load fixture saves with the normal policy: contract rejection is intentional. The pre-closure checkpoint is around December 1836.
3. Host that disposable save and have all three players connect with identical assets. Observe the public deadline, inspect declining output, jointly serve or neglect selected mines, and verify that one small shipment does not earn the three-year extension.
4. Save, restart, reconnect and check unchanged forecasts/service history. At closure confirm physical disappearance, surviving unregistered industries, remaining infrastructure/vehicles and accessible alternatives. Observe that engine deletion can lag the forecast by months.
5. Record losses, warning usefulness, whether cargo can be collected then discarded to exploit survival, and whether a shared service benefit creates unfair competition. No vehicle-price, recipe or payment adjustments are included here.

See [implementation](PHASE_7B_EXISTING_MINES_IMPLEMENTATION.md), [policy](PHASE_7B_DEPLETION_POLICY.md), [validation](PHASE_7B_ENGINE_VALIDATION.md) and [migration/safety](PHASE_7B_MIGRATION_AND_SAFETY.md). Source, tests, reports and raw logs are committed locally only; no remote push or merge is part of Phase 7B.
