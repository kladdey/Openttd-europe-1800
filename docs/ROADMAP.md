# Development roadmap

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

## Active geographic work, without OpenTTD

- [x] V11: review all 28 V10 terrain cases, add 25 site references and restore Namur.
- [ ] Resolve the 27 remaining V11 terrain cases using stronger historic centre/river/coast evidence.
- [x] Identify the distributed heightmap: exact pixel match to UseYourIllusion’s Europe v4.
- [x] Add frozen-model inland lake diagnostics and named-river overlays for both bank holds; no unsupported town shifts.
- [x] Reverse-audit V11 export, comparisons and provenance; enforce inland model/reference dependencies.
- [x] Research Arles/Alençon bank context and dated crossings; demonstrate fragile targets and retain both bank holds.
- [ ] Recover upstream DEM projection/crop provenance or add independent inland controls.
- [ ] Preserve consistent neighbouring-town registration when changing a regional model.
- [ ] Continue the Modica/Pozzallo population-unit and identity investigation.
- [ ] Rank the 132 non-flat clear targets for later founding checks.
- [ ] Keep candidate maps, source references and all-600 decisions synchronized.

## Population research

- [ ] Extend verified historical source joins; keep census, estimates and gameplay sizes separate.
- [ ] Resolve ambiguous historical units and aliases before changing any game populations.
- [ ] Complete outstanding British, Polish and Prussian source acquisition/review.

## Gameplay and release, when a test platform is available

- [ ] Test actual founding locations/failures, growth, spacing and infrastructure room.
- [ ] Validate FIRS 5.2.0 Temperate Basic and the intended vehicle/track/station sets.
- [ ] Tune 1800 starts, town growth, economy and two-player performance.
- [ ] Save and validate a new playable scenario; preserve originals and current NewGRFs.
- [ ] Finish third-party asset licensing and safe Windows portable installer/release work.

An unavailable game platform does not block the active geographic/source tasks.
No complete playable scenario or release has been validated.
