"""Fresh controlled copper recipe/delivery check; never a Europe profit test."""
import json
from industrial_phase6b_controls import fresh,script
from inland_phase6c_runtime import BASE,ROOT,GRF,GRF_HASH,SOURCE,EXPECTED,sha


def main():
    assert sha(SOURCE)==EXPECTED and sha(GRF)==GRF_HASH
    home=fresh(script('copper'),'phase6c-regression-copper',600000)
    log=(home/'engine.log').read_text(encoding='utf8')
    result=dict(case=str(home),evidence='VERIFIED IN GAME' if 'I6 CONTROL_PASS|copper|' in log else 'BLOCKED',
        scope='Controlled disposable 256x256 recipe regression; not Europe route profitability',
        engine_log_sha256=sha(home/'engine.log'),script_sha256=sha(home/'game/registration/main.nut'),
        events=[l for l in log.splitlines() if 'I6 CONTROL_' in l or 'C6 DONE' in l])
    path=BASE/'controlled-copper-regression.json'
    if path.exists():
        old=json.loads(path.read_text());(BASE/('archived-control-'+__import__('pathlib').Path(old['case']).name+'.json')).write_text(json.dumps(old,indent=2))
    path.write_text(json.dumps(result,indent=2))
    assert result['evidence']=='VERIFIED IN GAME','Inspect the retained blocked fixture'
    print(result['evidence'],home)


if __name__=='__main__':main()
