# Reverse audit: conclusions traced back to inputs

Audit date: 2026-10-26. Scope: the current V11 export and comparisons, the heightmap
identity claim, and the recent inland diagnostics. This is an adversarial offline
check, not an OpenTTD test or certification of historical geography.

## Findings and fixes

| ID | Severity | Finding | Outcome |
|---|---|---|---|
| RA-01 | Medium | The inland tool recorded a model hash but did not enforce the claimed frozen model. An edited model could still produce a report labelled V6. | Enforce the exact V6 model hash before projection; mutation test rejects a one-pixel coefficient change. |
| RA-02 | Medium | River overlays trusted the generated reference-audit CSV without pinning it or recomputing its target from the historic-site reference. Stale or duplicate rows could mark a wrong pixel. | Pin reference inputs, reject duplicate IDs, verify town/hold/model identity, recompute normalized and exact importer targets, and recheck elevation and both terrain types. |
| RA-03 | Low | The minimum spacing report uses a legacy 4096-scaled normalized metric, which differs from both 4095-scaled coordinates and actual float32/truncated importer targets. | Report all three explicitly; current nearest pair remains above 15 tiles in all metrics. Earlier versioned reports are preserved. |
| RA-04 | Low | River-overlay markers were drawn at a pixel corner, with a hardcoded scale factor of five. | Center markers on their importer pixels and derive display scaling from each window size; new images are stored in inland_v2. |
| RA-05 | Limitation | Reproducible model-guided lake identification and generalized river geometry are not independent survey validation. | Retain the limitation and all bank/terrain holds; no geographic accuracy claim or town translation is authorized by these diagnostics. |

The two medium findings are validation gaps; this audit did **not** discover that
the committed model or held V11 target rows were actually corrupted. The fixes
prevent those faults from silently passing later. Source assets, master records,
all town coordinates, prior experiment outputs and NewGRFs are unchanged.

## Backward checks on the export

The new `scripts/reverse_audit.py` starts with the exported JSON and compares it
with the master and decision records. It does not call the placement generator,
its eligibility logic or its importer helper. Its scalar float32 implementation
uses Python's `struct` independently of the production NumPy implementation.
It shares the existing read-only binary scenario decoder and preserved-asset hash
manifest; this is therefore not an independently implemented binary-file parser.

Results:

- All **600** decision rows account for the hash-preserved master, including
  population and city metadata; all **537** candidate records match the retained set.
- All 537 exact importer targets have nonzero original elevation and clear terrain
  in **both** supplied scenarios. Recorded target columns, rows, types, elevation,
  flatness and normalized coordinates agree with recomputation.
- **132** candidate targets have non-flat corner heights in at least one scenario.
- All **49** retained pairs within 30 tiles under either physical spacing metric
  have documented reviews. No retained pair falls below 15 tiles.
- Both **564**- and **576**-town comparisons pass membership, bounds, metadata,
  coordinate and count checks. Their terrain conflicts remain intentionally present;
  these are comparison imports, not clear-target candidates.
- **63** deferrals remain: 27 terrain, 11 spacing, 24 outside-map, 1 identity.
- All recorded V11 input hashes and original PNG/scenario hashes match.
- Repeating the archived package comparison reproduces the committed provenance
  report exactly, including all **16,777,216 RGBA pixels**. This establishes the
  distributed image identity, not the upstream DEM or original projection.

[Machine-readable result](candidate_summary.json),
[all candidate targets and nearest actual neighbours](candidate_reverse_audit.csv),
[all close pairs](candidate_close_pairs.csv),
[provenance recheck](provenance_recheck.json), and
[findings CSV](findings.csv).

### Manchester–Oldham spacing

| Metric | Minimum (tiles), Manchester–Oldham |
|---|---:|
| Legacy normalized separation × 4096, used in the V11 summary | 16.221519 |
| Normalized separation × 4095, image/importer span | 16.217558 |
| Actual integer targets after float32 parsing and truncation | 15.620499 |

The difference is not evidence of a geographic correction. Actual target spacing
is the relevant distance between founded target tiles; later town growth and
infrastructure room still need OpenTTD. No arbitrary town count is introduced.

## Hardened inland replay

[Inland V2](../inland_v2/README.md) preserves the same ten lake observations, seven
diagnostic comparisons, two open bank holds and all prior geometric conclusions.
The summary now records enforced reference-input hashes, and the river image uses
pixel-centered markers. V1's historical artifacts are preserved. Lake plateaus
remain inset from generalized outlines; centroid differences must not move towns.

## Reproduce and challenge the checks

```powershell
python -m pip install -r requirements-visualization.txt
python scripts/reverse_audit.py --out scratch/reverse-audit
python scripts/validate_inland_features.py --out scratch/inland-v2
python -W error::ResourceWarning -m unittest discover -s tests -v
```

Use new output directories. The reverse checker exits nonzero when it records an
error. It checks original hashes before decoding terrain; it does not write a
scenario, modify an import or require network access. The optional archive-based
provenance replay uses the separately downloaded package and the command documented
in [the provenance report](../provenance_v1/README.md).

Eight new regression tests deliberately introduce metadata changes, missing towns,
invalid coordinates, duplicate names, stale target reports, saved-water targets,
false counts, unreviewed close pairs, changed comparison exports, edited model
coefficients, duplicate bank references and stale bank pixels. Full suite:
**67 Python tests passed**, with ResourceWarnings treated as errors.

## Remaining uncertainties

Historical site identification, river banks, original DEM/CRS and every town's
real-world registration are not certified by this audit. Source population values
are preserved, not independently validated as 1800 census measurements. Neither
clear terrain nor passing spacing checks guarantees founding, growth or playability.
All **27** terrain cases remain open. Arles and Alençon still require stronger local
bank/channel evidence; generalized river centerlines do not resolve their holds.
