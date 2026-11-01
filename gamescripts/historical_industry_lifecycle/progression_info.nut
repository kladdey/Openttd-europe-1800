class LifecycleInfo extends GSInfo {
 function GetAuthor(){return "Europe historical economy project";}
 function GetName(){return "Historical Industry Lifecycle";}
 function GetDescription(){return "Phase 7D v4: layout-aware regional progression; AXIS 0.6 retained.";}
 function GetVersion(){return 4;}
 function MinVersionToLoad(){return 3;}
 function GetDate(){return "2026-11-01";}
 function GetShortName(){return "HIL1";}
 function CreateInstance(){return "ProgressionController";}
 function GetAPIVersion(){return "16";}
}
RegisterGS(LifecycleInfo());
