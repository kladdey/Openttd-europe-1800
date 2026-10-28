"""Render audit reports from the measured, local evidence tables."""
import csv,json,collections
from pathlib import Path
R=Path('docs/research');D=Path('docs')

def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(str(c).replace('|','/') for c in row)+' |' for row in rows)+'\n'

def main():
    inv=json.loads((R/'newgrf_inventory.json').read_text(encoding='utf8'));refs=inv['scenario']['references'];roster=list(csv.DictReader((R/'vehicle_roster.csv').open(encoding='utf-8-sig')))
    active={r['grfid']:r for r in refs};instances=inv['installed_newgrfs'];seen={g.get('grfid'):g for g in instances}
    candidates=[('53410808','GETS 0.7'),('44441000','UKRS2 1.05'),('54574607',"Timberwolf UK Trains 1.7.7"),('5457460C','Timberwolf Addon 1.2.6'),('4D560103','Polish Train Set 3.0.3 (file label)'),('4D560105','Polish Rolling Stock Pack 0.19.11 (archive label)'),('44440302','NARS 2.52'),('4E4D0518','NARS Add-On Set 2cc rev.2401131718'),('544D0101','2cc TrainsInNML 3.1'),('434D4301','Sailing Ships community 0.73'),('414E0201','Squid Ate FISH 2.0.3'),('41560103','eGRVTS 2.1 r240')]
    candidates.extend([('4A4D0101','Sailing Ships 0.62'),('54540501',"Sal's Canalboats 0.4.1"),('41560102','PIPE 6.40 (train-feature utility)'),('4D635769','Wired 1.2 (train-feature utility)'),('4A565201','Project Gondola 0.4')])
    installed_table=table(['Set','GRFID','Installed','Scenario reference / load','Measured train/ship entries'],[(name,g,'Yes' if g in seen else 'No','Yes' if g in active else 'No',inv['runtime_counts'].get(g,'Outside train/ship probe')) for g,name in candidates])
    refs_table=table(['Order','GRFID','Saved name','Saved integer version','Raw parameter vector'],[(i+1,r['grfid'],r['name'],r['version'],r['params']) for i,r in enumerate(refs)])
    nars=''
    for gid in ('44440302','4E4D0518'):
        g=seen[gid];ref=active[gid]
        nars+=f"\n### {ref['name']}\n\n- Archive: `{g['path']}`\n- Member / filename: `{g.get('member')}`\n- Internal Action 8 name: `{g.get('internal_name')}` (replacement characters represent embedded legacy colour controls).\n- GRFID: `{gid}`; saved version integer `{ref['version']}`.\n- Installed **yes**; newest scenario reference **yes**; successful original-scenario runtime load **yes**; enabled test-map engine entries **{inv['runtime_counts'][gid]}**.\n- GRF SHA-256: `{g['sha256']}`\n- Archive SHA-256: `{g['archive_sha256']}`\n- Scenario NewGRF MD5 identity: `{ref['md5']}`. This identity can hash only the data section of a v2 GRF; it is not the full-file SHA-256.\n"
    inventory=f"""# Local vehicle NewGRF inventory — 2026-10-28

NARS 2.52 **is installed and loaded by the newest scenario**. It is distinct from the NARS Add-On Set 2cc, which is also installed and loaded. The scenario contains six train sets and two ship sets. No installed game file was edited and no rolling stock was installed or removed.

## Installation and scenario selection

Two byte-identical JGRPP executables were found:

- `C:\\Program Files (x86)\\Steam\\steamapps\\common\\OpenTTD\\openttd.exe`
- `C:\\Users\\Kladd\\Downloads\\OpenTTD\\openttd.exe`

Windows executable version resources report **jgrpp-0.73.4**. Both executables have SHA-256 `{inv['fingerprints'][0]['sha256']}`. The portable copy supplied the isolated measurement runtime; the original scenario's `SLXI` chunk independently identifies jgrpp-0.73.4.

The newest discovered configuration is `C:\\Users\\Kladd\\Documents\\OpenTTD\\openttd.cfg`, modified **2026-10-28 02:30 local time**. The portable configuration is older, **2026-10-26 22:57**. The Documents configuration has nine current NewGRF entries; this does **not** describe the 15-GRF scenario.

The newest standalone scenario is `C:\\Users\\Kladd\\Documents\\OpenTTD\\scenario\\Europe 1800 V2 newGRFS.scn`, modified **2026-10-28 01:07:36**, SHA-256 `{inv['scenario']['sha256']}`. Its filename says 1800, but its embedded date is **1830-01-01**, and `MAPS` confirms **4096 × 4096**. The portable `Europe 1800 - Toni.scn` and five other Documents scenarios are older. Modification time is the selection rule, then embedded date/GRFs verify identity; filenames alone were not used.

The later `Documents\\OpenTTD\\save\\autosave\\autosave6.sav`, **02:21:51**, was inspected separately. It has the same 15 GRF identities, parameter vectors and relevant economy settings. See [autosave evidence](research/newest_autosave_economy.json). It is a subsequent gameplay save, not a newer standalone scenario.

## Search coverage and actual data paths

Bounded discovery covered the initially empty task directory, the adjacent existing project checkout, Documents/OpenTTD, Downloads/OpenTTD, Desktop entries, OneDrive/Documents and localized OneDrive/Dokumenty, AppData directory names, Program Files directory names, Steam's library configuration and its OpenTTD folder. No unrestricted disk scan was performed. No OpenTTD content directory was found at the checked OneDrive locations. The Steam installation contains no additional vehicle `newgrf` or `content_download/newgrf` directory. Downloads also contains loose copies of GETS and the Polish train GRF, outside the game's normal search subdirectories.

Installed content-bearing roots:

- `C:\\Users\\Kladd\\Documents\\OpenTTD\\newgrf` — includes `gets0.7.grf`.
- `C:\\Users\\Kladd\\Documents\\OpenTTD\\content_download\\newgrf` — the downloaded TAR collection and loose Polish train GRF.
- `C:\\Users\\Kladd\\Downloads\\OpenTTD\\newgrf` — older portable copies.
- `C:\\Users\\Kladd\\Downloads\\OpenTTD\\content_download\\newgrf` — checked; no additional audited vehicle collection.

OpenTTD resolves content through working, binary, Windows personal and autodownload search roots, including TAR members. The effective personal/config root depends on launch directory and `-c`; there is no single universal path independent of launch arguments. Steam has no local configuration, while Downloads has an older portable configuration. A currently running user's launch command could not be established. These findings establish the files and loaded scenario, rather than claiming an unobserved shortcut's arguments.

For the audit, `-c probe.cfg -x` with the working directory inside `.vehicle-audit-runtime` explicitly routed all writes to the repository's ignored disposable directory. The GRFs were locally copied there without editing. The original scenario was opened read-only for one headless load with autosave disabled; it was never saved. [Scenario load evidence](research/vehicle_scenario_load_evidence.log) records the resolved sets and local cost multipliers.

## Installed versus referenced and loaded

{installed_table}

"Active" here means referenced and loaded by this scenario, with train/ship definitions observed in the matching isolated runtime. It does not mean every engine is purchasable in 1830. Deity-mode API enumeration includes definitions available in earlier or later years. Counts include individual livery variants, articulated definitions exposed as engines and powered control vehicles; they are not counts of distinct historical prototypes.

The complete scan found **83 GRF instances, 74 distinct full-file hashes** in the normal vehicle content roots, including non-vehicle scenery/infrastructure GRFs. The six train sets yielded **2,854** entries; the two ship sets yielded **33**. Other installed GRFs using train features include PIPE, Wired and Project Gondola, which are not active campaign rolling-stock sets. Older Sailing Ships 0.62 is installed under GRFID `4A4D0101` and is not referenced; community 0.73 has a different GRFID and is the active edition.

Nine GRFIDs have duplicate copies across Documents and the portable directory. Each duplicate group has identical GRF SHA-256 values: eGRVTS, CHIPS, Sailing Ships community, av8, UKRS2, ISR, Polish Rolling Stock Pack, FIRS and Polish Train Set. No conflicting binary versions were found within those groups. Different GRFIDs, such as the two Sailing Ships editions, are reported separately. Full paths and members are in [inventory JSON](research/newgrf_inventory.json).

## NARS identification
{nars}
The NARS archive is advertised as North American **Renewal** Set, but its actual internal name says North American **Railway** Set (NARS) 2.52. Both names refer here to the binary with GRFID `44440302`, not the add-on's `4E4D0518`. The add-on's public version string is `2401131718`; its saved integer is also `2401131718`.

## Exact scenario list and parameters

{refs_table}

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
"""
    D.joinpath('VEHICLE_NEWGRF_INVENTORY.md').write_text(inventory,encoding='utf8')
    engines=[r for r in roster if r['category']=='locomotive_or_powered_unit' and int(r['introduction_year'])<=1850]
    engine_table=table(['Set / local ID','Engine','Intro year','£ purchase','£/year','hp','kN','t','km-ish/h'],[(r['source_grfid']+' / '+r['local_vehicle_id'],r['vehicle_name'],r['introduction_year'],r['purchase_price_gbp'],r['annual_running_cost_gbp'],r['power_hp'],r['tractive_effort_kn'],r['weight_t'],r['max_speed_kmish_h']) for r in engines])
    metrics=table(['Engine','£/hp','£/year/hp','£/kN','Annual / purchase'],[(r['vehicle_name'],r['purchase_per_hp'],r['running_per_hp'],r['purchase_per_kn'],f"{float(r['annual_running_to_purchase'])*100:.2f}%") for r in engines])
    audit=f"""# Locomotive price audit — measured baseline

The player-reported **Grasshopper ≈ £6,000 / Planet ≈ £1,500** purchase-price comparison was **not reproduced** under the newest scenario's verified settings. At the common 1830 baseline the installed UKRS2 Planet is **£7,031**, while the NARS Add-On Grasshopper is **£4,687**. Their annual engine API running costs are **£525** and **£3,150**, respectively. The running-cost imbalance is real in this measurement, but the claimed fourfold purchase-price direction is not established.

## What was measured

The existing JGRPP 0.73.4 executable ran a read-only engine-query GameScript on a disposable 64 × 64 generated map. The map used the exact newest scenario's **15 GRF identities, order and parameters**, its 1830 date, matching low purchase/running difficulty, no inflation and day length 1. The original 4096-square scenario was separately loaded without saving and its final local multipliers were checked. The later autosave retains the same settings. Thus these are controlled **JGRPP API measurements**, not guessed stats or manually transcribed buy-window screenshots.

The script queries GSEngine name, design date, price, annual cost, speed, power, weight, maximum TE, default articulated capacity, reliability and cargo-refit labels. JGRPP's GRF diagnostics join runtime engine IDs to **GRFID + local ID**. Runtime IDs are session-specific; use GRFID/local ID as stable keys. The engine API calls the same Engine::GetCost/GetRunningCost property and callback path used for engine prices. No depot, locomotive or wagon was built or changed. Whole-consist attachment/refit/build-command costs have not been measured.

Results: **2,887 entries = 2,854 train entries + 33 ship entries**. Heuristic powered categories separate 1,330 locomotive/powered entries, 436 multiple-unit/railcar candidates and 42 powered control/dummy entries; 1,046 wagon entries are identified by the engine API. These counts include liveries, rather than distinct historical prototypes. There are **28 early train entries**, including **five locomotives** with runtime introduction years through 1850; the remainder are wagons. The complete loaded roster is in [vehicle_roster.csv](research/vehicle_roster.csv). Six snapshots at **1830, 1850, 1900, 1950, 2000 and 2025** provide **17,322 observations** in [vehicle_economy_snapshots.csv](research/vehicle_economy_snapshots.csv). All six runs completed their full enumeration. Future definitions queried in an early snapshot are not thereby purchasable then.

## Early locomotive comparison

Values below are the 1830 API snapshot of each definition, including later introductions. Introduction dates are game definitions, not historical claims. Some engine dates have normal game randomisation; base introduction of both Planet and Grasshopper is explicitly 1830-01-01. Reliability is a transient runtime value and must not be treated as a fixed performance advantage. Speed is the API's km-ish/h integer (mph × 1.6), not a claim of exact SI km/h.

{engine_table}
{metrics}

No early GETS, Polish Train Set or Polish Rolling Stock Pack locomotive appears in the enabled-throughout-history 1830–1850 subset. This does not mean those sets failed to load: their later definitions are in the full roster. NARS's first locomotive here is the 1838 Norris. Grasshopper comes from its separate add-on.

## Planet versus Grasshopper: source, factors and modifiers

| Field | Planet | Grasshopper |
| --- | --- | --- |
| Provider | UK Railway Set (UKRS2), archive 1.05 | NARS Add-On Set 2cc rev.2401131718 |
| GRFID / local ID | 44441000 / 124 | 4E4D0518 / 116 |
| Measured runtime engine ID | 1534 | 2038 |
| Introduction | 1830-01-01 | 1830-01-01 |
| Purchase, low difficulty | £7,031 | £4,687 |
| Annual running cost, 1830 | £525 | £3,150 |
| Power / TE | 120 hp / 11 kN | 63 hp / 11 kN |
| Weight / speed | 14 t / 48 km-ish/h | 8 t / 38 km-ish/h |
| Resolved train purchase-base exponent | 0 (1×) | +1 (2×) |
| Resolved steam running-base exponent | +3 (8×) | +3 (8×) |
| Effective purchase factor inferred from exact runtime price | 6 | 2 |
| Effective running factor inferred from exact runtime cost | 4 | 24 |
| Raw factor extraction | UNVERIFIED: UKRS2 uses runtime transformations | Purchase 2 and running 24 directly decoded in Action 0 at byte offset 24148 |

"Effective factor" is a numerical inference from the verified base, local exponent and final cost, not an assertion that every raw field equals that value. Grasshopper's raw 0E running base is `0x4C30`, steam; raw power 63, weight 8 and TE coefficient 36 were also decoded. Runtime evaluation is authoritative if callbacks alter a property.

At this baseline the core train purchase base is £400,000 and steam running base £5,600 before difficulty. Low difficulty multiplies each relevant base by 6/8. With no inflation and the observed local exponents:

```text
Planet purchase     = floor(400000 × 0.75 × 6 × 2^0 / 256) = £7031
Grasshopper purchase= floor(400000 × 0.75 × 2 × 2^1 / 256) = £4687
Planet running      = floor(5600 × 0.75 × 4 × 2^3 / 256)   = £525/year
Grasshopper running = floor(5600 × 0.75 × 24 × 2^3 / 256)  = £3150/year
```

The raw purchase factor ratio is 3:1 in Planet's direction, while the add-on's purchase-base scaling adds 2× in Grasshopper's direction, producing Planet's net 1.5× price. Running bases have the same exponent, so the 6× annual running gap comes from the effective individual running factors. This is a mixture of set-level and vehicle-level definitions, not evidence for blaming one vehicle's nominal price alone.

Changing only construction difficulty from low to medium would predict Grasshopper **£6,250**, close to the player's approximate £6,000, but also predicts Planet **£9,375**, not £1,500. This is a **counterfactual calculation**, not proof of the player's original settings. Neither currency, accumulated inflation nor the latest autosave explains the entire reported pair. A company buy-window observation from the exact file/date/engine instance is still required to reconcile it. A diagnostic company-mode API query at the immediate test-map start returned "not buildable", so it supplies no additional price confirmation and is not used in the numerical tables.

At 1830, Planet adds £2,344 in capital cost but saves £2,625/year in engine running costs: simple break-even **0.893 full-cost operating years**. It has nearly twice the horsepower and higher speed, with the same API maximum TE. Grasshopper is lighter and cheaper up front, so it is **not strictly dominated on every dimension**. Actual route results depend on loads, gradients, running time, wagon speed limits, servicing and attachment behaviour.

## Complete-consist estimates, 1830 baseline

These are **additive estimates from verified individual API values**, not built-train command quotes. Four coaches deliberately compare a standard vehicle count; the capacities are unequal. Do not infer equal earning potential or equal train length.

| Representative consist | Purchase estimate | Annual cost estimate | Default seats | Notes |
| --- | --- | --- | --- | --- |
| Planet + 4 UKRS2 Passenger Coaches (ID 44) | £9,935 | £677 | 36 | 4 × £726, 4 × £38/year; 9 seats each |
| Grasshopper + 4 NARS Passenger Cars (ID 80) | £22,311 | £3,910 | 100 | 4 × £4,406, 4 × £190/year; attachment untested |
| Norris + 4 NARS Passenger Cars | £29,342 | £7,060 | 100 | Appropriate locomotive introduction is 1838 |
| Planet + 4 UKRS2 Open Wagons (ID 12) | £8,059 | £553 | 24 default cargo units | Capacity 6 each, cargo/refit compatibility must be checked |
| Grasshopper + 4 NARS Single Hoppers (ID 101) | £15,187 | £3,302 | 80 default cargo units | Capacity 20 each, attachment untested |

UKRS2's early coach is £80.67 per default seat versus NARS's £176.24. The open wagon is £42.83 per default capacity unit versus £131.25 for the NARS hopper; however they are different wagon types with different speeds, weights and cargo options. Larger wagons may save train length and total dead weight per transported unit. Mixing cheap wagons across sets is a potential exploit to test, not a verified compatible consist.

## Ten highest-priority numerical balance findings

The following are **verified displayed-stat/engine-cost discrepancies**, ranked for investigation. "Candidate domination" means the listed purchase/running/performance dimensions favour one definition. Reliability, rail compatibility, articulation, heating, cargo/refit callbacks and purchase availability can still give an apparent loser a useful role. No vehicle removal is proposed. Later-year comparisons use the **2000 snapshot**, not 1830 prices for future technology.

| Rank | Comparison and numerical evidence | Implication / limit |
| --- | --- | --- |
| 1 | 1830 Grasshopper £3,150/year, 63 hp versus Planet £525/year, 120 hp: **£50 versus £4.375/year/hp (11.43×)** | Very strong early operating-cost disparity. Planet needs extra capital and is heavier; decide whether either set's early costs fit campaign earning rates. |
| 2 | Norris (1838) £11,718 / £6,300 yearly / 200 hp / 19 kN / 56 speed; Coppernob (1844) £12,890 / £1,181 / 250 hp / 43 kN / 64 speed | A £1,172 capital premium buys a £5,119 annual saving and stronger performance. After 1844 this is a candidate economic displacement; Norris has earlier availability and lower weight. |
| 3 | Polish ST43: PTS local 134 **£30,468 / £3,686 yearly**, PRSP local 330 **£22,265 / £2,833**. Both 2,071 hp, 316 kN, 118 t, speed 100 | PRSP is £8,203 cheaper and £853/year cheaper with matching main stats. Candidate domination, pending operational callback checks. |
| 4 | ET21: PTS local 147 **£33,984 / £1,968 yearly / 333 kN**; PRSP local 570 **£39,843 / £2,109 / 310 kN**. Both 2,494 hp, 121 t, speed 100 | PTS is cheaper to buy/run and has higher TE. Candidate domination across overlapping definitions. |
| 5 | EU07: PTS local 148 versus PRSP local 620 both **£41,015 / £2,221 yearly / 2,682 hp / speed 125**; TE **223 versus 278 kN**, weight 81 versus 80 t | PRSP grants 24.7% more maximum TE without a monetary premium. Investigate axle/adhesion assumptions before treating the higher TE as historically appropriate. |
| 6 | ET22: PTS and PRSP both **£48,046 / £3,093 yearly / 4,023 hp / 120 t / speed 125**; TE **353 versus 413 kN** | PRSP offers 17.0% more TE at the same cost. A base-cost-only solution would miss the performance reason. |
| 7 | UKRS2 Class 66 local 91 **£49,218 / £10,106 yearly / 3,300 hp / 411 kN** versus GETS BR266 local 2660 **£20,507 / £6,870 / 3,200 hp / 400 kN**; both speed 120 | UKRS2 costs 2.40× to purchase and 1.47× annually for only about 3% more power/TE. Strong near-equivalent freight comparison, not strict domination. |
| 8 | EN57: PTS local 161 **£43,359**, PRSP local 1800 **£58,593**; both £1,068/year, 939 hp, 96 kN, 126 t, speed 110 and 265 default seats | PRSP premium 35.1% with matching principal passenger-unit stats. PTS also lists mail refit, so capacity does not explain this premium. |
| 9 | EN71: PTS local 162 **£63,281**, PRSP local 2100 **£83,203**; both £1,715/year, 2,092 hp, 195 kN, 182 t, speed 110, 364 seats | PRSP premium 31.5%; reliability differs in this runtime snapshot, so do not call unconditional domination. Recheck with equal reliability assumptions. |
| 10 | ED72: PTS local 163 **£66,796 / speed 130**, PRSP local 2200 **£85,546 / speed 120**; both £1,800/year, 1,877 hp, 195 kN, 182 t, 336 seats | PRSP costs 28.1% more and is slower with otherwise matching measured main stats. Candidate domination; verify whole-unit composition and callbacks. |

An additional same-cost discrepancy occurs with ET41: TE 460 versus 562 kN. Livery rows are not independent examples of a pricing anomaly; the 1,602 GETS entries include many variants and must not be used to overweight that set in aggregate statistics.

## Time-dependent costs and raw properties

The six snapshots expose effects that a binary-only factor list would miss. Planet remains £7,031 to buy, but its engine annual cost is £525 in 1830, 1850 and 1900, **£1,181 in 1950, £4,462 in 2000 and £5,775 in 2025**. Grasshopper stays £4,687 / £3,150 throughout these snapshots. This is a **GRF calendar-context effect** with inflation off; no old train was constructed and aged in the test. It is not a measured per-vehicle wear curve. Historical definitions can remain queryable after purchase expiry, so these late Planet values do not prove the player can buy it then.

The source path in JGRPP is `src/engine.cpp`: `Engine::GetCost` selects the train or wagon cost base, obtains the cost property through `GetEngineProperty`, and calls `GetPrice(..., -8)`. `GetRunningCost` similarly resolves the running factor and its steam/diesel/electric class. `src/newgrf_engine.cpp` permits callback 0x36 to replace eligible properties. `src/economy.cpp` applies difficulty, accumulated inflation, global base exponents and GRF-local exponents; `GetDisplayRunningCost` may additionally apply client calendar/day-length display scaling. GBP is a presentation unit; it is not the raw property factor.

Resolved local base exponents in this configuration (multipliers are powers of two):

| Set | Train purchase (15) | Wagon purchase (16) | Steam running (42) | Diesel running (43) | Electric running (44) |
| --- | --- | --- | --- | --- | --- |
| Polish Train Set | 0 | +4 | +1 | +1 | +1 |
| Polish Rolling Stock Pack | 0 | +4 | +1 | +1 | +1 |
| UKRS2 | 0 | +2 | +3 | -3 | +5 |
| NARS 2.52 | -1 | +3 | +4 | -3 | No explicit local entry observed |
| NARS Add-On 2cc | +1 | +3 | +3 | +2 | +1 |
| GETS | -2 | +1 | -3 | -5 | No explicit local entry observed |

An omitted entry is **not automatically zero**: defaults and inherited/global multipliers must be resolved by the engine. These exponents alone do not rank prices, because cost-factor ranges differ too. The matching Polish base exponents demonstrate that their ST43/ET21/EMU discrepancies are not explained by different set-wide base scales alone.

## Sources, reproduction and remaining uncertainty

Primary evidence is local: `C:\\Users\\Kladd\\Documents\\Codex\\2026-10-28\\openttd-europe-1830-2025-historical-industry\\.research\\jgr734\\src` supplies the 0.73.4 source definitions cited above, plus `script/api/script_engine.cpp`, `table/pricebase.h`, `newgrf_config.cpp` and the `sl`/`saveload` loaders. Public cross-checks: [JGRPP source at release](https://github.com/JGRennison/OpenTTD-patches/tree/jgrpp-0.73.4/src), [train property specification](https://newgrf-specs.tt-wiki.net/wiki/Action0/Vehicles/Trains), [GETS 0.7 catalogue identity](https://bananas.openttd.org/package/newgrf/53410808/2026-05-03T23%3A08%3A38%2B00%3A00). The public specification explains property formats; the locally executed JGRPP build determines reported numbers.

Preserved evidence: [runtime rows](research/vehicle_runtime_evidence.log), [engine mapping and multiplier diagnostics](research/vehicle_runtime_mapping.log), [scenario references](research/scenario_vehicle_references.json), [snapshot manifest](research/vehicle_snapshot_manifest.json), [parameter definitions](research/vehicle_grf_parameters.json). The checked-in data contain metadata and measurements only, no GRF assets.

Repeat from repository root, using an installed Python with NumPy (the existing scenario chunk module imports it). First choose a **new** output directory for the raw scan; the scanner refuses to overwrite an existing inventory. The preparation/export scripts currently use the recorded `vehicle_audit_v2` path; update that path for a new dated run and retain prior reports in a dated directory before regenerating. The preparation utility copies source files only into `.vehicle-audit-runtime/newgrf` and does not install anything.

```powershell
python scripts/audit_vehicle_newgrfs.py --root "$env:USERPROFILE/Documents/OpenTTD/newgrf" --root "$env:USERPROFILE/Documents/OpenTTD/content_download/newgrf" --root "$env:USERPROFILE/Documents/OpenTTD/scenario" --root "$env:USERPROFILE/Downloads/OpenTTD/newgrf" --root "$env:USERPROFILE/Downloads/OpenTTD/scenario" --output docs/research/vehicle_audit_v2
python scripts/vehicle_audit_tables.py
python scripts/extract_vehicle_grf_parameters.py
python scripts/prepare_vehicle_probe.py
python scripts/run_vehicle_probe.py --exe "$env:USERPROFILE/Downloads/OpenTTD/openttd.exe" --year 1830 --log probe-detailed.log
python scripts/run_vehicle_probe.py --exe "$env:USERPROFILE/Downloads/OpenTTD/openttd.exe" --scenario "$env:USERPROFILE/Documents/OpenTTD/scenario/Europe 1800 V2 newGRFS.scn" --ticks 1 --log scenario-load.log
# Repeat the runtime probe with --year 1850, 1900, 1950, 2000 and 2025,
# giving each log the corresponding name probe-1850.log, etc.
python scripts/export_vehicle_audit.py
python scripts/analyze_vehicle_snapshots.py
python scripts/write_vehicle_audit_reports.py
python scripts/validate_vehicle_audit.py
```

Actual execution used the bundled Python `C:\\Users\\Kladd\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe`; no dependencies were installed. OTTS/zstd autosave decoding uses the already installed Git `libzstd.dll`; OTTX scenarios use Python lzma. Files were never extracted from TARs into the installation.

UNVERIFIED: exact purchase-expiry/retirement dates; historical accuracy of each model's attributes; all MU/DVT classifications; built-consist costs and articulation effects; refitted capacities for every cargo; actual route revenue and profitability; company-specific/depot buy-window confirmation of the reported prices; compatibility/attachment of mixed-set wagons; existing-vehicle age/wear running costs. API -1 values are explicitly UNVERIFIED in the roster (the snapshot CSV preserves the raw -1). Introduction randomisation and reliability values mean not every future definition's date/reliability is identical across independent starts. No statistical extrapolation replaces these missing tests.
"""
    D.joinpath('LOCOMOTIVE_PRICE_AUDIT.md').write_text(audit,encoding='utf8')
    recommendations="""# Vehicle balancing recommendations — proposals only

Start with each set's existing cost parameters, then use narrowly scoped source changes if individual anomalies survive. No balancing changes, vehicle removals, introduction-date changes or new rolling stock have been implemented. The numerical baseline is in [price audit](LOCOMOTIVE_PRICE_AUDIT.md); installations and hashes are in [inventory](VEHICLE_NEWGRF_INVENTORY.md).

## Recommended method

1. **Resolve the reported price pair before assigning targets.** The controlled current-scenario baseline has Planet £7,031 / £525 yearly and Grasshopper £4,687 / £3,150 yearly. An approximately £6,000 Grasshopper can be consistent with medium construction difficulty, but that does not explain a £1,500 UKRS2 Planet. Capture the exact scenario/save, calendar date, buy-menu provider, company, currency and full parameter vector in a future controlled player test. Use GRFID/local ID, not name alone.
2. **Agree on representative duties and service economics.** Use light local passenger, early freight, trunk passenger, mainline freight and shunting benchmarks. On a 4096-square map, annual expenditure and earning potential depend on trip duration, infrastructure, gradients and capacity. Do not set a universal £/hp target. Compare full trains of similar load, speed and role with demonstrated rail and cargo compatibility.
3. **Tune existing set-wide controls where the whole set needs movement.** NARS's reduce-costs switch halves purchase and running together. Its separate add-on has independent powers-of-two purchase and running controls. GETS has separate labelled running and purchase controls. Both Polish sets expose separate purchase/running cost multipliers. Timberwolf has both controls but is not active; changing it would not repair this scenario. UKRS2's exposed metadata has no general purchase-price slider. None of these controls can align two engines within one set independently.
4. **Use source-level per-vehicle price/running-factor changes for residual outliers.** Preserve every existing GRFID, local ID, name, roster member and introduction date in the experimental branch/build. Change only economic definitions or the precise property-0x36 callback branch that produces the cost. Rebuild for private testing and verify hashes and compatibility. Check original licence/source availability first; the audit does not redistribute assets. This is more controllable than trying to neutralise a large callback graph from another GRF.
5. **Consider a cost-only override GRF only after a prototype proves support.** JGRPP's engine-scope override mechanism allows selected GRFs to address another set's ID scope, but a correct patch must map the target and handle callback properties. A static Action 0 assignment alone may be superseded by callback 0x36. Per-set local price bases, load order, dynamic engine mapping, articulation and save compatibility require explicit testing. No working override is claimed or supplied by this audit.

Do not use a general base-cost modifier as a per-engine editor. A global train base affects its price category; a GRF-local train base affects that set's category. Separate wagon and steam/diesel/electric running categories help broad adjustments, but do not independently price Planet, Coppernob or an individual EU07. `src/economy.cpp::GetPrice` takes a price category and GRF pointer, not an engine ID. Individual discrimination comes from the engine's property/callback definitions, not a general global-base switch.

## What the evidence suggests

| Problem | Practical proposal | Caution |
| --- | --- | --- |
| Early add-on running costs versus UKRS2 | First model several comparable passenger/freight routes; experiment with the add-on's independent running multiplier in a disposable copy | It is already at 1/2×. Another reduction changes every add-on vehicle and may create later bargains. No exact factor is recommended yet. |
| Norris operating premium | Compare 1838–1850 complete trains and later competitors before adjusting its factor | Norris supplies the earlier 1838 option; do not remove it or move its introduction. NARS's halve-costs switch affects all eras and both purchase/running costs. |
| ST43 and ET21 overlaps | Target only the economic definitions of the overlapping variants if attachment, heating, refit and reliability tests confirm the advantage | Their set-wide base exponents are equal. Moving the entire Polish collection will not solve all overlaps. |
| EU07, ET22 and ET41 TE discrepancies | Establish which physics definitions suit the campaign, then price each existing variant for its measured useful performance | This audit proposes economic compensation, not automatic changes to TE or historical rosters. More TE is useful on grades but not the same as more high-speed horsepower. |
| EN57 / EN71 / ED72 premiums | Price whole units after verifying articulated parts and passenger/mail refits | Equal aggregate API stats may still hide callback behaviour. EN71's reliability differs in the sampled state. |
| UKRS2 versus GETS Class 66 | Benchmark both on the same freight duty; test whether a UKRS2 cost callback adjustment is needed | The higher-cost model has slightly more power/TE; calendar-dependent costs contribute to the gap. |
| Early wagon disparities | Compare pounds per usable capacity, train length, empty mass and speed; test mixed-set attachment | A cheap small coach is not necessarily better than a larger expensive coach on a congested railway. Preserve both. |
| Costs varying by calendar year | Record per-era economic targets and test old built trains separately | Planet's API yearly cost rises 11× by 2025 despite zero inflation. Flattening that automatically would remove set behaviour that may be intentional. |

## Required validation before implementation

- Player buy-window and actual build-command prices for Planet and Grasshopper in the same date/company/depot, with corresponding GRF and config hashes. Reconcile the original fourfold observation; retain it as player-reported until then.
- Whole-unit build/refit/attachment tests for each selected locomotive, MU and its wagons; include tender/dual-head handling, capacity and cargo labels. The audit's consist totals are additive estimates.
- Purchase availability/retirement and reliability behaviour across the campaign. Deity-mode enumeration of all definitions does not prove year-specific purchasability.
- Equal-load flat and graded routes with recorded travel time, annual expense and revenue. Test early low-TE locomotives under genuinely different duties, not only maximum-power ratios.
- Idle, stopped, depot, servicing, breakdown and repair behaviour; compare calendar/economic-year displays if day length changes later. Current day length is 1, so it does not explain the baseline gap.
- Recheck targeted overlaps in 1900/1950/2000/2025 as appropriate. Sample snapshots already exist; they do not replace a continuous campaign or ageing a constructed vehicle.
- In any future fork/override prototype, verify that only intended economic properties change: retain every vehicle ID, introduction date and asset; preserve multiplayer load order, save identity and permitted licences. Keep the production installation untouched until separately authorised.

No firm target prices or universal multiplier are proposed yet: route earning data and built-consist checks are still missing. The most practical next implementation is a reversible, private parameter experiment for broad set-wide differences, followed by a minimal source fork for confirmed individual outliers. Source edits and binary generation require a separate implementation task; this task provides the measured baseline only.
"""
    D.joinpath('VEHICLE_BALANCING_RECOMMENDATIONS.md').write_text(recommendations,encoding='utf8')
    print('Wrote three reports')

if __name__=='__main__':main()
