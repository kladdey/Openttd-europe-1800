# SPDX-License-Identifier: GPL-2.0-only
"""Render and compile the isolated prepared source; never install into OpenTTD."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    source = ROOT / ".work/source"
    if not (source / "src/historical_availability.py").exists():
        raise SystemExit("Run prepare.py --upstream PATH first")
    logs = ROOT / ".work/logs"
    logs.mkdir(parents=True, exist_ok=True)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    steps = {
        "render-lang": [sys.executable, "src/render_lang.py"],
        "render-nml": [sys.executable, "src/render_nml.py"],
        "compile": [sys.executable, "-m", "nml.main", "-c", "-l", "generated/lang", "--verbosity=3",
                    "--grf=" + str(dist / "axis-historical-europe-0.1.0.grf"), "generated/firs.nml"],
    }
    for label, command in steps.items():
        print(label, flush=True)
        with (logs / (label + ".log")).open("w", encoding="utf-8") as out:
            result = subprocess.run(command, cwd=source, stdout=out, stderr=subprocess.STDOUT,
                                    env={**os.environ, "PYTHONHASHSEED": "0"})
        if result.returncode:
            raise SystemExit(f"{label} failed; inspect {logs / (label + '.log')}")
    artifact = dist / "axis-historical-europe-0.1.0.grf"
    report = {"artifact": artifact.name, "bytes": artifact.stat().st_size,
              "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
              "upstream_commit": json.loads((ROOT / "historical_manifest.json").read_text())["upstream_commit"],
              "runtime_tested_by_build_step": False}
    (dist / "build-result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
