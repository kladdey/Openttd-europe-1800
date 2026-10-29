# SPDX-License-Identifier: GPL-2.0-only
"""Run fresh headless JGRPP worlds using an isolated portable installation.

No network downloads, user installation discovery, existing save loading or
campaign edits. The supplied engine directory must be under this fork's .work.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-directory", type=Path, required=True)
    parser.add_argument("--case", default="all")
    args = parser.parse_args()
    engine = args.engine_directory.resolve()
    if not engine.is_relative_to((ROOT / ".work").resolve()):
        raise SystemExit("Engine must be a disposable copy inside this project's .work")
    version = json.loads((ROOT / 'historical_manifest.json').read_text())['version']
    artifact = ROOT / f"dist/axis-historical-europe-{version}.grf"
    (engine / "newgrf").mkdir(exist_ok=True)
    shutil.copyfile(artifact, engine / "newgrf" / artifact.name)
    game = engine / "game/historical-steel-runtime-test"
    game.mkdir(parents=True, exist_ok=True)
    for name in ["info.nut", "main.nut"]:
        shutil.copyfile(ROOT / "tests/game" / name, game / name)
    ai = engine / "ai/historical-funding-company"
    ai.mkdir(parents=True, exist_ok=True)
    for name in ["info.nut", "main.nut"]:
        shutil.copyfile(ROOT / "tests/ai" / name, ai / name)
    (engine / "scripts").mkdir(exist_ok=True)
    (engine / "scripts/game_start.scr").write_text('start_ai "Historical Funding Test Company"\n', encoding="utf-8")
    cases = [(str(year), year, 1, 1, 0) for year in [1830, 1850, 1859, 1860, 1900, 1905, 1906, 1950, 1951, 1952, 1955, 2000]]
    cases += [("unrestricted-1830", 1830, 0, 1, 0), ("spawning-off-2000", 2000, 1, 0, 0),
              ("generated-1830", 1830, 1, 1, 4), ("generated-2000", 2000, 1, 1, 4)]
    selected = [c for c in cases if args.case in {"all", c[0]}]
    if not selected:
        raise SystemExit("Unknown case")
    results = []
    for index, (name, year, historical, spawning, density) in enumerate(selected):
        case_dir = ROOT / ".work/runtime-results" / name
        case_dir.mkdir(parents=True, exist_ok=True)
        log = case_dir / "console.log"
        if log.exists():
            log.write_text("", encoding="utf-8")
        # A unique file is used per case. No user's openttd.cfg is read/written.
        config = case_dir / "openttd.cfg"
        config.write_text(f"""[misc]
resolution = 640,480
[gui]
developer = 2
[game_creation]
map_x = 8
map_y = 8
generation_seed = 734
land_generator = 0
starting_year = {year}
[difficulty]
industry_density = {density}
terrain_type = 0
quantity_sea_lakes = 0
number_towns = 2
[economy]
timekeeping_units = 0
[ai]
ai_in_multiplayer = true
[network]
server_name = AXIS Historical disposable runtime test
server_game_type = local
server_port = {43970 + index}
min_active_clients = 0
[newgrf]
{artifact.name} = 0 0 {4 if spawning else 0} 0 0 0 16 150 80 300 {historical}
[game_scripts]
"Historical Steel Runtime Test" = historical={historical},spawning={spawning}
""", encoding="utf-8")
        (engine / "scripts/pre_dedicated.scr").write_text(f'script "{log.as_posix()}"\n', encoding="utf-8")
        command = [str(engine / "openttd.exe"), "-D", "127.0.0.1:" + str(43970 + index),
                   "-X", "-x", "-c", str(config), "-t", str(year), "-d", "script=5,grf=1"]
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        with (case_dir / "process.log").open("w", encoding="utf-8") as output:
            process = subprocess.Popen(command, cwd=engine, stdout=output, stderr=subprocess.STDOUT,
                                       startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                deadline = time.monotonic() + 90
                text = ""
                while time.monotonic() < deadline and process.poll() is None:
                    # Windows dedicated builds mirror debug output to stderr;
                    # the console script's stdio log can remain buffered.
                    text = (case_dir / "process.log").read_text(encoding="utf-8", errors="replace")
                    if log.exists():
                        text += log.read_text(encoding="utf-8", errors="replace")
                    if "AHETEST DONE" in text or "Your script made an error" in text:
                        break
                    time.sleep(0.25)
                result = {"case": name, "passed": "AHETEST DONE failures=0" in text and
                          "Starting dedicated server, version jgrpp-0.73.4" in text,
                          "log": (case_dir / "process.log").relative_to(ROOT).as_posix(),
                          "test_lines": list(dict.fromkeys(s for s in text.splitlines() if "AHETEST" in s))}
                results.append(result)
                print(json.dumps(result), flush=True)
            finally:
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=10)
        if not results[-1]["passed"]:
            break
    report = {"engine": "JGRPP 0.73.4", "engine_sha256": hashlib.sha256((engine / "openttd.exe").read_bytes()).hexdigest(),
              "grf_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(), "map_size": [256, 256],
              "cases": results, "passed": len(results) == len(selected) and all(r["passed"] for r in results),
              "scope": "fresh headless worlds; deity and company-mode funding commands, map generation and inventory; no human joins or transported cargo"}
    (ROOT / ("runtime-phase5-result.json" if args.case == "all" else "runtime-phase5-" + args.case + "-result.json")).write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
