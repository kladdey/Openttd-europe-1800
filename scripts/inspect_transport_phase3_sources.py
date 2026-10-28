"""Record read-only source provenance and the installed AXIS parameter mask."""
import hashlib,json,tarfile
from pathlib import Path
from audit_vehicle_newgrfs import actions
from extract_vehicle_grf_parameters import nodes
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'docs/research'
SOURCE=ROOT.parent/'openttd-europe-1830-2025-historical-industry/.research'
def main():
    names=['jgr734/src/script/api/script_industrytype.cpp','jgr734/src/script/api/script_date.cpp','jgr734/src/script/api/script_company.cpp','jgr734/src/script/api/script_vehicle.cpp','jgr734/src/company_cmd.cpp','jgr734/src/economy.cpp','axis/src/templates/header.pynml','axis/src/templates/availability.pynml']
    sources=[{'path':str(SOURCE/n),'sha256':hashlib.sha256((SOURCE/n).read_bytes()).hexdigest()} for n in names]
    g=next(g for g in json.loads((R/'newgrf_inventory.json').read_text())['installed_newgrfs'] if g.get('grfid')=='4A4B8808')
    with tarfile.open(g['path']) as tf:data=tf.extractfile(g['member']).read()
    meta=[]
    for offset,a in actions(data):
        if a and a[0]==20:nodes(a,1,'',meta)
    name=next(m for m in meta if m['path']=='/INFO/PARA/1/NAME' and m.get('language')==127)
    mask=next(m for m in meta if m['path']=='/INFO/PARA/1/MASK');assert mask['hex']=='020201'
    ref=next(r for r in json.loads((R/'scenario_vehicle_references.json').read_text())['references'] if r['grfid']=='4A4B8808')
    result={'local_sources':sources,'installed_axis_grfid':'4A4B8808','installed_axis_sha256':hashlib.sha256(data).hexdigest(),'parameter_name':name['text'],'parameter_mask_hex':mask['hex'],'decoded_mask':{'parameter':2,'first_bit':2,'number_of_bits':1},'saved_parameter_value':ref['params'][2],'effective_allow_spawning':bool(ref['params'][2]&(1<<2)),'official_clock_source':'https://github.com/JGRennison/OpenTTD-patches/blob/jgrpp-0.73.4/src/script/api/script_date.cpp'}
    (R/'transport_source_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='local_sources'},indent=2))
if __name__=='__main__':main()
