// SPDX-License-Identifier: GPL-2.0-only
class HistoricalSteelProductionTest extends GSController {
    state = null;
    function Save() { return this.state; }
    function Load(version, data) { this.state = data; }
    function Require(value, text) { if (!value) throw text + ": " + GSError.GetLastErrorString(); }
    function Tile(x, y) { return GSMap.GetTileIndex(x, y); }
    function Cargo(label) {
        local list = GSCargoList();
        for (local c = list.Begin(); !list.IsEnd(); c = list.Next()) if (GSCargo.GetCargoLabel(c) == label) return c;
        throw "Missing cargo " + label;
    }
    function Industry(id, x, y) {
        local type = GSIndustryType.ResolveNewGRFID(0x4B484531, id);
        this.Require(GSIndustryType.BuildIndustry(type, this.Tile(x, y)), "industry " + id);
        local list = GSIndustryList();
        for (local i = list.Begin(); !list.IsEnd(); i = list.Next()) if (GSIndustry.GetIndustryType(i) == type) return i;
        throw "Industry was built but not found";
    }
    function Stop(x, y) {
        local tile = this.Tile(x - 3, y + 2);
        this.Require(GSRoad.BuildRoad(this.Tile(x - 6, y + 2), this.Tile(x - 4, y + 2)), "stop approach");
        this.Require(GSRoad.BuildRoadStation(tile, this.Tile(x - 4, y + 2), GSRoad.ROADVEHTYPE_TRUCK, GSStation.STATION_NEW), "truck stop");
        GSRoad.BuildRoad(tile, this.Tile(x - 4, y + 2));
        this.Require(GSRoad.AreRoadTilesConnected(tile, this.Tile(x - 4, y + 2)), "stop road connection");
        return tile;
    }
    function Truck(engine, cargo, source, destination, start, full = true) {
        local v = GSVehicle.BuildVehicleWithRefit(this.state.depot, engine, cargo);
        this.Require(GSVehicle.IsValidVehicle(v), "vehicle for cargo " + cargo);
        this.Require(GSOrder.AppendOrder(v, source, (full ? GSOrder.OF_FULL_LOAD : GSOrder.OF_NONE) | GSOrder.OF_NO_UNLOAD), "pickup order");
        this.Require(GSOrder.AppendOrder(v, destination, GSOrder.OF_UNLOAD | GSOrder.OF_NO_LOAD), "delivery order");
        if (start) this.Require(GSVehicle.StartStopVehicle(v), "start truck");
        return v;
    }
    function FindClearBlock() {
        for (local y = 12; y < 130; y += 8) {
            for (local x = 12; x < 160; x += 8) {
                local clear = true;
                for (local dy = 0; dy < 90 && clear; dy++) for (local dx = 0; dx < 70; dx++) {
                    if (!GSTile.IsBuildable(this.Tile(x + dx, y + dy)) || GSTile.GetSlope(this.Tile(x + dx, y + dy)) != GSTile.SLOPE_FLAT) { clear = false; break; }
                }
                if (clear) return {x=x, y=y};
            }
        }
        throw "No clear flat diagnostic block";
    }
    function Setup() {
        this.state = {phase=0};
        for (local wait = 0; wait < 100 && GSCompany.ResolveCompanyID(0) == GSCompany.COMPANY_INVALID; wait++) this.Sleep(1);
        this.Require(GSCompany.ResolveCompanyID(0) != GSCompany.COMPANY_INVALID, "test company");
        GSCompany.ChangeBankBalance(0, 100000000, GSCompany.EXPENSES_OTHER, GSMap.TILE_INVALID);
        local labels = ["COAL", "IORE", "COKE", "IRON", "STEL", "SLAG"];
        this.state.cargo <- {};
        local engines = {};
        local list = GSEngineList(GSVehicle.VT_ROAD);
        foreach (label in labels) {
            local cargo = this.Cargo(label);
            this.state.cargo[label] <- cargo;
            if (label == "SLAG") continue;
            local selected = null;
            for (local e = list.Begin(); !list.IsEnd(); e = list.Next()) {
                if (GSEngine.IsValidEngine(e) && GSEngine.CanRefitCargo(e, cargo)) { selected = e; break; }
            }
            this.Require(selected != null, "refittable diagnostic engine for " + label);
            GSLog.Info("PRODTEST ENGINE " + label + "=" + GSEngine.GetName(selected) + " id=" + selected);
            // Explicit diagnostic concession: base trucks are enabled before
            // their normal dates ONLY in this disposable 1860 test company.
            this.Require(GSEngine.EnableForCompany(selected, 0), "enable diagnostic truck");
            engines[label] <- selected;
        }
        local base = this.FindClearBlock();
        this.state.base <- base;
        local mode = GSCompanyMode(0);
        GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD);
        local x = base.x;
        local y = base.y;
        this.Industry(0, x + 10, y + 10);
        this.Industry(4, x + 45, y + 10);
        this.Industry(78, x + 10, y + 35);
        this.Industry(7, x + 45, y + 35);
        this.state.works <- this.Industry(2, x + 10, y + 65);
        this.state.customer <- this.Industry(9, x + 45, y + 65);
        this.Require(GSRoad.BuildRoad(this.Tile(x + 4, y + 4), this.Tile(x + 4, y + 80)), "left road");
        this.Require(GSRoad.BuildRoad(this.Tile(x + 39, y + 4), this.Tile(x + 39, y + 80)), "right road");
        this.Require(GSRoad.BuildRoad(this.Tile(x + 4, y + 4), this.Tile(x + 39, y + 4)), "joining road");
        this.Require(GSRoad.BuildRoad(this.Tile(x + 4, y + 55), this.Tile(x + 39, y + 55)), "middle joining road");
        this.state.depot <- this.Tile(x + 3, y + 6);
        this.Require(GSRoad.BuildRoadDepot(this.state.depot, this.Tile(x + 4, y + 6)), "depot");
        GSRoad.BuildRoad(this.state.depot, this.Tile(x + 4, y + 6));
        this.Require(GSRoad.AreRoadTilesConnected(this.state.depot, this.Tile(x + 4, y + 6)), "depot road connection");
        local coal = this.Stop(x + 10, y + 10);
        local ore = this.Stop(x + 45, y + 10);
        local coke = this.Stop(x + 10, y + 35);
        local blast = this.Stop(x + 45, y + 35);
        local works = this.Stop(x + 10, y + 65);
        local customer = this.Stop(x + 45, y + 65);
        this.state.works_station <- GSStation.GetStationID(works);
        foreach (label in ["IRON", "COKE"]) this.Require(GSTile.GetCargoAcceptance(works, this.state.cargo[label], 1, 1, 3) >= 8, "works station accepts " + label);
        this.Truck(engines.COAL, this.state.cargo.COAL, coal, coke, true);
        this.Truck(engines.IORE, this.state.cargo.IORE, ore, blast, true);
        this.state.iron_truck <- this.Truck(engines.IRON, this.state.cargo.IRON, blast, works, true, false);
        this.state.coke_truck <- this.Truck(engines.COKE, this.state.cargo.COKE, coke, works, false);
        this.state.steel_truck <- this.Truck(engines.STEL, this.state.cargo.STEL, works, customer, true, false);
        GSCargoMonitor.GetIndustryPickupAmount(0, this.state.cargo.STEL, this.state.works, true);
        GSCargoMonitor.GetIndustryDeliveryAmount(0, this.state.cargo.STEL, this.state.customer, true);
        GSLog.Info("PRODTEST SETUP works=" + this.state.works + " customer=" + this.state.customer);
    }
    function Checkpoint() {
        local iron = this.state.cargo.IRON;
        local coke = this.state.cargo.COKE;
        local steel = this.state.cargo.STEL;
        local start = GSController.GetTick();
        while (GSIndustry.GetStockpiledCargo(this.state.works, iron) < 6) {
            if (GSController.GetTick() - start > 24000) throw "Timed out waiting for transported pig iron";
            GSLog.Info("PRODTEST WAIT_IRON tick=" + GSController.GetTick() + " stock=" + GSIndustry.GetStockpiledCargo(this.state.works, iron) +
                " paused=" + GSGame.IsPaused() + " ore_prod=" + GSIndustry.GetLastMonthProduction(1, this.state.cargo.IORE) +
                " pigiron_prod=" + GSIndustry.GetLastMonthProduction(3, iron));
            {
                local mode = GSCompanyMode(0);
                GSLog.Info("PRODTEST TRUCK iron_pos=" + GSVehicle.GetLocation(this.state.iron_truck) + " iron_load=" + GSVehicle.GetCargoLoad(this.state.iron_truck, iron));
            }
            this.Sleep(740);
        }
        {
            local mode = GSCompanyMode(0);
            this.Require(GSVehicle.StartStopVehicle(this.state.iron_truck), "stop iron deliveries");
        }
        this.Sleep(256);
        this.state.saved_iron <- GSIndustry.GetStockpiledCargo(this.state.works, iron);
        this.state.saved_coke <- GSIndustry.GetStockpiledCargo(this.state.works, coke);
        this.Require(this.state.saved_iron > 0 && this.state.saved_coke == 0, "iron-only stockpile");
        this.Require(GSIndustry.GetLastMonthProduction(this.state.works, steel) == 0, "no steel from iron alone");
        this.Require(GSCargoMonitor.GetIndustryPickupAmount(0, steel, this.state.works, true) == 0, "no premature steel pickup");
        this.state.phase = 1;
        GSLog.Info("PRODTEST CHECKPOINT iron=" + this.state.saved_iron + " coke=" + this.state.saved_coke + " steel=0");
        while (true) this.Sleep(74);
    }
    function Resume() {
        this.Require(this.state.phase == 1, "saved phase");
        local cargo = this.state.cargo;
        local iron = GSIndustry.GetStockpiledCargo(this.state.works, cargo.IRON);
        local coke = GSIndustry.GetStockpiledCargo(this.state.works, cargo.COKE);
        this.Require(iron == this.state.saved_iron && coke == this.state.saved_coke, "stockpile survived reload");
        GSLog.Info("PRODTEST RELOAD iron=" + iron + " coke=" + coke);
        {
            local mode = GSCompanyMode(0);
            this.Require(GSVehicle.StartStopVehicle(this.state.coke_truck), "start coke deliveries after reload");
        }
        local start = GSController.GetTick();
        local delivered = 0;
        local produced = 0;
        local slag = 0;
        local polls = 0;
        while (delivered == 0) {
            if (GSController.GetTick() - start > 20000) throw "Timed out waiting for steel delivery";
            delivered += GSCargoMonitor.GetIndustryDeliveryAmount(0, cargo.STEL, this.state.customer, true);
            local monthly_steel = GSIndustry.GetLastMonthProduction(this.state.works, cargo.STEL);
            if (monthly_steel > 0) {
                produced = monthly_steel;
                slag = GSIndustry.GetLastMonthProduction(this.state.works, cargo.SLAG);
            }
            if (polls++ % 10 == 0) GSLog.Info("PRODTEST WAIT_STEEL tick=" + GSController.GetTick() +
                " iron=" + GSIndustry.GetStockpiledCargo(this.state.works, cargo.IRON) +
                " coke=" + GSIndustry.GetStockpiledCargo(this.state.works, cargo.COKE) + " steel_month=" + monthly_steel);
            this.Sleep(74);
        }
        // Wait until a completed production month records both output cargoes.
        while (produced == 0) {
            if (GSController.GetTick() - start > 26000) throw "No completed steel production month";
            produced = GSIndustry.GetLastMonthProduction(this.state.works, cargo.STEL);
            slag = GSIndustry.GetLastMonthProduction(this.state.works, cargo.SLAG);
            this.Sleep(74);
        }
        this.Require(produced == 3 * slag, "steel/slag batch ratio");
        local remaining = GSIndustry.GetStockpiledCargo(this.state.works, cargo.IRON);
        this.Require(remaining == this.state.saved_iron % 3, "pig iron remainder");
        GSLog.Info("PRODTEST DONE steel_last_month=" + produced + " slag_last_month=" + slag +
            " delivered_steel=" + delivered + " remaining_iron=" + remaining + " failures=0");
        this.state.phase = 2;
        while (true) this.Sleep(365);
    }
    function Start() {
        try {
            this.Sleep(1);
            GSLog.Info("PRODTEST START year=" + GSDate.GetYear(GSDate.GetCurrentDate()));
            if (this.state == null) { this.Setup(); this.Checkpoint(); }
            else this.Resume();
        } catch (error) {
            GSLog.Error("PRODTEST FAILED " + error);
            while (true) this.Sleep(365);
        }
    }
}
