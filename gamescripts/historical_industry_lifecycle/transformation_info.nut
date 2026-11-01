class LifecycleInfo extends GSInfo {
 function GetAuthor(){return "Europe historical economy project";}
 function GetName(){return "Historical Industry Lifecycle";}
 function GetDescription(){return "Phase 7H v7: two regional transformations; AXIS 0.6 retained.";}
 function GetVersion(){return 7;}
 function MinVersionToLoad(){return 6;}
 function GetDate(){return "2026-11-01";}
 function GetShortName(){return "HIL1";}
 function CreateInstance(){return "TransformationController";}
 function GetAPIVersion(){return "16";}
}
RegisterGS(LifecycleInfo());
