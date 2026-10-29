# Historical AXIS release readiness — Phase 5

## PARTIALLY READY

Historical Europe **0.2.0 is a real compiled, loadable NewGRF**, with full-type construction policy, actual transport and persistent-world tests. It is suitable for isolated technical tests in **new worlds**. It is **not ready to replace stock AXIS in the existing Europe campaign**.

| Required answer | Assessment |
|---|---|
| 1. Did it compile? | **Yes.** 7,842,417 bytes, local ignored `dist/axis-historical-europe-0.2.0.grf`. Corresponding source rebuilt identically |
| 2. Loads in JGRPP 0.73.4? | **Yes**, including fresh worlds with all 14 other campaign GRFs, real deliveries and two save/reload tests |
| 3. Enforces introduction dates? | **Yes for the implemented policy** in tested generation/deity/company paths. All 92 types checked at nine milestones; steel boundaries also executed. Historical accuracy of provisional dates is a separate unresolved review |
| 4. Can players bypass restrictions? | Ordinary company-mode pre-date construction rejected; tested eligible constructions succeeded. History-off parameter deliberately disables added gates for a new game. Editor/ignore-restrictions behavior and player UI need manual checks; not described as proven enforcement |
| 5. All 91 accounted for? | **Yes**, unchanged IDs/recipes/layouts; plus the existing prototype's reused steelworks, total 92 |
| 6. All 64 slots preserved? | **Yes**, model ordering and all 320 compiled branch cargo records match stock |
| 7. Is 1830 viable? | **Functional chains and paying transport demonstrated** on fresh small worlds. Five services produced actual paid deliveries; grain horses lose money in both fork and stock controls. Three-player geographic access on Europe remains unverified |
| 8. Existing Europe loads safely with it? | **Not established; no hot-swap attempted.** Distinct identity and 463 currently incompatible-by-policy existing sites require a safe new candidate/migration decision |
| 9. Can three players use it? | Fresh-world technical prototype exists; human network compatibility, fairness and 4096² performance are **MANUAL TEST REQUIRED** |
| 10. Exact remaining work? | Sector/date and cargo-proxy review; manual editor/funding checks; clean Europe candidate, production/refit checks and three-player save/rejoin playtest |

## Prioritized action plan

| Priority | Issue | Action / confidence |
|---|---|---|
| P0 / release blocker | No certified existing-scenario migration; 463 old instances fail the new policy | Build a separate editor candidate with the historical GRF selected from creation. Do not overwrite the stock campaign. **High** confidence in identity and grandfathering limitation |
| P0 / historical completeness | Many draft-band dates, early ports producing modern parts, resource/import exclusions | Review recipes sector by sector; decide the smallest date-dependent production/import correction without changing cargo IDs. Keep provisional policy explicitly experimental. **High** that these limitations remain; exact correction needs evidence |
| P1 / validation | Editor, UI, supplied 1830 iron chain and actual three-player runtime untested | Run the short manual protocol in the gameplay report, then limited Europe playtest. **High** confidence in the missing evidence |
| P1 / geographic economy | Small-map tests cannot establish three separate starting districts | Validate coal/coke/iron, agriculture, timber and customer distances at actual candidate locations. Keep horses as an optional local/mixed strategy. **Moderate** confidence beyond tested duties |
| P2 / polish | Shared Bessemer/open-hearth abstraction, contemporary graphics and no regional calendar | Document the abstraction; do not add cargoes or destroy served industries to simulate technology changes. Regional adoption and separate process representation are later work |

No price, performance, train-limit or vehicle changes are proposed from this phase. Do not transfer the stock campaign's **READY WITH CAVEATS** verdict automatically to this changed industry set. Nothing was installed, pushed, merged or published.
