"""One compressed cycle proof; optional matching-policy reload remains unverified."""
import json
from cycles_phase7g import *
PROBE='''
class CycleProbe extends CyclesController {
 function Start(){try{GSGame.Unpause();Initialize(Calendar());local last=-1;
 while(true){local now=Calendar();Tick(now);local r=state.cycles,month=GSDate.GetYear(now)*12+GSDate.GetMonth(now);
 if(last!=month){last=month;if(r.signature!=null){local i=r.signature.id,cargo=-1;foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)=="COAL")cargo=c;
 Log("cycle_sample","ruhr","calendar="+now+"|economy="+GSDate.GetCurrentDate()+"|industry="+i+"|stage="+r.stage+"|level="+GSIndustry.GetProductionLevel(i)+"|coal="+GSIndustry.GetLastMonthProduction(i,cargo)+"|days_since_change="+(now-r.last_change)+"|flags="+GSIndustry.GetControlFlags(i));}}
 if(now>=BOUNDARY){local intact=0;foreach(sig in state.baseline)if(Matches(sig.id,sig))intact++;
 Log("cycle_boundary","proof","calendar="+now+"|schema="+Save().schema+"|stage="+r.stage+"|boom="+r.boom+"|downturn="+r.downturn+"|target="+(r.signature==null?-1:r.signature.id)+"|towns="+GSTownList().Count()+"|industries="+GSIndustryList().Count()+"|originals="+intact);
 if(intact!=542||GSTownList().Count()!=617||r.signature==null)throw "Preservation or cycle construction failed";
 GSGame.Pause();while(true)Sleep(365);}
 Sleep(74*2);}
 }catch(e){GSLog.Error("P7 G_ERROR|"+e);GSGame.Pause();while(true)Sleep(365);}}
}
'''
def main(part,boundary=None):
 end=boundary or '1830-12-15';h=prepare('cycle-part'+str(part),bundle()+PROBE.replace('BOUNDARY',str(absolute_date(end))),policy(True))
 info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"CyclesController"','"CycleProbe"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 source=SOURCE if part==1 else Path(json.loads((BASE/'part1.json').read_text())['case'])/'save/autosave/exit.sav'
 before=sha(source);r=execute(h,33000,source=source);assert sha(source)==before
 r.update(source=str(source),source_sha256=before);(BASE/('part'+str(part)+'.json')).write_text(json.dumps(r,indent=2))
 assert not any('G_ERROR|' in s for s in r['observations']) and any('cycle_boundary|' in s for s in r['observations']),r['log']
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('part',type=int,choices=[1,2]);ap.add_argument('--boundary');a=ap.parse_args();main(a.part,a.boundary)
