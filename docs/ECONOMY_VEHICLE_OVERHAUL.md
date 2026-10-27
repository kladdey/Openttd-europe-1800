# Economy and vehicle overhaul - findings and test plan

Updated 2026-10-27. **Planning document, not an implemented configuration.**

## Playtest evidence

A three-company multiplayer playtest ran on the Europe 1800 map using OpenTTD JGRPP 0.73.4. The group progressed from 1800 to **1813**. Road vehicles and ships were operational. The test session is **disposable**: there is no requirement to migrate its companies, finances, or save into the eventual campaign. The playtest does not establish long-duration stability or compatibility of a proposed replacement NewGRF stack.

Two player-reported shortcomings:
1. **Insufficient industry diversity** with the present FIRS Temperate Basic setup, especially for a continent-wide 1800-2025 simulation.
2. **Unsatisfying early vehicle selection**: notably a two-horse passenger carriage contrasted with a six-horse mail carriage, and no useful train options encountered by 1813.

The screenshot of the playtest confirms three participating companies, including road and ship fleets, but **does not prove any AXIS compatibility or establish an exhaustive vehicle roster**.

## Industry direction

- **Candidate:** AXIS eXtreme Industry Set, **Extreme Classic** economy, to be evaluated as a replacement for FIRS rather than layered on top.
- **Alternative/reference:** XIS Extreme Industry Set, predecessor to AXIS. Both merit documentation, but AXIS is the leading candidate.
- AXIS is reported to use the full **64 cargo slots**. Verify exact AXIS version, economy configuration, cargo labels, NewGRF compatibility and redistribution license against authoritative upstream metadata before shipping.
- The current FIRS Temperate Basic economy is considered too narrow for the project goal.
- **Historical progression** is required: regional industry clusters and gradual development from 1800 to 2025, rather than all industries present in 1800.
- Proposed historical regions include Britain, the Ruhr, Belgium, northern France, Silesia and Bohemia. Dates, counts and placements remain research tasks, not approved historical facts.
- Investigate whether a GameScript can introduce industry types and place sites under AXIS's siting rules. Do not assume GameScript can override NewGRF restrictions.
- Run all conversion experiments on **fresh, disposable scenario copies**. Preserve original source scenarios and validated geographic checkpoints.

## Vehicle direction - especially 1800-1850

The goal is **meaningful choices every decade**, not simply a high total number of vehicles.

### Roads
Audit the installed eGRVTS v2.1 r240 roster, specifically introduction dates, purchase/running costs, capacity, speed and supported cargoes. Earlier published rosters suggest that larger passenger coaches arrive later than several multi-horse mail coaches; **verify this in the installed version**. Identify gaps in:
- Passenger stagecoaches and multi-horse carriages
- Mail coaches
- Light carts, heavy freight wagons and agricultural carts
- Specialist industrial cargo transport

The player specifically encountered a two-horse passenger carriage versus a six-horse mail carriage. Do not claim that the latter is historically impossible; the issue is gameplay variety and balancing.

### Rail
The playtest reached 1813 without useful trains. Investigate compatible wagonway/horse-tram and experimental locomotive NewGRFs. Historical design targets to investigate:
- 1800: horse-drawn wagonways and industrial tramroads
- c. 1804: experimental steam locomotives, with severe limits
- 1825 onward: early commercial locomotive railways
- 1830 onward: broader railway expansion

These are **design targets, not proof that the installed UKRS2 or Polish train sets contain these vehicles**. Verify introduction years and JGRPP compatibility. Do not fabricate vehicle availability.

### Water
Audit Sailing Ships community 0.73 and any complementary early steam vessel sets for river barges, coastal vessels, cargo variety, dates and cargo labels. Retain meaningful shipping competition with rail.

## Compatibility and release safeguards

1. Inventory **all** NewGRFs currently loaded and their exact versions/settings.
2. Build a cargo-label compatibility matrix: AXIS cargoes against road, rail and ship sets, including refits.
3. Verify AXIS and proposed vehicle-set behavior in JGRPP **0.73.4** on a **4096 x 4096** Europe map.
4. Test a fresh 1800 scenario: industry generation, siting restrictions, costs, year-based availability, routes and multiplayer joins.
5. Measure game performance and test the 1800-1850 progression before adopting the stack.
6. Do not distribute third-party NewGRF binaries without individual license review. Prefer documented upstream downloads; see [LICENSING.md](LICENSING.md).

## Acceptance criteria for next playable candidate

- A demonstrably broader and functioning cargo/industry network than current FIRS Temperate Basic.
- At least several viable passenger, mail and freight choices in the 1800s, with documented progression.
- A credible early rail option or a clearly documented technical limitation and fallback.
- Working cargo transport across road, rail and shipping without silent unsupported cargoes.
- Successful clean-start and multiplayer smoke tests with the selected stack.
- No changes to the validated town baseline or original source scenarios.

**Status:** Research and testing pending. No AXIS conversion, new vehicle mod installation, or historical industry script has yet been verified in this repository.
