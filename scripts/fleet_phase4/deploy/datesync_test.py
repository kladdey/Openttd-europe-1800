"""Economy/calendar date sync for the Europe 1830 campaign: verification on save COPIES (test area only).

Problem: calendar 1893, economy date (finances ledger, GSDate) 1863, a 30-year offset from the 1800 scenario.

Method tested and REJECTED: switching economy.timekeeping_units to wallclock and back
(src/settings_table.cpp ChangeTimekeepingUnits). On a server the change applies one tick later and the
campaign GameScript stops at once ("P7 FATAL|Pinned AXIS/calendar time required", main.nut:814).

Method USED: the change-date cheat (src/cheat_gui.cpp ClickChangeDateCheat), year 1893 -> 1892 -> 1893,
single-player, game paused, on a copy of the package save. In calendar mode it sets the economy date
to the calendar date, shifts vehicle and link-graph dates and the period display offset, and never
leaves calendar mode. The cheat is GUI-only; it was applied by hand on runs/datesync-gui (getfulldate
before/after recorded below) and the result saved to runs/_saves/datesync_synced.sav.

This script verifies that synced save against the unsynced package save:
  1. both run headless with the campaign's own GameScript: dates, GS events, failures, errors
  2. observer copies (measurement GameScript): trains, engine costs, company finances
"""
import hashlib, json, re, shutil, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import phase4 as P4          # noqa: E402
import rv                    # noqa: E402
import save_tools as S       # noqa: E402
import savetest as ST        # noqa: E402
import savecompare as SC     # noqa: E402

PKG = rv.RUNS.parent / 'deploy' / 'europe1830-balance-v1'
SAVE = next(PKG.glob('campaign_*_balance-v1.sav'))
SYNCED = rv.RUNS / '_saves' / 'datesync_synced.sav'
GS_DIR = Path(r'C:\Users\Kladd\Documents\OpenTTD\game')
GRFS = json.loads((PKG / 'balance_grfs.json').read_text())
EXTRAS = [dict(path=str(PKG / 'newgrf' / g['filename']), after=g['after'], grfid=g['grfid']) for g in GRFS]
CHEAT_CONSOLE = {  # RUNTIME, read from the GUI console of the test copy (runs/datesync-gui), 2026-11-12
    'before': ['Calendar Date: 1893-06-05 (691560)', 'Economy Date: 1863-06-06 (680603)', 'Period display offset: -1799', 'Elapsed years: 63'],
    'after': ['Calendar Date: 1893-06-05 (691560)', 'Economy Date: 1893-06-05 (691560)', 'Period display offset: -1829', 'Elapsed years: 63'],
    'finances_window_years_after': [1891, 1892, 1893]}


def campaign_run(tag, save, wall=300):
    """Headless run of a save copy with the campaign's own GameScript; console dates now and next month."""
    rv.KEEP_RUN_DIRS = True
    if (rv.RUNS / tag).exists():
        rv.KEEP_RUN_DIRS = False
        shutil.rmtree(rv.RUNS / tag)
        rv.KEEP_RUN_DIRS = True
    home = rv.prepare(tag, year=1893, seed=734, mode='observe', extras=EXTRAS, load=save,
                      gs_config=dict(watch_months=1, engines=[]))
    for sub in GS_DIR.iterdir():
        if sub.is_dir():
            shutil.copytree(sub, home / 'game' / sub.name)
    (home / 'scripts' / 'game_start.scr').write_text('unpause\ngetfulldate\nschedule on-next-calendar-month later.scr\n')
    (home / 'scripts' / 'later.scr').write_text('getfulldate\n')
    rec = rv.run(home, wall=wall)
    text = (home / 'game.log').read_text(errors='replace')
    rv.KEEP_RUN_DIRS = False
    rv.cleanup(home)
    return rec, text


def gs_events(text):
    ev = re.findall(r'P7 EVENT\|([a-z_]+)\|([^|\s]+)', text)
    bad = [e for e in ev if any(k in e[0] for k in ('failed', 'cancel', 'expired'))] + \
          [(l,) for l in text.splitlines() if 'administrator review' in l or 'authorization expired' in l or 'timed out' in l]
    return ev, bad


def main():
    rv.check_disk('datesync')
    assert SYNCED.exists(), 'apply the change-date cheat on a copy first (see docstring)'
    res = dict(method='change-date cheat 1893 -> 1892 -> 1893 (single-player, paused, save copy)',
               rejected_method='timekeeping_units 1 -> 0: campaign GameScript stops (P7 FATAL|Pinned AXIS/calendar time required)',
               cheat_console=CHEAT_CONSOLE, synced_sha256=hashlib.sha256(SYNCED.read_bytes()).hexdigest())
    for tag, save in (('datesync-control', SAVE), ('datesync-synced', SYNCED)):
        rec, text = campaign_run(tag, save)
        ev, bad = gs_events(text)
        res[tag] = dict(reason=rec['reason'], seconds=rec['seconds'],
                        dates=[l.split('] ')[-1].strip() for l in text.splitlines() if 'Calendar Date:' in l or 'Economy Date:' in l or 'Period display offset' in l],
                        gs_events=len(ev), gs_event_kinds=sorted({e[0] for e in ev}), gs_failures=bad[:20],
                        script_errors=[l for l in text.splitlines() if 'made an error' in l or 'died' in l or 'FATAL' in l][:5])
        (P4.OUT / 'datesync_logs').mkdir(exist_ok=True)
        (P4.OUT / 'datesync_logs' / f'{tag}.log').write_text('\n'.join(l for l in text.splitlines() if 'Date:' in l or 'offset' in l or 'P7 ' in l or 'error' in l.lower() or 'FATAL' in l))

    # observer copies (measurement GameScript), same settings for both. The synced save was made while
    # paused (the cheat was applied paused), so that run unpauses after load like the server admin would.
    recs = {}
    for tag, src in (('datesync-observe-unsynced', SAVE), ('datesync-observe-synced', SYNCED)):
        obs = rv.RUNS / '_saves' / f'{tag}.sav'
        S.rewrite(src, obs, gs_name='RVProbe')
        if (P4.OUT / 'runs' / tag).exists():
            shutil.rmtree(P4.OUT / 'runs' / tag)
        rv.KEEP_RUN_DIRS = True
        home = rv.prepare(tag, year=1893, seed=734, mode='observe', extras=EXTRAS, gs_config=dict(watch_months=2, engines=[]), load=obs)
        (home / 'scripts' / 'game_start.scr').write_text('start_ai EconomyBootstrap\nunpause\n')
        recs[tag] = rv.run(home, wall=900)
        rv.KEEP_RUN_DIRS = False
        rv.cleanup(home)
        obs.unlink()
    b, be = SC.obs('datesync-observe-unsynced')
    s, se = SC.obs('datesync-observe-synced')
    ident = lambda v: {k: (x['owner'], x['unit'], x['engine'], x['wagons'], x['length']) for k, x in v.items()}
    lines = lambda tag: list(__import__('p4lib').A.lines(tag))
    months = lambda tag: [int(f[2]) for f in lines(tag) if f[0] == 'OBSERVE_MONTH']
    comp = lambda tag, m: {f[2]: (int(f[3]), int(f[4])) for f in lines(tag) if f[0] == 'COMPANY' and f[1] == str(m)}
    res['observer'] = dict(reasons={t: r['reason'] for t, r in recs.items()}, trains_before=len(b[0]), trains_after=len(s[0]),
                           identity_unchanged=ident(b[0]) == ident(s[0]),
                           engine_costs_unchanged=all(se[0][e]['running'] == be[0][e]['running'] for e in se[0] if e in be[0]),
                           economy_month_samples_before=months('datesync-observe-unsynced'), economy_month_samples_after=months('datesync-observe-synced'),
                           companies_at_load_identical=comp('datesync-observe-unsynced', 0) == comp('datesync-observe-synced', 0),
                           company_train_running_and_cash_at_load=comp('datesync-observe-synced', 0),
                           company_month2_before=comp('datesync-observe-unsynced', 2), company_month2_after=comp('datesync-observe-synced', 2),
                           note='later months differ slightly because the economy day of month moved from the 6th to the 5th, '
                                'so each sampled month is one economy day longer')
    (P4.OUT / 'datesync_result.json').write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1)[:5000])


if __name__ == '__main__':
    main()
