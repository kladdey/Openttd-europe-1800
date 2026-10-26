# Validation record

2026-10-26, Python in the shared Linux workspace; target game is Windows
JGRPP 0.73.4. No game executable was run and no scenario was resaved.

```text
python -W error::ResourceWarning -m unittest discover -s tests -v
14 tests: PASS, no skips with the supplied source assets and dependencies.
```

Actual-source checks read the uploaded 4096×4096 PNG and both original
scenarios. Every retained target has nonzero original red-channel elevation
and saved type-zero clear land in both scenarios. Inputs retain their
original SHA-256 hashes. Master population/city flags and all 600 catalogue
entries are preserved; V2 anchors and V3/V4 experiments remain unchanged.

The coastline calibration was regenerated in another fresh directory with
the same inputs and libraries. All previously generated V6 files matched
byte for byte; the final V4 evidence CSV additionally includes inverse-model
geographic estimates and connected-raster landmass labels. These estimates
make geographic discrepancies reviewable and are not surveyed positions.

Passing tests establish code behaviour, arithmetic, data integrity and
target-tile terrain checks. They do not establish exact source projection,
correct historical town centres, in-game founding success or town-growth
behaviour. Those remain explicit release blockers in README.md.
