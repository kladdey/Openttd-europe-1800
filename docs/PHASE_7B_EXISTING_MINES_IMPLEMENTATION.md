# Phase 7B — Existing-mine lifecycle implementation

This extends the working Phase 7A GameScript rather than introducing a second scheduler. Historical AXIS **0.5.0 legacy candidate** is a separate same-GRFID version; stock JGRPP 0.73.4 remains unchanged. The source 0.3 Inland Markets and 0.4 Lifecycle Foundation scenarios and both GRFs are protected by hash guards. Experimental profiles stay outside the normal OpenTTD installation.

## Enrollment and closure

The source inventory reads all 542 original industry records. The engine independently resolves all 96 local industry definitions to actual runtime type IDs. The pilot selects genuine original industry IDs **1, 11, 12 and 438**: Coalbrookdale district coal, Nachtigall/Ruhr coal, Queen Louise/Silesian coal and Dolcoath copper. None is a Phase 7A newly constructed test mine.

Each policy site records the original scenario hash, complete original industry-record SHA-256, engine ID, runtime/local type, tile, construction date, founder, layout and random bits. GameScript validates ID/type/tile/construction date; the NewGRF independently validates the complete available native fingerprint before permitting its per-instance handshake. Numeric industry IDs alone, type alone and coordinates alone cannot authorize closure.

The monthly callback is added only to the coal and copper primary templates. Its dispatch is a fixed allowlist of four original instances, not a type-wide closure condition. The existing Phase 7A deity-coal pathway remains available outside these protected original locations. Unregistered neutral mines cannot use that deity-only pathway.

At an authorized deadline, the GS protects the selected industry and sends its reserved arm level (5, 6, 7 or 9). A monthly callback writes the site's nonce and arm date into persistent registers **200/201**. After 40 economy days, but no more than 65 from the request, the GS rechecks identity, clears protection and commits native production level 4. The callback accepts that only with the correct original fingerprint and nonce within 90 native date days, consumes the nonce into its negative value, and returns the actual engine CLOSE result. Register 202 records consumption time. Native last-instance safeguards remain.

The ordinary primary production storage occupies registers 0–38. No existing register is reassigned. The nonce belongs to the industry's persistent storage and is consumed once. A replacement has different origin/construction state and fresh storage. The script waits for physical disappearance before recording CLOSED; failure remains explicit. A missing script after arming leaves a reduced-production site rather than automatically committing closure. A legitimately submitted, already committed engine closure is not magically undone when the script stops.

## Persistent controller

The version-2 controller extends `LifecycleController`; the isolated package combines the retained Phase 7A base `main.nut` with `legacy.nut`. It preserves scheduled openings and their ledger. The registered GS name/short name remain unchanged, with version 2 and minimum load version 1. Schema 2 adds enrolled legacy states, fingerprints, rolling observations, forecast, warning dates, extension and authorization phase.

The older bundled Squirrel dialect does not implement the modern `base` shorthand. Parent methods are bound with `bindenv(this)` and then called normally. Calling a suspendable parent through native closure `.call` fails when an actual construction command yields; that diagnostic failure was identified and corrected before acceptance. Failed diagnostic runs are not counted as passing engine evidence.

The shared Python engine harness gained optional per-run timeout and fatal-log rejection arguments; their defaults preserve Phase 7A behaviour. This is test tooling, not an executable/engine patch.

Saved policy text forms a deterministic contract, alongside the existing schedule contract. Partial enrollment, missing fields, changed identities, invalid forecasts, unknown statuses, changed policy and lost state fail closed. Phase 7A saves are rejected unless an explicit adoption policy is supplied; adoption preserves old events and enrolls **zero** legacy mines. The production scenario starts fresh with the explicit four-site roster.

## Production and service

Actual `SetProductionLevel` commands control primary cargo output through unchanged AXIS recipes. Decline is progressive, rather than a text-only status. The service model reads actual last economy-month production and transported quantities, accumulating a 36-month rolling window. It requires both a transported fraction of at least 25% and at least 1,200 units over the complete window; a nearby station or tiny delivery cannot earn survival. An earned extension is finite and never exceeds the site's hard latest year. Short interruptions do not erase past service or instantly close a mine.

The native transported counter measures cargo taken from the industry, not an audited end-to-end payment for every unit. Real fixture routes separately verify loading and credited vehicle income. Deliberate cargo dumping/transfer abuse is not claimed to be fully detectable through this public API.

The calendar workaround and supported clock mode remain Phase 7A's verified mechanism. `GSDate` is economy time: calendar 1830 starts with economy 1800. Historical eligibility, warnings and exhaustion use actual calendar dates; production samples use economy-month boundaries so the same counter is not counted twice.

See [policy](PHASE_7B_DEPLETION_POLICY.md), [safety and migration](PHASE_7B_MIGRATION_AND_SAFETY.md), [engine validation](PHASE_7B_ENGINE_VALIDATION.md) and [readiness](PHASE_7B_READINESS.md) for final scoped results and limitations.
