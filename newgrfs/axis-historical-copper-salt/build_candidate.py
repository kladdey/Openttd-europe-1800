# SPDX-License-Identifier: GPL-2.0-only
"""Build separately from the immutable 0.2.0 source/artifact; never install."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'axis-historical-europe'
M=json.loads((ROOT/'candidate_manifest.json').read_text(encoding='utf8'))


def main():
    assert hashlib.sha256((BASE/'dist/axis-historical-europe-0.2.0.grf').read_bytes()).hexdigest()==M['base_grf_sha256']
    source=ROOT/'.work/source'
    rebuild='--rebuild' in sys.argv
    if source.exists() and not rebuild:raise SystemExit('Refusing to overwrite prepared candidate source; --rebuild archives the prior compiled candidate')
    source.parent.mkdir(parents=True,exist_ok=True)
    if not source.exists():shutil.copytree(BASE/'.work/source',source,ignore=shutil.ignore_patterns('generated','__pycache__','.cache'))
    shutil.copyfile(ROOT/'overlay/new_industries.py',source/'src/historical_copper_salt.py')
    shutil.copyfile(ROOT/'candidate_manifest.json',source/'src/copper_salt_manifest.json')
    shutil.copyfile(ROOT/'overlay/produce_historical_batch.pynml',source/'src/templates/produce_historical_batch.pynml')
    init=(BASE/'.work/source/src/industries/__init__.py').read_text(encoding='utf8')
    (source/'src/industries/__init__.py').write_text(init+'\n# Append-only Historical Europe 0.3.0 candidate.\nimport historical_copper_salt\n',encoding='utf8')
    secondary=(source/'src/templates/industry_secondary.pynml').read_text(encoding='utf8').replace('load: produce_secondary.pynml','load: produce_historical_batch.pynml')
    for callback in ['produce_cargo_arrival','produce_256_ticks']:
        secondary=secondary.replace('${industry.id}_'+callback+';','${industry.id}_historical_batch;')
    secondary=secondary.replace('${industry.id}_extra_text;','return string(STR_HISTORICAL_BATCH_RECIPE);')
    secondary=secondary.replace('${industry.id}_cargo_subtype_display;','return CB_RESULT_NO_TEXT;')
    (source/'src/templates/industry_historical_batch.pynml').write_text(secondary,encoding='utf8')
    header=source/'src/templates/header.pynml';text=(BASE/'.work/source/src/templates/header.pynml').read_text(encoding='utf8');assert 'version: 2;' in text and 'min_compatible_version: 1;' in text
    header.write_text(text.replace('version: 2;','version: 3;').replace('min_compatible_version: 1;','min_compatible_version: 2;'),encoding='utf8')
    lang=source/'src/lang_templates/english.pylng';text=(BASE/'.work/source/src/lang_templates/english.pylng').read_text(encoding='utf8').replace('Historical Europe 0.2.0','Historical Europe 0.3.0 copper/salt candidate')
    text+='''\nSTR_IND_TRADITIONAL_COPPER_SMELTER :Traditional Copper Smelter
STR_IND_FISH_SALTERY :Fish Saltery
STR_IND_MEAT_SALTERY :Meat Curing House
STR_HISTORICAL_BATCH_RECIPE :Stockpiles every required input. Copper: 6 copper ore + 18 coal + 1 sand yields 1 copper + 4 slag. Fish or meat curing house: 3 fish or livestock, respectively, plus 1 salt yields 3 preserved food. Game batches, not chemical assays. No output from incomplete inputs.
'''
    lang.write_text(text,encoding='utf8')
    logs=ROOT/'.work/logs';logs.mkdir(exist_ok=True);dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    artifact=dist/'axis-historical-europe-0.3.0-candidate.grf'
    if artifact.exists():
        archive=dist/'archive';archive.mkdir(exist_ok=True)
        old=hashlib.sha256(artifact.read_bytes()).hexdigest();backup=archive/(old+'.grf')
        if not backup.exists():shutil.copyfile(artifact,backup)
    commands=[('language',[sys.executable,'src/render_lang.py']),('render',[sys.executable,'src/render_nml.py']),('compile',[sys.executable,'-m','nml.main','-c','-l','generated/lang','--verbosity=3','--grf='+str(artifact),'generated/firs.nml'])]
    for name,cmd in commands:
        print(name,flush=True)
        with (logs/(name+'.log')).open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=source,env={**os.environ,'PYTHONHASHSEED':'0'},stdout=f,stderr=subprocess.STDOUT,check=True)
    report=dict(artifact=str(artifact),bytes=artifact.stat().st_size,sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),base_0_2_unchanged=hashlib.sha256((BASE/'dist/axis-historical-europe-0.2.0.grf').read_bytes()).hexdigest()==M['base_grf_sha256'],compiled=True,runtime_verified=False)
    (dist/'build-result.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
