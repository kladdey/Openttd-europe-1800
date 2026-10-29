class LifecycleInfo extends GSInfo {
 function GetAuthor(){return "Europe historical economy project";}
 function GetName(){return "Historical Industry Lifecycle";}
 function GetDescription(){return "Experimental persistent historical coal-mine openings, warnings and closure adapter. Requires separate AXIS 0.4 candidate, parameter 11 enabled; not for existing campaigns.";}
 function GetVersion(){return 1;}
 function GetDate(){return "2026-10-29";}
 function GetShortName(){return "HIL1";}
 function CreateInstance(){return "LifecycleController";}
 function GetAPIVersion(){return "16";}
}
RegisterGS(LifecycleInfo());
