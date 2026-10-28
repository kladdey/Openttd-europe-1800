class HistoricalFundingCompanyInfo extends AIInfo {
    function GetAuthor() { return "Openttd-europe-1800 contributors"; }
    function GetName() { return "Historical Funding Test Company"; }
    function GetDescription() { return "Idle company for isolated funding-command tests."; }
    function GetVersion() { return 1; }
    function GetDate() { return "2026-10-28"; }
    function CreateInstance() { return "HistoricalFundingCompany"; }
    function GetShortName() { return "HFCo"; }
    function GetAPIVersion() { return "16"; }
}
RegisterAI(HistoricalFundingCompanyInfo());
