"""Extend the preserved Phase 1 audit using a separate disposable subdirectory.

Never launches a campaign save; never changes a GRF or original configuration.
Run from the repository root. Runtime outputs are ignored. A bootstrap AI makes
an empty test company; the GS grants test capital, not included as revenue.
"""
import argparse,json,re,shutil,subprocess,csv,hashlib
from pathlib import Path

PYTHON=Path(__file__).resolve().parents[1]
RUN=PYTHON/'.vehicle-audit-runtime/phase2'
def prepare():
    RUN.mkdir(parents=True,exist_ok=True)
    (RUN/'newgrf').mkdir(exist_ok=True)
    for p in (PYTHON/'.vehicle-audit-runtime/newgrf').iterdir():
        if p.is_file() and not (RUN/'newgrf'/p.name).exists():shutil.copyfile(p,RUN/'newgrf'/p.name)
    for part in ('game/phase2','ai/bootstrap','scripts'):(RUN/part).mkdir(parents=True,exist_ok=True)
    for name in ('info.nut','main.nut'):shutil.copyfile(PYTHON/'scripts/vehicle_phase2_probe'/name,RUN/'game/phase2'/name)
    (RUN/'ai/bootstrap/info.nut').write_text('class BootstrapInfo extends AIInfo { function GetAuthor(){return "Local audit";} function GetName(){return "EconomyBootstrap";} function GetDescription(){return "Empty test company";} function GetVersion(){return 1;} function GetDate(){return "2026-10-28";} function CreateInstance(){return "Bootstrap";} function GetShortName(){return "EBP2";} function GetAPIVersion(){return "15";} } RegisterAI(BootstrapInfo());')
    (RUN/'ai/bootstrap/main.nut').write_text('class Bootstrap extends AIController {function Start(){while(true) Sleep(10000);}}')
    (RUN/'scripts/game_start.scr').write_text('start_ai EconomyBootstrap\n')
    rows=list(csv.DictReader((PYTHON/'docs/research/vehicle_roster.csv').open(encoding='utf-8-sig')))
    lookup={(r['source_grfid'],int(r['local_vehicle_id'])):int(r['runtime_engine_id']) for r in rows}
    cases=[]
    def case(key,g,e,wg=None,w=-1,n=0,c=0):
        if (g,e) not in lookup or wg is not None and (wg,w) not in lookup:return
        cases.append(dict(key=key,engine=lookup[g,e],wagon=-1 if wg is None else lookup[wg,w],n=n,cargo=c,engine_grfid=g,engine_local_id=e,wagon_grfid=wg,wagon_local_id=w))
    for g,e,label in [('44441000',124,'planet'),('44441000',113,'coppernob'),('44440302',0,'norris'),('4E4D0518',116,'grasshopper')]:
        case(label+'_mixed_4',g,e,'44441000',12,4,14)
        for cargo,cid,w in [('passenger',0,44),('mail',2,44),('coal',14,12),('goods',5,12)]:
            for n in (2,4,8):case(f'{label}_{cargo}_{n}_uk',g,e,'44441000',w,n,cid)
        for cargo,cid,w in [('passenger',0,80),('mail',2,86),('coal',14,101),('goods',5,92)]:
            case(f'{label}_{cargo}_4_nars',g,e,'44440302',w,4,cid)
    for label,g,e in [('st43_pts','4D560103',134),('st43_prsp','4D560105',330),('et21_pts','4D560103',147),('et21_prsp','4D560105',570),('eu07_pts','4D560103',148),('eu07_prsp','4D560105',620),('class66_uk','44441000',91),('class66_gets','53410808',2660)]:
        # Same baseline coal wagons across locomotives; era availability/refits
        # and cross-set attachment are tested, not presumed.
        for n in (4,12,24):case(f'{label}_coal_{n}',g,e,'44440302',101,n,14)
        case('solo_'+label,g,e,c=-1)
    for label,g,e in [('en57_pts','4D560103',161),('en57_prsp','4D560105',1800),('en71_pts','4D560103',162),('en71_prsp','4D560105',2100),('ed72_pts','4D560103',163),('ed72_prsp','4D560105',2200)]:case(label,g,e)
    # Include earliest available express locomotive and heavy freight/MU cases
    # selected by actual roster attributes, not invented wagon/engine names.
    for g in ('53410808','44441000','44440302','4D560103','4D560105','4E4D0518'):
        choices=[r for r in rows if r['source_grfid']==g and r['category']=='locomotive_or_powered_unit' and r['power_hp']!='UNVERIFIED' and int(r['introduction_year'])<=2025]
        if choices:
            best=max(choices,key=lambda r:int(r['power_hp']))
            case('heavy_'+g,g,int(best['local_vehicle_id']),'44440302',101,24,14)
    def nut(v):
        return '"'+v+'"' if isinstance(v,str) else str(v)
    calibration=list(dict.fromkeys(c['engine'] for c in cases))
    groups={g:[int(r['runtime_engine_id']) for r in rows if r['source_grfid']==g and r['category'] not in ('ship','wagon')] for g in ('53410808','44441000','44440302','4D560103','4D560105','4E4D0518')}
    wagons=sorted([r for r in rows if r['category']=='wagon'],key=lambda r:(r['source_grfid']!='44440302',-int(r['introduction_year']),int(r['local_vehicle_id'])))
    (RUN/'game/phase2/cases.nut').write_text('TEST_CASES <- [\n'+',\n'.join('{'+','.join(k+'='+nut(c[k]) for k in ('key','engine','wagon','n','cargo'))+'}' for c in cases)+'\n];\nCALIBRATION_ENGINES <- '+json.dumps(calibration)+';\nSET_GROUPS <- {'+','.join('['+json.dumps(g)+']='+json.dumps(v) for g,v in groups.items())+'};\nWAGON_CANDIDATES <- '+json.dumps([int(r['runtime_engine_id']) for r in wagons])+';\n')
    (RUN/'cases.json').write_text(json.dumps(cases,indent=2))
    return cases

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--exe',type=Path,default=Path(r'C:\Users\Kladd\Downloads\OpenTTD\openttd.exe'));ap.add_argument('--years',type=int,nargs='+',default=[1830,1849,1879,1913,1945,1970,1990,2025]);ap.add_argument('--ticks',type=int,default=120000);ap.add_argument('--tag',default='final');args=ap.parse_args()
    prepare()
    baseline=(PYTHON/'.vehicle-audit-runtime/probe.cfg').read_text(encoding='utf8')
    campaign=json.loads((PYTHON/'docs/research/scenario_economy_settings.json').read_text())['PATS'][0]
    section='';differences=[];lines=[]
    for line in baseline.splitlines():
        if line.startswith('['):section=line.strip('[]')
        if ' = ' in line:
            key,value=line.split(' = ',1);full=section+'.'+key
            if full in campaign and isinstance(campaign[full],int) and section!='locale':
                cv=campaign[full]
                value_new=('true' if cv else 'false') if value in ('true','false') else str(cv)
                if value_new!=value:differences.append(dict(setting=full,phase1_config=value,campaign=cv))
                line=key+' = '+value_new
        lines.append(line)
    baseline='\n'.join(lines)+'\n'
    (RUN/'config-corrections.json').write_text(json.dumps(differences,indent=2))
    baseline=re.sub(r'\[game_scripts\][\s\S]*?(?=\n\[|\Z)','[game_scripts]\nVehicleEconomyPhase2 = \n',baseline)
    # Flat, small disposable layout for reliable depot construction; economics
    # and all 15 GRF identities/parameters remain those of the original probe.
    changes={'map_x':7,'map_y':7,'land_generator':0,'terrain_type':0,'quantity_sea_lakes':0,'tree_placer':0,'autosave_on_exit':'false','autosave_interval':0,'survey_participation':'false'}
    for key,value in changes.items():baseline=re.sub(r'(?m)^'+key+r' = .*$',f'{key} = {value}',baseline)
    for year in args.years:
        config=re.sub(r'(?m)^starting_year = .*$',f'starting_year = {year}',baseline)
        name=f'phase2-{args.tag}-{year}.cfg';(RUN/name).write_text(config,encoding='utf8')
        log=RUN/f'phase2-{args.tag}-{year}.log'
        if log.exists():raise SystemExit(f'Refusing to overwrite {log}; rename prior experiment first')
        with log.open('wb') as f:
            command=[str(args.exe.resolve()),'-c',name,'-x','-v',f'null:ticks={args.ticks}','-s','null','-m','null','-d','script=4,grf=5','-G','1830','-g']
            proc=subprocess.Popen(command,cwd=RUN,stdout=f,stderr=f)
            try:rc=proc.wait(timeout=180)
            except subprocess.TimeoutExpired:proc.kill();proc.wait();rc='TIMEOUT'
        print(year,rc,log,flush=True)
if __name__=='__main__':main()
