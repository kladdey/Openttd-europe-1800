# Current roadmap — Historical Europe 1830–2025

Current separate development candidate: **Phase 7H**, 617 towns / 542 initial industries, unchanged AXIS 0.6.0 plus isolated GS v7/schema 6. Verdict: **READY WITH CAVEATS for controlled testing**. Phase 7D/7E remains the earlier established evidence baseline; older geography checkpoints below remain historical.

## Completed milestones

- [x] Phases 6B/6C: historical industrialization, copper/salt processing and 75 inland markets.
- [x] Phases 7A/7B: persistent scheduling and guarded four-original-mine depletion pilot, with retained safety evidence.
- [x] **Phase 7C complete with caveats:** ten-event slice, paid Galician chain, guarded mill transition, later steel construction and 36 recorded engine runs.
- [x] **Phase 7D implementation:** 32-event regional policy, legal layout/house-aware modern siting and GS v4 fresh-candidate isolation. Both Rhine and Lille sequences constructed in Europe, all originals preserved.
- [x] Lean long-horizon attempt to 2026 with one reload and no duplicate openings; actual cancellations and fixture/final-policy differences recorded rather than hidden.

- [x] **Phase 7E targeted freight validation:** actual paid RCYC/PLAS/MNSP and SCMT legs, native EAF output and physical gameplay reload; no changes to AXIS or normal GS. [Evidence and economics](PHASE_7E_READINESS.md).

- [x] **Phase 7F partial implementation:** separate candidate and eight conditional port events; native Liverpool facility constructed. Paid shipping acceptance criterion remains unmet. [Readiness/blockers](PHASE_7F_READINESS.md).

- [x] **Phase 7G supply-cycle slice:** real neutral Ruhr mine, observed boom/downturn/recovery; unchanged NewGRFs and prior policies. [Readiness](PHASE_7G_READINESS.md).

- [x] **Phase 7G.1 ended-state persistence gate:** native schema-5 reload retained exactly one pilot mine and ended ledger, with no repeated cycle effect. Active-boundary reload remains unverified. [Evidence](PHASE_7G1_PERSISTENCE_READINESS.md).

## Next priorities

- [x] Phase 7G active-boundary reload across downturn/restoration passed in the Phase 7H gate.
- [ ] Verify Phase 7H active/closing-row reload and normal historical milestones; hauled freight and finances remain untested. [Transformation readiness](PHASE_7H_READINESS.md).
- [ ] Resolve Phase 7F receiving dock/connected-water and feeder blockers; prove one actual paid maritime leg, then normal-policy save/reload.
- [ ] Measure sustained profit with appropriately sized downstream fleets; Phase 7E proved delivery, but the two-truck MNSP leg lost money. Test complete steel/slag outlets and fuller EAF inputs separately.
- [ ] Test three human clients through public openings, save/rejoin and competitive access; retain prior service-abuse caveats.
- [ ] Review conditional/blocked regional events with targeted native site diagnostics. Do not flatten sites or grow towns artificially to force success.
- [ ] Validate selected future stages as needed; no automatic broad regression campaign or full-Europe economic certification.
- [ ] Review any additional depletion/retirement policy separately; preserve the four-mine and one-mill scope until then.
- [ ] Resolve packaging/licensing and any explicit live-save migration before distribution; do not silently substitute assets.

[Phase 7D readiness](PHASE_7D_READINESS.md) · [implementation](PHASE_7D_IMPLEMENTATION.md) · [Phase 7C readiness](PHASE_7C_READINESS.md).

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
