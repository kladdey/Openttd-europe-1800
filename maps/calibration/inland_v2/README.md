# Inland V2 — dependency checks and marker correction

This is the hardened replay of [inland V1](../inland_v1/README.md) following the
[reverse audit](../reverse_audit_v1/README.md). The ten lake observations, geometry
subsets and frozen model are unchanged. Seven descriptive lake comparisons and
both river-bank holds remain; no town coordinates or placement decisions change.

The tool now enforces the exact V6 model hash and both V11 reference-input hashes,
rejects duplicate references, and recomputes held importer targets and their terrain
samples before rendering. River markers are centered on importer pixels, with
scaling calculated from the window dimensions. V1 outputs are retained unchanged.

- [Lake diagnostics CSV](inland_shape_audit.csv) and [contact sheet](inland_contact_sheet.png).
- [River review CSV](river_bank_review.csv) and [overlays](river_bank_overlays.png).
- [Summary and enforced input hashes](summary.json).

From the repository root, choose an output directory that does not exist:

```powershell
python scripts/validate_inland_features.py --out scratch/inland-v2
python -W error::ResourceWarning -m unittest discover -s tests -v
```

All V1 source and interpretation limits continue to apply. Plateau-to-outline
centroid differences are not town-position errors. Generalized river lines do not
identify saved channels or establish historical river banks. No founding tests ran.
