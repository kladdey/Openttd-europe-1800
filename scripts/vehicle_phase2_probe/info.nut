class Phase2Info extends GSInfo {
 function GetAuthor(){return "Local economy investigation";}
 function GetName(){return "VehicleEconomyPhase2";}
 function GetDescription(){return "Measurements on disposable maps only";}
 function GetVersion(){return 1;}
 function GetDate(){return "2026-10-28";}
 function GetShortName(){return "VEP2";}
 function CreateInstance(){return "Phase2Probe";}
 function GetAPIVersion(){return "15";}
}
RegisterGS(Phase2Info());
