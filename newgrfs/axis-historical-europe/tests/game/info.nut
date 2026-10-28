class HistoricalSteelRuntimeInfo extends GSInfo {
    function GetAuthor() { return "Openttd-europe-1800 contributors"; }
    function GetName() { return "Historical Steel Runtime Test"; }
    function GetDescription() { return "Disposable-test-only AXIS Historical Europe construction checks."; }
    function GetVersion() { return 1; }
    function GetDate() { return "2026-10-28"; }
    function CreateInstance() { return "HistoricalSteelRuntimeTest"; }
    function GetShortName() { return "HSRT"; }
    function GetAPIVersion() { return "16"; }
    function GetSettings() {
        AddSetting({name="historical", description="Expected historical mode", min_value=0, max_value=1, default_value=1, flags=0});
        AddSetting({name="spawning", description="Expected AXIS spawning permission", min_value=0, max_value=1, default_value=1, flags=0});
    }
}
RegisterGS(HistoricalSteelRuntimeInfo());
