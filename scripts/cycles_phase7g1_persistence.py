"""Reload the existing native schema-5 fixture, observe a short bounded window, never rebuild it."""
import json,datetime
from pathlib import Path
import cycles_phase7g as g
ROOT=g.ROOT;BASE=g.BASE/'persistence';BASE.mkdir(exist_ok=True)
PROBE='''
class PersistenceProbe extends CyclesController {
 function Snapshot(tag){local r=state.cycles,s=r.signature,intact=0,pilot_count=0,coal=-1;
 foreach(c,_ in GSCargoList())if(GSCargo.GetCargoLabel(c)=="COAL")coal=c;
 foreach(sig in state.baseline)if(Matches(sig.id,sig))intact++;
 foreach(i,_ in GSIndustryList())if(Matches(i,s))pilot_count++;
 Log("g1_snapshot",tag,"calendar="+Calendar()+"|economy="+GSDate.GetCurrentDate()+"|schema="+state.schema+"|contract="+state.cycle_contract+"|boom_id="+CYCLE.events[0]+"|downturn_id="+CYCLE.events[1]+"|boom="+r.boom+"|downturn="+r.downturn+"|stage="+r.stage+"|target="+s.id+"|type="+s.type+"|tile="+s.tile+"|born="+s.born+"|last_change="+r.last_change+"|last_month="+r.last_month+"|attempts="+r.attempts+"|batches="+r.batches+"|boosted="+r.boosted+"|base_level="+r.base_level+"|base_flags="+r.base_flags+"|level="+GSIndustry.GetProductionLevel(s.id)+"|flags="+GSIndustry.GetControlFlags(s.id)+"|coal="+GSIndustry.GetLastMonthProduction(s.id,coal)+"|pilot_count="+pilot_count+"|industries="+GSIndustryList().Count()+"|originals="+intact+"|towns="+GSTownList().Count());
 if(state.schema!=5||r.stage!="ended"||r.boom!="ended"||r.downturn!="ended"||s.id!=542||pilot_count!=1||intact!=542||GSTownList().Count()!=617||GSIndustryList().Count()!=543||GSIndustry.GetProductionLevel(s.id)!=r.base_level||GSIndustry.GetControlFlags(s.id)!=r.base_flags)throw "Persistence invariant failed";
 }
 function Start(){try{GSGame.Unpause();
 if(loaded==null||!("cycles" in loaded))throw "No native cycle saved data";
 Log("g1_saved","native","schema="+loaded.schema+"|stage="+loaded.cycles.stage+"|target="+loaded.cycles.signature.id+"|last_change="+loaded.cycles.last_change+"|boom="+loaded.cycles.boom+"|downturn="+loaded.cycles.downturn);
 Initialize(Calendar());Snapshot("before");local start=Calendar();
 while(Calendar()-start<2){Tick(Calendar());Sleep(74*2);}
 Snapshot("after");Log("g1_done","ended","days="+(Calendar()-start)+"|save_schema="+Save().schema);GSGame.Pause();
 }catch(e){GSLog.Error("P7 G1_ERROR|"+e);GSGame.Pause();}while(true)Sleep(365);}
}
'''

def validate(lines):
 if any('G1_ERROR|' in s or 'FATAL|' in s for s in lines):raise ValueError('Native reload failed')
 snapshots={}
 for line in lines:
  if 'EVENT|g1_snapshot|' not in line:continue
  tail=line.split('EVENT|g1_snapshot|',1)[1];tag,fields=tail.split('|',1);snapshots[tag]=dict(v.split('=',1) for v in fields.split('|'))
 if set(snapshots)!={'before','after'}:raise ValueError('Missing before/after snapshots')
 a,b=snapshots['before'],snapshots['after']
 expected=dict(schema='5',boom='ended',downturn='ended',stage='ended',target='542',level='16',flags='0',pilot_count='1',industries='543',originals='542',towns='617')
 for row in [a,b]:
  if any(row.get(k)!=v for k,v in expected.items()):raise ValueError('Ended-state invariant mismatch')
 for key in a:
  if key not in ['calendar','economy','coal'] and a[key]!=b[key]:raise ValueError('Persisted state changed: '+key)
 if int(b['calendar'])-int(a['calendar'])<2:raise ValueError('No bounded advance')
 effects=[s for s in lines if any('EVENT|'+k+'|' in s for k in ['cycle_opened','cycle_level'])]
 if effects:raise ValueError('Repeated cycle effect after ended-state reload')
 return snapshots

def main():
 source_run=json.loads((g.BASE/'part1.json').read_text());source=Path(source_run['case'])/'save/autosave/exit.sav'
 assert source.exists(),'Existing checkpoint missing; no automatic reconstruction'
 source_sha=g.sha(source);assert source_sha=='0fe80e8acde0d9b3333a92703350d0570aef0c67ca9380d3199b709aab171e33'
 h=g.prepare('g1-ended-reload',g.bundle()+PROBE,g.policy(True));info=h/'game/lifecycle/info.nut';info.write_text(info.read_text().replace('"CyclesController"','"PersistenceProbe"'))
 (h/'scripts').mkdir();(h/'scripts/game_start.scr').write_text('unpause\n')
 raw=g.execute(h,6000,source=source);assert g.sha(source)==source_sha
 attempt=1+len(list(BASE.glob('attempt*.json')));(BASE/f'attempt{attempt}.json').write_text(json.dumps(raw,indent=2));(BASE/'ended-run.json').write_text(json.dumps(raw,indent=2));snapshots=validate(raw['observations'])
 manifest=json.loads((ROOT/'docs/research/phase7g_candidate_delivery.json').read_text())
 for key in ['candidate','source','engine','grf','script']:assert g.sha(Path(manifest[key]))==manifest[key+'_sha256'],key
 for item in manifest['script_files']+manifest['asset_files']:assert g.sha(Path(item['path']))==item['sha256']
 receipt=dict(normal_candidate=manifest['candidate'],normal_candidate_sha256=manifest['candidate_sha256'],normal_assets_verified=True,verdict='PASS — ENDED-STATE RELOAD',engine_invocations=len(list(g.BASE.glob('g1-ended-reload-*/engine.log'))),first_attempt='Fixture count assertion failed after legitimate Liverpool 1831 opening; cycle state itself persisted; observation shortened before port date',active_boundary_reload='NOT TESTED: no pre-existing active checkpoint; generating and reloading would exceed remaining budget',source_checkpoint=str(source),source_checkpoint_sha256=source_sha,matching_fixture_contract=True,gs_version=6,schema=5,checkpoint_unchanged=True,before=snapshots['before'],after=snapshots['after'],new_cycle_openings=0,new_level_commands=0,prior_attempts=[json.loads(p.read_text()) for p in sorted(BASE.glob('attempt*.json')) if p.name!=f'attempt{attempt}.json'],raw=raw)
 (ROOT/'docs/research/phase7g1_persistence_receipts.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(verdict=receipt['verdict'],before=receipt['before'],after=receipt['after']),indent=2))
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--verify-receipts',action='store_true');a=ap.parse_args()
 if a.verify_receipts:
  r=json.loads((ROOT/'docs/research/phase7g1_persistence_receipts.json').read_text());validate(r['raw']['observations']);print('Existing ended-state receipt validated; no engine invoked')
 else:main()
