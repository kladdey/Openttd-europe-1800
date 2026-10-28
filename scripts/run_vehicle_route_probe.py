"""Attempt real early coal service. Isolated files only; never load a save."""
from pathlib import Path
import re,shutil,subprocess,argparse
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--engine',type=int,default=1534);ap.add_argument('--year',type=int,default=1830);ap.add_argument('--tag',default='attempt1');args=ap.parse_args()
    source=ROOT/'.vehicle-audit-runtime/phase2';run=ROOT/'.vehicle-audit-runtime/route';run.mkdir(parents=True,exist_ok=True)
    for folder in ('newgrf','ai','scripts'):
        if not (run/folder).exists():shutil.copytree(source/folder,run/folder)
    gs=run/'game/route';gs.mkdir(parents=True,exist_ok=True)
    info=(ROOT/'scripts/vehicle_phase2_probe/info.nut').read_text().replace('VehicleEconomyPhase2','VehicleRouteProbe').replace('Phase2Probe','RouteProbe')
    (gs/'info.nut').write_text(info);(gs/'main.nut').write_text(f'ROUTE_ENGINE <- {args.engine};\n'+(ROOT/'scripts/vehicle_route_probe.nut').read_text())
    cfg=(source/'phase2-verified-1830.cfg').read_text().replace('VehicleEconomyPhase2','VehicleRouteProbe')
    for key,value in {'map_x':8,'map_y':8,'starting_year':args.year}.items():cfg=re.sub(r'(?m)^'+key+r' = .*$',f'{key} = {value}',cfg)
    (run/'route.cfg').write_text(cfg)
    log=run/f'route-{args.engine}-{args.year}-{args.tag}.log'
    if log.exists():raise SystemExit('Refusing to overwrite '+str(log))
    with log.open('wb') as out:
        p=subprocess.Popen([r'C:\Users\Kladd\Downloads\OpenTTD\openttd.exe','-c','route.cfg','-x','-v','null:ticks=90000','-s','null','-m','null','-d','script=4','-G','1830','-g'],cwd=run,stdout=out,stderr=out)
        try:print('Exit',p.wait(timeout=150),log)
        except subprocess.TimeoutExpired:p.kill();p.wait();print('Timeout',log)
if __name__=='__main__':main()
