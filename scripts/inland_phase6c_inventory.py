"""Read-only town/house inventory and a bounded low-impact retail proof."""
import argparse,csv,hashlib,json,re
import numpy as np
from inland_phase6c_runtime import ROOT,BASE,SOURCE,run,sha
from coastal_phase6_preservation import parts,maps
from transport_phase4 import squirrel

ENGINE_SRC=ROOT.parent/'openttd-europe-1830-2025-historical-industry/.research/jgr734/src'


def houses():
    m=maps(parts(SOURCE));types=np.frombuffer(m['MAPT'],dtype='u1')>>4
    tiles=np.flatnonzero(types==3)
    owners=np.frombuffer(m['MAP2'],dtype='>u2');ids=np.frombuffer(m['MAP8'],dtype='>u2')&4095
    complete=(np.frombuffer(m['M3LO'],dtype='u1')&128)!=0
    protected=(np.frombuffer(m['M3LO'],dtype='u1')&32)!=0
    text=(ENGINE_SRC/'table/town_land.h').read_text()
    spec={}
    # Delimit by the explicit house-ID comments, preserving nested HouseZones.
    for match in re.finditer(r'\bMS\(\s*[^,]+,\s*[^,]+,\s*(\d+),([\s\S]*?)//\s*([0-9A-Fa-f]{2})\b',text):
        pop,block,id_=match.groups();spec[int(id_,16)]=dict(population=int(pop),one_tile='BuildingFlag::Size1x1' in block,ordinary=not any(k in block for k in ['IsChurch','IsStadium','IsProtected','NAME_PARK','NAME_STATUE','NAME_FOUNTAIN']),building_name=re.search(r'STR_TOWN_BUILDING_NAME_[A-Z0-9_]+',block).group(0))
    assert len(spec)==110,len(spec)
    rows=[]
    for tile in tiles:
        id_=int(ids[tile]);assert id_ in spec,('Unrecognized / NewGRF house',id_)
        h=spec[id_]
        if not h['one_tile'] or not h['ordinary'] or protected[tile]:continue
        x=int(tile%4096);y=int(tile//4096)
        road=any(types[tile+d]==2 for d in [-1,1,-4096,4096])
        if not road:continue
        rows.append(dict(tile=int(tile),x=x,y=y,town_id=int(owners[tile]),house_id=id_,estimated_population_loss=h['population'] if complete[tile] else 0,completed=bool(complete[tile])))
    return rows,spec


def main():
    p=argparse.ArgumentParser();p.add_argument('--proof',action='store_true');args=p.parse_args();BASE.mkdir(exist_ok=True)
    rows,spec=houses();(BASE/'house-sites.json').write_text(json.dumps(rows))
    (ROOT/'docs/research/inland_house_specifications.json').write_text(json.dumps(dict(engine_source=str(ENGINE_SRC/'table/town_land.h'),engine_source_sha256=sha(ENGINE_SRC/'table/town_land.h'),method='Vanilla house IDs from MAP8 & 0xfff; town index from MAP2; completed/protected M3LO bits 7/5, per JGRPP 0.73.4 town_map.h. Only ordinary 1x1 houses; no NewGRF houses assumed.',houses=spec),indent=2))
    script='''class CoastalProbe extends GSController {function Start(){while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
foreach(t,_ in GSTownList())GSLog.Info("M6 TOWN|"+t+"|"+GSTown.GetName(t)+"|"+GSTown.GetLocation(t)+"|"+GSTown.GetPopulation(t));
foreach(id in [57,59,61]){local type=GSIndustryType.ResolveNewGRFID(0x4B484531,id),accept="";foreach(c,_ in GSIndustryType.GetAcceptedCargo(type))accept+=GSCargo.GetCargoLabel(c)+",";local deity=GSIndustryType.CanBuildIndustry(type),company=false;{local cm=GSCompanyMode(0);company=GSIndustryType.CanBuildIndustry(type);}GSLog.Info("M6 TYPE|"+id+"|"+type+"|"+deity+"|"+company+"|"+accept);}
GSLog.Info("C6 DONE inland inventory");while(true)Sleep(365);}}'''
    home=run(script,'inventory');log=(home/'engine.log').read_text(encoding='utf8')
    towns=[]
    for tid,name,tile,pop in re.findall(r'M6 TOWN\|(\d+)\|([^|]+)\|(\d+)\|(\d+)',log):
        towns.append(dict(town_id=int(tid),name=name,tile=int(tile),x=int(tile)%4096,y=int(tile)//4096,population=int(pop)))
    assert len(towns)==617
    (BASE/'towns.json').write_text(json.dumps(towns,indent=2,ensure_ascii=False),encoding='utf8')
    print('Towns',len(towns),'eligible 1x1 road-adjacent house sites',len(rows),'towns with sites',len({r['town_id'] for r in rows}))
    print('\n'.join(l for l in log.splitlines() if 'M6 TYPE|' in l))
    if not args.proof:return
    town=next(t for t in towns if t['name']=='LONDON')
    sites=sorted([r for r in rows if r['town_id']==town['town_id'] and r['estimated_population_loss']<=town['population']*.05],key=lambda r:(r['estimated_population_loss'],abs(r['x']-town['x'])+abs(r['y']-town['y'])))[:80]
    script='SITES <- '+squirrel(sites)+'; TOWN <- '+str(town['town_id'])+';\n'+'''class CoastalProbe extends GSController {function Start(){
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSCompany.ChangeBankBalance(0,1000000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
local cm=GSCompanyMode(0),type=GSIndustryType.ResolveNewGRFID(0x4B484531,61),before=GSTown.GetPopulation(TOWN);
foreach(s in SITES){if(!GSTile.IsHouseTile(s.tile))continue;
 if(GSIndustryType.BuildIndustry(type,s.tile)){local id=-1;foreach(i,_ in GSIndustryList())if(i>=467){id=i;break;}
  local after=GSTown.GetPopulation(TOWN);GSLog.Info("M6 PROOF|"+id+"|"+s.tile+"|"+s.house_id+"|"+s.estimated_population_loss+"|"+before+"|"+after);
  foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)=="FOOD" || GSCargo.GetCargoLabel(c)=="GOOD")GSLog.Info("M6 ACCEPT|"+GSCargo.GetCargoLabel(c)+"|"+GSIndustry.IsCargoAccepted(id,c));
  GSLog.Info("C6 DONE replacement proof");while(true)Sleep(365);
 }
 GSLog.Info("M6 PROOF_RETRY|"+s.tile+"|"+GSError.GetLastErrorString());
}throw "No low-impact site accepted";}}'''
    proof=run(script,'proof');text=(proof/'engine.log').read_text(encoding='utf8');assert 'C6 DONE replacement proof' in text,text[-3000:]
    (BASE/'proof.json').write_text(json.dumps(dict(case=str(proof),town=town,events=[l.split('M6 ',1)[1] for l in text.splitlines() if 'M6 ' in l]),indent=2))
    print('\n'.join(l for l in text.splitlines() if 'M6 PROOF|' in l or 'M6 ACCEPT|' in l))


if __name__=='__main__':main()
