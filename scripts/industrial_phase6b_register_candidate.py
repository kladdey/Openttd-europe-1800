"""Generate authoritative 0.3.0 metadata in a fresh isolated all-15-GRF world."""
import json,os,shutil,subprocess,time
from pathlib import Path
from PIL import Image
from industrial_phase6b_runtime import ROOT,BASE,SOURCE,sha
from coastal_phase6_runtime import ASSETS,ENGINE
from historical_scenario_migration import inspect


def main():
    grf=ROOT/'newgrfs/axis-historical-copper-salt/dist/axis-historical-europe-0.3.0-candidate.grf'
    expected=json.loads((ROOT/'newgrfs/axis-historical-copper-salt/candidate_manifest.json').read_text())['expected_industry_count']
    home=BASE/('candidate-registration-'+str(time.time_ns()));home.mkdir()
    for folder in ['newgrf','baseset']:
        shutil.copytree(ASSETS/folder,home/folder,copy_function=os.link,ignore=shutil.ignore_patterns('axis-historical-europe-0.2.0.grf'))
    shutil.copyfile(grf,home/'newgrf'/grf.name)
    game=home/'game/registration';game.mkdir(parents=True)
    (game/'info.nut').write_text('''class RegistrationInfo extends GSInfo {
function GetAuthor(){return "Historical economy project";}function GetName(){return "CopperSaltRegistration";}
function GetDescription(){return "Disposable candidate tests";}function GetVersion(){return 1;}function GetDate(){return "2026-10-29";}function GetShortName(){return "CSRG";}function CreateInstance(){return "CoastalProbe";}function GetAPIVersion(){return "16";}}
RegisterGS(RegistrationInfo());''',encoding='utf8')
    (game/'main.nut').write_text('''class CoastalProbe extends GSController {function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSLog.Info("I6 REGISTER|version="+GSNewGRF.GetVersion(0x4B484531)+"|types="+GSIndustryTypeList().Count()+"|cargos="+GSCargoList().Count()+"|grfs="+GSNewGRFList().Count());
foreach(c,_ in GSCargoList())GSLog.Info("I6 CARGO|"+c+"|"+GSCargo.GetCargoLabel(c));
foreach(id in [64,67,105,117,123,124,125]){local t=GSIndustryType.ResolveNewGRFID(0x4B484531,id);GSLog.Info("I6 REGISTER_TYPE|"+id+"|"+t+"|"+GSIndustryType.GetName(t));}
foreach(e,_ in GSEngineList(GSVehicle.VT_ROAD))if(GSEngine.IsBuildable(e))GSLog.Info("I6 ROAD_ENGINE|"+e+"|"+GSEngine.GetName(e));
GSLog.Info("C6 DONE registration");while(true)Sleep(365);}}''',encoding='utf-8-sig')
    cfg='''[gui]
autosave_interval = 0
autosave_on_exit = true
[game_creation]
map_x = 8
map_y = 8
heightmap_height = 16
starting_year = 1830
custom_town_number = 3
generation_seed = 1830
[difficulty]
industry_density = 0
number_towns = 4
max_no_competitors = 0
[economy]
timekeeping_units = 0
[construction]
raw_industry_construction = 1
[newgrf]
'''
    for ref in inspect(SOURCE)['newgrfs']:
        if ref['grfid']=='4B484531':line=grf.name
        else:line=f'{ref["grfid"]}|{ref["md5"].upper()}|{ref["filename"]}'
        cfg+=line+' = '+' '.join(map(str,ref['params']))+'\n'
    cfg+='[game_scripts]\nCopperSaltRegistration =\n'
    (home/'test.cfg').write_text(cfg,encoding='utf8');Image.new('L',(256,256),255).save(home/'flat.png')
    cmd=[str(ENGINE),'-X','-x','-c',str(home/'test.cfg'),'-g',str(home/'flat.png'),'-v','null:ticks=1500','-s','null','-m','null','-d','script=4']
    start=time.monotonic()
    with (home/'engine.log').open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=home,stdout=f,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW,check=True)
    log=(home/'engine.log').read_text(encoding='utf8');assert f'I6 REGISTER|version=3|types={expected}|cargos=64|grfs=15' in log,log[-3000:]
    saved=home/'save/autosave/exit.sav';result=dict(case=str(home),saved=str(saved),grf_sha256=sha(grf),engine_sha256=sha(ENGINE),command=cmd,seconds=round(time.monotonic()-start,2),industry_types=expected,cargos=64,grfs=15)
    (BASE/'candidate-registration.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
