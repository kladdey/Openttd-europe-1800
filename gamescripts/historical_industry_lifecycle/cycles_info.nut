class LifecycleInfo extends GSInfo {
 function GetAuthor(){return "Europe historical economy project";}
 function GetName(){return "Historical Industry Lifecycle";}
 function GetDescription(){return "Phase 7G v6: bounded regional cycles; AXIS 0.6 retained.";}
 function GetVersion(){return 6;}
 function MinVersionToLoad(){return 5;}
 function GetDate(){return "2026-11-01";}
 function GetShortName(){return "HIL1";}
 function CreateInstance(){return "CyclesController";}
 function GetAPIVersion(){return "16";}
}
RegisterGS(LifecycleInfo());
