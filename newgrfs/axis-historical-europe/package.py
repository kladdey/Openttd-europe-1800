# SPDX-License-Identifier: GPL-2.0-only
"""Bundle complete corresponding source locally; publish nothing."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import zipfile
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
VERSION = json.loads((ROOT / 'historical_manifest.json').read_text())['version']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-rebuild", action="store_true")
    args = parser.parse_args()
    artifact = ROOT / f"dist/axis-historical-europe-{VERSION}.grf"
    report = json.loads((ROOT / "validation-phase5-result.json").read_text())
    if not report["passed"] or report["artifact_sha256"] != hashlib.sha256(artifact.read_bytes()).hexdigest():
        raise SystemExit("Build and validate matching artifact before packaging")
    source = ROOT / ".work/source"
    bundle = ROOT / f"dist/axis-historical-europe-{VERSION}-source.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as out:
        for name in ["src", "license.pt", "README.md", "Makefile"]:
            target = source / name
            files = sorted(target.rglob("*")) if target.is_dir() else [target]
            for path in files:
                if path.is_file() and "__pycache__" not in path.parts:
                    out.write(path, "source/" + path.relative_to(source).as_posix())
        for path in sorted(ROOT.iterdir()):
            if (path.is_file() and not path.name.endswith("-result.json")
                    and path.suffix in {".py", ".json", ".txt", ".md", ".patch"}):
                out.write(path, "project/" + path.name)
        for folder in ["overlay", "tests"]:
            for path in sorted((ROOT / folder).rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    out.write(path, "project/" + path.relative_to(ROOT).as_posix())
        out.writestr("BUILD_FROM_SOURCE.txt", f"""AXIS Historical Europe {VERSION} corresponding source (GPL v2)
Install the exact versions in project/requirements-build.txt into Python 3.12.
From the source/ directory run:
  Set environment variable PYTHONHASHSEED=0 before starting Python.
  PowerShell: $env:PYTHONHASHSEED = '0'
  POSIX shell: export PYTHONHASHSEED=0
  python src/render_lang.py
  python src/render_nml.py
  python -m nml.main -c -l generated/lang --grf=../axis-historical-europe-{VERSION}.grf generated/firs.nml
All source graphics and templates are included. HTML documentation generation
is not needed for the GRF. See project/ATTRIBUTION.md and project/LICENSE.txt.
This is a modified AXIS release; never load it together with original AXIS.
""")
    with zipfile.ZipFile(bundle) as check:
        assert check.testzip() is None
        assert "source/src/graphics/industries/steel_mill_1.png" in check.namelist()
        assert "source/src/historical_manifest.json" in check.namelist()
    result = {"source_bundle": bundle.name, "bytes": bundle.stat().st_size,
              "sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
              "matching_grf_sha256": report["artifact_sha256"]}
    (ROOT / "dist/source-bundle-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if args.verify_rebuild:
        # A fresh, tool-created child of .work only; verify before automatic cleanup.
        with tempfile.TemporaryDirectory(prefix="bundle-rebuild-", dir=ROOT / ".work") as folder:
            temporary = Path(folder).resolve()
            assert temporary.is_relative_to((ROOT / ".work").resolve())
            with zipfile.ZipFile(bundle) as data:
                data.extractall(temporary)
            rebuilt = temporary / artifact.name
            log_path = ROOT / ".work/bundle-rebuild.log"
            with log_path.open("w", encoding="utf-8") as log:
                for command in [[sys.executable, "src/render_lang.py"], [sys.executable, "src/render_nml.py"],
                                [sys.executable, "-m", "nml.main", "-c", "-l", "generated/lang", "--verbosity=3",
                                 "--grf=" + str(rebuilt), "generated/firs.nml"]]:
                    subprocess.run(command, cwd=temporary / "source", stdout=log, stderr=subprocess.STDOUT, check=True,
                                   env={**os.environ, "PYTHONHASHSEED": "0"})
            rebuilt_hash = hashlib.sha256(rebuilt.read_bytes()).hexdigest()
            assert rebuilt_hash == report["artifact_sha256"], rebuilt_hash
            check = {"passed": True, "rebuilt_grf_sha256": rebuilt_hash,
                     "source_bundle_sha256": result["sha256"], "method": "extract complete source ZIP and run its documented build commands"}
            (ROOT / "bundle-rebuild-phase5-result.json").write_text(json.dumps(check, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(check, indent=2))


if __name__ == "__main__":
    main()
