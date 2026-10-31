class LifecycleInfo extends GSInfo {
 function GetAuthor(){return "Europe historical economy project";}
 function GetName(){return "Historical Industry Lifecycle";}
 function GetDescription(){return "Experimental v3 regional expansion and guarded processor transition; separate AXIS 0.6 required.";}
 function GetVersion(){return 3;}
 function MinVersionToLoad(){return 2;}
 function GetDate(){return "2026-10-29";}
 function GetShortName(){return "HIL1";}
 function CreateInstance(){return "ExpansionLifecycleController";}
 function GetAPIVersion(){return "16";}
}
RegisterGS(LifecycleInfo());
