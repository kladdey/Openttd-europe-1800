# Current roadmap — Historical Europe 1830–2025

The active branch now has a **617-town / 542-industry** playable development candidate. Older V12/V13 geography tasks remain historical backlog, not the main critical path.

## Completed milestones

- [x] Phase 6B: historical industrialized scenario, copper and salt processing.
- [x] Phase 6C: 75 inland retail markets and verified paid FOOD/GOOD deliveries.
- [x] Phase 7A: guarded server-side scheduling, openings, warnings and actual closure in JGRPP; isolated AXIS 0.4.0 candidate.
- [x] Phase 7B: guarded four-mine existing-site depletion pilot, native production decline, warning windows, finite service extensions, save/reload and dedicated-server smoke; isolated AXIS 0.5.0 candidate.

## Next priorities

- [ ] **Phase 7C:** historically researched industrial expansion by era and region, including factory openings, obsolete chains, replacement policy and paid freight-chain verification. **Prompt prepared only; no implementation evidence.**
- [ ] Extend 7B depletion beyond four original mines with documented regional policies; investigate four unresolved soda-ash sites.
- [ ] Test three actual multiplayer clients through closures, reconnects, shared transport and potential cargo-dumping exploits.
- [ ] Validate long-duration 1830–2025 behavior, performance, demand continuity and economic balance.
- [ ] Complete Europe coastal GOOD and copper export end-to-end tests.
- [ ] Test short-distance horse feeders on existing roads before considering price changes.
- [ ] Plan explicit migration for any existing campaign save; never silently switch NewGRF or GS versions.
- [ ] Resolve licensing and release packaging before public distribution.

See [Phase 7B readiness](PHASE_7B_READINESS.md), [Phase 6C readiness](INLAND_MARKETS_READINESS.md), [project status](PROJECT_STATUS.md).

---

## Historical geography roadmap (archived checkpoint)

# Development roadmap

Current offline candidate: [V13 coverage implementation](../maps/calibration/geography_v13/README.md), 45 additions to the saved 568-town map, 613 full candidate, 17 deferred research leads. Run `python scripts/build_gap_additions.py --out /tmp/europe_v13_rebuild` from the repository root. The V12 checkpoint remains the last user-confirmed component; V13 founding is pending. Earlier version-specific details below remain historical.

The current state and counts live in [project status](PROJECT_STATUS.md).
No arbitrary final town count is imposed; the 600-record master remains preserved.

## Completed offline groundwork

- [x] Preserve and account for all 600 catalogue records.
- [x] Commit the original 4096×4096 heightmap and supplied scenario assets with hashes.
- [x] Verify JGRPP 0.73.4 importer schema, orientation and float32 pixel mapping.
- [x] Implement reproducible calibration, import generation, terrain and spacing audits.
- [x] Produce regional/full comparisons, explicit deferrals and offline maps.
- [x] V10: correct 27 original terrain flags and account for every remaining case.
- [x] Add automated source-preservation, model, coordinate, terrain and spacing checks.

## Active geographic work

- [x] V11: review all 28 V10 terrain cases, add 25 site references and restore Namur.
- [ ] Resolve the 27 remaining V11 terrain cases using stronger historic centre/river/coast evidence.
- [x] Identify the distributed heightmap: exact pixel match to UseYourIllusion’s Europe v4.
- [x] Add frozen-model inland lake diagnostics and named-river overlays for both bank holds; no unsupported town shifts.
- [x] Reverse-audit V11 export, comparisons and provenance; enforce inland model/reference dependencies.
- [x] Research Arles/Alençon bank context and dated crossings; demonstrate fragile targets and retain both bank holds.
- [x] Screen the full 568-town map for coverage gaps and distinguish new research leads from existing holds.
- [ ] Verify historic centres and terrain for selected priority gaps before producing further additions.
- [ ] Recover upstream DEM projection/crop provenance or add independent inland controls.
- [ ] Preserve consistent neighbouring-town registration when changing a regional model.
- [ ] Continue the Modica/Pozzallo population-unit and identity investigation.
- [ ] Rank the 132 non-flat clear targets for later founding checks.
- [ ] Keep candidate maps, source references and all-600 decisions synchronized.

## Population research

- [ ] Extend verified historical source joins; keep census, estimates and gameplay sizes separate.
- [ ] Resolve ambiguous historical units and aliases before changing any game populations.
- [ ] Complete outstanding British, Polish and Prussian source acquisition/review.

## Gameplay and release

- [x] User confirmed a 537-town baseline import and a saved checkpoint.
- [x] User supplied supplement regional views and confirmed completion after the 568-count/save prompt.
- [x] Publish a single 568-town full import for fresh-map rebuilds.
- [ ] Verify a fresh-map one-step V12 import, exact positions and later growth.

- [ ] Test actual founding locations/failures, growth, spacing and infrastructure room.
- [ ] Validate FIRS 5.2.0 Temperate Basic and the intended vehicle/track/station sets.
- [ ] Tune 1800 starts, town growth, economy and two-player performance.
- [ ] Save and validate a new playable scenario; preserve originals and current NewGRFs.
- [ ] Finish third-party asset licensing and safe Windows portable installer/release work.

An unavailable game platform does not block the active geographic/source tasks.
No complete playable scenario or release has been validated.

The first coverage supplement reviews all 35 old Swedish entries and 16 new
Mediterranean proposals, plus the existing Palma hold; 31 additions qualify for
separate game testing. No fixed final town count is imposed.
