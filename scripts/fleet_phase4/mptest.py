"""Localhost multiplayer check on a cloned save with the balance GRFs (test area only).

Dedicated server bound to 127.0.0.1 (not advertised), one null-video client that joins, leaves and
rejoins. The server log is scanned for joins, desyncs and GRF mismatches. Also checks that a client
WITHOUT the balance GRFs is refused (GRF mismatch), which is what protects the live campaign.

  python -B mptest.py --variant <name>
"""
import argparse, json, re, subprocess, time
from pathlib import Path
import phase4 as P4
import rv
import variants as V

PORT = 3989


def home_for(tag, extras, load=None):
    rv.KEEP_RUN_DIRS = True
    h = rv.prepare(tag, year=1893, seed=734, mode='observe', extras=extras, load=load,
                   extra_settings={'network.server_game_type': 'local', 'network.client_name': tag[-12:], 'network.server_name': 'rv-local-test'},
                   gs_config=dict(watch_months=600, engines=[]))
    # client/server names live in private.cfg next to the -c config (test dir only)
    (h / 'private.cfg').write_text(f'[network]\nclient_name = rv-{tag[-10:]}\nserver_name = rv-local-test\n')
    return h


def start(home, args, log):
    f = open(home / log, 'wb')
    return subprocess.Popen([str(rv.EXE), '-X', '-x', '-c', str(home / 'test.cfg'), '-s', 'null', '-m', 'null', '-d', 'net=3,misc=1,script=4'] + args,
                            cwd=home, stdout=f, stderr=f, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))


def text(p):
    return Path(p).read_text(errors='replace') if Path(p).exists() else ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', required=True)
    ap.add_argument('--gui', action='store_true', help='normal windowed client (real-time, sync checks performed)')
    ap.add_argument('--seconds', type=int, default=120)
    a = ap.parse_args()
    extras = V.extras(a.variant)
    save = rv.RUNS / '_saves' / f'clone_{a.variant}_gs.sav'
    assert save.exists(), 'run savetest.py first'
    srv = home_for(f'mp-{a.variant}-server', extras, load=save)
    cli = home_for(f'mp-{a.variant}-client', extras)
    bad = home_for(f'mp-{a.variant}-client-nogrf', [])
    S = start(srv, ['-D', f'127.0.0.1:{PORT}', '-g', str(srv / 'game.sav')], 'server.log')
    res = dict(variant=a.variant, port=PORT, events=[])
    t0 = time.time()
    while 'RV_OBSERVE_MONTH|0' not in text(srv / 'server.log') and time.time() - t0 < 600:
        time.sleep(2)
    res['server_ready_s'] = round(time.time() - t0)
    steps = ((cli, 'gui join'), (cli, 'gui rejoin')) if a.gui else ((cli, 'join'), (cli, 'rejoin'), (bad, 'client without balance GRFs'))
    for i, (home, label) in enumerate(steps):
        log = f'client{i}.log'
        video = ['-r', '1280x720'] if a.gui else ['-v', 'null:ticks=100000000']
        C = start(home, video + ['-n', f'127.0.0.1:{PORT}'], log)
        time.sleep(a.seconds)
        res.setdefault('client_full', []).append(dict(step=label, missed=text(home / log).count('Missed frame'), desync=[l for l in text(home / log).splitlines() if 'desync' in l.lower() or 'sync error' in l.lower()][:10], lost=[l for l in text(home / log).splitlines() if 'lost' in l.lower() or 'closed' in l.lower() or 'error' in l.lower()][:10]))
        C.kill(); C.wait()
        res['events'].append(dict(step=label, client_log_tail=text(home / log)[-1500:]))
        time.sleep(5)
    S.kill(); S.wait()
    log = text(srv / 'server.log')
    res['server_joins'] = len(re.findall(r'has joined|joined the game| joined as ', log, re.I))
    res['server_connect_lines'] = [l for l in log.splitlines() if '[server]' in l][:40]
    res['client_sync_missed'] = [e['step'] + ': ' + str(e['client_log_tail'].count('Missed frame')) for e in res['events']]
    res['server_desync_lines'] = [l for l in log.splitlines() if 'desync' in l.lower()][:20]
    res['server_grf_lines'] = [l for l in log.splitlines() if 'newgrf' in l.lower() and ('mismatch' in l.lower() or 'missing' in l.lower())][:20]
    res['server_net_lines'] = [l for l in log.splitlines() if '[net' in l][:80]
    res['server_observe_months'] = log.count('RV_OBSERVE_MONTH|')
    (P4.OUT / f"mptest_{a.variant}{'_gui' if a.gui else ''}.json").write_text(json.dumps(res, indent=2))
    rv.KEEP_RUN_DIRS = False
    for h in (srv, cli, bad):
        for f in ('server.log', 'client0.log', 'client1.log', 'client2.log'):
            if (h / f).exists():
                (P4.OUT / 'mp_logs').mkdir(exist_ok=True)
                lines = [l for l in text(h / f).splitlines() if '[net' in l or 'RV_' in l or 'desync' in l.lower() or 'error' in l.lower()]
                (P4.OUT / 'mp_logs' / f"{a.variant}{'_gui' if a.gui else ''}_{h.name}_{f}").write_text('\n'.join(lines[-400:]))
        rv.cleanup(h)
    print(json.dumps({k: res[k] for k in ('server_ready_s', 'server_joins', 'server_desync_lines', 'server_observe_months')}, indent=1))


if __name__ == '__main__':
    main()
