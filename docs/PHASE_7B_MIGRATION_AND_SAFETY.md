# Phase 7B — Migration and closure safety

## Compatibility contract

Historical AXIS 0.5.0 retains GRFID `4B484531`, existing industry/cargo IDs and all model recipes. Numeric version is 5; minimum-compatible version is 4. Parameter 11 still defaults **OFF**. The old 0.3 and 0.4 binaries are preserved. All six source economy models compare equal to 0.4; generated monthly closure callbacks intentionally differ. Only Classic historical mode is validated end-to-end.

This is not permission to replace a GRF in an ongoing campaign. The separately named 0.5 scenario was created by loading a disposable 0.4 copy in Scenario Editor with the compatible 0.5 asset, then saving a **new** scenario. That final file embeds version 5 and its actual checksum. Initial compatible-version notices occurred only during conversion; the named final candidate reopens without them. The normal user configuration and source scenarios were not rewritten.

The GameScript retains the same name/short name, now packaged as version 2 with minimum load version 1. It extends the retained v1 controller, preserving scheduled events. The v1 source files remain available for regression; the v2 isolated package combines `main.nut` plus `legacy.nut`, uses `legacy_info.nut` as its `info.nut`, and includes native schedule/policy files. Copying the source directory blindly still selects v1's base info: use the tested candidate packager/launcher or follow the explicit packaging instructions.

## Existing saves

Default v2 policy **rejects** schema-1 state, preventing silent enrollment. The tested explicit migration is `adopt_only`, with `enroll_legacy=false` and no enrolled sites. It preserves the three original scheduled events, changes schema to 2, enrolls zero legacy mines and survives another engine save/reload. The source save is copied/read only; it is never overwritten.

Activating legacy depletion on a live old campaign needs a separate reviewed enrollment migration. No automatic discovery of already exhausted/replaced mines is implemented. The shipped four-site policy is for the fresh, separately created 1830 candidate, where enrollment requires the intact 617-town/542-industry baseline and original pilot identities. Later code/schedule/policy changes require explicit saved-contract migration. Missing/unknown/partial state is retained or refused rather than reset into new closure commands.

## Independent safety layers

1. Server-side opt-in and exact GRF version/availability checks; supported clock mode only.
2. Explicit policy roster tied to the immutable original snapshot and per-record hashes.
3. GS ID/type/tile/construction-date checks before enrollment and each action. Reused/mismatched instances become LOST and receive no commands.
4. Independent NewGRF fingerprint: full tile, build date, founder, random bits and layout, dispatched only for the selected original type/site.
5. Instance-specific arm level and nonce in free persistent storage; a bare level 4 never closes an original mine.
6. Short-lived token and one-shot consumption; an expired or consumed token cannot authorize another closure.
7. Saved forecast/status bounds and actual calendar warning lead checked before arm; bounded extension and last-producer protection.
8. Physical-absence verification before CLOSED, explicit failure/defer outcomes, and preserved infrastructure/vehicles.

These are safeguards within trusted server administration, not a cryptographic security boundary against arbitrary malicious deity scripts. An administrator with full game-command authority can deliberately manipulate authorized mines. The GS cannot read every native random/layout field directly; that is why the independent GRF guard is necessary. The complete original-record hash is provenance, not a fictional engine API that can hash live industry objects.

Unregistered neutral mines, factories, markets, wharves and ports receive no lifecycle commands. All 538 non-pilot instances retained identity, native production level and control flags in actual ten-year Europe tests. No blanket type-based legacy closure, raw save-byte editing, engine patch, global spawning toggle or subsidy was used.

## Known bounds

* The native engine controls final deletion timing. A requested forecast is not a same-day physical closure promise. Actual tests closed roughly three months after the nominal request window, within the configured latest **year**. A failed closure remains open and needs review; the script never invents deletion to satisfy a deadline.
* No script after arm means no new commit. A legitimate commit already submitted to the engine may still finish if the script disappears. Unrelated industries remain outside its authorization.
* Exact old-tile rebuilding was rejected by native siting rules. Actual reused-ID/different-site protection passed; same-tile replacement is not presented as an engine pass.
* Existing phase-7A deity-coal closure behaviour remains for new scheduled mines outside original protected locations. The v2 controller validates managed signatures; arbitrary administrator production commands are outside that saved-state contract.
* Public industry transport counts cannot prove final payment for every ton. The paid comparison route is observed evidence; deliberate dumping remains a multiplayer policy/testing concern.
* Deferred closure, blocked construction and brownfield reuse require administrator review. No automatic terraforming, rolling-stock removal or compensation occurs.

The safest migration for a new campaign is the delivered separate 1830 candidate. Keep the original 0.3/0.4 files and all tests; obtain explicit approval before any future production-save migration, push or merge.
