"""Strict orphan-ID cleanup and map restoration for an EMPTY industry scenario.

Uses the NewGRF list already produced by JGRPP's editor. Never manufactures a
replacement identity entry or edits an installed GRF. Refuses populated worlds.
"""
import argparse
import json
from pathlib import Path
import lzma
from historical_scenario_migration import inspect, decode, digest
from scenario_geography import chunks, gamma
from transport_phase3 import encode


def replace_pause(records):
    schema=records[0];p=0;fields=[]
    while schema[p]:
        typ=schema[p];p+=1;n,p=gamma(schema,p);name=schema[p:p+n].decode();p+=n
        fields.append((name,typ))
    row=bytearray(records[1]);p=0;changed=False
    for name,typ in fields:
        base=typ&15;count=1
        if typ&16:count,p=gamma(row,p)
        size=1 if base==10 else {1:1,2:1,3:2,4:2,5:4,6:4,7:8,8:8}[base]
        if name=='pause_mode':
            assert size==1 and count==1
            old=row[p];row[p]=1;changed=True  # PauseMode::Normal bit, not a calendar/economy change.
        p+=size*count
    assert p==len(row) and changed
    return [records[0],bytes(row)],old


def validate_empty_world(original,pilot):
    assert original['industry_records']==pilot['industry_records']==0
    assert original['industry_tiles']==pilot['industry_tiles']==0
    for tag in ['VEHS','STNN','PSAC']:
        assert original['chunks'][tag]['records']==pilot['chunks'][tag]['records']==1,tag
    a=original['newgrfs'];b=pilot['newgrfs'];assert len(a)==len(b)==15
    for old,new in zip(a,b):
        if old['grfid']=='4A4B8808':
            assert new['grfid']=='4B484531' and new['version']==2
            assert new['params']==old['params']+[1]
        else:assert old==new,(old,new)


def main():
    if not __debug__:raise SystemExit('Safety assertions required; do not run this tool with Python -O')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path);ap.add_argument('editor_pilot',type=Path)
    ap.add_argument('output',type=Path);ap.add_argument('--report',required=True,type=Path)
    args=ap.parse_args()
    assert not args.output.exists() and not args.report.exists()
    original=inspect(args.source);pilot=inspect(args.editor_pilot)
    validate_empty_world(original,pilot)
    raw=args.source.read_bytes();payload=decode(raw)
    parts=list(chunks(payload));parts=[(tag,kind,[bytes(r) for r in records]) for tag,kind,records in parts]
    assert b''.join(encode(tag,kind,records) for tag,kind,records in parts)+b'\0'*4==payload
    editor={tag:(kind,[bytes(r) for r in records]) for tag,kind,records in chunks(decode(args.editor_pilot.read_bytes()))}
    output=[];changes=[];old_pause=None
    for tag,kind,records in parts:
        before=encode(tag,kind,records)
        if tag in ['NGRF','GLOG']:kind,records=editor[tag]
        elif tag in ['IIDS','TIDS']:records=records[:1]
        elif tag=='DATE':records,old_pause=replace_pause(records)
        after=encode(tag,kind,records);output.append(after)
        if after!=before:changes.append(tag)
    assert set(changes)=={'NGRF','GLOG','IIDS','TIDS','DATE'}
    args.output.write_bytes(raw[:8]+lzma.compress(b''.join(output)+b'\0'*4))
    result=inspect(args.output)
    protected=[tag for tag in original['chunks'] if tag.startswith(('MAP','M3','M6','M7','M8')) or tag in ['CITY','OBJS','STNN','VEHS','PATS','ECMY']]
    for tag in protected:assert original['chunks'][tag]==result['chunks'][tag],tag
    report=dict(method='Editor-generated NGRF/GLOG; empty orphan IIDS/TIDS; original map/towns restored; start paused',
                source_sha256=original['sha256'],editor_pilot_sha256=pilot['sha256'],output_sha256=result['sha256'],
                source=original['path'],output=str(args.output.resolve()),changed_chunks=changes,
                previous_pause_mode=old_pause,new_pause_mode=1,protected_chunks_identical=protected,
                safety_preconditions='Zero industry records/tiles, zero vehicles/stations/persistent storage; exact other 14 GRFs unchanged',
                engine_reference='JGRPP 0.73.4 src/sl/newgrf_sl.cpp Load_NewGRFMapping resets managers before loading records',
                runtime_verified=False)
    args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
