"""Unmodified JGRPP, isolated assets/config; no scenario/save-byte mutation."""
import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'newgrfs/axis-historical-lifecycle/.work/runtime'
ENGINE=ROOT/'newgrfs/axis-historical-europe/.work/runtime/engine/openttd-jgrpp-0.73.4-windows-win64/openttd.exe'
SOURCE=Path(r'C:\Users\Kladd\Documents\OpenTTD\scenario\Europe 1830 Historical AXIS 0.3.0 - Inland Markets.scn')
OLD_GRF=SOURCE.parent.parent/'newgrf/axis-historical-europe-0.3.0-candidate.grf'
GRF=ROOT/'newgrfs/axis-historical-lifecycle/dist/axis-historical-europe-0.4.0-lifecycle-candidate.grf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guards():
    if not __debug__:raise SystemExit('Do not run lifecycle tooling with Python -O')
    assert sha(SOURCE)=='afcab50864e87f56a7260c62d87bd37560fa3d7676713afb14c480c555d0bc06'
    assert sha(OLD_GRF)=='f0da622873c91107fa4d2b768d88cd95d5db009c2b2975bdb6d7ab6caaed3c33'
    assert sha(ENGINE)=='1b3fd69c1ea5f77eebe881c6d8a6ad9a03b71f98928a05e0c3c08c79482e2789'

def prepare(tag,script,policy=True,old=False,density=0):
    from historical_scenario_migration import inspect
    guards();home=BASE/(tag+'-'+str(time.time_ns()));home.mkdir(parents=True)
    assets=Path(json.loads((ROOT/'newgrfs/axis-historical-europe/.work/industrial6b/candidate-registration.json').read_text())['case'])
    for folder in ['newgrf','baseset']:
        shutil.copytree(assets/folder,home/folder,copy_function=os.link,ignore=shutil.ignore_patterns('axis-historical-europe-0.3.0-candidate.grf'))
    artifact=OLD_GRF if old else GRF;shutil.copyfile(artifact,home/'newgrf'/artifact.name)
    game=home/'game/lifecycle';game.mkdir(parents=True)
    (game/'info.nut').write_text('''class LifecycleInfo extends GSInfo {
function GetAuthor(){return "Europe historical economy project";}function GetName(){return "Historical Industry Lifecycle";}
function GetDescription(){return "Experimental historical lifecycle foundation";}function GetVersion(){return 1;}function GetDate(){return "2026-10-29";}function GetShortName(){return "HIL1";}
function CreateInstance(){return "LifecycleController";}function GetAPIVersion(){return "16";}}
RegisterGS(LifecycleInfo());''')
    (game/'main.nut').write_text(script,encoding='utf-8-sig')
    cfg=f'''[gui]
autosave_interval = 0
autosave_on_exit = true
scenario_developer = true
[locale]
currency = GBP
[game_creation]
map_x = 8
map_y = 8
heightmap_height = 1
starting_year = 1830
generation_seed = 734
custom_town_number = 3
[difficulty]
industry_density = {density}
number_towns = 4
max_no_competitors = 0
[economy]
timekeeping_units = 0
inflation = false
infrastructure_maintenance = true
[vehicle]
max_train_length = 7
[newgrf]
'''
    for ref in inspect(SOURCE)['newgrfs']:
        params=ref['params'][:]
        if ref['grfid']=='4B484531':
            filename=artifact.name
            if not old:
                params+=([0]*max(0,12-len(params)));params[11]=int(policy)
        else:filename=f'{ref["grfid"]}|{ref["md5"].upper()}|{ref["filename"]}'
        cfg+=filename+' = '+' '.join(map(str,params))+'\n'
    cfg+='[game_scripts]\n"Historical Industry Lifecycle" =\n'
    (home/'test.cfg').write_text(cfg);Image.new('L',(256,256),255).save(home/'flat.png')
    (home/'inputs.json').write_text(json.dumps(dict(engine_sha256=sha(ENGINE),grf_sha256=sha(artifact),original_scenario_sha256=sha(SOURCE),script_sha256=sha(game/'main.nut'),policy=policy,old_0_3=old,industry_density=density),indent=2))
    return home

def execute(home,ticks=45000,source=None,tag='engine',dedicated=False):
    guards();home=Path(home);cmd=[str(ENGINE),'-X','-x','-c',str(home/'test.cfg'),'-g',str(source or home/'flat.png'),'-v',f'null:ticks={ticks}','-s','null','-m','null','-d','script=4']
    if dedicated:
        cmd.insert(1,'-D127.0.0.1:39873');cmd[cmd.index('-v')+1]='dedicated'
    log=home/(tag+'.log');start=time.monotonic()
    with log.open('w',encoding='utf8') as f:
        p=subprocess.Popen(cmd,cwd=home,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.PIPE if dedicated else None,creationflags=subprocess.CREATE_NO_WINDOW)
        quit_sent=None;forced_stop=False
        try:
            while p.poll() is None:
                time.sleep(.25);text=log.read_text(encoding='utf8',errors='replace')
                if any(s in text for s in ['Your script made an error','Failed to compile','The script died unexpectedly.']):raise RuntimeError('Script failure: '+str(log))
                if dedicated and 'P7 DEDICATED_SMOKE_DONE' in text:
                    if quit_sent is None:
                        p.stdin.write(b'quit\n');p.stdin.flush();quit_sent=time.monotonic()
                    elif time.monotonic()-quit_sent>5:
                        p.terminate();forced_stop=True;p.wait()
                if time.monotonic()-start>300:raise subprocess.TimeoutExpired(cmd,300)
            if p.returncode and not forced_stop:raise subprocess.CalledProcessError(p.returncode,cmd)
        finally:
            if p.poll() is None:p.kill();p.wait()
    result=dict(case=str(home),command=cmd,seconds=round(time.monotonic()-start,3),log=str(log),log_sha256=sha(log),script_sha256=sha(home/'game/lifecycle/main.nut'),dedicated=dedicated,dedicated_forced_stop=forced_stop,observations=[s for s in log.read_text(encoding='utf8').splitlines() if 'P7 ' in s])
    (home/(tag+'-result.json')).write_text(json.dumps(result,indent=2));guards();print(json.dumps(result,indent=2),flush=True);return result
