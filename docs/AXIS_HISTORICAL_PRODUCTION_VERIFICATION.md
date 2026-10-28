# Transported steel production and save/reload verification

Executed 2026-10-28 with **JGRPP 0.73.4** and AXIS Historical Europe **0.1.0**.
**PASS:** actual vehicle-delivered inputs, no observed steel from pig iron alone,
exact one-input stockpile persistence through a disk save/new process, resumed
steel/slag production and downstream steel delivery.

The NewGRF was **unchanged** from the construction-tested build:
`cd1d5a5a704613469207d726b15c1bec02afff8cb0c2c70b2877c8fe429ecd09`.
No campaign save, map, installed AXIS or transport NewGRF was edited.

## What actually ran

The [production runner](../newgrfs/axis-historical-europe/production_test.py)
created a new flat **256×256** diagnostic heightmap and an **1860** game inside
the ignored `.work/` directory. A GS built six industries, road corridors,
truck stops and five trucks in a test company:

1. Coal mine → coke oven: coal.
2. Iron-ore mine → blast furnace: iron ore.
3. Blast furnace → historical steelworks: pig iron.
4. Coke oven → historical steelworks: coke, withheld until after reload.
5. Historical steelworks → metal workshop: steel.

The upstream processors use their existing AXIS recipes, including partial-input
operation. No cargo was injected, no industry stockpile was directly edited,
and no production-debug cheat replaced vehicle deliveries. Newly funded
industries completed construction before their routes could operate.

Default trucks were explicitly enabled early using the supported
`GSEngine.EnableForCompany` API **only in this disposable company**. The fleet
used DW Coal Truck (coal/coke), Chippy Iron Ore Truck, Goss Goods Truck (pig
iron), and Kelling Steel Truck. This is a diagnostic concession for testing
industry mechanics at 1860, **not proof of historical vehicle availability**.
GETS, UKRS2, Polish Train Set, NARS, eGRVTS and the ship sets were not installed
or modified in this fixture.

## Measured results

| Observation | Engine result |
|---|---|
| Pig iron physically delivered while coke truck remained stopped | **8 IRON**, **0 COKE** in steelworks stockpile |
| Before coke delivery | Completed-month STEL production **0**; monitored steel pickup **0** |
| Disk checkpoint | `partial-stockpile.sav`, saved successfully |
| New engine process loading the checkpoint | Exactly **8 IRON**, **0 COKE** restored; original industry IDs and script state retained |
| Processing after starting the coke truck | **6 STEL**, **2 SLAG** recorded for a completed production month |
| Integer-batch remainder | **2 IRON**, matching `8 mod 3` |
| Actual downstream delivery | **4 STEL** delivered by truck to the metal workshop |

Production and delivery are different measurements: 6 produced and 4 delivered
do not establish that every output unit was transported. The test does not claim
a complete accounting of station-rating effects, cargo waiting or discarded
output. The completed-month steel/slag figures independently confirm the **3:1
production ratio**.

Exact evidence, engine/GRF/checkpoint hashes and log excerpts are in
[production-result.json](../newgrfs/axis-historical-europe/production-result.json).
Full logs and the 78,692-byte checkpoint remain locally under
`newgrfs/axis-historical-europe/.work/production-test/`.

The initial phase was run to a passing disk checkpoint. The reload phase was
then replayed from that checkpoint after improving the observer to retain a
nonzero monthly production reading while waiting for the delivery truck. This
avoids missing a finite batch when its production month rolls out of the
last-month statistic. The GRF, its recipe and the saved stockpiles were not
changed. `--resume` makes that independent reload replay reproducible.

## Reproduce and remaining scope

See the [fixture instructions](../newgrfs/axis-historical-europe/tests/production/README.md).
Use a disposable engine beneath the project's `.work/`; the runner refuses
an engine outside that directory. Run with the pinned build environment:

```powershell
newgrfs/axis-historical-europe/.venv/Scripts/python.exe newgrfs/axis-historical-europe/production_test.py --engine-directory ABSOLUTE_PATH_TO_DISPOSABLE_ENGINE
```

`--resume` replays only the reload phase using this fixture's existing checkpoint
and initial log. A new complete run can take several real minutes for industry
construction and physical transport. A failed run writes `passed: false` and
returns a nonzero process exit status.

This verifies **one representative pig-iron-first batch and save/reload case**,
in addition to the previous 16 construction tests. It does not cover reverse
delivery order, simultaneous unloads, every batch size, byproduct transport,
long-term operation/expiry, human multiplayer, 4096² performance or campaign
vehicle compatibility. The next milestone is a small three-player test with
the actual historical vehicle sets on a separate campaign candidate.
