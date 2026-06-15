#!/usr/bin/env python3
"""_common.py — shared paths, imports, and helpers for the dev-factory /debug/ ralph-loop harness.

The harness stands up a fresh project from a one-paragraph brief, runs the cold-start (brief -> spec ->
hydrated lattice -> build tickets), then runs the bounded autonomous build loop and a verdict check — the
end-to-end exercise of the Software Dark Factory. This module is the common spine the four bin/ scripts share.

Layout (REPO = the claude-plugins working tree):
  REPO/debug/runs/<name>/                     a fresh scaffolded project (gitignored)
  REPO/debug/runs/<name>/.agents/dev-factory/ the instance (DEV_FACTORY_DIR)
The instance lives TWO levels under the project so dispatch.project_root = grandparent(DEV_FACTORY_DIR)
resolves to the project — exactly where worktrees + built assets land (verified against dispatch.py).

Stdlib only; Python 3.8+. The dev-server/dev-kernel are imported from the working tree (no install needed —
the harness uses LOCAL source).
"""
import json
import os
import subprocess
import sys
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # .../debug/bin/_ -> repo
DEVFACTORY = os.path.join(REPO, "dev-factory")
DEV_SERVER = os.path.join(DEVFACTORY, "dev-server")
KERNEL_BIN = os.path.join(DEVFACTORY, "dev-kernel", "bin")
KIT_CORPUS = os.path.join(DEVFACTORY, "dev-kit-corpus")
KIT_APP = os.path.join(DEVFACTORY, "dev-kit-app")
RUNS = os.path.join(REPO, "debug", "runs")
BRIEFS = os.path.join(REPO, "debug", "briefs")

# import the dev-server ops layer + the kernel from the working tree (LOCAL source, no plugin install)
sys.path.insert(0, DEV_SERVER)
sys.path.insert(0, KERNEL_BIN)


def _import_api():
    import api  # noqa: E402  — the single-writer ops layer (stdlib, tested)
    return api


def project_dir(name):
    return os.path.join(RUNS, name)


def instance_dir(name):
    return os.path.join(project_dir(name), ".agents", "dev-factory")


def read_json(p, default=None):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w", encoding="utf-8"), indent=2)
    os.replace(tmp, p)


def sh(cmd, cwd=None, check=True, capture=False):
    """Run a command. Returns the CompletedProcess. Raises on non-zero when check (and not capture)."""
    return subprocess.run(cmd, cwd=cwd, check=check and not capture,
                          capture_output=capture, text=True)


def http_get(url, timeout=5):
    """GET a JSON endpoint (stdlib urllib) — for polling a live dev-server's /api/status. None on failure."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def http_post(url, payload, timeout=5):
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                     headers={"content-type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def banner(msg):
    print(f"\n\033[1m▶ {msg}\033[0m" if sys.stdout.isatty() else f"\n▶ {msg}")


def bind_env(name):
    """Apply the scaffolded dev-factory.env (DEV_FACTORY_KIT, DEV_KERNEL_BIN, …) to os.environ for IN-PROCESS
    runs — the mock build + the planner read DEV_FACTORY_KIT from the environment exactly as run.sh does for a
    live server. setdefault, so a value already in the shell wins."""
    envf = os.path.join(project_dir(name), "dev-factory.env")
    if not os.path.isfile(envf):
        return
    for line in open(envf, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def brief_bank():
    """The idea-bank: every brief under debug/briefs/ (the thought-starters to pick between)."""
    return sorted(f for f in os.listdir(BRIEFS) if f.endswith(".md")) if os.path.isdir(BRIEFS) else []


def load_brief(brief_arg):
    """Resolve a brief: a file path, a bare name under debug/briefs/, or 'random' — pick one from the idea-bank
    (for the 'did the improvement hold?' runs, where a random project keeps us from overfitting to solitaire)."""
    if brief_arg == "random":
        import random
        bank = brief_bank()
        if not bank:
            raise SystemExit(f"no briefs in {BRIEFS}")
        brief_arg = random.choice(bank)
        print(f"» random brief from the idea-bank ({len(bank)} ideas): {brief_arg}")
    for cand in (brief_arg, os.path.join(BRIEFS, brief_arg),
                 os.path.join(BRIEFS, brief_arg + ".md")):
        if cand and os.path.isfile(cand):
            return cand, open(cand, encoding="utf-8").read()
    raise SystemExit(f"brief not found: {brief_arg} (looked in {BRIEFS}; the bank: {', '.join(brief_bank())})")
