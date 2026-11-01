# SPDX-License-Identifier: GPL-2.0-only
"""Separate 0.5 candidate: per-instance legacy closure handshake, no engine patch."""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];BASE=HERE.parent/'axis-historical-lifecycle'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert __debug__;assert sha(BASE/'dist/axis-historical-europe-0.4.0-lifecycle-candidate.grf')=='e05de519b4695bc68bde7064c17ee0ae833edfe281579c3b92cb79532f466c52'
    source=HERE/'.work/source'
    if source.exists():
        assert '--rebuild' in sys.argv,'Candidate source exists: use explicit --rebuild'
        archive=source.with_name('source-previous-'+str(time.time_ns()));assert source.resolve().is_relative_to((HERE/'.work').resolve()) and archive.resolve().is_relative_to((HERE/'.work').resolve());shutil.move(str(source),str(archive))
    shutil.copytree(BASE/'.work/source',source,ignore=shutil.ignore_patterns('generated','__pycache__','.cache'))
    inv=json.loads((ROOT/'docs/research/phase7b_extractive_inventory.json').read_text());chosen=[next(r for r in inv if r['industry_id']==i) for i in [1,11,12,438]]
    for i,r in enumerate(chosen):r.update(site_id='legacy_'+str(r['industry_id']),token=int(r['record_sha256'][:7],16),arm_level=[5,6,7,9][i])
    (HERE/'.work/enrollment-build.json').write_text(json.dumps(chosen,indent=2))
    p=source/'src/templates/header.pynml';s=p.read_text().replace('version: 4;','version: 5;').replace('min_compatible_version: 3;','min_compatible_version: 4;');p.write_text(s)
    p=source/'src/lang_templates/english.pylng';p.write_text(p.read_text().replace('0.4.0 lifecycle candidate','0.5.0 legacy mine candidate'))
    p=source/'src/templates/industry_primary.pynml';s=p.read_text();marker='<!--! graphics block defined explicitly'
    conditions=[]
    for r in chosen:
        name='phase7b_instance_'+str(r['industry_id']);token=r['token']
        # Source inspection proves 0x80 is the full absolute tile, not its low byte.
        fingerprint=f"var[0x80, 0, 0xFFFFFFFF] == {r['tile']} && build_date == {r['construction_date']} && founder == {r['founder']} && random_bits == {r['random']} && layout_num == {r['selected_layout']}"
        conditions.append(f'''<tal:legacy condition="industry.id == '{r['industry']}'">
switch(FEAT_INDUSTRIES, SELF, {name}_consume, [STORE_PERM(-{token}, 200), STORE_PERM(current_date, 202)]) {{ return CB_RESULT_IND_PROD_CLOSE; }}
switch(FEAT_INDUSTRIES, SELF, {name}_arm, [STORE_PERM({token}, 200), STORE_PERM(current_date, 201)]) {{ return CB_RESULT_IND_PROD_NO_CHANGE; }}
switch(FEAT_INDUSTRIES, SELF, {name}_arm_gate, LOAD_PERM(200) == 0) {{ 1: {name}_arm; return CB_RESULT_IND_PROD_NO_CHANGE; }}
switch(FEAT_INDUSTRIES, SELF, {name}_close_gate, LOAD_PERM(200) == {token} &amp;&amp; current_date &gt; LOAD_PERM(201) &amp;&amp; current_date - LOAD_PERM(201) &lt;= 90) {{ 1: {name}_consume; return CB_RESULT_IND_PROD_NO_CHANGE; }}
switch(FEAT_INDUSTRIES, SELF, {name}_command, production_level) {{
 {r['arm_level']}: {name}_arm_gate;
 4: {name}_close_gate;
 return CB_RESULT_IND_PROD_NO_CHANGE;
}}
switch(FEAT_INDUSTRIES, SELF, {name}_guard, {fingerprint.replace('&&','&amp;&amp;')}) {{ 1: {name}_command; return CB_RESULT_IND_PROD_NO_CHANGE; }}
</tal:legacy>
''')
    # One wrapper per industry: unsupported types receive no new callback.
    for industry in sorted({r['industry'] for r in chosen}):
        sites=[r for r in chosen if r['industry']==industry]
        arms='\n'.join(f" {r['tile']}: phase7b_instance_{r['industry_id']}_guard;" for r in sites)
        default='lifecycle_coal_closure' if industry=='coal_mine' else 'CB_RESULT_IND_PROD_NO_CHANGE'
        conditions.append(f'''<tal:legacy condition="industry.id == '{industry}'">
switch(FEAT_INDUSTRIES, SELF, phase7b_{industry}_tile, var[0x80, 0, 0xFFFFFFFF]) {{
{arms}
 {default};
}}
switch(FEAT_INDUSTRIES, SELF, phase7b_{industry}_dispatch, lifecycle_scheduler_mode &amp;&amp; historical_europe_mode &amp;&amp; economy == 0) {{
 1: phase7b_{industry}_tile;
 return CB_RESULT_IND_PROD_NO_CHANGE;
}}
</tal:legacy>
''')
    s=s.replace(marker,''.join(conditions)+'\n'+marker)
    s=s.replace('monthly_prod_change: lifecycle_coal_closure;','monthly_prod_change: phase7b_coal_mine_dispatch;')
    s=s.replace('random_prod_change:       CB_RESULT_IND_PROD_NO_CHANGE;', '''<tal:legacy condition="industry.id == 'copper_mine'">monthly_prod_change: phase7b_copper_mine_dispatch;</tal:legacy>
                random_prod_change:       CB_RESULT_IND_PROD_NO_CHANGE;''')
    p.write_text(s)
    # Existing primary storage occupies 0..38. Reserve isolated protocol slots.
    assert 'STORE_PERM(200' not in (BASE/'.work/source/src/templates/industry_primary.pynml').read_text()
    dist=HERE/'dist';dist.mkdir(exist_ok=True);artifact=dist/'axis-historical-europe-0.5.0-legacy-candidate.grf'
    if artifact.exists():shutil.copyfile(artifact,HERE/'.work'/('previous-'+sha(artifact)+'.grf'))
    commands=[[sys.executable,'src/render_lang.py'],[sys.executable,'src/render_nml.py'],[sys.executable,'-m','nml.main','-c','-l','generated/lang','--grf='+str(artifact),'generated/firs.nml']]
    for i,cmd in enumerate(commands):
        print('build',i,flush=True)
        with (HERE/'.work'/f'build-{i}.log').open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=source,env={**os.environ,'PYTHONHASHSEED':'0'},stdout=f,stderr=subprocess.STDOUT,check=True)
    result=dict(version='0.5.0 legacy candidate',grfid='4B484531',grf_version=5,min_compatible_version=4,artifact=str(artifact),sha256=sha(artifact),base_0_4_sha256=sha(BASE/'dist/axis-historical-europe-0.4.0-lifecycle-candidate.grf'),registered_instances=chosen,commands=commands,engine_patch=False)
    (dist/'build-result.json').write_text(json.dumps(result,indent=2));print(result['sha256'])
if __name__=='__main__':main()
