class HistoricalIndustryProbe extends GSController {
    attempted = false;

    function Save() { return {version = 1, attempted = this.attempted}; }
    function Load(version, data) {
        // Unknown saved state fails closed: do not construct again.
        this.attempted = !("attempted" in data) || data.attempted;
    }

    function RunProbe() {
        // GSDate uses economy time in this exact JGRPP version. Require calendar
        // timekeeping so this value also represents historical calendar year.
        if (!GSGameSettings.IsValid("economy.timekeeping_units") ||
            GSGameSettings.GetValue("economy.timekeeping_units") != 0) {
            GSLog.Warning("Unsupported timekeeping: calendar-based timekeeping required.");
            return;
        }
        local year = GSDate.GetYear(GSDate.GetCurrentDate());
        GSLog.Info("Current year: " + year);
        local types = GSIndustryTypeList();
        for (local t = types.Begin(); !types.IsEnd(); t = types.Next()) {
            GSLog.Info("Type " + t + ": " + GSIndustryType.GetName(t) +
                "; accepted=" + GSIndustryType.GetAcceptedCargo(t).Count() +
                "; produced=" + GSIndustryType.GetProducedCargo(t).Count());
        }
        // API uses GRFID in displayed byte order. AXIS header: JK\88\08;
        // AXIS 2.3.1 global_constants.py: coal_mine=0. Never use a game-local ID.
        local target = GSIndustryType.ResolveNewGRFID(0x4A4B8808, 0);
        if (!GSIndustryType.IsValidIndustryType(target)) {
            GSLog.Warning("AXIS coal mine mapping absent; no construction.");
            return;
        }
        if (this.attempted || GSController.GetSetting("attempt_build") == 0) {
            GSLog.Info("Inventory complete; construction disabled or already attempted.");
            return;
        }
        this.attempted = true;
        if (!GSIndustryType.CanBuildIndustry(target)) {
            GSLog.Warning("Construction unavailable: check AXIS spawning parameter and year.");
            return;
        }
        // A bounded runtime grid, NOT historical Europe coordinates. Check clear
        // land before asking the engine, which validates all AXIS location rules.
        local sx = GSMap.GetMapSizeX();
        local sy = GSMap.GetMapSizeY();
        local tries = 0;
        for (local gy = 1; gy <= 16; gy++) {
            for (local gx = 1; gx <= 16; gx++) {
                local x = (sx * gx) / 17;
                local y = (sy * gy) / 17;
                if (x + 8 >= sx || y + 8 >= sy) continue;
                local clear = true;
                for (local dy = 0; dy < 8 && clear; dy++) {
                    for (local dx = 0; dx < 8; dx++) {
                        if (!GSTile.IsBuildable(GSMap.GetTileIndex(x + dx, y + dy))) {
                            clear = false;
                            break;
                        }
                    }
                }
                if (!clear) continue;
                local tile = GSMap.GetTileIndex(x, y);
                tries++;
                if (GSIndustryType.BuildIndustry(target, tile)) {
                    GSLog.Info("SUCCESS: AXIS coal mine built at tile " + tile +
                        " after " + tries + " command attempts.");
                    return;
                }
                GSLog.Info("Build rejected at " + tile + ": " + GSError.GetLastErrorString());
                if (tries >= 32) break;
                this.Sleep(1);
            }
            if (tries >= 32) break;
        }
        GSLog.Warning("FAILED: no accepted site in bounded search; commands attempted=" + tries);
    }

    function Start() {
        // Default GS context is deity; keep it (do not enter a player company).
        try { this.RunProbe(); }
        catch (error) { GSLog.Error("Probe stopped (missing API or runtime failure): " + error); }
        while (true) this.Sleep(365);
    }
}
