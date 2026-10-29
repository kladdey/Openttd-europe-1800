"""Copy verified candidates to distinct local filenames. Never overwrite files."""
import hashlib,json,shutil
from pathlib import Path
from industrial_phase6b_runtime import ROOT,BASE,SOURCE,EXPECTED,sha


def copy_new(source,destination):
    if destination.exists():
        assert sha(source)==sha(destination),'Refusing to overwrite '+str(destination)
    else:
        with source.open('rb') as src,destination.open('xb') as dst:shutil.copyfileobj(src,dst)
    return dict(path=str(destination),sha256=sha(destination),bytes=destination.stat().st_size)


def main():
    proof=json.loads((ROOT/'docs/research/industrialized_scenario_validation.json').read_text())
    controls=json.loads((ROOT/'docs/research/copper_salt_runtime_validation.json').read_text())
    compiled=json.loads((ROOT/'newgrfs/axis-historical-copper-salt/bundle-rebuild-result.json').read_text())
    candidate=Path(proof['candidate']);grf=ROOT/'newgrfs/axis-historical-copper-salt/dist/axis-historical-europe-0.3.0-candidate.grf'
    assert sha(SOURCE)==EXPECTED and proof['source_scenario_unchanged']
    assert proof['scenario_editor_load_save_reload_verified'] and len(proof['gameplay_roundtrips'])==2
    assert sha(candidate)==proof['candidate_sha256']
    assert compiled['passed'] and sha(grf)==compiled['rebuilt_grf_sha256']==controls['candidate_grf_sha256']
    assert len(controls['tests'])==3 and all(t['evidence']=='VERIFIED IN GAME' for t in controls['tests'])
    scenario_dir=SOURCE.parent;grf_dir=scenario_dir.parent/'newgrf';assert grf_dir.is_dir()
    result=dict(candidate=copy_new(candidate,scenario_dir/'Europe 1830 Historical AXIS 0.3.0 Candidate - Industrialized.scn'),newgrf=copy_new(grf,grf_dir/grf.name),legacy_0_2=copy_new(Path(json.loads((BASE/'candidate.json').read_text())['candidate']),scenario_dir/'Europe 1830 Historical AXIS 0.2.0 - Industrialized.scn'),source_scenario_sha256=sha(SOURCE),normal_configuration_modified=False,existing_newgrf_files_modified=False,notes='0.3.0 is the copper/salt candidate. The 438-industry 0.2.0 file is a separately preserved earlier working version, not the copper/salt release. No file was overwritten.')
    (ROOT/'docs/research/industrialized_scenario_delivery.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
