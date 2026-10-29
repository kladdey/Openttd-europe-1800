"""Load a measurement-only child of the engine-saved candidate, then save/reload.

The delivered scenario is not assigned a GS or modified by these tests. The
measurement child differs only in GSDT, and stays paused to preserve geography.
"""
import hashlib
import json
import lzma
import os
from pathlib import Path
import shutil
import subprocess
import time
from historical_scenario_migration import inspect, decode
from scenario_geography import chunks
from transport_phase3 import encode, gamma

ROOT=Path(__file__).resolve().parents[1]
FORK=ROOT/'newgrfs/axis-historical-europe'
WORK=FORK/'.work/europe-migration'
ENGINE=FORK/'.work/runtime/engine/openttd-jgrpp-0.73.4-windows-win64/openttd.exe'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    source=WORK/'scenario/r.scn';assert source.exists()
    home=WORK/('probe-'+str(time.time_ns()));home.mkdir()
    for folder in ['newgrf','baseset']:shutil.copytree(WORK/folder,home/folder,copy_function=os.link)
    game=home/'game/migration';game.mkdir(parents=True)
    (game/'info.nut').write_text('''class MigrationInfo extends GSInfo {
function GetAuthor(){return "Local scenario validation";}
function GetName(){return "HistoricalMigrationProbe";}
function GetDescription(){return "Read-only inventory in a disposable copy";}
function GetVersion(){return 1;} function GetDate(){return "2026-10-28";}
function GetShortName(){return "HMIG";} function CreateInstance(){return "MigrationProbe";}
function GetAPIVersion(){return "16";}}
RegisterGS(MigrationInfo());
''')
    rules=json.loads((FORK/'historical_manifest.json').read_text())['industries']
    ids=','.join(str(r['local_id']) for r in rules.values())
    (game/'main.nut').write_text('IDS <- ['+ids+'];\n'+'''class MigrationProbe extends GSController {
state=null;
function Save(){return {checked=true};}
function Load(version,data){state=data;}
function Start(){
 local failures=0,types=GSIndustryTypeList(),cargos=GSCargoList();
 GSLog.Info("HMIG START reload="+(state!=null)+" economy_year="+GSDate.GetYear(GSDate.GetCurrentDate())+" towns="+GSTownList().Count()+" industries="+GSIndustryList().Count()+" cargos="+cargos.Count()+" types="+types.Count()+" train_limit="+GSGameSettings.GetValue("vehicle.max_train_length"));
 if(GSIndustryList().Count()!=0 || cargos.Count()!=64 || types.Count()!=92 || GSTownList().Count()!=613 || GSDate.GetYear(GSDate.GetCurrentDate())!=1800)failures++;
 foreach(c,_ in cargos)GSLog.Info("HMIG CARGO|"+c+"|"+GSCargo.GetCargoLabel(c));
 foreach(id in IDS){
  local type=GSIndustryType.ResolveNewGRFID(0x4B484531,id),valid=GSIndustryType.IsValidIndustryType(type);
  if(!valid)failures++;
  GSLog.Info("HMIG INDUSTRY|"+id+"|"+type+"|"+valid+"|"+(valid?GSIndustryType.GetName(type):"INVALID"));
 }
 GSLog.Info("HMIG DONE failures="+failures);while(true)Sleep(365);
}}
''')
    original=source.read_bytes();parts=[];changed=[]
    for tag,kind,records in chunks(decode(original)):
        before=encode(tag,kind,records)
        if tag=='GSDT':
            name=b'HistoricalMigrationProbe';records=[records[0],gamma(len(name))+name+b'\0'+(1).to_bytes(4,'big')+b'\0']
        after=encode(tag,kind,records);parts.append(after)
        if before!=after:changed.append(tag)
    assert changed==['GSDT']
    (home/'probe.scn').write_bytes(original[:8]+lzma.compress(b''.join(parts)+b'\0'*4))
    (home/'probe.cfg').write_text('''[gui]
autosave_interval = 0
autosave_on_exit = true
[locale]
currency = GBP
''')
    reports=[]
    for phase in ['initial','reload']:
        load=home/'probe.scn'
        if phase=='reload':
            saved=home/'save/autosave/exit.sav';assert saved.exists()
            shutil.copyfile(saved,home/'checkpoint.sav');load=home/'checkpoint.sav'
        log=home/(phase+'.log')
        command=[str(ENGINE),'-X','-x','-c',str(home/'probe.cfg'),'-g',str(load),'-v','null:ticks=1000','-s','null','-m','null','-d','script=4,grf=1']
        with log.open('w') as f:
            subprocess.run(command,cwd=home,stdout=f,stderr=subprocess.STDOUT,timeout=120,
                           creationflags=subprocess.CREATE_NO_WINDOW,check=True)
        text=log.read_text(errors='replace');lines=[s for s in text.splitlines() if 'HMIG ' in s]
        reports.append(dict(phase=phase,passed='HMIG DONE failures=0' in text,
                            allocation_overflow='Too many industry' in text,lines=lines,log_sha256=sha(log),command=command))
        print(phase,reports[-1]['passed'],reports[-1]['allocation_overflow'],flush=True)
    before=inspect(source);saved=inspect(home/'save/autosave/exit.sav')
    protected=[tag for tag in before['chunks'] if tag in ['MAPS','CITY','OBJS','STNN','PATS','ECMY']]
    for tag in protected:assert before['chunks'][tag]==saved['chunks'][tag],tag
    assert before['map_array_sha256']==saved['map_array_sha256']
    assert sha(source)==hashlib.sha256(original).hexdigest()
    result=dict(engine_sha256=sha(ENGINE),candidate_sha256=sha(source),probe_copy_changes=changed,
                phases=reports,passed=all(r['passed'] and not r['allocation_overflow'] for r in reports),
                protected_chunks_identical_after_game_save_reload=protected,
                map_arrays_normalized_identical_after_game_save_reload=before['map_array_sha256'],
                delivered_candidate_modified_by_test=False,
                limitation='Read-only paused inventory and save/reload, no industry placement or multiplayer gameplay in the delivered empty scenario')
    output=ROOT/'docs/research/axis_europe_migration_runtime.json'
    assert not output.exists();output.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
