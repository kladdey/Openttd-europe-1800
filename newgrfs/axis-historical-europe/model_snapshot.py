# SPDX-License-Identifier: GPL-2.0-only
"""Evaluate trusted upstream models in a separate process, without renderer stubs."""
import json
import os
from pathlib import Path
import sys

source, output = (Path(p).resolve() for p in sys.argv[1:3])
sys.path.insert(0, str(source / "src"))
os.chdir(source)
import firs

cargos = {c.id: c for c in firs.registered_cargos}
snapshot = {}
for economy in firs.registered_economies:
    industries = {}
    for item in firs.registered_industries:
        if not item.get_property("enabled", economy):
            continue
        industries[item.id] = {
            "local_id": item.numeric_id, "model_class": type(item).__name__,
            "inputs": item.get_accept_cargo_types(economy), "outputs": item.get_prod_cargo_types(economy),
            "properties": {k: item.get_property(k, economy) for k in vars(item.default_industry_properties)},
            "layouts": [vars(layout) for layout in item.industry_layouts],
        }
    snapshot[economy.id] = {
        "numeric_id": economy.numeric_id,
        "cargo_ids": economy.cargo_ids,
        "cargo_labels": [cargos[c].cargo_label for c in economy.cargo_ids],
        "industries": industries,
    }
output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
