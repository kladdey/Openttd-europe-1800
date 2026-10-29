"""Isolated paused JGRPP harness for Phase 6A; source scenario is immutable."""
import argparse
import hashlib
import json
import lzma
import os
from pathlib import Path
import shutil
import subprocess
import time
from historical_scenario_migration import decode
from scenario_geography import chunks
from transport_phase3 import encode, gamma

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'newgrfs/axis-historical-europe/.work/coastal6a'
ASSETS=ROOT/'newgrfs/axis-historical-europe/.work/europe-migration'
ENGINE=ROOT/'newgrfs/axis-historical-europe/.work/runtime/engine/openttd-jgrpp-0.73.4-windows-win64/openttd.exe'
SOURCE=Path(r'C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.2.0 - No Industries.scn')
EXPECTED='9b4dbd70e27653fcb72d5778993988d257d5f83adcaf4a394c01af110d366735'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(script,tag,ticks=15000,source=SOURCE,unpaused=False):
    if not __debug__:raise SystemExit('Safety assertions required; do not run with Python -O')
    assert sha(SOURCE)==EXPECTED
    home=BASE/(tag+'-'+str(time.time_ns()));home.mkdir(parents=True)
    for folder in ['newgrf','baseset']:shutil.copytree(ASSETS/folder,home/folder,copy_function=os.link)
    game=home/'game/coastal';game.mkdir(parents=True)
    (game/'info.nut').write_text('''class CoastalInfo extends GSInfo {
function GetAuthor(){return "Historical coastal validation";}
function GetName(){return "HistoricalCoastalPhase6";}function GetDescription(){return "Disposable test only";}
function GetVersion(){return 1;}function GetDate(){return "2026-10-29";}function GetShortName(){return "HC6A";}
function CreateInstance(){return "CoastalProbe";}function GetAPIVersion(){return "16";}}
RegisterGS(CoastalInfo());
''')
    # JGRPP's Squirrel loader selects UTF-8 only when the BOM is present.
    # Without it, accented historical names are interpreted byte-by-byte.
    (game/'main.nut').write_text(script,encoding='utf-8-sig')
    raw=source.read_bytes();payload=[]
    for tag_,kind,records in chunks(decode(raw)):
        if tag_=='GSDT':
            name=b'HistoricalCoastalPhase6';records=[records[0],gamma(len(name))+name+b'\0'+(1).to_bytes(4,'big')+b'\0']
        elif tag_=='DATE' and unpaused:
            # Disposable movement test only. All delivered candidates retain
            # the source DATE chunk bit-for-bit, including normal pause.
            from repair_industry_free_editor_candidate import replace_pause
            from scenario_geography import gamma as read_gamma
            records,_=replace_pause(list(map(bytes,records)))
            schema=records[0];row=bytearray(records[1]);p=0;q=0
            while schema[p]:
                typ=schema[p];p+=1;n,p=read_gamma(schema,p);name=schema[p:p+n].decode();p+=n
                count=1
                if typ&16:count,q=read_gamma(row,q)
                size=1 if typ&15==10 else {1:1,2:1,3:2,4:2,5:4,6:4,7:8,8:8}[typ&15]
                if name=='pause_mode':row[q]=0
                q+=size*count
            records=[records[0],bytes(row)]
        payload.append(encode(tag_,kind,records))
    (home/'probe.scn').write_bytes(b'OTTX'+raw[4:8]+lzma.compress(b''.join(payload)+b'\0'*4))
    (home/'probe.cfg').write_text('''[gui]
autosave_interval = 0
autosave_on_exit = true
[locale]
currency = GBP
''')
    log=home/'engine.log'
    cmd=[str(ENGINE),'-X','-x','-c',str(home/'probe.cfg'),'-g',str(home/'probe.scn'),'-v',f'null:ticks={ticks}','-s','null','-m','null','-d','script=4']
    (home/'manifest.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source),script_sha256=sha(game/'main.nut'),unpaused_movement_test=unpaused,command=cmd),indent=2))
    with log.open('w',encoding='utf8') as f:
        subprocess.run(cmd,cwd=home,stdout=f,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW,check=True)
    assert sha(SOURCE)==EXPECTED
    print(home,flush=True)
    print('\n'.join(s for s in log.read_text(errors='replace').splitlines() if 'C6 DONE' in s or 'Error ' in s),flush=True)
    return home


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('script',type=Path);p.add_argument('--tag',required=True);p.add_argument('--ticks',type=int,default=15000)
    a=p.parse_args();run(a.script.read_text(encoding='utf8'),a.tag,a.ticks)
