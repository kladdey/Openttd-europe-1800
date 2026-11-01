"""One bounded native reload of the new schema-6 ended transformation ledger."""
import json
from pathlib import Path
from transformation_phase7h import *
PROBE='''
class TransformationReload extends TransformationController {
 function Snapshot(tag){local originals=0;foreach(s in state.baseline)if(Matches(s.id,s))originals++;
 foreach(e in TRANSFORMATION.events){local r=state.transformation[e.id];
 Log("h_reload_row",tag,"event="+e.id+"|status="+r.status+"|stage="+r.stage+"|industry="+r.signature.id+"|tile="+r.signature.tile+"|born="+r.signature.born+"|exists="+Matches(r.signature.id,r.signature)+"|attempts="+r.attempts+"|batches="+r.batches);
 if(r.status!="ended"||(e.kind=="open"&&!Matches(r.signature.id,r.signature))||(e.kind=="retire"&&Matches(r.signature.id,r.signature)))throw "Transformation state lost";
 }
 Log("h_reload_map",tag,"schema="+state.schema+"|calendar="+Calendar()+"|originals="+originals+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count());
 if(originals!=542||GSTownList().Count()!=617)throw "Original map identities lost";
 }
 function Start(){try{GSGame.Unpause();if(loaded==null||loaded.schema!=6)throw "Missing native schema6 state";
 Log("h_reload_saved","native","schema="+loaded.schema+"|events="+loaded.transformation.len());Initialize(Calendar());Snapshot("before");
 Tick(Calendar());Sleep(74*2);Snapshot("after");Log("h_reload_done","proof","schema="+Save().schema);GSGame.Pause();
 }catch(e){GSLog.Error("P7 H_RELOAD_ERROR|"+e);GSGame.Pause();}while(true)Sleep(365);}
}
'''
if __name__=='__main__':
 h=prepare('transformation-reload',bundle()+PROBE,policy(True));info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"TransformationController"','"TransformationReload"'));(h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 source=Path(json.loads((BASE/'transformation.json').read_text())['case'])/'save/autosave/exit.sav';before=sha(source);r=execute(h,6000,source=source);assert sha(source)==before
 r.update(source=str(source),source_sha256=before);(BASE/'reload.json').write_text(json.dumps(r,indent=2));obs='\n'.join(r['observations'])
 assert 'H_RELOAD_ERROR|' not in obs and 'h_reload_done|' in obs
 assert all('EVENT|'+k+'|' not in obs for k in ['h_opened','h_decline','h_retire_command','h_retired'])
