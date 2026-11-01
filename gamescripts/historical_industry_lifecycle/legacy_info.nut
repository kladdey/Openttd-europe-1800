class LifecycleInfo extends GSInfo {
 function GetAuthor(){return "Europe historical economy project";}
 function GetName(){return "Historical Industry Lifecycle";}
 function GetDescription(){return "Experimental v2: explicitly enrolled legacy mine decline, service survival and one-shot closure; separate AXIS 0.5 required.";}
 function GetVersion(){return 2;}
 function MinVersionToLoad(){return 1;}
 function GetDate(){return "2026-10-29";}
 function GetShortName(){return "HIL1";}
 function CreateInstance(){return "LegacyLifecycleController";}
 function GetAPIVersion(){return "16";}
}
RegisterGS(LifecycleInfo());
