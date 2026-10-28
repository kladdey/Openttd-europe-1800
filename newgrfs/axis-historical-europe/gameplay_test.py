# SPDX-License-Identifier: GPL-2.0-only
"""Reuse Phase 4 route builder on fresh historical worlds, never the campaign.

Selects actual generated compatible industries/towns. Failures are retained as
BLOCKED, not payment estimates. Settings come from the measured embedded PATS.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from integration_test import ROOT, REPO, setup, sha
sys.path.insert(0, str(REPO / 'scripts'))
import transport_phase4 as p4

CASES = {
 'coal_rail': ('rail', 'COAL', 0, 78, 1534, 1),
 'grain_horse': ('road', 'GRAI', 26, 34, 402, 4),
 'iron_horse': ('road', 'IRON', 7, 21, 402, 4),
 'timber_rail': ('rail', 'WOOD', 11, 12, 1534, 1),
 'passenger_horse': ('road', 'PASS', -1, -1, 147, 2),
 'passenger_ship': ('ship', 'PASS', -1, -1, 616, 1),
}

PICKER = '''
 function CoastalSite(town,cargo){
  local center=GSTown.GetLocation(town),x=GSMap.GetTileX(center),y=GSMap.GetTileY(center);
  for(local dx=-14;dx<=14;dx++)for(local dy=-14;dy<=14;dy++){
   local tx=x+dx,ty=y+dy;
   if(tx<3 || ty<3 || tx>=GSMap.GetMapSizeX()-3 || ty>=GSMap.GetMapSizeY()-3)continue;
   local tile=GSMap.GetTileIndex(tx,ty);
   if(!GSTile.IsCoastTile(tile) || GSTile.GetCargoAcceptance(tile,cargo,1,1,5)<8 || GSTile.GetCargoProduction(tile,cargo,1,1,5)==0)continue;
   {local cm=GSCompanyMode(0),tm=GSTestMode(),ok=GSMarine.BuildDock(tile,GSStation.STATION_NEW);tm=null;if(!ok)continue;}
   foreach(d in [[1,0],[-1,0],[0,1],[0,-1]]){
    local w=GSMap.GetTileIndex(tx+d[0],ty+d[1]),far=GSMap.GetTileIndex(tx+2*d[0],ty+2*d[1]);
    if(!GSTile.IsWaterTile(w) || !GSTile.IsWaterTile(far))continue;
    local builder=RouteBuilder(),component=builder.WaterComponent(far,GSMap.TILE_INVALID);
    if(component.len()>1000){SHIP_TILES[town]<-tile;AHE5_SHIP_WATER[town]<-far;SHIP_COMPONENTS[town]<-component;return true;}
   }
  }
  return false;
 }
 function Fixture(type,x0,y0){
  for(local y=y0;y<y0+30;y+=6)for(local x=x0;x<x0+30;x+=6){
   if(GSIndustryType.BuildIndustry(type,GSMap.GetTileIndex(x,y)))return true;
  }
  return false;
 }
 function SelectRoute(){
  local cargo=-1;foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)=="LABEL")cargo=c;
  if(cargo<0)throw "missing cargo";
  local cfg=CONFIG.routes[0];cfg.cargo=cargo;
  local from=[],to=[];
  if(cfg.endpoints=="industry"){
   local st=GSIndustryType.ResolveNewGRFID(0x4B484531,SOURCE);
   local dt=GSIndustryType.ResolveNewGRFID(0x4B484531,DESTINATION);
   if(CONTROLLED){
    local a=Fixture(st,35,35),b=Fixture(dt,90,35);
    GSLog.Info("AHE5G FIXTURE source="+a+" destination="+b);
   }
   foreach(i,_ in GSIndustryList()){
    local t=GSIndustry.GetIndustryType(i);
    if(t==st)from.append(i);if(t==dt)to.append(i);
   }
  }else{
   foreach(t,_ in GSTownList()){
    local okay=cfg.mode!="ship";
    if(!okay && cfg.mode=="ship")okay=CoastalSite(t,cargo);
    if(!okay && cfg.mode!="ship"){
     local center=GSTown.GetLocation(t),x=GSMap.GetTileX(center),y=GSMap.GetTileY(center);
     for(local dx=-14;dx<=14 && !okay;dx++)for(local dy=-14;dy<=14;dy++){
      if(x+dx<1 || y+dy<1 || x+dx>=GSMap.GetMapSizeX()-1 || y+dy>=GSMap.GetMapSizeY()-1)continue;
      local tile=GSMap.GetTileIndex(x+dx,y+dy);
      if(GSTile.IsCoastTile(tile) && GSTile.GetCargoAcceptance(tile,cargo,1,1,5)>=8 && GSTile.GetCargoProduction(tile,cargo,1,1,5)>0){okay=true;break;}
     }
    }
    if(okay){from.append(t);to.append(t);}
   }
  }
  local distance=100000,found=false;
  foreach(a in from)foreach(b in to){
   if(a==b)continue;
   if(cfg.mode=="ship" && !(AHE5_SHIP_WATER[b] in SHIP_COMPONENTS[a]))continue;
   if(cfg.mode=="ship" && GSMap.DistanceManhattan(SHIP_TILES[a],SHIP_TILES[b])<15)continue;
   local at=cfg.endpoints=="industry"?GSIndustry.GetLocation(a):GSTown.GetLocation(a);
   local bt=cfg.endpoints=="industry"?GSIndustry.GetLocation(b):GSTown.GetLocation(b);
   local d=GSMap.DistanceManhattan(at,bt);
   if(d<distance && d>=12){distance=d;cfg.a=a;cfg.b=b;found=true;}
  }
  if(!found){GSLog.Info("AHE5G BLOCKED no eligible endpoint pair");return false;}
  GSLog.Info("AHE5G SELECT|"+cfg.mode+"|LABEL|"+cfg.a+"|"+cfg.b+"|"+distance);
  return true;
 }
'''


def config_text(grfs, seed, sea):
    measured=json.loads((REPO/'docs/research/scenario_economy_settings.json').read_text())['PATS'][0]
    groups={}
    # Preserve scalar economic/operating settings. Arrays and scenario-only
    # fields are excluded and the complete config is retained in each fixture.
    for key,value in measured.items():
        if key.split('.')[0] not in {'economy','difficulty','vehicle','construction','linkgraph'}:continue
        if '[' in key or not isinstance(value,(int,float,bool,str)):continue
        group,name=key.split('.',1);groups.setdefault(group,{})[name]=value
    groups.setdefault('game_creation',{}).update(map_x=8,map_y=8,generation_seed=seed,land_generator=0,starting_year=1830,custom_town_number=20)
    groups['difficulty'].update(quantity_sea_lakes=sea,terrain_type=0,number_towns=4)
    groups['vehicle']['max_train_length']=7
    groups['economy']['infrastructure_maintenance']='true'
    groups['gui']=dict(autosave_interval=0,autosave_on_exit='false')
    text=''
    for group,settings in groups.items():
        text+=f'[{group}]\n'+''.join(f'{k} = {v}\n' for k,v in settings.items())
    return text+'[newgrf]\n'+'\n'.join(grfs)+'\n[game_scripts]\nTransportPhase3 =\n'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--case',choices=CASES)
    ap.add_argument('--controlled', action='store_true', help='Flat, industry-free starting map; construct eligible fixture endpoints')
    ap.add_argument('--stock', action='store_true', help='Matched stock AXIS control, same spawning/test settings')
    args=ap.parse_args()
    engine,base,grfs,artifact,original,ref=setup()
    if args.stock:
        grfs=[line if not line.startswith('axis-historical-europe-') else
              '4A4B8808|B580AE20D12247F3A7EDD28FADC6F2E5|4a4b8808-axis_extreme_industry_set-2.3.1.tar\\axis_extreme_industry_set-2.3.1\\axis_2.3.1.grf = 0 0 4 0 0 0 16 150 80 300' for line in grfs]
    results=[]
    for name,(mode,label,source,dest,eng,fleet) in CASES.items():
        if args.case and args.case!=name:continue
        case=base/(name+'-'+str(time.time_ns()));case.mkdir()
        for folder in ['baseset','newgrf']:shutil.copytree(base/folder,case/folder,copy_function=os.link)
        shutil.copytree(REPO/'.vehicle-audit-runtime/phase2/ai',case/'ai')
        gs=case/'game/p3';gs.mkdir(parents=True)
        info=(REPO/'scripts/vehicle_phase2_probe/info.nut').read_text().replace('VehicleEconomyPhase2','TransportPhase3').replace('Phase2Probe','TransportProbe')
        (gs/'info.nut').write_text(info)
        cfg=p4.route(mode,0,0,0,eng,fleet,endpoints='town' if source<0 else 'industry',wagons=4,platform=4 if mode=='rail' else 2,brake=mode=='rail')
        main=p4.generate(dict(years=5,routes=[cfg]))
        main='SHIP_TILES <- {};\nAHE5_SHIP_WATER <- {};\nSHIP_COMPONENTS <- {};\n'+main
        main=main.replace(' function Candidates(id,production){',' function Candidates(id,production){\n  if(MODE=="ship" && id in SHIP_TILES)return [SHIP_TILES[id]];')
        if args.controlled and mode=='rail':
            # The inherited fixture connects outer station ends and places its
            # depot on the inner side. On a straight flat fixture this forms a
            # depot shuttle. Connect the facing ends and put the depot behind A.
            main=main.replace('Path(Step(origin_tile,-1,0),origin_tile,Step(tile,MODE=="rail"?PLATFORM:-1,0))',
                              'Path(Step(origin_tile,PLATFORM,0),Step(origin_tile,PLATFORM-1,0),Step(tile,-1,0))')
            main=main.replace('local start=Step(a,-1,0),previous=a,goal=MODE=="rail"?Step(b,PLATFORM,0):Step(b,-1,0);',
                              'local start=Step(a,PLATFORM,0),previous=Step(a,PLATFORM-1,0),goal=Step(b,-1,0);')
            main=main.replace('Step(goal,MODE=="rail"?-1:1,0)','Step(goal,1,0)')
            main=main.replace('(MODE=="rail"?Step(b,PLATFORM-1,0):b)','b')
            main=main.replace('depot=Step(a,PLATFORM+1,0);local f=Step(a,PLATFORM,0);',
                              'depot=Step(a,-2,0);local f=Step(a,-1,0);')
        picker=PICKER.replace('LABEL',label).replace('SOURCE',str(source)).replace('DESTINATION',str(dest)).replace('CONTROLLED',str(args.controlled).lower())
        marker=' function Start(){\n  local count=CONFIG.routes.len()'
        assert main.count(marker)==1
        main=main.replace(marker,picker+' function Start(){\n  while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(2);\n  if(!SelectRoute()){GSLog.Info("P4_DONE");while(true)Sleep(10000);}\n  local count=CONFIG.routes.len()')
        main=main.replace('end=1800+CONFIG.years','end=1830+CONFIG.years')
        if args.stock:main=main.replace('0x4B484531','0x4A4B8808')
        (gs/'main.nut').write_text(main)
        (case/'scripts').mkdir();(case/'scripts/game_start.scr').write_text('start_ai EconomyBootstrap\n')
        config=config_text(grfs,734,2 if mode=='ship' else 0)
        load=[]
        if args.controlled:
            from PIL import Image
            image=case/'fixture.png';Image.new('L',(256,256),255).save(image);load=[str(image)]
            config=config.replace('industry_density = 4','industry_density = 0')
            config=config.replace('[game_creation]','[game_creation]\nheightmap_height = 16')
        (case/'test.cfg').write_text(config)
        log=case/'engine.log';command=[str(engine),'-X','-x','-c',str(case/'test.cfg'),'-g']+load+['-v','null:ticks=240000','-s','null','-m','null','-d','script=4']
        start=time.monotonic()
        with log.open('w') as f:
            process=subprocess.Popen(command,cwd=case,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                while process.poll() is None and time.monotonic()-start<180:
                    if 'P4_DONE' in log.read_text(errors='replace'):break
                    time.sleep(.25)
            finally:
                if process.poll() is None:process.terminate()
                process.wait(timeout=10)
        lines=[s for s in log.read_text(errors='replace').splitlines() if any(x in s for x in ['AHE5G','P4_YEAR','P4_COMMISSION','P4_BLOCKED','P3_BLOCKED','P4_BUILT','P4_DONE','P4_START','P4_NO_SERVICE'])]
        rows=[]
        for line in lines:
            if 'P4_YEAR|' in line:
                parts=line.split('P4_YEAR|')[1].split('|');ledger=[int(v) for v in parts[8].strip(',').split(',')]
                rows.append(dict(year=int(parts[1]),cash=int(parts[2]),loan=int(parts[3]),delivered=int(parts[5]),vehicle_profit=int(parts[7]),ledger=ledger))
        # Native ledger indices: running 2..5, Property 6, revenue 7..10,
        # interest 11, Other 12, sharing cost/income 13/14.
        paid=any(any(r['ledger'][i]<0 for i in range(7,11)) and r['delivered']>0 for r in rows)
        result=dict(case=name,controlled=args.controlled,stock_control=args.stock,mode=mode,cargo=label,evidence='VERIFIED BY ENGINE TEST' if paid else 'BLOCKED',
                    paid_delivery_verified=paid,lines=lines,years=rows,log=str(log.relative_to(ROOT)),
                    log_sha256=sha(log),settings_sha256=sha(case/'test.cfg'),script_sha256=sha(gs/'main.nut'))
        results.append(result);print(name,result['evidence'],len(rows),flush=True)
    report=dict(engine_sha256=sha(engine),grf_sha256=sha(artifact),results=results,
                limitations='Fresh 256x256 geography; inherited scalar PATS settings, changed map generation. No matched geographic baseline or multiplayer network test.')
    output=ROOT/(('stock-' if args.stock else '')+('gameplay-controlled' if args.controlled else 'gameplay')+('-'+args.case if args.case else '')+'-result.json')
    output.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
