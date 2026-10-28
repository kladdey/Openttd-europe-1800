# AXIS Historical Europe modifications, 2026, Openttd-europe-1800 contributors.
# SPDX-License-Identifier: GPL-2.0-only
"""Small model extension; policy lives exclusively in historical_manifest.json."""
import json
from pathlib import Path

MANIFEST = json.loads(Path(__file__).with_name("historical_manifest.json").read_text(encoding="utf-8"))


def condition_for_rule(rule):
    return (
            f"(current_year >= {rule['earliest_year']})"
            + (f" && (current_year <= {rule['final_construction_year']})"
               if rule["final_construction_year"] is not None else "")
            + " && ((extra_callback_info2 == IND_CREATION_GENERATION && "
            + str(int(rule["allow_map_generation"])) + ")"
            + " || (extra_callback_info2 == IND_CREATION_RANDOM && "
            + str(int(rule["allow_natural_and_gs"])) + ")"
            + " || ((extra_callback_info2 == IND_CREATION_FUND || extra_callback_info2 == IND_CREATION_PROSPECT) && "
            + str(int(rule["allow_player_funding_and_prospecting"])) + "))"
    )


def apply_to_industries(industries):
    by_id = {i.id: i for i in industries}
    for identifier, rule in MANIFEST["industries"].items():
        item = by_id[identifier]
        item.historical_rule = rule
        item.historical_condition = condition_for_rule(rule)
    # Reuse an existing disabled-in-Classic industry; no industry/tile ID changes.
    steel = by_id["steel_mill"]
    recipe = MANIFEST["industries"]["steel_mill"]["recipe"]
    classic = steel.economy_variations[MANIFEST["economy"]]
    classic.enabled = True
    classic.name = "string(STR_IND_HISTORICAL_STEELWORKS)"
    classic.accept_cargos_with_input_ratios = [(k, v * 2) for k, v in recipe["inputs"].items()]
    classic.prod_cargo_types_with_output_ratios = [(k, v * 2) for k, v in recipe["outputs"].items()]
    steel.template = "industry_historical_steelworks.pynml"
