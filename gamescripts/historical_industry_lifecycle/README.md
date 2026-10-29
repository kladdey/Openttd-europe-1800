# Historical Industry Lifecycle — experimental v1

GPL-2.0-only source. Requires **stock JGRPP 0.73.4**, Historical AXIS **0.4.0 lifecycle candidate**, Classic historical economy, NewGRF parameter 11 enabled, calendar timekeeping mode 0 and a **new separate scenario**. Do not attach to an existing campaign. Only newly deity-founded scheduled coal mines are managed.

`schedule.json` is the authored production configuration. From repository root run `python scripts/lifecycle_phase7a_schedule.py` to validate and regenerate native `schedule.nut` and the schedule CSV. Copy `info.nut`, `main.nut`, `schedule.nut` together into an **isolated** OpenTTD `game/lifecycle` directory. Select **Historical Industry Lifecycle** in that profile's Scenario Editor, then save a new scenario. The delivered local profile already has these files; launch with `python scripts/lifecycle_phase7a_launch.py`.

The save ledger is schema 1. Event IDs, dates, sites, lifetimes, dependencies and seed form a saved contract. Do not edit the schedule on an existing save without an explicit migration. Missing state after the first event, unknown schema, a changed contract or unsupported clock mode fails closed. Test code injection is restricted to disposable profiles; the production bundle does not use accelerated dates.

See [architecture](../../docs/PHASE7A_LIFECYCLE_ARCHITECTURE.md), [engine evidence](../../docs/PHASE7A_ENGINE_VALIDATION.md) and [readiness](../../docs/PHASE7A_READINESS.md). Neither the script nor these tests constitute a complete campaign-wide historical scheduler.
