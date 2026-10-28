class HistoricalSteelProductionInfo extends GSInfo {
    function GetAuthor() { return "Openttd-europe-1800 contributors"; }
    function GetName() { return "Historical Steel Production Test"; }
    function GetDescription() { return "Isolated transport and save/reload fixture; never use in a campaign."; }
    function GetVersion() { return 1; }
    function GetDate() { return "2026-10-28"; }
    function CreateInstance() { return "HistoricalSteelProductionTest"; }
    function GetShortName() { return "HSPT"; }
    function GetAPIVersion() { return "16"; }
}
RegisterGS(HistoricalSteelProductionInfo());
