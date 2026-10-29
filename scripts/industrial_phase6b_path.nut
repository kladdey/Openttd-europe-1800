 // Goal-directed search; every proposed link uses real command tests.
 function HPush(heap,item){heap.append(item);local i=heap.len()-1;while(i>0){local p=((i-1)/2).tointeger();if(heap[p].score<=heap[i].score)break;local t=heap[p];heap[p]=heap[i];heap[i]=t;i=p;}}
 function HPop(heap){local first=heap[0],last=heap.pop();if(heap.len()>0){heap[0]=last;local i=0;while(true){local left=i*2+1;if(left>=heap.len())break;local right=left+1,b=right<heap.len() && heap[right].score<heap[left].score?right:left;if(heap[i].score<=heap[b].score)break;local t=heap[i];heap[i]=heap[b];heap[b]=t;i=b;}
  }
  return first;}
 function Path(start,previous,goal){
  local nodes=[{tile=start,prev=previous,backidx=-1,g=0}],heap=[],seen={};
  HPush(heap,{index=0,score=GSMap.DistanceManhattan(start,goal)});seen[previous+"_"+start]<-true;
  local xmin=max(1,min(GSMap.GetTileX(start),GSMap.GetTileX(goal))-24),xmax=min(GSMap.GetMapSizeX()-2,max(GSMap.GetTileX(start),GSMap.GetTileX(goal))+24);
  local ymin=max(1,min(GSMap.GetTileY(start),GSMap.GetTileY(goal))-24),ymax=min(GSMap.GetMapSizeY()-2,max(GSMap.GetTileY(start),GSMap.GetTileY(goal))+24);
  local expanded=0;
  while(heap.len()>0 && expanded<45000){
   local index=HPop(heap).index,node=nodes[index];expanded++;
   if(node.tile==goal && Link(node.prev,goal,Step(goal,MODE=="rail"?-1:1,0))){local path=[];while(index>=0){path.insert(0,nodes[index].tile);index=nodes[index].backidx;}return path;}
   local adjacent=[];
   foreach(d in [[1,0],[-1,0],[0,1],[0,-1]]){
    local n=Step(node.tile,d[0],d[1]);adjacent.append(n);
    if(MODE=="road" && GSTile.IsWaterTile(n))for(local length=2;length<=12;length++){
     local end=Step(node.tile,d[0]*length,d[1]*length);if(!GSTile.IsWaterTile(end)){adjacent.append(end);break;}
    }
   }
   if(MODE=="road" && GSRoad.HasRoadType(node.tile,GSRoad.GetCurrentRoadType())){
    if(GSBridge.IsBridgeTile(node.tile))adjacent.append(GSBridge.GetOtherBridgeEnd(node.tile));
    if(GSTunnel.IsTunnelTile(node.tile))adjacent.append(GSTunnel.GetOtherTunnelEnd(node.tile));
   }
   foreach(next in adjacent){
    local x=GSMap.GetTileX(next),y=GSMap.GetTileY(next),key=node.tile+"_"+next;
    if(x<xmin || x>xmax || y<ymin || y>ymax || next==node.prev || key in seen)continue;
    if(MODE=="road" && GSRoad.IsDriveThroughRoadStationTile(next))continue;
    if(MODE=="rail" && GSRail.IsRailStationTile(next))continue;
    if(!Link(node.prev,node.tile,next))continue;
    local g=node.g+GSMap.DistanceManhattan(node.tile,next);seen[key]<-true;
    nodes.append({tile=next,prev=node.tile,backidx=index,g=g});HPush(heap,{index=nodes.len()-1,score=g+GSMap.DistanceManhattan(next,goal)*1.5});
   }
  }
  GSLog.Info("I6 PATH_BLOCKED|"+expanded);return null;
 }
