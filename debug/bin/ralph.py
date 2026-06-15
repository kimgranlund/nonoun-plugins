#!/usr/bin/env python3
"""ralph.py — the BOUNDED outer loop: scaffold -> cold-start -> build -> verdict, on a brief.

    python3 debug/bin/ralph.py <name> [--brief solitaire] [--mock] [--max-iters 40] [--deadline-s 3600] [--fresh]

The "ralph loop": drive the whole Software Dark Factory from a one-paragraph brief to a built app, repeatedly,
until a verdict passes or a hard outer cap is hit. The loop is ALWAYS bounded — it wraps the factory's own armed
run budget with its own ceiling (max-iters / wall-clock), so it can never run away.

Two modes:
  --mock  (default unless DEBUG_RALPH_LIVE=1) : deterministic, no model, no server. Drives the MockAdapter over
          ready tickets until the lattice is built — the CI plumbing proof of the whole arc.
  live    (DEBUG_RALPH_LIVE=1)                : boots the dev-server in Walk via run.sh, lets the heartbeat
          dispatch REAL `claude` workers, monitors /api/status, injects steering guidance on a stall, and stops
          on the verdict or the caps. THIS SPENDS REAL TOKENS and dispatches live workers — opt-in by design.

Stdlib only; Python 3.8+.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C   # noqa: E402
import scaffold as _scaffold   # noqa: E402
import coldstart as _coldstart  # noqa: E402
import verdict as _verdict     # noqa: E402

POLL_S = 5            # the monitor cadence (the server also reads operator input every 5s, independently)
SRV = {"kind": "server", "id": "dev-server"}


def _ensure_seeded(name, brief, mock, api):
    inst = C.instance_dir(name)
    if not os.path.isdir(inst):
        _scaffold.scaffold(name, brief)
    # cold-start if there are no build cells yet (spec/capability)
    grid = api.lattice_grid(inst)
    if not any(c["layer"] in ("spec", "capability") for c in grid):
        _coldstart.coldstart(name, mock=mock)


def _mock_build(name, api, max_iters):
    """Drive the MockAdapter over ready active tickets until the lattice is built or the cap is hit."""
    from dispatch import MockAdapter, dispatch_unit
    inst, proj = C.instance_dir(name), C.project_dir(name)
    C.banner(f"build (mock) — driving the MockAdapter, cap {max_iters} iterations")
    it = 0
    while it < max_iters:
        grid = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
        ready = []
        for t in api.list_tickets(inst, state="active"):
            full = api.get_ticket(inst, t["id"])
            if full.get("claim"):
                continue
            deps = (full.get("dependencies") or {}).get("cells_ready") or []
            if all(grid.get(c) == "validated" for c in deps):
                ready.append(full)
        if not ready:
            break
        it += 1
        for t in ready:
            ok, _tk, msg = dispatch_unit(inst, t, MockAdapter(), SRV, tier=2, repo_root=proj)
            print(f"    [{it}] {t.get('target_cell')}: {'validated' if ok else 'FAILED — ' + msg}")
    return it


def _live_build(name, api, max_iters, deadline_s):
    """Boot the dev-server (Walk) via run.sh, monitor, steer on stall, stop on verdict or caps. Real workers."""
    inst, proj = C.instance_dir(name), C.project_dir(name)
    base = "http://127.0.0.1:8731"
    C.banner(f"build (LIVE) — booting the dev-server (Walk); caps: {max_iters} iters / {deadline_s}s wall-clock")
    print("  ⚠ this dispatches REAL headless `claude` workers — they cost tokens + write the worktree.")
    proc = subprocess.Popen([os.path.join(C.DEV_SERVER, "run.sh")], cwd=proj, env=os.environ.copy())
    start, it, last_done, stalls = time.time(), 0, -1, 0
    try:
        while it < max_iters and (time.time() - start) < deadline_s:
            time.sleep(POLL_S)
            it += 1
            st = C.http_get(base + "/api/status") or {}
            fac = st.get("factory", {})
            done = (st.get("tickets", {}) or {}).get("done", 0)
            print(f"  [{it}] state={fac.get('state','?')} running={fac.get('running_agents',0)} "
                  f"ready={fac.get('ready_to_dispatch',0)} done={done}")
            v = _verdict.verdict(name, quiet=True)
            if v["ok"]:
                C.banner("verdict PASSED — the factory built the app")
                return it
            # stall detection: no new done ticket across a few polls -> inject steering guidance
            if done == last_done:
                stalls += 1
                if stalls in (3, 6):
                    C.http_post(base + "/api/input",
                                {"text": "the build appears stalled — re-rank the frontier and unblock the "
                                         "smallest dep-ready cell; prefer finishing a started cell over starting a new one"})
                    print("    · injected steering guidance (stall)")
            else:
                stalls = 0
            last_done = done
        print("  outer cap reached — stopping the loop (bounded by construction)")
        return it
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def ralph(name, brief="solitaire", mock=None, max_iters=40, deadline_s=3600, fresh=False):
    api = C._import_api()
    if fresh:
        _scaffold.scaffold(name, brief, force=True)
    # default to mock unless the operator explicitly opted into a live run
    live = (mock is False) or (mock is None and os.environ.get("DEBUG_RALPH_LIVE") == "1")
    if not live and mock is None:
        mock = True
    if live and os.environ.get("DEBUG_RALPH_LIVE") != "1":
        raise SystemExit("a LIVE ralph run dispatches real `claude` workers (tokens). Set DEBUG_RALPH_LIVE=1 to confirm.")

    C.banner(f"RALPH — brief '{brief}' -> project '{name}'  [{'LIVE' if live else 'mock'}]")
    _ensure_seeded(name, brief, mock=not live, api=api)
    iters = _live_build(name, api, max_iters, deadline_s) if live else _mock_build(name, api, max_iters)

    v = _verdict.verdict(name)
    C.banner(f"RALPH done after {iters} iteration(s) — verdict: {'PASS ✓' if v['ok'] else 'FAIL ✗'}")
    return 0 if v["ok"] else 1


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    name = argv[0]
    brief = argv[argv.index("--brief") + 1] if "--brief" in argv else "solitaire"
    mock = True if "--mock" in argv else (False if "--live" in argv else None)
    max_iters = int(argv[argv.index("--max-iters") + 1]) if "--max-iters" in argv else 40
    deadline_s = int(argv[argv.index("--deadline-s") + 1]) if "--deadline-s" in argv else 3600
    fresh = "--fresh" in argv
    return ralph(name, brief, mock=mock, max_iters=max_iters, deadline_s=deadline_s, fresh=fresh)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
