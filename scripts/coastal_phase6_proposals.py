"""Bounded seed calibration and labelled local map evidence; never found towns."""
import json
import math
import numpy as np
from PIL import Image,ImageDraw
from coastal_phase6_analysis import ROOT,BASE,key,write


def project(lat,lon):return np.array([4095-(104.42263446189997*lon+1379.7176323206816),-164.09816527178702*lat+9729.142746398953])


def main():
    towns=json.loads((BASE/'towns.json').read_text())
    config=json.loads((ROOT/'data/geography/phase6a_port_candidates.json').read_text())
    types=np.load(BASE/'types.npy');height=np.load(BASE/'heights.npy')
    images=BASE/'coordinate-review';images.mkdir(exist_ok=True)
    rows=[]
    for c in config['records']:
        direct=project(c['lat'],c['lon'])
        anchors=[]
        for t in towns:
            if t['latitude']=='UNVERIFIED' or t['longitude']=='UNVERIFIED':continue
            p=project(float(t['latitude']),float(t['longitude']))
            distance=float(np.linalg.norm(p-direct))
            if distance<230:anchors.append((distance,t,np.array([t['x'],t['y']])-p))
        anchors=sorted(anchors,key=lambda a:a[0])[:4]
        # Only small residual correction from actual nearby towns, never a
        # continent-wide least squares fit or a nearest-land displacement.
        if anchors:
            weights=np.array([1/max(12,a[0])**2 for a in anchors]);residual=np.average([a[2] for a in anchors],axis=0,weights=weights)
            residual=np.clip(residual,-8,8)
        else:residual=np.zeros(2)
        corrected=direct+residual;x,y=map(lambda v:int(round(v)),corrected)
        nearest=min(towns,key=lambda t:abs(t['x']-x)+abs(t['y']-y))
        d=abs(nearest['x']-x)+abs(nearest['y']-y)
        c.update(seed_x=x,seed_y=y,global_seed_x=round(float(direct[0]),3),global_seed_y=round(float(direct[1]),3),
                 local_residual_x=round(float(residual[0]),3),local_residual_y=round(float(residual[1]),3),
                 calibration_anchors='; '.join(f'{a[1]["name"]}:{a[0]:.1f} tiles' for a in anchors),
                 nearest_existing_town=nearest['name'],nearest_existing_manhattan=d,
                 proposed_x=x,proposed_y=y,coordinate_status='REQUIRES LOCAL TERRAIN REVIEW',
                 reasoning='Historically documented missing port; bounded local-anchor calibration, no automatic nearest-land snapping')
        radius=55;crop=types[y-radius:y+radius+1,x-radius:x+radius+1]
        rgba=np.zeros((*crop.shape,3),dtype=np.uint8);rgba[:]=[125,160,100];rgba[crop==6]=[50,105,175]
        rgba[crop==3]=[220,190,90];rgba[crop==2]=[170,160,145];rgba[crop==4]=[55,110,55]
        im=Image.fromarray(rgba).resize((666,666),Image.Resampling.NEAREST);draw=ImageDraw.Draw(im)
        def point(tx,ty,color,label):
            px=(tx-(x-radius))*6+3;py=(ty-(y-radius))*6+3
            draw.ellipse((px-5,py-5,px+5,py+5),outline=color,width=2);draw.text((px+7,py),label,fill=color,stroke_width=1,stroke_fill='black')
        point(x,y,'red',f'{c["name"]} seed {x},{y}')
        for t in towns:
            if abs(t['x']-x)<=radius and abs(t['y']-y)<=radius:point(t['x'],t['y'],'yellow',t['name'])
        draw.text((4,4),'Map tiles: x increases right, y increases down. Blue=water. 6 pixels/tile.',fill='white',stroke_width=1,stroke_fill='black')
        file=images/(key(c['name'])+'.png');im.save(file);c['terrain_review_image']=str(file.relative_to(ROOT))
        c['seed_tile_type']=int(types[y,x]);c['seed_height']=int(height[y,x])
        rows.append(c)
    write('proposed_port_towns.csv',rows)
    (BASE/'proposals.json').write_text(json.dumps(rows,indent=2))
    for r in rows:print(r['name'],r['seed_x'],r['seed_y'],'type',r['seed_tile_type'],'near',r['nearest_existing_town'],r['nearest_existing_manhattan'])


if __name__=='__main__':main()
