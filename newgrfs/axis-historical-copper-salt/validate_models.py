# SPDX-License-Identifier: GPL-2.0-only
"""Compare every enabled industry in every economy against immutable 0.2.0."""
import hashlib,json,subprocess,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    base=HERE.parent/'axis-historical-europe';work=HERE/'.work';snapshots=[]
    for name,source in [('base',base/'.work/source'),('candidate',work/'source')]:
        out=work/(name+'-models.json')
        subprocess.run([sys.executable,str(base/'model_snapshot.py'),str(source),str(out)],check=True)
        snapshots.append(json.loads(out.read_text(encoding='utf8')))
    a,b=snapshots;changes={}
    for economy,old in a.items():
        new=b[economy]
        assert old['cargo_ids']==new['cargo_ids'] and old['cargo_labels']==new['cargo_labels'],economy
        assert len(new['cargo_labels'])<=64
        changed=[id_ for id_,definition in old['industries'].items() if new['industries'].get(id_)!=definition]
        assert not changed,(economy,changed)
        added=sorted(set(new['industries'])-set(old['industries']))
        assert added==(sorted(['salt_mine','traditional_copper_smelter','fish_saltery','meat_saltery']) if economy=='BASIC_TEMPERATE' else []),(economy,added)
        changes[economy]=dict(changed_existing=changed,added=added)
    result=dict(all_existing_industry_models_identical=True,all_economy_cargo_orders_identical=True,changes=changes,base_grf_sha256=hashlib.sha256((base/'dist/axis-historical-europe-0.2.0.grf').read_bytes()).hexdigest(),candidate_grf_sha256=hashlib.sha256((HERE/'dist/axis-historical-europe-0.3.0-candidate.grf').read_bytes()).hexdigest(),method='Separate interpreter evaluation of trusted prepared source; every enabled old model/property/recipe/layout in all six economies. This is not a claim that globally generated neighbour checks are byte-identical after registering new types.')
    (ROOT/'docs/research/copper_salt_source_preservation.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
