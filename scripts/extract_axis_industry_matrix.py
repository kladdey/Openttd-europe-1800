"""Extract AXIS model metadata, without rendering/building a GRF.

Run against a disposable upstream checkout at the recorded release commit.
Only the unavailable renderer and messaging module are stubbed; industry and
economy inheritance and cargo methods execute unchanged. Never use on untrusted
Python sources. This does not validate the compiled GRF or production callbacks.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import types

RELEASE = "11c8353ccf7444b143e57080b1aa2b5e38839a23"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != RELEASE:
        raise SystemExit("Expected AXIS 2.3.1 release commit " + RELEASE)
    sys.path.insert(0, str(source / "src"))
    renderer = types.ModuleType("chameleon")
    renderer.PageTemplateLoader = lambda *a, **kw: None
    sys.modules["chameleon"] = renderer
    utils = types.ModuleType("utils")
    utils.echo_message = lambda *a, **kw: None
    sys.modules["utils"] = utils
    os.chdir(source)
    # Match upstream initialization order (the modules have circular imports).
    from industries import registered_industries
    from economies import registered_economies
    economy = next(e for e in registered_economies if e.id == "BASIC_TEMPERATE")
    rows = []
    for item in sorted(registered_industries, key=lambda i: i.numeric_id):
        if not item.get_property("enabled", economy):
            continue
        rows.append(dict(
            id=item.id, local_id=item.numeric_id, model_class=type(item).__name__,
            inputs=item.get_accept_cargo_types(economy),
            outputs=item.get_prod_cargo_types(economy),
            intro_year=item.get_intro_year(economy), expiry_year=item.get_expiry_year(economy),
            input_ratios=item.get_property("accept_cargos_with_input_ratios", economy),
            combined_cargos_boost_prod=getattr(item, "combined_cargos_boost_prod", None),
            prob_in_game=item.get_property("prob_in_game", economy),
            source="src/industries/" + item.id + ".py"))
    assert len({r["local_id"] for r in rows}) == len(rows)
    assert next(r for r in rows if r["id"] == "coal_mine")["local_id"] == 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(source_commit=revision, economy=economy.id,
                                     cargo_count=len(economy.cargo_ids), industries=rows), indent=2) + "\n", encoding="utf-8")
    print(f"Extracted {len(rows)} industries; {len(economy.cargo_ids)} cargo slots -> {output}")


if __name__ == "__main__":
    main()
