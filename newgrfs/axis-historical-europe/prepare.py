# SPDX-License-Identifier: GPL-2.0-only
"""Export pinned upstream and apply a small auditable overlay. No install step."""
import argparse
import difflib
import io
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "historical_manifest.json").read_text(encoding="utf-8"))


def replace_once(path, old, new):
    # Preserve upstream line endings so a one-line edit stays a one-line patch.
    text = path.read_bytes().decode("utf-8")
    ending = "\r\n" if "\r\n" in text else "\n"
    old = old.replace("\n", ending)
    new = new.replace("\n", ending)
    if text.count(old) != 1:
        raise RuntimeError(f"Patch context not unique: {path}: {old[:65]!r}")
    path.write_bytes(text.replace(old, new, 1).encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True, help="Trusted AXIS Git checkout (never modified)")
    parser.add_argument("--refresh", action="store_true", help="Recreate only this tool's isolated generated .work/source")
    args = parser.parse_args()
    revision = MANIFEST["upstream_commit"]
    subprocess.run(["git", "-C", str(args.upstream), "cat-file", "-e", revision + "^{commit}"], check=True)
    source = ROOT / ".work/source"
    if source.exists():
        if not args.refresh:
            raise SystemExit("Prepared source already exists; pass --refresh to regenerate the isolated export.")
        if source.is_symlink() or source.resolve() != ROOT / ".work/source":
            raise SystemExit("Unexpected generated-source path; refusing cleanup")
        shutil.rmtree(source)
    archive = subprocess.check_output(["git", "-C", str(args.upstream), "archive", "--format=zip", revision,
                                       "src", "license.pt", "README.md", "Makefile"])
    source.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(archive)) as data:
        data.extractall(source)
    original = {p.relative_to(source).as_posix(): p.read_bytes()
                for p in source.rglob("*") if p.is_file()}
    # Upstream iterates a set of industry objects, whose order depends on memory
    # addresses. Sort those commutative siting checks for reproducible GRF bytes.
    replace_once(source / "src/industry.py", "for industry in set(incompatible_industries[self.industry]):",
                 "for industry in sorted(set(incompatible_industries[self.industry]), key=lambda item: item.numeric_id):")
    for name in ["historical_availability.py", "historical_manifest.json"]:
        shutil.copyfile(ROOT / ("overlay/" + name if name.endswith(".py") else name), source / "src" / name)
    for name in ["historical_availability.pynml", "historical_location.pynml", "produce_historical_steelworks.pynml"]:
        shutil.copyfile(ROOT / "overlay" / name, source / "src/templates" / name)
    init = source / "src/industries/__init__.py"
    with init.open("a", encoding="utf-8", newline="\n") as out:
        out.write("\n# AXIS Historical Europe overlay (GPL-2.0-only).\nfrom industries import steel_mill\n# The upstream file exists but its registration was commented out.\n# Enable it ONLY in Classic; do not activate it in upstream's unused economies.\nfor variation in steel_mill.industry.economy_variations.values():\n    variation.enabled = False\nsteel_mill.industry.economy_variations['BASIC_TEMPERATE'].enabled = True\nsteel_mill.industry.register()\nfrom historical_availability import apply_to_industries\napply_to_industries(registered_industries)\n")
    header = source / "src/templates/header.pynml"
    replace_once(header, 'grfid: "JK\\88\\08";', f'grfid: "{MANIFEST["nml_grfid"]}";')
    replace_once(header, 'version: ${git_info.get_revision()};', f'version: {MANIFEST["grf_version"]};')
    replace_once(header, 'min_compatible_version: 6745;', 'min_compatible_version: 1;')
    replace_once(header, '\tparam 0 {', '''    param 10 {
        historical_europe_mode {
            name: string(STR_PARAM_HISTORICAL_EUROPE);
            desc: string(STR_PARAM_HISTORICAL_EUROPE_DESC);
            type: bool;
            def_value: 1;
        }
    }
\tparam 0 {''')
    available = source / "src/templates/availability.pynml"
    replace_once(available, '${industry.id}_check_availability, economy)', '${industry.id}_check_availability_upstream, economy)')
    with available.open("a", encoding="utf-8") as out:
        out.write('\n<tal:include metal:use-macro="load: historical_availability.pynml" />\n')
    location = source / "src/templates/location_check_macros_industry.pynml"
    replace_once(location, '${industry.id}_check_location,\n', '${industry.id}_check_location_upstream,\n')
    with location.open("a", encoding="utf-8") as out:
        out.write('\n<tal:include metal:use-macro="load: historical_location.pynml" />\n')
    secondary = (source / "src/templates/industry_secondary.pynml").read_text(encoding="utf-8")
    secondary = secondary.replace('load: produce_secondary.pynml', 'load: produce_historical_steelworks.pynml')
    for callback in ['produce_cargo_arrival', 'produce_256_ticks']:
        secondary = secondary.replace('${industry.id}_' + callback + ';',
            "${'historical_steelworks_batch' if economy.id == 'BASIC_TEMPERATE' else industry.id + '_" + callback + "'};")
    secondary = secondary.replace('${industry.id}_extra_text;',
        "${'return string(STR_HISTORICAL_STEELWORKS_RECIPE)' if economy.id == 'BASIC_TEMPERATE' else industry.id + '_extra_text'};")
    secondary = secondary.replace('${industry.id}_cargo_subtype_display;',
        "${'return CB_RESULT_NO_TEXT' if economy.id == 'BASIC_TEMPERATE' else industry.id + '_cargo_subtype_display'};")
    secondary = secondary.replace('${industry.get_extra_text_fund(economy)};',
        "${'return string(STR_HISTORICAL_STEELWORKS_FUND)' if economy.id == 'BASIC_TEMPERATE' else industry.get_extra_text_fund(economy)};")
    (source / "src/templates/industry_historical_steelworks.pynml").write_text(secondary, encoding="utf-8")
    names = source / "src/lang_templates/english.pylng"
    replace_once(names, ':AXIS 2.3.1', ':AXIS Historical Europe 0.1.0 (AXIS 2.3.1 base)')
    replace_once(names, ':https://github.com/EmperorJake/AXIS', ':https://github.com/kladdey/Openttd-europe-1800')
    years = {name: rule["earliest_year"] for name, rule in MANIFEST["industries"].items()}
    recipe = MANIFEST["industries"]["steel_mill"]["recipe"]
    with names.open("a", encoding="utf-8") as out:
        out.write(f'''
STR_PARAM_HISTORICAL_EUROPE :Historical Europe steelmaking dates (Classic only)
STR_PARAM_HISTORICAL_EUROPE_DESC :Default on. Steelworks from {years['steel_mill']}, EAF from {years['electric_arc_furnace']}, BOF from {years['basic_oxygen_furnace']}. Off disables added date/route restrictions, not original AXIS dates. Natural and deity GameScript construction share permission. New games only.
STR_IND_HISTORICAL_STEELWORKS :Nineteenth-century Steelworks
STR_HISTORICAL_STEELWORKS_RECIPE :Stockpiles both inputs. Each complete batch: {recipe['inputs']['IRON']} pig iron + {recipe['inputs']['COKE']} coke yields {recipe['outputs']['STEL']} steel + {recipe['outputs']['SLAG']} slag. No output from either input alone.
STR_HISTORICAL_STEELWORKS_FUND :Historical mode: new construction from {years['steel_mill']}. Existing works keep operating.
''')
    incompatible = source / "src/incompatible_grfs.py"
    with incompatible.open("a", encoding="utf-8") as out:
        out.write('\nIncompatibleGRF(DwordGrfID("4A4B8808"), "Original AXIS (use only one AXIS variant)")\n')
    diff = []
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        name = path.relative_to(source).as_posix()
        old, new = original.get(name, b""), path.read_bytes()
        if old != new:
            for line in difflib.unified_diff(old.decode("utf-8").splitlines(True), new.decode("utf-8").splitlines(True),
                                             fromfile="a/" + name, tofile="b/" + name):
                diff.append(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n")
    # Do not translate newlines: upstream has CRLF source and a missing final
    # newline in incompatible_grfs.py. A text-mode rewrite corrupts that patch.
    (ROOT / "source-changes.patch").write_text("".join(diff), encoding="utf-8", newline="")
    print(f"Prepared pinned source in {source}; original checkout unchanged")


if __name__ == "__main__":
    main()
