"""One short real-Europe fixture proving the two new events, no paid-profit claim."""
import json
from transformation_phase7h import *
PROBE='''
class TransformationProbe extends TransformationController {
 function Start(){try{GSGame.Unpause();Initialize(Calendar());local month=-1;
 while(true){local now=Calendar();Tick(now);local m=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
 if(m!=month){month=m;
 foreach(e in TRANSFORMATION.events){local r=state.transformation[e.id];
 if(r.signature!=null&&Matches(r.signature.id,r.signature)){
 foreach(c,_ in GSIndustryType.GetProducedCargo(Type(e.local_id)))Log("h_sample",e.id,"calendar="+now+"|industry="+r.signature.id+"|stage="+r.stage+"|status="+r.status+"|cargo="+GSCargo.GetCargoLabel(c)+"|production="+GSIndustry.GetLastMonthProduction(r.signature.id,c)+"|level="+GSIndustry.GetProductionLevel(r.signature.id)+"|flags="+GSIndustry.GetControlFlags(r.signature.id)+"|days_since_change="+(now-r.changed));
 }
 }
 }
 if(now>=END){local originals=0;foreach(sig in state.baseline)if(Matches(sig.id,sig))originals++;
 foreach(e in TRANSFORMATION.events){local r=state.transformation[e.id];Log("h_final",e.id,"status="+r.status+"|stage="+r.stage+"|industry="+(r.signature==null?-1:r.signature.id)+"|exists="+(r.signature!=null&&Matches(r.signature.id,r.signature))+"|attempts="+r.attempts+"|batches="+r.batches);}
 Log("h_done","proof","schema="+Save().schema+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|originals="+originals);
 if(originals!=542||GSTownList().Count()!=617)throw "Original preservation failed";
 GSGame.Pause();while(true)Sleep(365);}
 Sleep(74*2);
 }
 }catch(e){GSLog.Error("P7 H_ERROR|"+e);GSGame.Pause();while(true)Sleep(365);}}
}
'''
if __name__=='__main__':
 h=prepare('two-transformations',bundle()+PROBE.replace('END',str(absolute_date('1830-12-15'))),policy(True));info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"TransformationController"','"TransformationProbe"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n');before=sha(SOURCE);r=execute(h,37000);assert sha(SOURCE)==before
 (BASE/'transformation.json').write_text(json.dumps(r,indent=2));assert not any('H_ERROR|' in s for s in r['observations']) and any('h_done|' in s for s in r['observations']),r['log']
