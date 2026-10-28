"""Deliver only the verified new scenario/fork files, without replacing originals."""
import json
import hashlib
from pathlib import Path
import shutil
from historical_scenario_migration import inspect
from vehicle_audit_tables import decode_table
from audit_vehicle_newgrfs import scenario

ROOT=Path(__file__).resolve().parents[1]
FORK=ROOT/'newgrfs/axis-historical-europe'
WORK=FORK/'.work/europe-migration'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def copy_new(source,target):
    assert not target.exists(),'Refusing to overwrite '+str(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target);assert sha(source)==sha(target)
    return dict(path=str(target),sha256=sha(target),bytes=target.stat().st_size)


def main():
    if not __debug__:raise SystemExit('Safety assertions required; do not run with Python -O')
    runtime=json.loads((ROOT/'docs/research/axis_europe_migration_runtime.json').read_text())
    assert runtime['passed'] and all(p['passed'] for p in runtime['phases'])
    protected=json.loads((WORK/'protected-inputs.json').read_text())
    for name,h in protected.items():assert sha(Path(name))==h,name
    source=Path(next(name for name in protected if name.endswith('.scn')))
    candidate=WORK/'scenario/r.scn';assert sha(candidate)==runtime['candidate_sha256']
    before=inspect(source);after=inspect(candidate)
    assert before['map_array_sha256']==after['map_array_sha256']
    for tag in ['CITY','PATS','ECMY','STNN','VEHS','OBJS']:assert before['chunks'][tag]==after['chunks'][tag],tag
    assert after['industry_records']==after['industry_tiles']==0 and after['town_records']==613
    date=decode_table(scenario(candidate)['DATE'])[0]
    assert date['date']==668394 and date['pause_mode']==1  # 1 January 1830, normal pause bit.
    installed=Path(r'C:\Users\Kladd\Documents\OpenTTD')
    outputs=[]
    outputs.append(copy_new(candidate,installed/'scenario/Europe 1830 Historical AXIS 0.2.0 - No Industries.scn'))
    outputs.append(copy_new(FORK/'dist/axis-historical-europe-0.2.0.grf',installed/'newgrf/axis-historical-europe-0.2.0.grf'))
    outputs.append(copy_new(FORK/'dist/axis-historical-europe-0.2.0-source.zip',installed/'newgrf/axis-historical-europe-0.2.0-source.zip'))
    for name,h in protected.items():assert sha(Path(name))==h,name
    report=dict(passed=True,source_sha256=sha(source),outputs=outputs,protected_originals_unchanged=protected,
                calendar_date='1830-01-01',industry_instances=0,industry_tiles=0,towns=613,
                map_arrays_bit_identical=after['map_array_sha256'],town_chunk_bit_identical=True,
                original_other_14_grfs_unchanged=True,stock_axis_preserved=True,
                start_paused=True,spawning_parameter_preserved=0,history_parameter=1,
                runtime_report='docs/research/axis_europe_migration_runtime.json')
    (ROOT/'docs/research/axis_europe_scenario_delivery.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
