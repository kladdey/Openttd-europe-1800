class HistoricalIndustryProbeInfo extends GSInfo {
    function GetAuthor()      { return "Openttd-europe-1800 contributors"; }
    function GetName()        { return "Historical Industry Probe"; }
    function GetDescription() { return "Isolated AXIS 2.3.1 construction probe. Use a disposable game only."; }
    function GetVersion()     { return 1; }
    function GetDate()        { return "2026-10-28"; }
    function CreateInstance() { return "HistoricalIndustryProbe"; }
    function GetShortName()   { return "HIPr"; }
    function GetAPIVersion()  { return "16"; }
    function GetSettings() {
        AddSetting({name = "attempt_build", description = "Attempt one coal mine construction (disposable game only)",
            min_value = 0, max_value = 1, default_value = 0, flags = 0});
    }
}
RegisterGS(HistoricalIndustryProbeInfo());
