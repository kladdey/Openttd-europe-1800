"""Stage a separate editor workspace; never changes the original scenario/config."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
FORK=ROOT/'newgrfs/axis-historical-europe'
WORK=FORK/'.work/europe-migration'
SOURCE=Path(r'C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1800 V2 newGRFS fuck industry.scn')


def main():
    WORK.mkdir(exist_ok=False)
    (WORK/'scenario').mkdir()
    shutil.copyfile(SOURCE,WORK/'scenario/Europe-industry-free-original-copy.scn')
    shutil.copytree(ROOT/'.vehicle-audit-runtime/phase2/newgrf',WORK/'newgrf')
    artifact=FORK/'dist/axis-historical-europe-0.2.0.grf'
    shutil.copyfile(artifact,WORK/'newgrf'/artifact.name)
    engine=FORK/'.work/runtime/engine/openttd-jgrpp-0.73.4-windows-win64'
    shutil.copytree(engine/'baseset',WORK/'baseset')
    (WORK/'editor.cfg').write_text('''[misc]
resolution = 1400,900
fullscreen = false
[gui]
scenario_developer = true
newgrf_developer_tools = true
autosave_interval = 0
autosave_on_exit = false
[locale]
currency = GBP
[game_scripts]
none =
''')
    inputs=[SOURCE,Path(r'C:\Users\Kladd\Documents\OpenTTD\openttd.cfg'),Path(r'C:\Users\Kladd\Downloads\OpenTTD\openttd.cfg')]
    (WORK/'protected-inputs.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2))
    print(WORK)


if __name__=='__main__':main()
