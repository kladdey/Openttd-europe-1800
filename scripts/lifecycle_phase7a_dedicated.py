"""Loopback-only dedicated smoke; not a three-human-client network test."""
import json
from pathlib import Path
from lifecycle_phase7a_runtime import BASE,prepare,execute
from lifecycle_phase7a_fixture import code
from lifecycle_phase7a_schedule import fixture,compile_schedule

if __name__=='__main__':
    original=Path((BASE/'vertical-slice-case.txt').read_text())/'checkpoint.sav'
    script=code(2).replace('GSGame.Unpause();','GSLog.Info("P7 DEDICATED|multiplayer="+GSGame.IsMultiplayer());GSGame.Unpause();')
    script=script.replace('Initialize(now);','Initialize(now);GSLog.Info("P7 DEDICATED_SMOKE_DONE|loaded=true|events="+state.events.len());GSGame.Pause();while(true)Sleep(365);')
    home=prepare('dedicated-loopback',script);compile_schedule(fixture(),home/'game/lifecycle/schedule.nut')
    cfg=home/'test.cfg';cfg.write_text(cfg.read_text()+'\n[network]\nserver_game_type = local\nserver_advertise = false\nmin_active_clients = 0\nserver_name = Phase7A isolated loopback\n')
    result=execute(home,150000,source=original,dedicated=True)
    assert any('P7 DEDICATED|multiplayer=true' in s for s in result['observations'])
    for marker in ['EVENT|loaded|','P7 DEDICATED_SMOKE_DONE|loaded=true|events=4']:assert any(marker in s for s in result['observations'])
    (BASE/'dedicated-smoke.json').write_text(json.dumps(result,indent=2))
