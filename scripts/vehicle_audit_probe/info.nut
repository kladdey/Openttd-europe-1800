class VehicleAuditInfo extends GSInfo {
 function GetAuthor() { return "Local audit"; }
 function GetName() { return "VehicleAuditProbe"; }
 function GetDescription() { return "Read-only engine API measurements on disposable map"; }
 function GetVersion() { return 1; }
 function GetDate() { return "2026-10-28"; }
 function GetShortName() { return "VAP1"; }
 function CreateInstance() { return "VehicleAuditProbe"; }
 function GetAPIVersion() { return "15"; }
}
RegisterGS(VehicleAuditInfo());
