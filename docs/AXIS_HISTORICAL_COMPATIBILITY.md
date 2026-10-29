# Historical AXIS compatibility — 0.2.0

**PARTIALLY READY.** A compiled and engine-tested replacement industry set exists. Existing stock-AXIS saves/scenarios are **not certified compatible**.

| Contract | Evidence |
|---|---|
| Upstream | AXIS 2.3.1 pinned commit `11c8353ccf7444b143e57080b1aa2b5e38839a23`; Extreme Classic, economy 0 |
| Historical identity | `4B484531` (`KHE1`), numeric version 2, minimum compatible 1; provisional/unregistered project ID |
| Stock identity | `4A4B8808`; explicitly rejected alongside the historical fork |
| Cargo slots | All 64 Classic labels and positions unchanged; compiled 320-record all-branch cargo sequence identical |
| Industries | All 91 original IDs, model recipes, layouts and source graphics unchanged; original dormant steelworks ID 2 enabled only in Classic, total 92 |
| Other economies | Enabled model/cargo data unchanged. Historical policy applies only to Classic; other economies were not given a full runtime campaign test |
| Vehicle stack | Exact campaign versions/parameters of the other 14 GRFs retained in fresh runtime worlds. Planet wagons, horse hoppers/carriages and brig actually refitted/operated where applicable. Not every vehicle/refit has been retested |
| Production | Only the already implemented stockpile steelworks recipe differs from stock. Availability wrappers do not rewrite original recipes |
| Existing industries | Date and permission gates affect new construction. They do not remove, replace, convert or close existing sites |

Matching local IDs and cargo slots are necessary but **do not make a new GRFID a safe existing-save replacement**. Industry and tile mappings carry GRF identity. The declared minimum version concerns saves of this historical identity, not stock AXIS. Even historical 0.1.0→0.2.0 upgrades need disposable-load checks: existing modern industries would be grandfathered. No save was relabeled, no saved GRF list patched and no safety check bypassed to claim compatibility.

The read-only English/US-English source-name crosswalk covers all **1,387** original Europe industry instances. **463** are outside this build's 1830 construction policy, including policy exclusions; **924** match it. These are policy classifications, not 463 independently proven historical errors. See [instance review](research/axis_historical_existing_industry_review.csv). Loading them unchanged would not create the intended progression, even if a loader accepted the GRF replacement.

The [availability matrix](research/axis_historical_availability.csv) accounts for every type, including permission flags, date evidence, cargo relationships and survival policy. Broad draft bands remain provisional. Early ports/wharves, machine shops and some other industries retain modern-input/output proxies. Rubber/nitrate/tar-sands types are excluded from new European construction, which needs a separate import-chain review; synthetic-rubber availability alone is not a satisfactory historical natural-rubber policy. No new cargo ID is introduced to conceal that limitation.

Installed-asset verification checks **83** original asset paths and the original scenario SHA256, and resolves all **15** original GRF MD5 identities in the isolated input library. Runtime replaces exactly the AXIS entry. One normal Documents config differs from the older Phase 1 fingerprint; its last-write time **21:11:16**, before the first Phase 5 engine run at approximately **21:15:32**, is recorded in `preservation-phase5-result.json`. It was not restored or used as an embedded-settings substitute. Test commands explicitly use disposable `-c` paths and `-X -x`; no claim is made that all historical config checksums still match.

No third-party vehicle/base-set/engine assets or scenario binaries are committed or included in the historical source bundle. AXIS's pinned GPLv2 notice permits the local fork build and matching corresponding-source packaging; preserve all notices and the paired source if redistributing. No release or upload was made.
