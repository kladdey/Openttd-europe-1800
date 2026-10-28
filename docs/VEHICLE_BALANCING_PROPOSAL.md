# Vehicle balancing proposal — private benchmark candidates only

**No changes have been implemented.** The smallest evidence-supported starting point is **five overlapping vehicle families**, rather than a whole-campaign multiplier or a change to performance, dates or roster. Only the ST43 matching-cost target is comparatively straightforward; the remaining targets require callback/reliability and loaded-route qualification. The absolute target points below are economic policy proposals, not extracted historical prices.

Evidence and limitations are in [Phase 2 analysis](VEHICLE_ECONOMY_PHASE2.md). The machine-readable proposal, including evidence, unintended effects and implementation method, is [vehicle_balancing_candidates.csv](research/vehicle_balancing_candidates.csv).

## Economic framework

Use contemporary duty groups and actual complete trains. Preserve the distinction between capital-constrained early operators, operating efficiency, high-speed capability, gradient capacity, loading/refit flexibility and infrastructure demand. Historical improvements may make old engines economically inferior; that is not an error to eliminate. Compare prices in constant GBP at the same settings, but preserve state-dependent running behaviour and meaningful performance trade-offs.

A change should correct a demonstrated choice trap or cost-system discontinuity, not merely move an outlier toward a median. Do not price all horsepower alike, conflate an express power head with a shunter, count liveries as independent prototypes, or treat a quoted annual cost as a billed fixed overhead. Demand and actual loaded route performance remain prerequisites for broad profitability policy.

## Prioritized candidate changes

The verification years and exact base IDs are in the CSV. Running targets refer to the same engine-list callback context as the current verified figure; any source change must then be checked in the actual built train. Values are in GBP under the saved low-cost difficulty and no inflation.

| Priority / vehicle | Current purchase → proposed | Change | Current list running → proposed/year | Change | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 Polish Train Set ST43 | £30,468 → £22,265 | -26.92% | £3,686 → £2,833 | -23.14% | High for discrepancy; medium for matching-cost target |
| 2 Polish Rolling Stock Pack EN57 | £58,593 → £43,359 | -26.00% | £1,068 → £1,068 | 0.00% | High for capital premium; medium for target |
| 3 Polish Rolling Stock Pack EN71 | £83,203 → £63,281 | -23.94% | £1,715 → £1,715 | 0.00% | High for purchase gap; medium/low for target |
| 4 Polish Rolling Stock Pack ED72 | £85,546 → £62,109 | -27.40% | £1,800 → £1,800 | 0.00% | High for duplicate premium; low for the proposed trade-off point |
| 5 Polish Rolling Stock Pack ET21 | £39,843 → £31,640 | -20.59% | £2,109 → £1,968 | -6.69% | High for measured gap; low/medium for target |


For variants/liveries, apply any future change only to economically identical verified members of the intended prototype family. Do not indiscriminately change every name sharing a prefix. Preserve all GRF/local IDs, variant identities, dates, graphics, physics, capacities, refits and reliability behaviour.

The suggested purchase prices respect the current Polish sets' integer property-factor grid: `floor(300000 × factor /256)` under low construction cost and local purchase exponent zero. Proposed effective factors are respectively **19, 37, 54, 53 and 27**. These are economic-property/callback result targets, not literal pound constants to embed in a GRF. If a callback overrides the base property, its economic branch must be changed and retested. Prices under other difficulty settings scale through the normal engine formula.

### 1. Polish Train Set — ST43 (4D560103 / 134)

Evidence: Equal principal stats; equal 120t coal consist capacity and length; actual four-wagon purchase 43592 vs 35389, moving-empty rate 4143 vs 3290.

Expected effect: Remove or reduce an existing duplicate-choice trap without changing performance or dates.

Risk and qualification: Cheaper PTS version competes with adjacent PTS diesels; benchmark these too. Aligning a duplicate does not by itself lower the cheapest option already available.

Method: Targeted source economic property/callback edit; preserve GRFID/local IDs, performance, dates, all variants; cross-GRF override not proven.

### 2. Polish Rolling Stock Pack — EN57 (4D560105 / 1800)

Evidence: Same full built unit capacity and length; identical observed moving rate; PTS comparator already available at target.

Expected effect: Remove or reduce an existing duplicate-choice trap without changing performance or dates.

Risk and qualification: Check mail refits, ageing and model reliability before matching every livery; consider alternative rebuilding cost rather than indiscriminate family-wide scaling.

Method: Targeted source economic property/callback edit; preserve GRFID/local IDs, performance, dates, all variants; cross-GRF override not proven.

### 3. Polish Rolling Stock Pack — EN71 (4D560105 / 2100)

Evidence: Same 364-seat built unit length and observed moving rate; comparator purchase 63281 vs 83203.

Expected effect: Remove or reduce an existing duplicate-choice trap without changing performance or dates.

Risk and qualification: Model reliability differs with seeded engine generation. The two units need repeat breakdown-duty tests before a final target is adopted.

Method: Targeted source economic property/callback edit; preserve GRFID/local IDs, performance, dates, all variants; cross-GRF override not proven.

### 4. Polish Rolling Stock Pack — ED72 (4D560105 / 2200)

Evidence: Both built units 338 seats, same length and observed active rate; PTS speed130 versus PRSP120; current prices66796 versus85546.

Expected effect: Remove or reduce an existing duplicate-choice trap without changing performance or dates.

Risk and qualification: 62109 is a policy test point on the attainable factor53 price grid: about7.0% below the faster comparator, not an extracted fair price. Check route time and demand before adoption.

Method: Targeted source economic property/callback edit; preserve GRFID/local IDs, performance, dates, all variants; cross-GRF override not proven.

### 5. Polish Rolling Stock Pack — ET21 (4D560105 / 570)

Evidence: Same coal capacity, length, hp and weight; PTS stronger333 vs310kN and cheaper purchase/running; four-wagon actual47108/2425 versus52967/2566.

Expected effect: Remove or reduce an existing duplicate-choice trap without changing performance or dates.

Risk and qualification: 31640 is a policy test point on the factor27 price grid, about6.9% below the stronger PTS version; it restores a capital/TE trade-off instead of pricing unequal performance identically.

Method: Targeted source economic property/callback edit; preserve GRFID/local IDs, performance, dates, all variants; cross-GRF override not proven.


## Approaches evaluated in order

1. **Existing parameters:** retain current parameters for the baseline. They are valid coarse controls, but cannot discriminate the opposite-direction ST43/ET21 overlaps or selected MU families. UKRS2 lacks a general purchase slider in its current metadata.
2. **Set-wide purchase/running multipliers:** no blanket adjustment is supported yet. NARS's half-cost option couples purchase and running; reducing high running costs would also halve capital already comparable in some groups. The add-on's independent running scale is more flexible, but halving it again would affect every era, not only an early locomotive. Raising GETS capital would change many unrelated designs and wagons. Require duty- and era-specific route outcomes before choosing such a multiplier.
3. **Targeted source definitions:** preferred for these five candidate families. Edit only economic property values or the applicable economic callback branch, rebuilding a private experimental fork while preserving identity and all non-economic definitions. The common Polish base exponents show that a global base shift is not the whole explanation. Re-test both standalone and complete trains, including nearby competitors in the same set.
4. **Compatibility/balancing GRF:** not approved as a verified arbitrary-property mechanism. JGRPP has engine-scope overrides, but that alone does not prove that a separate ordinary GRF can safely replace these cost properties through callback 0x36 and load order. A minimal private proof would be required before considering it an implementation method. No balancing GRF was created.

General base-cost controls operate by category and/or GRF, not individual engine ID. Their existence is not evidence for an individual-vehicle override capability.

## Hold unchanged for now

- **EU07, ET22, ET41:** same-price TE differences need grade, adhesion, variant and loaded-performance validation. Do not alter their physics or automatically charge a TE premium.
- **Class 66:** the capital gap is verified, but state costs, slightly different performance/length and the unresolved GETS empty-motion result prevent a sufficiently supported full-service target.
- **Planet, Grasshopper, Norris and other early stock:** their role, capital, weight, duty and route revenue trade-offs matter. The early recollection of prices is not used as an anchor, and no broad early-steam change is proposed on that basis.
- **ASF/EL16 battery shunters:** zero listed running cost at 23 hp and speed 6 is a special case worth testing, not sufficient evidence of a mainline exploit.
- **Wagons and coaches:** keep all existing types. Use capacity, usable train length, weight, actual AXIS refits and same-duty complete trains before changing price. A cheaper small coach is not interchangeable with a larger fast one.

## Adoption gate for a later implementation task

Construct matched loaded services with actual AXIS supply and acceptance and timed station orders; include flat and graded cases. Record duty-state expense, cargo packet payments, delivered volume, breakdown/repair cost, finance and allocated infrastructure. Repeat seeded reliability cases and observe vehicle/calendar ageing. Test 5/10/20/30-year cash flows with realistic replacement/resale rather than frozen new-engine rates. Resolve any hidden attachment, heating, powered-wagon or refit differences before treating a cheaper duplicate as an unconditional winner.

For each candidate, accept the change only if it removes the identified choice trap without introducing a new advantage over neighbouring contemporary engines. Re-evaluate the five-family list after those tests: it is a **minimal starting experiment**, not a proof that five changes balance the entire 195-year campaign. No release, production file change, push or merge is part of this proposal.
