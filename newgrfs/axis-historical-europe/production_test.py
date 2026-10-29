# SPDX-License-Identifier: GPL-2.0-only
"""Real truck deliveries and a disk save/reload in an isolated 1860 world."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import time

from PIL import Image

ROOT = Path(__file__).resolve().parent


def enrich_report(report, engine, resumed):
    """Extract measured values from captured engine logs, never infer output."""
    case = ROOT / ".work/production-test"
    initial = (case / "initial.log").read_text(encoding="utf-8", errors="replace")
    reloaded_path = case / "reloaded.log"
    reloaded = reloaded_path.read_text(encoding="utf-8", errors="replace") if reloaded_path.exists() else ""
    report["engine_sha256"] = hashlib.sha256((engine / "openttd.exe").read_bytes()).hexdigest()
    report["reload_replayed_existing_checkpoint"] = resumed
    if report["passed"]:
        assert "Starting dedicated server, version jgrpp-0.73.4" in initial
        assert "Starting dedicated server, version jgrpp-0.73.4" in reloaded
        saved = re.search(r"PRODTEST CHECKPOINT iron=(\d+) coke=(\d+) steel=(\d+)", initial)
        loaded = re.search(r"PRODTEST RELOAD iron=(\d+) coke=(\d+)", reloaded)
        done = re.search(r"PRODTEST DONE steel_last_month=(\d+) slag_last_month=(\d+) delivered_steel=(\d+) remaining_iron=(\d+) failures=0", reloaded)
        assert saved and loaded and done
        report["observations"] = {
            "saved_stockpile": {"IRON": int(saved[1]), "COKE": int(saved[2])},
            "steel_before_coke": int(saved[3]),
            "reloaded_stockpile": {"IRON": int(loaded[1]), "COKE": int(loaded[2])},
            "observed_completed_month_production": {"STEL": int(done[1]), "SLAG": int(done[2])},
            "steel_delivered_to_customer": int(done[3]), "remaining_pig_iron": int(done[4]),
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-directory", required=True, type=Path)
    parser.add_argument("--resume", action="store_true", help="Replay the reload phase from this fixture's existing checkpoint")
    args = parser.parse_args()
    if json.loads((ROOT / 'historical_manifest.json').read_text())['version'] != '0.1.0':
        raise SystemExit('Legacy 0.1.0 fixture: use production_phase5.py for the current fork')
    engine = args.engine_directory.resolve()
    assert engine.is_relative_to((ROOT / ".work").resolve()), "Disposable engine under .work required"
    case = ROOT / ".work/production-test"
    case.mkdir(exist_ok=True)
    for folder, source in [("game/historical-steel-production", "tests/production"),
                           ("ai/historical-funding-company", "tests/ai")]:
        destination = engine / folder
        destination.mkdir(parents=True, exist_ok=True)
        for name in ["info.nut", "main.nut"]:
            shutil.copyfile(ROOT / source / name, destination / name)
    artifact = ROOT / "dist/axis-historical-europe-0.1.0.grf"
    shutil.copyfile(artifact, engine / "newgrf" / artifact.name)
    heightmap = case / "flat-diagnostic.png"
    image = Image.new("L", (256, 256), 255)
    image.save(heightmap)
    config = case / "openttd.cfg"
    config.write_text(f"""[gui]
developer = 2
autosave_interval = 0
[game_creation]
map_x = 8
map_y = 8
generation_seed = 734
heightmap_height = 16
custom_town_number = 1
starting_year = 1860
[difficulty]
industry_density = 0
number_towns = 4
vehicle_breakdowns = 0
disasters = false
[economy]
timekeeping_units = 0
[construction]
raw_industry_construction = 1
[ai]
ai_in_multiplayer = true
[network]
server_game_type = local
server_port = 43995
min_active_clients = 0
[newgrf]
{artifact.name} = 0 0 4 0 0 0 16 150 80 300 1
[game_scripts]
"Historical Steel Production Test" =
""", encoding="utf-8")
    checkpoint = case / "partial-stockpile.sav"
    reports = []
    if args.resume:
        initial_text = (case / "initial.log").read_text(encoding="utf-8", errors="replace")
        assert checkpoint.exists() and "PRODTEST CHECKPOINT" in initial_text and "Map successfully saved" in initial_text
        reports.append({"phase": "initial", "passed": True,
                        "test_lines": list(dict.fromkeys(s for s in initial_text.splitlines() if "PRODTEST" in s))})
    for phase in (["reloaded"] if args.resume else ["initial", "reloaded"]):
        log = case / (phase + ".log")
        (engine / "scripts/game_start.scr").write_text(
            'start_ai "Historical Funding Test Company"\n' if phase == "initial" else "", encoding="utf-8")
        (engine / "scripts/pre_dedicated.scr").write_text("", encoding="utf-8")
        command = [str(engine / "openttd.exe"), "-D", "127.0.0.1:43995", "-X", "-x", "-c", str(config),
                   "-d", "script=5,grf=1", "-g", str(heightmap if phase == "initial" else checkpoint)]
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        with log.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(command, cwd=engine, stdout=output, stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE, startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
            text, saved = "", False
            try:
                deadline = time.monotonic() + 1000
                while process.poll() is None and time.monotonic() < deadline:
                    text = log.read_text(encoding="utf-8", errors="replace")
                    if "PRODTEST FAILED" in text or "Your script made an error" in text:
                        break
                    if phase == "initial" and "PRODTEST CHECKPOINT" in text and not saved:
                        process.stdin.write(('save "' + checkpoint.with_suffix("").as_posix() + '"\n').encode())
                        process.stdin.flush()
                        saved = True
                    if phase == "initial" and saved and "Map successfully saved" in text and checkpoint.exists():
                        break
                    if phase == "reloaded" and "PRODTEST DONE" in text:
                        break
                    time.sleep(0.25)
                passed = (("Map successfully saved" in text) if phase == "initial" else
                          ("PRODTEST DONE" in text and "failures=0" in text)) and "PRODTEST FAILED" not in text
                result = {"phase": phase, "passed": passed,
                          "test_lines": list(dict.fromkeys(s for s in text.splitlines() if "PRODTEST" in s))}
                reports.append(result)
                print(json.dumps(result), flush=True)
            finally:
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=10)
        if not passed:
            break
    report = {"engine": "JGRPP 0.73.4", "map_size": [256, 256], "year": 1860,
              "grf_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
              "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest() if checkpoint.exists() else None,
              "phases": reports, "passed": len(reports) == 2 and all(r["passed"] for r in reports),
              "diagnostic_concession": "Default trucks force-enabled through GSEngine.EnableForCompany in the disposable company; campaign vehicle NewGRFs not tested"}
    enrich_report(report, engine, args.resume)
    (ROOT / "production-result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
