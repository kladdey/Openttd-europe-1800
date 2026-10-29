"""Bounded reviewed port placement trials using supported JGRPP commands.

No source modifications. Each trial must pass map guards before promotion.
"""
import json
import numpy as np
from coastal_phase6_runtime import BASE,run


def script(rows,attempt=0):
    terrain=np.load(BASE/'types.npy');height=np.load(BASE/'heights.npy')
    out=['class CoastalProbe extends GSController {function Start(){while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);']
    for r in rows:
        x,y=r['seed_x'],r['seed_y'];options=[]
        for dx in range(-8,9):
            for dy in range(-8,9):
                if abs(dx)+abs(dy)>10:continue
                xx,yy=x+dx,y+dy
                if terrain[yy,xx] not in (0,4):continue
                flat=int(np.count_nonzero(height[yy-4:yy+5,xx-4:xx+5]!=height[yy,xx]))
                options.append((flat*3+abs(dx)+abs(dy),xx,yy))
        options.sort();options=options[attempt*5:attempt*5+5]
        name=json.dumps(r['name'],ensure_ascii=False)
        out.append('{local ok=false;')
        for _,xx,yy in options:
            out.append(f'if(!ok){{ok=GSTown.FoundTown(GSMap.GetTileIndex({xx},{yy}),1,false,GSTown.ROAD_LAYOUT_ORIGINAL,{name});if(ok)GSLog.Info("C6 PLACED|"+{name}+"|{xx}|{yy}");}}')
        out.append('}')
    out.append('foreach(t,_ in GSTownList())if(t>=613)GSLog.Info("C6 NEW|"+t+"|"+GSTown.GetName(t)+"|"+GSTown.GetPopulation(t));GSLog.Info("C6 DONE");while(true)Sleep(365);}}')
    return '\n'.join(out)


if __name__=='__main__':
    rows=json.loads((BASE/'proposals.json').read_text())
    s=script(rows);(BASE/'bounded-placement.nut').write_text(s,encoding='utf8')
    run(s,'bounded-placement',1000)
