"""Real ship movement and real dock/water-edge tests on the accepted copy."""
import csv,json
from pathlib import Path
import numpy as np
from coastal_phase6_runtime import BASE,ROOT,run


def main():
    result=json.loads((BASE/'implementation.json').read_text(encoding='utf8'))
    source=Path(result['candidate']);accepted=[r for r in result['decisions'] if r['status']=='ACCEPTED']
    ports={r['name']:dict(name=r['name'],tile=r['dock_tile']) for r in accepted}
    original=list(csv.DictReader((ROOT/'docs/research/existing_coastal_towns.csv').open(encoding='utf8')))
    for r in original:
        if int(r['practical_dock_tile'])>=0:ports.setdefault(r['name'],dict(name=r['name'],tile=int(r['practical_dock_tile'])))
    routes=[dict(name='British Isles',a='Falmouth',b='PLYMOUTH')]
    if 'Viana' in ports:routes.append(dict(name='Iberia',a='Viana',b='PORTO'))
    elif 'Setúbal' in ports:routes.append(dict(name='Iberia',a='Setúbal',b='LISBOA'))
    else:routes.append(dict(name='Iberia',a='PORTO',b='LISBOA'))
    if 'Tarragona' in ports:routes.append(dict(name='Mediterranean',a='Tarragona',b='BARCELONA'))
    elif 'Cette' in ports:routes.append(dict(name='Mediterranean',a='Cette',b='MARSEILLE'))
    else:routes.append(dict(name='Mediterranean',a='BARCELONA',b='MARSEILLE'))
    if 'Wismar' in ports:routes.append(dict(name='Baltic / North Sea',a='Wismar',b='Świnoujście'))
    else:routes.append(dict(name='Baltic / North Sea',a='Świnoujście',b='Kołobrzeg'))
    selected={r['name'] for r in accepted}|{r[k] for r in routes for k in ('a','b')}
    water=np.load(BASE/'water_components.npy');types=np.load(BASE/'types.npy');height=np.load(BASE/'heights.npy')
    tests=[]
    for name in sorted(selected):
        p=ports[name];x=p['tile']%4096;y=p['tile']//4096;options=[]
        for dx in range(-42,43):
            for dy in range(-42,43):
                d=abs(dx)+abs(dy);xx=x+dx;yy=y+dy
                if not 25<=d<=42 or not(3<xx<4093 and 3<yy<4093):continue
                if water[yy,xx]==3 and np.all(types[yy-2:yy+3,xx-2:xx+3]==6) and np.all(height[yy-2:yy+3,xx-2:xx+3]==0):options.append((d,xx,yy))
        if options:
            _,xx,yy=min(options);p['witness']=yy*4096+xx
        tests.append(p)
    constants='PORTS <- '+json.dumps(tests,ensure_ascii=False).replace('"name":','name=').replace('"tile":','tile=').replace('"witness":','witness=')+';\n'
    constants+='ROUTES <- '+json.dumps(routes,ensure_ascii=False).replace('"name":','name=').replace('"a":','a=').replace('"b":','b=')+';\n'
    script=constants+(ROOT/'scripts/coastal_phase6_shipping.nut').read_text(encoding='utf8')
    (BASE/'shipping-plan.json').write_text(json.dumps(dict(ports=tests,routes=routes),indent=2,ensure_ascii=False),encoding='utf8')
    home=run(script,'shipping',105000,source=source,unpaused=True)
    (BASE/'shipping-case.txt').write_text(str(home))


if __name__=='__main__':main()
