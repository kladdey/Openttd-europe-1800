# AXIS Historical Europe — cargo and chain validation

2026-10-28, milestone 0.1.0. See
[implementation](AXIS_HISTORICAL_IMPLEMENTATION.md) for the exact source and
binary hashes. The audit compares the modified source with a pristine export
of AXIS 2.3.1, not with a newer upstream version.

## Cargo compatibility

The executed validator is
[validate.py](../newgrfs/axis-historical-europe/validate.py).
It loads both sets' original Python models in separate processes, using the
real dependencies. It compares every economy's ordered cargo IDs and labels,
every original enabled industry's properties, input/output lists, local ID and
layouts, then checks the compiled GRF cargo assignments against a separately
compiled unmodified baseline.

| Check | Result |
|---|---|
| Classic active cargo slots | **64 before / 64 after** |
| Ordered Classic cargo ID/label list | Identical |
| Ordered cargo lists of all other economy definitions | Identical |
| Emitted binary cargo slot/label records over all branches | **320 records, identical sequence** |
| Classic original industry model records | **All 91 preserved** |
| Classic new enabled industry | `steel_mill`, existing local ID 2; total **92** |
| Other enabled economy models | Identical, including recipes, dates and layouts |
| Source graphics, cargo/economy definitions and individual industry-definition modules (excluding registration `__init__.py`) | Unchanged bytes |
| GRFID and version | Intentionally changed; original save identity is **not** preserved |

The three complete economies have 64 cargoes each. The other upstream economy
definitions have 19, 49 and 29; these remain unchanged, rather than being
artificially expanded to 64. All-economy model equality covers those definitions
too, but they were not individually loaded into the game in this test.

The engine actually reported **64 cargoes and 92 industry types** in each tested
Classic world. This confirms the fork loaded the intended economy. It does
not establish vehicle-set refit compatibility: GETS, UKRS2, Polish Train Set,
NARS, eGRVTS and the ship sets were not installed in the isolated test engine.
Preserving labels, slots and cargo classes avoids introducing a new cargo
compatibility change, but those transport sets still require their own audit.

## Steelworks recipe and relationships

Upstream dormant `steel_mill.py` specifies ore, coke, limestone, acetic acid and
oxygen → `STEL`, but its registration is commented out, so that recipe was **not
part of the 91-type Classic baseline**. Re-enabling it unchanged would demand
cargoes absent from Classic. The fork registers the existing definition only
in Classic and uses the existing `IRON`, `COKE`, `STEL` and `SLAG` labels.

| Cargo | Existing producers | Consumers after the addition |
|---|---|---|
| `IRON` (pig iron) | `blast_furnace` | `iron_works`, `basic_oxygen_furnace`, new `steel_mill` |
| `COKE` | `coke_oven`, `ethylene_cracker` | `blast_furnace`, `aluminium_plant`, `cement_plant`, `pyrite_smelter`, new `steel_mill` |
| `STEL` | EAF, BOF; now also `steel_mill` | `metal_workshop`, `assembly_plant`, `sheet_and_pipe_mill`, `bulk_terminal` |
| `SLAG` | Blast furnace, aluminium/copper processing, EAF/BOF; now also `steel_mill` | `slag_grinding_plant` |

The nineteenth-century upstream path is coal → coke oven; ore + coke + limestone
→ blast furnace → pig iron; pig iron + coke → historical steelworks → steel.
Downstream metal parts/building materials and the slag chain retain their
original labels and recipes. Aluminium and other modern factories remain
available under AXIS's original policy; this milestone gates steelmaking only.

The new callback implements complete integer stockpile batches, independently
of AXIS's generic partial-input efficiency system:

| Pig iron waiting | Coke waiting | Consumed IRON/COKE | Produced STEL/SLAG | Remaining IRON/COKE |
|---|---|---|---|---|
| 0 | 100 | 0 / 0 | 0 / 0 | 0 / 100 |
| 300 | 0 | 0 / 0 | 0 / 0 | 300 / 0 |
| 300 | 100 | 300 / 100 | 300 / 100 | 0 / 0 |
| 5 | 2 | 3 / 1 | 3 / 1 | 2 / 1 |
| 2 | 1 | 0 / 0 | 0 / 0 | 2 / 1 |
| 6 | 1 | 3 / 1 | 3 / 1 | 3 / 0 |

These cases execute the expressions extracted from **generated NML**, and the
whole GRF compiles and loads. They are **not measurements of engine-delivered
cargo**; the transport/production test remains in the manual test plan. The
recipe intentionally simplifies heat, air, flux and metallurgical yield. It
must not be presented as a literal Bessemer chemical equation.

EAF and BOF cargo relationships are unchanged. Their availability dates change
construction only. No existing customer is removed or relabelled.

## Reachability and limits

The validator constructs producer/consumer indexes and a cargo-reachability
fixed point. Baseline primary/port/town producers seed the graph; ordinary
AXIS processors permit partial-input operation, while the new works explicitly
requires **both** pig iron and coke. Town passenger/mail sources are included.

Result: **64 reachable Classic labels before / 64 after; no newly unreachable
label and no missing input/output counterpart for the new works**. The detailed
lists and relationship indexes are recorded in
[validation-result.json](../newgrfs/axis-historical-europe/validation-result.json).
The original 91-type extracted matrix is cross-checked record by record.

This is an **all-types structural check**, not a guarantee of a viable 1830
transport economy. It does not model finite capacities, vehicle availability,
geographic accessibility, station catchments or the exact initial scenario.
It also accepts AXIS import ports as real on-map baseline producers. Those
ports can supply modern cargoes; that remains a historical compromise outside
this milestone. Some recipes/outputs are reachable only in later periods.

Before 1860 there is no enabled steel-producing type under the new three date
gates; nineteenth-century crucible steel is not yet represented. Steel-dependent
businesses can therefore be starved of steel in a strictly curated early map.
This is an explicit residual design gap, not hidden as a successful early-chain
test. The next milestone should decide whether early specialized steel/imports
are needed before gating more downstream sectors.

No production dead end was introduced into the full Classic graph. Actual
batch processing, byproduct transport, save/reload and three-company balance
still need in-game transport testing. No full economic balance or historical
regional viability claim is made.
