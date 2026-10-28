class HistoricalSteelRuntimeTest extends GSController {
    function FundingProbe(year, historical) {
        for (local wait = 0; wait < 100 && GSCompany.ResolveCompanyID(0) == GSCompany.COMPANY_INVALID; wait++) this.Sleep(1);
        if (GSCompany.ResolveCompanyID(0) == GSCompany.COMPANY_INVALID) {
            GSLog.Error("AHETEST no funding test company");
            return 1;
        }
        GSCompany.ChangeBankBalance(0, 100000000, GSCompany.EXPENSES_OTHER, GSMap.TILE_INVALID);
        local failures = 0;
        local mode = GSCompanyMode(0); // UserCreation, not deity RandomCreation.
        foreach (target in [{id=2, year=1860}, {id=79, year=1906}, {id=77, year=1952}]) {
            local type = GSIndustryType.ResolveNewGRFID(0x4B484531, target.id);
            local expected = !historical || year >= target.year;
            local allowed = GSIndustryType.CanBuildIndustry(type);
            local tile = null;
            if (allowed) tile = this.FindSite(type);
            else if (GSIndustryType.BuildIndustry(type, GSMap.GetTileIndex(12, 12))) failures++;
            GSLog.Info("AHETEST FUND id=" + target.id + " allowed=" + allowed + " expected=" + expected + " built=" + (tile != null));
            if (allowed != expected || (expected && tile == null)) failures++;
        }
        return failures;
    }

    function FindSite(type, anchor = null) {
        local attempts = 0;
        local size = GSMap.GetMapSizeX();
        for (local y = 12; y < size - 12; y += 8) {
            for (local x = 12; x < size - 12; x += 8) {
                local tile = GSMap.GetTileIndex(x, y);
                if (anchor != null && GSMap.DistanceManhattan(tile, anchor) > 60) continue;
                local clear = true;
                for (local dy = 0; dy < 8 && clear; dy++) {
                    for (local dx = 0; dx < 8; dx++) {
                        if (!GSTile.IsBuildable(GSMap.GetTileIndex(x + dx, y + dy))) { clear = false; break; }
                    }
                }
                if (!clear) continue;
                attempts++;
                if (GSIndustryType.BuildIndustry(type, tile)) return tile;
                if (attempts >= 200) return null;
                this.Sleep(1);
            }
        }
        return null;
    }

    function Start() {
        this.Sleep(1);
        local year = GSDate.GetYear(GSDate.GetCurrentDate());
        local historical = GSController.GetSetting("historical") == 1;
        local spawning = GSController.GetSetting("spawning") == 1;
        local failures = 0;
        GSLog.Info("AHETEST START year=" + year);
        local cargos = GSCargoList();
        local types = GSIndustryTypeList();
        GSLog.Info("AHETEST INVENTORY cargos=" + cargos.Count() + " types=" + types.Count());
        if (cargos.Count() != 64 || types.Count() != 92) failures++;
        local blast_type = GSIndustryType.ResolveNewGRFID(0x4B484531, 7);
        local blast = spawning ? this.FindSite(blast_type) : null;
        foreach (target in [{id=2, year=1860}, {id=79, year=1906}, {id=77, year=1952}]) {
            local type = GSIndustryType.ResolveNewGRFID(0x4B484531, target.id);
            if (!GSIndustryType.IsValidIndustryType(type)) { failures++; continue; }
            local expected = spawning && (!historical || year >= target.year);
            local allowed = GSIndustryType.CanBuildIndustry(type);
            local instances = GSIndustryList();
            local count = 0;
            for (local i = instances.Begin(); !instances.IsEnd(); i = instances.Next()) {
                if (GSIndustry.GetIndustryType(i) == type) count++;
            }
            if (historical && year < target.year && count != 0) failures++;
            local tile = null;
            if (allowed) tile = this.FindSite(type, target.id == 77 ? blast : null);
            else if (GSIndustryType.BuildIndustry(type, GSMap.GetTileIndex(12, 12))) failures++;
            GSLog.Info("AHETEST TYPE id=" + target.id + " allowed=" + allowed + " expected=" + expected +
                " initial=" + count + " built=" + (tile != null));
            if (allowed != expected || (expected && tile == null)) failures++;
        }
        failures += this.FundingProbe(year, historical);
        GSLog.Info("AHETEST DONE failures=" + failures);
        while (true) this.Sleep(365);
    }
}
