# Local vehicle NewGRF inventory — 2026-10-28

NARS 2.52 **is installed and loaded by the newest scenario**. It is distinct from the NARS Add-On Set 2cc, which is also installed and loaded. The scenario contains six train sets and two ship sets. No installed game file was edited and no rolling stock was installed or removed.

## Installation and scenario selection

Two byte-identical JGRPP executables were found:

- `C:\Program Files (x86)\Steam\steamapps\common\OpenTTD\openttd.exe`
- `C:\Users\Kladd\Downloads\OpenTTD\openttd.exe`

Windows executable version resources report **jgrpp-0.73.4**. Both executables have SHA-256 `1b3fd69c1ea5f77eebe881c6d8a6ad9a03b71f98928a05e0c3c08c79482e2789`. The portable copy supplied the isolated measurement runtime; the original scenario's `SLXI` chunk independently identifies jgrpp-0.73.4.

The newest discovered configuration is `C:\Users\Kladd\Documents\OpenTTD\openttd.cfg`, modified **2026-10-28 02:30 local time**. The portable configuration is older, **2026-10-26 22:57**. The Documents configuration has nine current NewGRF entries; this does **not** describe the 15-GRF scenario.

The newest standalone scenario is `C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1800 V2 newGRFS.scn`, modified **2026-10-28 01:07:36**, SHA-256 `5710beea8b3badf6aecc8ab679caea1fb2c4b66e96c4393b342a816c064e0688`. Its filename says 1800, but its embedded date is **1830-01-01**, and `MAPS` confirms **4096 × 4096**. The portable `Europe 1800 - Toni.scn` and five other Documents scenarios are older. Modification time is the selection rule, then embedded date/GRFs verify identity; filenames alone were not used.

The later `Documents\OpenTTD\save\autosave\autosave6.sav`, **02:21:51**, was inspected separately. It has the same 15 GRF identities, parameter vectors and relevant economy settings. See [autosave evidence](research/newest_autosave_economy.json). It is a subsequent gameplay save, not a newer standalone scenario.

## Search coverage and actual data paths

Bounded discovery covered the initially empty task directory, the adjacent existing project checkout, Documents/OpenTTD, Downloads/OpenTTD, Desktop entries, OneDrive/Documents and localized OneDrive/Dokumenty, AppData directory names, Program Files directory names, Steam's library configuration and its OpenTTD folder. No unrestricted disk scan was performed. No OpenTTD content directory was found at the checked OneDrive locations. The Steam installation contains no additional vehicle `newgrf` or `content_download/newgrf` directory. Downloads also contains loose copies of GETS and the Polish train GRF, outside the game's normal search subdirectories.

Installed content-bearing roots:

- `C:\Users\Kladd\Documents\OpenTTD\newgrf` — includes `gets0.7.grf`.
- `C:\Users\Kladd\Documents\OpenTTD\content_download\newgrf` — the downloaded TAR collection and loose Polish train GRF.
- `C:\Users\Kladd\Downloads\OpenTTD\newgrf` — older portable copies.
- `C:\Users\Kladd\Downloads\OpenTTD\content_download\newgrf` — checked; no additional audited vehicle collection.

OpenTTD resolves content through working, binary, Windows personal and autodownload search roots, including TAR members. The effective personal/config root depends on launch directory and `-c`; there is no single universal path independent of launch arguments. Steam has no local configuration, while Downloads has an older portable configuration. A currently running user's launch command could not be established. These findings establish the files and loaded scenario, rather than claiming an unobserved shortcut's arguments.

For the audit, `-c probe.cfg -x` with the working directory inside `.vehicle-audit-runtime` explicitly routed all writes to the repository's ignored disposable directory. The GRFs were locally copied there without editing. The original scenario was opened read-only for one headless load with autosave disabled; it was never saved. [Scenario load evidence](research/vehicle_scenario_load_evidence.log) records the resolved sets and local cost multipliers.

## Installed versus referenced and loaded

| Set | GRFID | Installed | Scenario reference / load | Measured train/ship entries |
| --- | --- | --- | --- | --- |
| GETS 0.7 | 53410808 | Yes | Yes | 1602 |
| UKRS2 1.05 | 44441000 | Yes | Yes | 94 |
| Timberwolf UK Trains 1.7.7 | 54574607 | Yes | No | Outside train/ship probe |
| Timberwolf Addon 1.2.6 | 5457460C | Yes | No | Outside train/ship probe |
| Polish Train Set 3.0.3 (file label) | 4D560103 | Yes | Yes | 135 |
| Polish Rolling Stock Pack 0.19.11 (archive label) | 4D560105 | Yes | Yes | 694 |
| NARS 2.52 | 44440302 | Yes | Yes | 113 |
| NARS Add-On Set 2cc rev.2401131718 | 4E4D0518 | Yes | Yes | 216 |
| 2cc TrainsInNML 3.1 | 544D0101 | Yes | No | Outside train/ship probe |
| Sailing Ships community 0.73 | 434D4301 | Yes | Yes | 8 |
| Squid Ate FISH 2.0.3 | 414E0201 | Yes | Yes | 25 |
| eGRVTS 2.1 r240 | 41560103 | Yes | Yes | Outside train/ship probe |
| Sailing Ships 0.62 | 4A4D0101 | Yes | No | Outside train/ship probe |
| Sal's Canalboats 0.4.1 | 54540501 | Yes | No | Outside train/ship probe |
| PIPE 6.40 (train-feature utility) | 41560102 | Yes | No | Outside train/ship probe |
| Wired 1.2 (train-feature utility) | 4D635769 | Yes | No | Outside train/ship probe |
| Project Gondola 0.4 | 4A565201 | Yes | No | Outside train/ship probe |


"Active" here means referenced and loaded by this scenario, with train/ship definitions observed in the matching isolated runtime. It does not mean every engine is purchasable in 1830. Deity-mode API enumeration includes definitions available in earlier or later years. Counts include individual livery variants, articulated definitions exposed as engines and powered control vehicles; they are not counts of distinct historical prototypes.

The complete scan found **83 GRF instances, 74 distinct full-file hashes** in the normal vehicle content roots, including non-vehicle scenery/infrastructure GRFs. The six train sets yielded **2,854** entries; the two ship sets yielded **33**. Other installed GRFs using train features include PIPE, Wired and Project Gondola, which are not active campaign rolling-stock sets. Older Sailing Ships 0.62 is installed under GRFID `4A4D0101` and is not referenced; community 0.73 has a different GRFID and is the active edition.

Nine GRFIDs have duplicate copies across Documents and the portable directory. Each duplicate group has identical GRF SHA-256 values: eGRVTS, CHIPS, Sailing Ships community, av8, UKRS2, ISR, Polish Rolling Stock Pack, FIRS and Polish Train Set. No conflicting binary versions were found within those groups. Different GRFIDs, such as the two Sailing Ships editions, are reported separately. Full paths and members are in [inventory JSON](research/newgrf_inventory.json).

## NARS identification

### North American Railway Set (NARS) 2.52

- Archive: `C:\Users\Kladd\Documents\OpenTTD\content_download\newgrf\44440302-North_American_Renewal_Set-2.52.tar`
- Member / filename: `North_American_Renewal_Set-2.52/newnars.grf`
- Internal Action 8 name: `North American Railway Set (NARS) 2.52` (replacement characters represent embedded legacy colour controls).
- GRFID: `44440302`; saved version integer `252`.
- Installed **yes**; newest scenario reference **yes**; successful original-scenario runtime load **yes**; enabled test-map engine entries **113**.
- GRF SHA-256: `2492f70bdd9a50a089b245e81b5b54ac6a1f4efaf733c4956a272809052bc854`
- Archive SHA-256: `7d1c6b816c8b7a6b06143712020769d8050272d8afa9eafa6e2a35c7aece4d47`
- Scenario NewGRF MD5 identity: `5f268de28cca8fa7fdd140ac031a5939`. This identity can hash only the data section of a v2 GRF; it is not the full-file SHA-256.

### NARS ADD-ON SET 2CC rev.2401131718 (STILL 218 Vehicles!)

- Archive: `C:\Users\Kladd\Documents\OpenTTD\content_download\newgrf\4e4d0518-NARS_Add_On_Set_2cc-2401131718.tar`
- Member / filename: `NARS_Add_On_Set_2cc-2401131718/nars_add_on_set.grf`
- Internal Action 8 name: `�NARS ADD-ON SET 2CC �rev.2401131718 �(STILL 218 Vehicles!)` (replacement characters represent embedded legacy colour controls).
- GRFID: `4E4D0518`; saved version integer `2401131718`.
- Installed **yes**; newest scenario reference **yes**; successful original-scenario runtime load **yes**; enabled test-map engine entries **216**.
- GRF SHA-256: `66104bc7965fc8cffa702a4a457d68413dbec1f696a208eb8efad04cce90a7bd`
- Archive SHA-256: `f01a247f596e0174e114b45cbc60c135063ef6b588b94f01783192e78931494b`
- Scenario NewGRF MD5 identity: `d4c3a76cd516a5fccfa0de58bb3e9c7b`. This identity can hash only the data section of a v2 GRF; it is not the full-file SHA-256.

The NARS archive is advertised as North American **Renewal** Set, but its actual internal name says North American **Railway** Set (NARS) 2.52. Both names refer here to the binary with GRFID `44440302`, not the add-on's `4E4D0518`. The add-on's public version string is `2401131718`; its saved integer is also `2401131718`.

## Exact scenario list and parameters

| Order | GRFID | Saved name | Saved integer version | Raw parameter vector |
| --- | --- | --- | --- | --- |
| 1 | 44440A01 | av8 Aviators Aircraft Set | 2210 | [] |
| 2 | 43485054 | CHIPS Station Set 2.0.0 | 376 | [] |
| 3 | 41560103 | eGRVTS v2.1 - r240 | 40 | [0, 63, 0, 3, 0] |
| 4 | 4A430002 | Industrial Stations Renewal 1.0.2 | 5518 | [0, 1] |
| 5 | 4D560103 | Polish Train Set 3.0 | 211 | [1, 1, 0, 0, 0, 0] |
| 6 | 434D4301 | Sailing Ships (community) 0.73 | 5 | [0, 0, 0] |
| 7 | 4D560105 | TEST Polish Rolling Stock Pack 0.19.1 | 17 | [1, 1, 0, 0, 0, 0] |
| 8 | 44441000 | UK Railway Set (UKRS2) | 1050 | [0, 0, 0, 0, 0, 3, 2] |
| 9 | 414E0201 | Squid Ate FISH r1687 | 1687 | [1, 1, 0] |
| 10 | 0100403A | City objects 1.3 | 0 | [] |
| 11 | 4F472B34 | OpenGFX+ Landscape 1.1.2 | 5524 | [12, 0, 4, 15, 4, 0] |
| 12 | 44440302 | North American Railway Set (NARS) 2.52 | 252 | [0] |
| 13 | 4E4D0518 | NARS ADD-ON SET 2CC rev.2401131718 (STILL 218 Vehicles!) | 2401131718 | [4, 3, 2] |
| 14 | 4A4B8808 | AXIS 2.3.1 | 6749 | [0, 0, 0, 0, 0, 0, 16, 150, 80, 300] |
| 15 | 53410808 |  GETS 0.7 | 19 | [3, 2] |


Saved/internal names can lag archive names: the Polish train archive/file label is 3.0.3, while Action 8 says 3.0; Rolling Stock Pack archive label is 0.19.11, while Action 8 says TEST 0.19.1. Preserve the hashes and saved integer versions when reproducing the audit. Squid's archive version 2.0.3 and internal r1687 likewise differ.

## Verified economy settings

The embedded `PATS`, `DATE`, `ECMY` and `MAPS` tables were parsed using their typed table headers and full record-length checks. [Decoded scenario settings](research/scenario_economy_settings.json) retain the full data.

| Setting | Scenario value | Meaning for this audit |
| --- | --- | --- |
| difficulty.construction_cost | 0 | Low; base purchase prices use 6/8 of medium |
| difficulty.vehicle_costs | 0 | Low; running cost bases use 6/8 of medium |
| economy.inflation | 0 | Off |
| ECMY inflation_prices / inflation_payment | 65536 / 65536 | Fixed-point 1.0; no accumulated inflation |
| economy.day_length_factor | 1 | No day-length scaling |
| economy.timekeeping_units | 0 | Calendar mode |
| economy.minutes_per_calendar_year | 12 | Saved setting; does not imply a cost multiplier in calendar mode |
| vehicle.dynamic_engines | 1 | Sets have separate engine ID scopes |
| difficulty.vehicle_costs_in_depot / when_stopped | 1 / 1 | Saved operating-cost modifiers; actual duty-cycle costs require built trains |
| vehicle.repair_cost | 100 | Separate breakdown/repair expense setting |
| Client locale currency | GBP | From newest client configuration, not a scenario currency property |
| Client show_running_costs_calendar_year | false | With day length 1 either display basis gives the same value |

Action 14 metadata was decoded directly from the installed GRFs; see [parameter definitions](research/vehicle_grf_parameters.json). NARS reduce-costs is false. NARS Add-On purchase multiplier is 1× and running multiplier 1/2× (`[4,3,2]`); the third parameter is loading speed, set to Normal. GETS running and purchase choices are both their labelled defaults (`[3,2]`). Polish cost multipliers omitted from the saved short vectors use their declared defaults. UKRS2's displayed parameter ordinals use MASK mappings into raw parameters: locomotive selection is raw parameter 5 = 3 (Normal), wagon selection is raw parameter 6 = 2 (Normal). Reading the first two raw zeros as "no locomotives / no wagons" would be incorrect.

## Reproduction and evidence limits

See the commands and API interpretation in [price audit](LOCOMOTIVE_PRICE_AUDIT.md). All installed GRFs, filenames, archive members, hashes, scan errors and duplicate groups are retained in JSON. The static parser deliberately does not emulate Action 6/7/9 or arbitrary callbacks. It encounters synthetic Action 0 data in Timberwolf and legacy GRFs; those errors are recorded and are not used as resolved statistics. Final numerical rows come from JGRPP itself. No GRF binary, sprite, sound or rendered copyrighted asset is included in the reports.

This checkout was cloned from the existing local `openttd-europe-1830-2025-historical-industry` checkout, whose upstream is `kladdey/Openttd-europe-1800`. Work is on `audit/local-vehicle-economy`. The source checkout was not edited; no push or merge was performed.
