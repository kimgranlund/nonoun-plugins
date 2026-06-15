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


def load_brief(brief_arg):
    """Resolve a brief path: an absolute/relative file, or a bare name under debug/briefs/."""
    for cand in (brief_arg, os.path.join(BRIEFS, brief_arg),
                 os.path.join(BRIEFS, brief_arg + ".md")):
        if cand and os.path.isfile(cand):
            return cand, open(cand, encoding="utf-8").read()
    raise SystemExit(f"brief not found: {brief_arg} (looked in {BRIEFS})")
