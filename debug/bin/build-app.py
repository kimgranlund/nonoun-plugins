#!/usr/bin/env python3
"""build-app.py — ONE command: a brief becomes a built, SERVED, linkable app.

    python3 debug/bin/build-app.py <name> --brief <brief> [--live] [--dash-port 8731] [--app-port 8900]
    python3 debug/bin/build-app.py stop <name>            # stop the detached servers this started

Scaffolds the run, cold-starts (mock = free · --live = real `claude` workers), launches the dev-server (the
dashboard + the bounded autonomous build loop), waits for SHIP, serves the built app, and prints BOTH links plus
the token cost. The servers are DETACHED (they survive this command); stop them with `build-app.py stop <name>`.

Collapses the scaffold → cold-start → env → run.sh → serve-app dance into one step (operability, #122d). The build
itself is the proven dev-server path (headless adapter), so what it produces is exactly what the manual flow did.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

REPO = C.REPO
RUN_SH = os.path.join(REPO, "dev-factory", "dev-server", "run.sh")
SERVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serve-app.py")


def _pidfile(name):
    return os.path.join(C.project_dir(name), ".build-app.pids")


def _status(port):
    return json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=5))


def _set_env(name, adapter, port, caps):
    p = os.path.join(C.project_dir(name), "dev-factory.env")
    import re
    repl = {"DEV_FACTORY_ADAPTER": adapter, "PORT": str(port), **caps}
    lines, have = [], set()
    for ln in (open(p).read().splitlines() if os.path.isfile(p) else []):
        m = re.match(r"(\w+)=", ln)
        if m and m.group(1) in repl:
            lines.append(f"{m.group(1)}={repl[m.group(1)]}"); have.add(m.group(1))
        else:
            lines.append(ln)
    for k, v in repl.items():
        if k not in have:
            lines.append(f"{k}={v}")
    open(p, "w").write("\n".join(lines) + "\n")


def stop(name):
    pf = _pidfile(name)
    if not os.path.isfile(pf):
        print(f"no detached servers recorded for '{name}'"); return 0
    for line in open(pf):
        try:
            pid = int(line.split()[0])
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            print(f"  stopped pid {pid}")
        except (ProcessLookupError, ValueError, PermissionError):
            pass
    os.remove(pf)
    return 0


def build(name, brief, live, dash_port, app_port, ship_timeout):
    logs = os.path.join(C.project_dir(name), "logs")
    # 1. scaffold + 2. cold-start
    C.banner(f"build-app: {name}  (adapter={'headless (LIVE)' if live else 'mock (free)'})")
    print("» scaffold"); C.sh([sys.executable, os.path.join(os.path.dirname(SERVE), "scaffold.py"), name, "--brief", brief, "--force"])
    os.makedirs(logs, exist_ok=True)
    print("» cold-start (planner → milestone lattice + the knowledge foundation)")
    env = dict(os.environ, DEBUG_RALPH_LIVE="1") if live else dict(os.environ)
    cs = subprocess.run([sys.executable, os.path.join(os.path.dirname(SERVE), "coldstart.py"), name],
                        env=env, capture_output=True, text=True)
    open(os.path.join(logs, "coldstart.log"), "w").write(cs.stdout + cs.stderr)
    print("  " + next((l for l in cs.stdout.splitlines() if "decomposed" in l or "seeded" in l), "seeded"))
    # 3. env + 4. launch the dev-server (detached)
    caps = {"DEV_FACTORY_HEARTBEAT": "1", "DEV_FACTORY_MAX_DISPATCHES": "40", "DEV_FACTORY_DEADLINE_S": "2400",
            "DEV_FACTORY_CONCURRENCY": "2", "DEV_FACTORY_PERIOD": "10"}
    _set_env(name, "headless" if live else "mock", dash_port, caps)
    srv = subprocess.Popen(["bash", RUN_SH], cwd=C.project_dir(name), start_new_session=True,
                           stdout=open(os.path.join(logs, "server.log"), "w"), stderr=subprocess.STDOUT)
    open(_pidfile(name), "w").write(f"{srv.pid} dev-server :{dash_port}\n")
    print(f"» dev-server (dashboard) → http://127.0.0.1:{dash_port}/   building…")
    # 5. poll to SHIP
    t0, prev = time.time(), None
    shipped = False
    while time.time() - t0 < ship_timeout:
        try:
            st = _status(dash_port)
        except Exception:
            time.sleep(3); continue
        ms = st.get("milestones") or {}
        line = " · ".join(f"{x['label']} {x['done']}/{x['total']}" for x in ms.get("stages", []))
        if line != prev:
            print(f"  [{int(time.time()-t0):4d}s] {line}"); prev = line
        if ms.get("shipped"):
            shipped = True; break
        time.sleep(10)
    # 6. serve the built app (detached)
    if shipped:
        app = subprocess.Popen([sys.executable, SERVE, name, str(app_port)], start_new_session=True,
                               stdout=open(os.path.join(logs, "app-server.log"), "w"), stderr=subprocess.STDOUT)
        with open(_pidfile(name), "a") as f:
            f.write(f"{app.pid} app-server :{app_port}\n")
        time.sleep(1)
    # 7. report links + cost
    try:
        tok = _status(dash_port)
        cost = subprocess.run([sys.executable, "-c",
            "import sys;sys.path.insert(0,'%s');import api;d='%s';t=api.token_snapshot(d);print(f\"{t['total_tokens']} tok · ${t['total_cost_usd']:.2f}\")"
            % (os.path.join(REPO, "dev-factory", "dev-server"), C.instance_dir(name))], capture_output=True, text=True).stdout.strip()
    except Exception:
        cost = "n/a"
    print()
    C.banner("SHIPPED ✓" if shipped else "NOT SHIPPED (timed out / capped)")
    print(f"  dashboard : http://127.0.0.1:{dash_port}/")
    if shipped:
        print(f"  ▶ APP     : http://127.0.0.1:{app_port}/app/index.html")
    print(f"  token cost: {cost}")
    print(f"  stop with : python3 debug/bin/build-app.py stop {name}")
    return 0 if shipped else 1


def main(argv):
    if argv and argv[0] == "stop":
        return stop(argv[1]) if len(argv) > 1 else 2
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--brief", default="solitaire")
    ap.add_argument("--live", action="store_true", help="real claude workers (spends tokens); default mock (free)")
    ap.add_argument("--dash-port", type=int, default=8731)
    ap.add_argument("--app-port", type=int, default=8900)
    ap.add_argument("--ship-timeout", type=int, default=1800)
    a = ap.parse_args(argv)
    return build(a.name, a.brief, a.live, a.dash_port, a.app_port, a.ship_timeout)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
