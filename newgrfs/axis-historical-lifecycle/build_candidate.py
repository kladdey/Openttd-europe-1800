# SPDX-License-Identifier: GPL-2.0-only
"""Separate 0.4.0 lifecycle candidate; preserves all 0.3.0 build inputs."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'axis-historical-copper-salt'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=ROOT/'.work/source'
    if source.exists():
        if '--rebuild' not in sys.argv:raise SystemExit('Refusing to overwrite prepared lifecycle candidate source')
        import time
        archive=source.parent/('source-previous-'+str(time.time_ns()))
        assert source.resolve().is_relative_to((ROOT/'.work').resolve()) and archive.resolve().is_relative_to((ROOT/'.work').resolve())
        shutil.move(str(source),str(archive))
    assert sha(BASE/'dist/axis-historical-europe-0.3.0-candidate.grf')=='f0da622873c91107fa4d2b768d88cd95d5db009c2b2975bdb6d7ab6caaed3c33'
    shutil.copytree(BASE/'.work/source',source,ignore=shutil.ignore_patterns('generated','__pycache__','.cache'))
    templates=source/'src/templates'
    p=templates/'header.pynml';s=p.read_text();assert 'version: 3;' in s
    s=s.replace('version: 3;','version: 4;').replace('min_compatible_version: 2;','min_compatible_version: 3;')
    s=s.replace('    param 10 {','''    param 11 {
        lifecycle_scheduler_mode {
            name: string(STR_PARAM_LIFECYCLE);
            desc: string(STR_PARAM_LIFECYCLE_DESC);
            type: bool;
            def_value: 0;
        }
    }
    param 10 {''');p.write_text(s)
    p=source/'src/lang_templates/english.pylng';s=p.read_text().replace('0.3.0 copper/salt candidate','0.4.0 lifecycle candidate')
    s+='\nSTR_PARAM_LIFECYCLE :Historical lifecycle scheduler contract (experimental)\nSTR_PARAM_LIFECYCLE_DESC :Default off. Classic historical mode only: authorize deity industry construction, reject natural RandomCreation at location checks. Deity-founded coal mines reserve production level 4 for explicit closure. Requires matching Historical Industry Lifecycle GameScript and a new separate scenario.\n'
    p.write_text(s)
    p=templates/'availability.pynml';s=p.read_text();s=s.replace('restrict_open_during_gameplay) {','(restrict_open_during_gameplay || (lifecycle_scheduler_mode && historical_europe_mode && economy == 0))) {');p.write_text(s)
    p=templates/'historical_location.pynml';s=p.read_text().replace('${industry.id}_check_location,','${industry.id}_phase7_original_location,')
    s+='''
/* Availability has no instance/founder. Location callback 0x28 does.
 * Natural helper passes OWNER_NONE=16; deity command passes OWNER_DEITY=18.
 * Keep every upstream date, terrain, cluster, town and neighbour check. */
switch(FEAT_INDUSTRIES, SELF, ${industry.id}_check_location,
    !(lifecycle_scheduler_mode && historical_europe_mode && economy == 0 && extra_callback_info2 == IND_CREATION_RANDOM) || founder == 18) {
    1: ${industry.id}_phase7_original_location;
    return CB_RESULT_LOCATION_DISALLOW;
}
''';p.write_text(s)
    p=templates/'industry_primary.pynml';s=p.read_text();insert='''
<tal:lifecycle condition="industry.id == 'coal_mine'">
/* Reserved opt-in command for deity-founded coal mines only. GS first warns,
 * then explicitly sets level 4. Existing neutral/player-founded mines cannot
 * enter this branch. Engine NoClosure/last-instance protections still apply. */
switch(FEAT_INDUSTRIES, SELF, lifecycle_coal_closure,
    lifecycle_scheduler_mode && historical_europe_mode && economy == 0 && founder == 18 && production_level == 4) {
    1: return CB_RESULT_IND_PROD_CLOSE;
    return CB_RESULT_IND_PROD_NO_CHANGE;
}
</tal:lifecycle>
'''
    s=s.replace('<!--! graphics block defined explicitly',insert+'\n<!--! graphics block defined explicitly')
    s=s.replace('                random_prod_change:', '''                <tal:lifecycle condition="industry.id == 'coal_mine'">
                monthly_prod_change: lifecycle_coal_closure;
                </tal:lifecycle>
                random_prod_change:''');p.write_text(s)
    logs=ROOT/'.work/logs';logs.mkdir(parents=True,exist_ok=True);dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    artifact=dist/'axis-historical-europe-0.4.0-lifecycle-candidate.grf'
    if artifact.exists():
        archive=dist/'archive';archive.mkdir(exist_ok=True);previous=archive/(sha(artifact)+'.grf')
        if not previous.exists():shutil.copyfile(artifact,previous)
    commands=[('language',[sys.executable,'src/render_lang.py']),('render',[sys.executable,'src/render_nml.py']),('compile',[sys.executable,'-m','nml.main','-c','-l','generated/lang','--verbosity=3','--grf='+str(artifact),'generated/firs.nml'])]
    for name,cmd in commands:
        print(name,flush=True)
        with (logs/(name+'.log')).open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=source,env={**os.environ,'PYTHONHASHSEED':'0'},stdout=f,stderr=subprocess.STDOUT,check=True)
    result=dict(version='0.4.0 lifecycle candidate',grfid='4B484531',grf_version=4,min_compatible_version=3,artifact=str(artifact),sha256=sha(artifact),engine_patch=False,experimental_parameter=11,default=0,base_0_3_sha256=sha(BASE/'dist/axis-historical-europe-0.3.0-candidate.grf'),commands=commands)
    (dist/'build-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
