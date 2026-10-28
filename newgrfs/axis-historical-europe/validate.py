# SPDX-License-Identifier: GPL-2.0-only
"""Source/model/generated-NML and compiled identity audit, not an engine test."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "validation-result.json"


def grf_sprites(path):
    data = path.read_bytes()
    assert data[:10] == b"\x00\x00GRF\x82\r\n\x1a\n"
    assert data[14] == 0, "Only uncompressed v2 container is supported"
    pos = 15
    while True:
        length = int.from_bytes(data[pos:pos + 4], "little")
        pos += 4
        if length == 0:
            break
        kind = data[pos]
        pos += 1
        if kind == 0xFF:
            yield data[pos:pos + length]
        pos += length


def read_cargo_definitions(sprites):
    """Read Action0 cargo properties, retaining all branch definitions in order.

    The source-model check establishes the economy→slot mapping; this checks
    the emitted binary slot/label assignments too, without interpreting Action7.
    """
    from nml.actions.action0properties import properties
    sizes = {v["num"]: v["size"] for v in properties[0x0B].values()}
    sizes[0x1A] = 1  # compiler-generated callback flags
    found = []
    for sprite in sprites:
        if sprite[:2] != b"\x00\x0b":
            continue
        count, items, first = sprite[2:5]
        pos = 5
        if first == 255:
            first = int.from_bytes(sprite[pos:pos + 2], "little")
            pos += 2
        for _ in range(count):
            prop = sprite[pos]
            pos += 1
            size = sizes[prop]
            for index in range(items):
                value = sprite[pos:pos + size]
                pos += size
                if prop == 0x17:
                    found.append([first + index, value.decode("ascii")])
        assert pos == len(sprite)
    return found


def condition_allows(condition, year, route, mode=1, economy=0):
    values = {"IND_CREATION_GENERATION": 0, "IND_CREATION_RANDOM": 1,
              "IND_CREATION_FUND": 2, "IND_CREATION_PROSPECT": 3,
              "current_year": year, "extra_callback_info2": route,
              "historical_europe_mode": mode, "economy": economy}
    condition = re.sub(r"!(?!=)", " not ", condition).replace("&&", " and ").replace("||", " or ")
    return bool(eval(condition, {"__builtins__": {}}, values))


def run_snapshot(source, output):
    with output.with_suffix(".log").open("w", encoding="utf-8") as log:
        subprocess.run([sys.executable, str(ROOT / "model_snapshot.py"), str(source), str(output)],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    return json.loads(output.read_text(encoding="utf-8"))


def reachable_cargos(industries):
    reachable = {"PASS", "MAIL"}  # town-generated cargo sources
    previous = None
    while reachable != previous:
        previous = reachable.copy()
        for identifier, item in industries.items():
            primary = item["model_class"].startswith(("IndustryPrimary", "IndustryTownProducer"))
            ready = primary or bool(set(item["inputs"]) & reachable)
            if identifier == "steel_mill":
                ready = {"IRON", "COKE"} <= reachable
            if ready:
                reachable.update(cargo for cargo, amount in item["outputs"])
    return reachable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "historical_manifest.json").read_text(encoding="utf-8"))
    base = ROOT / ".work/baseline"
    if not base.exists():
        archive = subprocess.check_output(["git", "-C", str(args.upstream), "archive", "--format=zip",
                                           manifest["upstream_commit"], "src", "license.pt", "README.md"])
        base.mkdir(parents=True)
        with zipfile.ZipFile(io.BytesIO(archive)) as data:
            data.extractall(base)
    source = ROOT / ".work/source"
    before = run_snapshot(base, ROOT / ".work/baseline-model.json")
    after = run_snapshot(source, ROOT / ".work/historical-model.json")
    classic = "BASIC_TEMPERATE"
    assert len(before[classic]["industries"]) == 91
    assert len(after[classic]["industries"]) == 92
    before_reachable = reachable_cargos(before[classic]["industries"])
    after_reachable = reachable_cargos(after[classic]["industries"])
    assert before_reachable <= after_reachable
    for economy, original in before.items():
        changed = after[economy]
        assert changed["cargo_ids"] == original["cargo_ids"]
        assert changed["cargo_labels"] == original["cargo_labels"]
        if economy == classic:
            assert len(changed["cargo_labels"]) == 64
        if economy != classic:
            assert changed == original, economy
        else:
            assert set(changed["industries"]) - set(original["industries"]) == {"steel_mill"}
            for identifier, item in original["industries"].items():
                assert changed["industries"][identifier] == item, identifier
    matrix = json.loads((ROOT.parents[1] / "docs/research/axis-2.3.1-extreme-classic.json").read_text())
    for record in matrix["industries"]:
        item = after[classic]["industries"][record["id"]]
        assert item["local_id"] == record["local_id"]
        assert item["inputs"] == record["inputs"] and item["outputs"] == record["outputs"]
    steel = after[classic]["industries"]["steel_mill"]
    assert steel["local_id"] == 2 and steel["inputs"] == ["IRON", "COKE"]
    assert steel["outputs"] == [["STEL", 6], ["SLAG", 2]]

    # No upstream artwork, cargo code, economy ordering or industry definitions changed.
    allowed_source_changes = {"src/industry.py", "src/industries/__init__.py", "src/templates/header.pynml",
                              "src/templates/availability.pynml", "src/templates/location_check_macros_industry.pynml",
                              "src/lang_templates/english.pylng", "src/incompatible_grfs.py"}
    changed_paths = []
    for path in (base / "src").rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(base)
        if path.read_bytes() != (source / relative).read_bytes():
            changed_paths.append(relative.as_posix())
    assert set(changed_paths) == allowed_source_changes, changed_paths
    generated = source / "generated/nml"
    truth_checks = 0
    sys.path.insert(0, str(source / "src"))
    from historical_availability import condition_for_rule
    synthetic = {"earliest_year": 1860, "final_construction_year": 1900,
                 "allow_map_generation": False, "allow_natural_and_gs": True,
                 "allow_player_funding_and_prospecting": False}
    synthetic_condition = condition_for_rule(synthetic)
    for year in [1859, 1860, 1900, 1901]:
        for route in range(4):
            assert condition_allows(synthetic_condition, year, route) == (1860 <= year <= 1900 and route == 1)
    for identifier, rule in manifest["industries"].items():
        nml = (generated / (identifier + ".nml")).read_text(encoding="utf-8")
        for callback in ["availability", "location"]:
            expression = re.search(r"switch\(FEAT_INDUSTRIES, SELF, " + identifier
                                   + r"_check_" + callback + r",\s*(.*?)\) \{", nml, re.S).group(1)
            # Regex removes the switch's closing parenthesis, leaving the condition intact.
            assert identifier + "_check_" + callback + "_upstream;" in nml
            for year in [1830, 1850, 1860, 1900, 1950, 1955, 2000,
                         rule["earliest_year"] - 1, rule["earliest_year"], rule["earliest_year"] + 1]:
                for route in range(4):
                    assert condition_allows(expression, year, route) == (year >= rule["earliest_year"])
                    assert condition_allows(expression, year, route, mode=0)
                    assert condition_allows(expression, year, route, economy=5)
                    truth_checks += 3
    steel_nml = (generated / "steel_mill.nml").read_text(encoding="utf-8")
    assert "produce_cargo_arrival:    historical_steelworks_batch;" in steel_nml
    assert "produce_256_ticks:        historical_steelworks_batch;" in steel_nml
    produce = re.search(r"produce\(historical_steelworks_batch,(.*?)\], 0\)", steel_nml, re.S).group(1)
    expressions = re.findall(r"(IRON|COKE|STEL|SLAG): (.*?);", produce)
    assert len(expressions) == 4
    recipe_checks = []
    for iron, coke, expected in [(0, 100, [0, 0, 0, 0]), (300, 0, [0, 0, 0, 0]),
                                  (300, 100, [300, 100, 300, 100]), (5, 2, [3, 1, 3, 1]),
                                  (2, 1, [0, 0, 0, 0]), (6, 1, [3, 1, 3, 1])]:
        actual = [eval(expr.replace(" / ", " // "), {"__builtins__": {}},
                       {"min": min, "incoming_cargo_waiting": lambda cargo: {"IRON": iron, "COKE": coke}[cargo]})
                  for cargo, expr in expressions]
        assert actual == expected, (iron, coke, actual)
        recipe_checks.append({"stockpile": [iron, coke], "consumed_and_produced": actual})
    # Baseline compile is useful to compare actual emitted cargo assignments.
    baseline_grf = ROOT / ".work/baseline.grf"
    if not baseline_grf.exists():
        for label, command in [
            ("lang", [sys.executable, "src/render_lang.py"]),
            ("nml", [sys.executable, "src/render_nml.py"]),
            ("compile", [sys.executable, "-m", "nml.main", "-c", "-l", "generated/lang", "--verbosity=3",
                         "--grf=" + str(baseline_grf), "generated/firs.nml"])]:
            print("baseline-" + label, flush=True)
            with (ROOT / ".work" / ("baseline-" + label + ".log")).open("w", encoding="utf-8") as log:
                subprocess.run(command, cwd=base, stdout=log, stderr=subprocess.STDOUT, check=True)
    artifact = ROOT / "dist/axis-historical-europe-0.1.0.grf"
    sprites = list(grf_sprites(artifact))
    action8 = [s for s in sprites if s[:1] == b"\x08"]
    assert len(action8) == 1 and action8[0][2:6] == b"KHE1"
    assert b"AXIS Historical Europe 0.1.0" in action8[0]
    # Action14 binary VRSN node has little-endian length=4, value=1.
    assert any(b"BVRSN\x04\x00\x01\x00\x00\x00" in s for s in sprites if s[:1] == b"\x14")
    cargo_binary = read_cargo_definitions(sprites)
    assert cargo_binary and cargo_binary == read_cargo_definitions(grf_sprites(baseline_grf))

    producers, consumers = {}, {}
    for identifier, item in after[classic]["industries"].items():
        for cargo, amount in item["outputs"]:
            producers.setdefault(cargo, []).append(identifier)
        for cargo in item["inputs"]:
            consumers.setdefault(cargo, []).append(identifier)
    for cargo in ["IRON", "COKE"]:
        assert producers[cargo]
    assert consumers["STEL"] and consumers["SLAG"]
    report = {
        "passed": True, "upstream_commit": manifest["upstream_commit"], "classic_industries": [91, 92],
        "cargo_slots": 64, "all_economy_cargo_orders_unchanged": True,
        "other_economies_identical_enabled_models": True,
        "all_original_classic_industries_unchanged_models": True,
        "binary_grfid": "4B484531", "binary_version": 1,
        "binary_cargo_slot_label_records_identical": len(cargo_binary),
        "generated_nml_gate_truth_checks": truth_checks, "recipe_tests": recipe_checks,
        "optional_final_year_and_route_mask_checks": 16,
        "graph_reachable_cargo_labels_before": sorted(before_reachable),
        "graph_reachable_cargo_labels_after": sorted(after_reachable),
        "unreachable_cargo_labels_after": sorted(set(after[classic]["cargo_labels"]) - after_reachable),
        "upstream_modified_paths": sorted(changed_paths),
        "cargo_relationships": {c: {"producers": producers.get(c, []), "consumers": consumers.get(c, [])}
                                for c in ["IRON", "COKE", "STEL", "SLAG"]},
        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "runtime_tested_by_this_validator": False,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
