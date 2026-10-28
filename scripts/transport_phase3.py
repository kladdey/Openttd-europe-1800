"""Isolated Phase 3 runner. Only GSDT is changed in a disposable scenario copy.

All geography/economy/vehicle/industry chunks and original files are preserved.
No GRF or engine patching. Run from repository root with the bundled Python.
"""
import argparse,hashlib,json,lzma,re,shutil,subprocess,time,os
from pathlib import Path
from scenario_geography import chunks
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'.vehicle-audit-runtime/phase3'
def sha(b):return hashlib.sha256(b).hexdigest()
def gamma(n):
    if n<128:return bytes([n])
    for extra in range(1,5):
        if n<(1<<(7+7*extra)):
            return bytes([(256-(1<<(8-extra)))|(n>>(8*extra))])+n.to_bytes(extra+1,'big')[1:]
    raise ValueError(n)
def encode(tag,kind,records):
    out=tag.encode()
    if kind==0:
        b=bytes(records[0]);return out+bytes([(len(b)>>24)<<4])+ (len(b)&0xffffff).to_bytes(3,'big')+b
    return out+bytes([kind])+b''.join(gamma(len(r)+1)+bytes(r) for r in records)+b'\0'
def prepare(script,constants):
    if not re.search(r'\bFLEET\s*<-',constants):constants+='\nFLEET <- 1;'
    if not re.search(r'\bMIN_SEPARATION\s*<-',constants):constants+='\nMIN_SEPARATION <- 2;'
    if not re.search(r'\bEXPAND\s*<-',constants):constants+='\nEXPAND <- false;'
    if not re.search(r'\bWAGONS\s*<-',constants):constants+='\nWAGONS <- 4;'
    if not re.search(r'\bPLATFORM\s*<-',constants):constants+='\nPLATFORM <- 2;'
    if not re.search(r'\bBRAKE_VAN\s*<-',constants):constants+='\nBRAKE_VAN <- false;'
    RUN.mkdir(parents=True,exist_ok=True)
    for folder in ('newgrf','ai','scripts'):
        if not (RUN/folder).exists():shutil.copytree(ROOT/'.vehicle-audit-runtime/phase2'/folder,RUN/folder,copy_function=os.link if folder=='newgrf' else shutil.copy2)
    gs=RUN/'game/p3';gs.mkdir(parents=True,exist_ok=True)
    info=(ROOT/'scripts/vehicle_phase2_probe/info.nut').read_text().replace('VehicleEconomyPhase2','TransportPhase3').replace('Phase2Probe','TransportProbe')
    (gs/'info.nut').write_text(info)
    (gs/'main.nut').write_text(constants+'\n'+(ROOT/script).read_text(),encoding='utf8')
    cfg=(ROOT/'.vehicle-audit-runtime/phase2/phase2-verified-1830.cfg').read_text()
    cfg=re.sub(r'\[game_scripts\][\s\S]*?(?=\n\[|\Z)','[game_scripts]\nTransportPhase3 = \n',cfg)
    (RUN/'test.cfg').write_text(cfg)
    ref=json.loads((ROOT/'docs/research/scenario_vehicle_references.json').read_text());original=Path(ref['scenario']).read_bytes();assert sha(original)==ref['sha256']
    shared=ROOT/'.vehicle-audit-runtime/phase3/scenario-test.scn'
    if shared.exists() and shared.parent!=RUN and not (RUN/'scenario-test.scn').exists():shutil.copyfile(shared,RUN/'scenario-test.scn')
    if (RUN/'scenario-test.scn').exists() and (ROOT/'docs/research/transport_scenario_copy_manifest.json').exists():
        manifest=json.loads((ROOT/'docs/research/transport_scenario_copy_manifest.json').read_text())
        assert sha((RUN/'scenario-test.scn').read_bytes())==manifest['test_copy_sha256']
        return
    result=[];checks=[]
    for tag,kind,records in chunks(lzma.decompress(original[8:])):
        before=encode(tag,kind,records)
        if tag=='GSDT':
            name=b'TransportPhase3';records=[records[0],gamma(len(name))+name+b'\0'+(1).to_bytes(4,'big')+b'\0']
        after=encode(tag,kind,records);result.append(after);checks.append({'chunk':tag,'unchanged':before==after,'sha256':sha(before)})
    assert [r['chunk'] for r in checks if not r['unchanged']]==['GSDT']
    copy=original[:8]+lzma.compress(b''.join(result)+b'\0\0\0\0')
    (RUN/'scenario-test.scn').write_bytes(copy)
    (ROOT/'docs/research/transport_scenario_copy_manifest.json').write_text(json.dumps({'original_path':ref['scenario'],'original_sha256':sha(original),'test_copy_sha256':sha(copy),'changes':'GSDT only: attach measurement GS, no previous active GS configured','chunk_checks':checks},indent=2))
def main():
    global RUN
    ap=argparse.ArgumentParser();ap.add_argument('--script',default='scripts/transport_phase3_probe.nut');ap.add_argument('--tag',default='inventory');ap.add_argument('--ticks',type=int,default=1000);ap.add_argument('--constants',default='');ap.add_argument('--replay',help='Retained tag from transport_run_configs.json; use a new --tag and sufficient --ticks');args=ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.tag):raise SystemExit('Invalid tag')
    RUN=RUN/args.tag
    log=RUN/(args.tag+'.log')
    if log.exists():raise SystemExit('Refusing to overwrite '+str(log))
    prepare(args.script,args.constants)
    if args.replay:
        configs=json.loads((ROOT/'docs/research/transport_run_configs.json').read_text());prior=next(c for c in configs if c['tag']==args.replay)
        frozen=json.loads((ROOT/'docs/research/transport_harness_sources.json').read_text())[prior['script_sha256']]
        (RUN/'game/p3/main.nut').write_text(frozen,encoding='utf8')
        assert sha((RUN/'game/p3/main.nut').read_bytes())==prior['script_sha256']
    (RUN/'run_manifest.json').write_text(json.dumps({'tag':args.tag,'constants':args.constants,'script':args.script,'ticks_limit':args.ticks,'script_sha256':sha((RUN/'game/p3/main.nut').read_bytes()),'config_sha256':sha((RUN/'test.cfg').read_bytes()),'scenario_sha256':sha((RUN/'scenario-test.scn').read_bytes()),'exe':r'C:\Users\Kladd\Downloads\OpenTTD\openttd.exe'},indent=2))
    with log.open('wb') as f:
        p=subprocess.Popen([r'C:\Users\Kladd\Downloads\OpenTTD\openttd.exe','-c','test.cfg','-x','-v',f'null:ticks={args.ticks}','-s','null','-m','null','-d','script=4','-g',str(RUN/'scenario-test.scn')],cwd=RUN,stdout=f,stderr=f)
        print('PID',p.pid,flush=True)
        start=time.monotonic()
        while p.poll() is None:
            time.sleep(1)
            content=log.read_text(errors='replace')
            if any(mark in content for mark in ('P3_SERVICE_DONE','P3_DONE','P3_BLOCKED','The script died unexpectedly.')) or time.monotonic()-start>1800:
                p.kill();p.wait();break
        print('Stopped',p.returncode,log,flush=True)
if __name__=='__main__':main()
