"""Actual loading/payment on disposable copies of the industrialized Europe map.

Construction grants isolate functionality. These are not profit or capital
recovery measurements and do not modify the scenario candidate.
"""
import argparse,json,re
from pathlib import Path
from industrial_phase6b_runtime import ROOT,BASE,run,sha
from industrial_phase6b_controls import COMMON,builder
from industrial_phase6b_results import records


def closest(rows,src,dst,region=None):
    producers=[r for r in rows if r['status']=='PLACED' and r['local_id']==src and (region is None or r['region']==region)]
    consumers=[r for r in rows if r['status']=='PLACED' and r['local_id']==dst]
    return min(((a,b) for a in producers for b in consumers if a['industry_id']!=b['industry_id']),key=lambda p:abs(p[0]['x']-p[1]['x'])+abs(p[0]['y']-p[1]['y']))


def main():
    p=argparse.ArgumentParser();p.add_argument('case',choices=['british_coal','ruhr_coal','grain','timber','iron','salt','coastal_fish','copper_export','passengers','mail']);a=p.parse_args()
    rows=records();specs={'british_coal':('COAL',0,45,'GB'),'ruhr_coal':('COAL',0,45,'DE'),'grain':('GRAI',26,34,None),'timber':('WOOD',11,12,None),'iron':('IORE',4,7,None),'salt':('SALT',105,125,'PL'),'coastal_fish':('FISH',32,90,'SC'),'copper_export':('COPR',123,46,'GB')}
    if a.case in ['passengers','mail']:
        label='PASS' if a.case=='passengers' else 'MAIL';origin=destination=dict(industry_id=191,local_id='TOWN',locality='LONDON',x=2724,y=1276)
    else:
        label,src,dst,region=specs[a.case];origin,destination=closest(rows,src,dst,region)
    # COPR has no automatic source. The complete three-input smelting test is
    # covered separately; do not report an empty service as a delivered export.
    c=dict(name=a.case,label=label,src=origin,dst=destination,mode='ship' if a.case=='coastal_fish' else 'road')
    s='SPEC <- '+json.dumps({k:v for k,v in c.items() if k not in ['src','dst']}).replace(':','=').replace('"name"','name').replace('"label"','label').replace('"mode"','mode')+';\n'
    # Use the same Squirrel serializer as the other audited harnesses.
    from transport_phase4 import squirrel
    s='SPEC <- '+squirrel(dict(name=a.case,label=label,src=origin['industry_id'],dst=destination['industry_id'],mode=c['mode']))+';\n'
    s+=builder()+'class CoastalProbe extends GSController {\n'+COMMON+'''function Start(){try{
while(GSCompany.ResolveCompanyID(0)==GSCompany.COMPANY_INVALID)Sleep(1);
GSCompany.ChangeBankBalance(0,100000000000,GSCompany.EXPENSES_OTHER,GSMap.TILE_INVALID);
local cm=GSCompanyMode(0);GSRoad.SetCurrentRoadType(0);
local s=null;
if(SPEC.label=="PASS" || SPEC.label=="MAIL"){
 local c=Cargo(SPEC.label),e=Engine(c);::ACTIVE={mode="road",cargo=c,a=191,b=191,engine=e,fleet=2,endpoints="town",wagons=0,platform=2,brake=false,sep=4};
 ::MODE="road";::CARGO=c;::A=191;::B=191;::ENGINE=e;::FLEET=2;::ENDPOINTS="town";::MIN_SEPARATION=4;::CASE=SPEC.name;
 local rb=RouteBuilder();s=rb.Build();if(s==null)throw "Town service failed";Loop(rb,s.a);Loop(rb,s.b);
 s.label<-SPEC.label;s.ever_loaded<-false;s.paid<-false;s.lastprofit<-{};s.lastyear<-GSDate.GetYear(GSDate.GetCurrentDate());foreach(v in s.vehicles)s.lastprofit[v]<-GSVehicle.GetProfitThisYear(v);
}else s=SPEC.mode=="ship"?ShipService(SPEC.name,SPEC.label,SPEC.src,SPEC.dst,true):Service(SPEC.name,SPEC.label,SPEC.src,SPEC.dst,true);
local peak=0,startdate=GSDate.GetCurrentDate();
for(local tick=0;tick<180000;tick+=10){Sleep(10);Sample(s);if(SPEC.label!="PASS" && SPEC.label!="MAIL")peak=max(peak,GSIndustry.GetLastMonthProduction(SPEC.src,Cargo(SPEC.label)));
 if(s.paid){GSLog.Info("I6 CAMPAIGN_PASS|"+SPEC.name+"|source_monthly_peak="+peak+"|elapsed_days="+(GSDate.GetCurrentDate()-startdate)+"|accepted_date="+GSIndustry.GetCargoLastAcceptedDate(SPEC.dst,Cargo(SPEC.label)));break;}
 if(tick>=179990)GSLog.Info("I6 CAMPAIGN_BLOCKED|"+SPEC.name+"|loaded="+s.ever_loaded+"|paid="+s.paid+"|source_monthly_peak="+peak);
}
GSGame.Pause();GSLog.Info("C6 DONE campaign route");}catch(e){GSLog.Error("I6 CAMPAIGN_ERROR|"+SPEC.name+"|"+e);GSGame.Pause();GSLog.Info("C6 DONE campaign route blocked");}while(true)Sleep(365);}}
'''
    candidate=Path(json.loads((BASE/'additions-candidate-final.json').read_text())['candidate']);migration=json.loads((BASE/'migration-0.3.json').read_text())
    home=run(s,'campaign-'+a.case,220000,source=candidate,unpaused=True,candidate_grf=Path(migration['candidate_assets']))
    log=(home/'engine.log').read_text(encoding='utf8')
    result=c|dict(case=str(home),source=str(candidate),source_sha256=sha(candidate),script_sha256=sha(home/'game/coastal/main.nut'),status='VERIFIED IN GAME' if 'I6 CAMPAIGN_PASS|' in log else 'BLOCKED',events=[line.split(' I6 ',1)[1] for line in log.splitlines() if ' I6 ' in line and any(k in line for k in ['CAMPAIGN_','CONTROL_PAID'])],limitations='Construction grant; functionality only. Original candidate unchanged. Actual campaign economy/calendar and all 15 GRF parameters preserved.')
    (BASE/('route-'+a.case+'.json')).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
