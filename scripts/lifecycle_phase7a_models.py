"""Independently compare every enabled model/recipe/layout in all six economies."""
import json,subprocess,sys
from lifecycle_phase7a_runtime import ROOT,BASE,GRF,sha,guards

if __name__=='__main__':
    guards();snapshots=[]
    for name,source in [('base',ROOT/'newgrfs/axis-historical-copper-salt/.work/source'),('candidate',ROOT/'newgrfs/axis-historical-lifecycle/.work/source')]:
        target=BASE/(name+'-models.json')
        subprocess.run([sys.executable,str(ROOT/'newgrfs/axis-historical-europe/model_snapshot.py'),str(source),str(target)],check=True)
        snapshots.append(json.loads(target.read_text(encoding='utf8')))
    assert snapshots[0]==snapshots[1],'Industry model/cargo order changed'
    result=dict(evidence='SOURCE MODEL VALIDATION; not a runtime test of all six economies',all_models_recipes_properties_layouts_cargo_ids_identical=True,
        economies={k:dict(industries=len(v['industries']),cargos=len(v['cargo_ids'])) for k,v in snapshots[1].items()},
        grf_sha256=sha(GRF),scope='Generated availability/location and coal monthly closure callbacks intentionally differ; unchanged models do not mean identical compiled callbacks')
    (ROOT/'docs/research/phase7a_model_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
