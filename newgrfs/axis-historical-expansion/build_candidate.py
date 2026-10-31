# SPDX-License-Identifier: GPL-2.0-only
"""Build separate 0.6 candidate from the pinned, immutable 0.5 source.

Only the allowlisted original flour mill gains a capacity/closure adapter.
All other recipes and the complete Phase 7B primary template are retained.
"""
import hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];BASE=HERE.parent/'axis-historical-legacy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert __debug__
    assert sha(BASE/'dist/axis-historical-europe-0.5.0-legacy-candidate.grf')=='473b4ac0ebc6962959408633dbbc2cf254546fe9bc7fdd6c3531b0f0a232e534'
    work=HERE/'.work';work.mkdir(exist_ok=True);source=work/'source'
    if source.exists():
        assert '--rebuild' in sys.argv
        assert source.resolve().is_relative_to(work.resolve())
        shutil.move(str(source),str(work/('previous-source-'+str(time.time_ns()))))
    shutil.copytree(BASE/'.work/source',source,ignore=shutil.ignore_patterns('generated','__pycache__','.cache'))
    p=source/'src/templates/header.pynml';p.write_text(p.read_text().replace('version: 5;','version: 6;').replace('min_compatible_version: 4;','min_compatible_version: 5;'))
    p=source/'src/lang_templates/english.pylng';p.write_text(p.read_text().replace('0.5.0 legacy mine candidate','0.6.0 expansion candidate'))
    original=(source/'src/templates/produce_secondary.pynml').read_text()
    capped=original.replace('${industry.id}_','${industry.id}_phase7c_')
    # Consume the SAME capped input batch used in the existing recipe formula.
    # Never scale output alone, and never discard the remainder of the inputs.
    # Native integer ratios round each input contribution. Do not consume tiny
    # batches that round to zero: retain partial eight-unit batches in storage.
    capped=re.sub(r'incoming_cargo_waiting\(([^)]+)\)',r'(min(incoming_cargo_waiting(\1) / 8, 1) * 8)',capped)
    (source/'src/templates/produce_secondary_phase7c.pynml').write_text(capped)
    p=source/'src/templates/industry_secondary.pynml';s=p.read_text();marker='<!--! graphics block defined explicitly'
    token=int('98bb982',16)
    guard='lifecycle_scheduler_mode &amp;&amp; historical_europe_mode &amp;&amp; economy == 0 &amp;&amp; var[0x80, 0, 0xFFFFFFFF] == 6173294 &amp;&amp; build_date == 668394 &amp;&amp; founder == 16 &amp;&amp; random_bits == 40626 &amp;&amp; layout_num == 3'
    addition='''<tal:c condition="industry.id == 'flour_mill'">
<tal:include metal:use-macro="load: produce_secondary_phase7c.pynml" />
produce(phase7c_hold, [], [], 0)
switch(FEAT_INDUSTRIES, SELF, phase7c_tick_dispatch, LOAD_PERM(203) == 0) { 1: ${industry.id}_phase7c_produce_cargo_arrival; phase7c_hold; }
switch(FEAT_INDUSTRIES, SELF, phase7c_tick_run, [${industry.id}_update_supplied_cycles_remaining_per_cargo(), STORE_PERM((LOAD_PERM(203) + 1) % max(1, 16 - production_level), 203)]) { phase7c_tick_dispatch; }
switch(FEAT_INDUSTRIES, SELF, phase7c_tick, GUARD &amp;&amp; production_level &lt; 16) { 1: phase7c_tick_run; ${industry.id}_produce_256_ticks; }
switch(FEAT_INDUSTRIES, SELF, phase7c_arrival, GUARD &amp;&amp; production_level &lt; 16) { 1: phase7c_hold; ${industry.id}_produce_cargo_arrival; }
switch(FEAT_INDUSTRIES, SELF, phase7c_consume, [STORE_PERM(-TOKEN, 200), STORE_PERM(current_date, 202)]) { return CB_RESULT_IND_PROD_CLOSE; }
switch(FEAT_INDUSTRIES, SELF, phase7c_arm, [STORE_PERM(TOKEN, 200), STORE_PERM(current_date, 201)]) { return CB_RESULT_IND_PROD_NO_CHANGE; }
switch(FEAT_INDUSTRIES, SELF, phase7c_arm_gate, LOAD_PERM(200) == 0) { 1: phase7c_arm; return CB_RESULT_IND_PROD_NO_CHANGE; }
switch(FEAT_INDUSTRIES, SELF, phase7c_close_gate, LOAD_PERM(200) == TOKEN &amp;&amp; current_date &gt; LOAD_PERM(201) &amp;&amp; current_date - LOAD_PERM(201) &lt;= 90) { 1: phase7c_consume; return CB_RESULT_IND_PROD_NO_CHANGE; }
switch(FEAT_INDUSTRIES, SELF, phase7c_command, production_level) { 11: phase7c_arm_gate; 4: phase7c_close_gate; return CB_RESULT_IND_PROD_NO_CHANGE; }
switch(FEAT_INDUSTRIES, SELF, phase7c_monthly, GUARD) { 1: phase7c_command; return CB_RESULT_IND_PROD_NO_CHANGE; }
</tal:c>
'''.replace('GUARD',guard).replace('TOKEN',str(token))
    s=s.replace(marker,addition+'\n'+marker)
    s=s.replace('produce_cargo_arrival:    ${industry.id}_produce_cargo_arrival;',"<tal:c condition=\"industry.id == 'flour_mill'\">produce_cargo_arrival: phase7c_arrival;</tal:c><tal:c condition=\"industry.id != 'flour_mill'\">produce_cargo_arrival: ${industry.id}_produce_cargo_arrival;</tal:c>")
    s=s.replace('produce_256_ticks:        ${industry.id}_produce_256_ticks;',"<tal:c condition=\"industry.id == 'flour_mill'\">produce_256_ticks: phase7c_tick; monthly_prod_change: phase7c_monthly;</tal:c><tal:c condition=\"industry.id != 'flour_mill'\">produce_256_ticks: ${industry.id}_produce_256_ticks;</tal:c>")
    p.write_text(s)
    assert (source/'src/templates/industry_primary.pynml').read_bytes()==(BASE/'.work/source/src/templates/industry_primary.pynml').read_bytes()
    dist=HERE/'dist';dist.mkdir(exist_ok=True);artifact=dist/'axis-historical-europe-0.6.0-expansion-candidate.grf'
    if artifact.exists():shutil.copyfile(artifact,work/('previous-'+sha(artifact)+'.grf'))
    commands=[[sys.executable,'src/render_lang.py'],[sys.executable,'src/render_nml.py'],[sys.executable,'-m','nml.main','-c','-l','generated/lang','--grf='+str(artifact),'generated/firs.nml']]
    for i,cmd in enumerate(commands):
        print('build',i,flush=True)
        with (work/f'build-{i}.log').open('w',encoding='utf8') as f:subprocess.run(cmd,cwd=source,env={**os.environ,'PYTHONHASHSEED':'0'},stdout=f,stderr=subprocess.STDOUT,check=True)
    result=dict(version=6,min_compatible_version=5,artifact=str(artifact),sha256=sha(artifact),base_sha256=sha(BASE/'dist/axis-historical-europe-0.5.0-legacy-candidate.grf'),primary_template_unchanged=True,commands=commands,engine_patch=False)
    (dist/'build-result.json').write_text(json.dumps(result,indent=2));print(result['sha256'])
if __name__=='__main__':main()
