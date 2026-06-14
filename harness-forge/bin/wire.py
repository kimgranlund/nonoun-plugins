#!/usr/bin/env python3
"""wire.py — the seed-into-loop installer: wire the blocking gates into the PROJECT'S OWN worker loop.

The plugin's session hook is advisory by design (a blocking gate in a shared interactive session is
hostile). The blocking enforcement belongs in the USER's autonomous worker loop — and that is a
*consent-gated install into the project's own `.claude/settings.json`*, never something a plugin does
silently. This script is that installer, and `check` is the mechanical H3 wiring test: a gate present in
`bin/` but wired nowhere is the false pass the rubric exists to catch.

What `apply` does (and `plan` previews, byte-for-byte):
  1. Copies the three hook species into `<project>/.agents/harness/hooks/` — `gate-signal` (PreToolUse deny on
     verifier assets), `emit-ledger` (PostToolUse audit trail), `propagate-staleness` (PostToolUse
     staleness cascade) — plus `_lattice.py`, a private byte-copy of the kernel the cascade imports.
     Inside `.agents/harness/hooks/` the gate protects ITSELF (the hooks are deny-on-write to workers).
  2. Merges the three hook entries into `<project>/.claude/settings.json` — non-destructively (unrelated
     keys, matchers, and hooks are preserved), idempotently (re-apply never duplicates), and refusing to
     touch a malformed settings file. `.claude/settings.json` is itself in the gate's protected set, so a
     worker cannot UNWIRE the gate it runs under.

Usage:
  wire.py plan    [--project DIR] [--harness-dir D]   # show exactly what apply would copy + merge; exit 0
  wire.py apply   [--project DIR] [--harness-dir D]   # do it (requires an existing harness dir — seed first)
  wire.py check   [--project DIR] [--harness-dir D]   # exit 0 = wired (entries + files present + no drift); 1 = not wired OR a copy has drifted from the plugin
  wire.py unwire  [--project DIR] [--harness-dir D]   # remove exactly our entries + copies; everything else preserved
  wire.py selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import shutil
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BIN)
try:
    import lattice as _lat                            # the installer runs from the plugin; lattice.py is a sibling
    KERNEL_VERSION = _lat.KERNEL_VERSION
except Exception:                                     # noqa: BLE001 — degrade rather than crash the installer
    KERNEL_VERSION = "unknown"
HOOK_FILES = ["gate-signal", "gate-budget", "emit-ledger", "propagate-staleness"]
LIB_COPY = ("lattice.py", "_lattice.py")              # kernel source → private copy name in .agents/harness/hooks/
VERSION_FILE = ".kernel-version"                      # stamped beside the copy so drift across a plugin update is detectable


def _cmd(hook, hd):
    rel = "{}/hooks/{}".format(hd.rstrip("/"), hook)
    env = "" if hd == ".agents/harness" else 'HARNESS_DIR="{}" '.format(hd.rstrip("/"))
    return '{}python3 "{}" --hook'.format(env, rel)


def _entries(hd):
    return {
        "PreToolUse": [_cmd("gate-signal", hd), _cmd("gate-budget", hd)],
        "PostToolUse": [_cmd("emit-ledger", hd), _cmd("propagate-staleness", hd)],
    }


MATCHER = "Write|Edit"


def _settings_path(project):
    return os.path.join(project, ".claude", "settings.json")


def _load_settings(project):
    """Returns (settings dict, error string|None). A missing file is an empty dict; malformed is an error."""
    p = _settings_path(project)
    if not os.path.isfile(p):
        return {}, None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f), None
    except ValueError as e:
        return None, "{} is not valid JSON ({}) — refusing to touch it".format(p, e)


def _merge(settings, hd):
    """Merge our entries in. Returns (settings, list of added command strings). Idempotency spans ALL groups that
    share our matcher (Simon/Scott): if the user already has two `Write|Edit` groups, a command present in *either*
    is not re-added — apply stays a no-op no matter which group a prior wiring landed in. New commands go to the
    first matching group (or a fresh one), never duplicated across groups."""
    added = []
    hooks = settings.setdefault("hooks", {})
    for event, cmds in _entries(hd).items():
        groups = hooks.setdefault(event, [])
        matching = [g for g in groups if g.get("matcher") == MATCHER]
        existing = {h.get("command") for g in matching for h in g.get("hooks", [])}   # across every matcher group
        if matching:
            target = matching[0]
        else:
            target = {"matcher": MATCHER, "hooks": []}
            groups.append(target)
        for cmd in cmds:
            if cmd not in existing:
                target.setdefault("hooks", []).append({"type": "command", "command": cmd})
                existing.add(cmd)
                added.append(cmd)
    return settings, added


def _unmerge(settings, hd):
    """Remove exactly our entries. Returns (settings, list of removed command strings)."""
    removed = []
    ours = {c for cmds in _entries(hd).values() for c in cmds}
    hooks = settings.get("hooks", {})
    for event in list(hooks):
        kept_groups = []
        for g in hooks[event]:
            kept = [h for h in g.get("hooks", []) if h.get("command") not in ours]
            removed.extend(h["command"] for h in g.get("hooks", []) if h.get("command") in ours)
            if kept or g.get("matcher") != MATCHER:
                g["hooks"] = kept
                kept_groups.append(g)
        if kept_groups:
            hooks[event] = kept_groups
        else:
            del hooks[event]
    if not hooks and "hooks" in settings:
        del settings["hooks"]
    return settings, removed


def _save_settings(project, settings):
    p = _settings_path(project)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def _copies(project, hd):
    """[(source path in the plugin, dest path in the project), ...]"""
    dest = os.path.join(project, hd, "hooks")
    pairs = [(os.path.join(_BIN, h), os.path.join(dest, h)) for h in HOOK_FILES]
    pairs.append((os.path.join(_BIN, LIB_COPY[0]), os.path.join(dest, LIB_COPY[1])))
    return pairs


def plan(project, hd):
    print("wire.py plan — what `apply` would do in {} (nothing has been changed):".format(os.path.abspath(project)))
    print("\n  copy into {}/hooks/ (the gate protects these once wired):".format(hd))
    for src, dst in _copies(project, hd):
        state = "refresh" if os.path.exists(dst) else "new"
        print("    {:8} {}  ←  {}".format(state, os.path.relpath(dst, project), src))
    settings, err = _load_settings(project)
    if err:
        print("\n  MERGE BLOCKED: {}".format(err))
        return 1
    merged, added = _merge(json.loads(json.dumps(settings)), hd)
    print("\n  merge into .claude/settings.json ({}):".format("new file" if not os.path.isfile(_settings_path(project)) else "existing — unrelated entries preserved"))
    for cmd in added or ["(already wired — apply would be a no-op)"]:
        print("    + {}".format(cmd))
    print("\n  consent note: apply edits the project's own settings; run it only with the user's explicit OK.")
    return 0


def apply(project, hd):
    if not os.path.isdir(os.path.join(project, hd)):
        print("wire.py: no {}/ in {} — seed the harness first (/harness-seed).".format(hd, project), file=sys.stderr)
        return 1
    settings, err = _load_settings(project)
    if err:
        print("wire.py: {}".format(err), file=sys.stderr)
        return 1
    print("wire.py apply → editing the project at {}".format(os.path.abspath(project)))   # echo the absolute target before mutating (Simon)
    dest = os.path.join(project, hd, "hooks")
    for src, dst in _copies(project, hd):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        os.chmod(dst, 0o755)
    with open(os.path.join(dest, VERSION_FILE), "w", encoding="utf-8") as f:   # stamp the wired kernel version
        f.write(KERNEL_VERSION + "\n")
    settings, added = _merge(settings, hd)
    _save_settings(project, settings)
    print("wired: {} hook file(s) in {}/hooks/ (kernel {}), {} new settings entr{} (re-apply is a no-op).".format(
        len(_copies(project, hd)), hd, KERNEL_VERSION, len(added), "y" if len(added) == 1 else "ies"))
    print("the worker loop now runs: PreToolUse gate-signal (deny verifier-asset writes) + gate-budget (deny writes to a blocked cell) + PostToolUse emit-ledger + propagate-staleness.")
    return 0


def check(project, hd, quiet=False):
    problems = []                                          # drift is a PROBLEM now (CV1), so the old `warns` list is gone
    settings, err = _load_settings(project)
    if err:
        problems.append(err)
        settings = {}
    wanted = {c for cmds in _entries(hd).values() for c in cmds}
    present = {h.get("command")
               for groups in (settings.get("hooks", {}) or {}).values()
               for g in groups for h in g.get("hooks", [])}
    for cmd in sorted(wanted - present):
        problems.append("settings entry missing: {}".format(cmd))
    for src, dst in _copies(project, hd):
        if not os.path.isfile(dst):
            problems.append("hook file missing: {}".format(os.path.relpath(dst, project)))
        elif os.path.isfile(src):
            try:
                if open(src, "rb").read() != open(dst, "rb").read():
                    # CV1 — drift is a PROBLEM (exit non-zero), not a WARN: a stale wired kernel runs old graph
                    # logic against signals the new engine mints. The H3 anchor must stop reading a drifted copy as healthy.
                    problems.append("wired copy is STALE vs the plugin: {} — re-run `wire.py apply` to refresh".format(os.path.relpath(dst, project)))
            except OSError:
                pass
    # the version stamp makes the drift human-meaningful (and catches a missing stamp from a pre-0.3.1 wiring)
    vpath = os.path.join(project, hd, "hooks", VERSION_FILE)
    wired_ver = None
    if os.path.isfile(vpath):
        try:
            wired_ver = open(vpath, encoding="utf-8").read().strip()
        except OSError:
            pass
    if any("STALE vs the plugin" in p for p in problems) and wired_ver and wired_ver != KERNEL_VERSION:
        problems.append("wired kernel is v{} but the installed plugin is v{} — `wire.py apply` to update".format(wired_ver, KERNEL_VERSION))
    if not quiet:
        if problems:
            print("NOT WIRED — {} problem(s):".format(len(problems)))
            for p in problems:
                print("  - {}".format(p))
        else:
            print("WIRED — the two blocking gates (gate-signal, gate-budget) + both feedback hooks are installed in this project's loop.")
    return 1 if problems else 0


def unwire(project, hd):
    settings, err = _load_settings(project)
    if err:
        print("wire.py: {}".format(err), file=sys.stderr)
        return 1
    settings, removed = _unmerge(settings, hd)
    _save_settings(project, settings)
    gone = 0
    for _, dst in _copies(project, hd):
        if os.path.isfile(dst):
            os.remove(dst)
            gone += 1
    vpath = os.path.join(project, hd, "hooks", VERSION_FILE)
    if os.path.isfile(vpath):
        os.remove(vpath)
    hooks_dir = os.path.join(project, hd, "hooks")
    if os.path.isdir(hooks_dir) and not os.listdir(hooks_dir):
        os.rmdir(hooks_dir)
    print("unwired: removed {} settings entr{} + {} copied file(s); unrelated hooks/settings preserved.".format(
        len(removed), "y" if len(removed) == 1 else "ies", gone))
    return 0


def selftest():
    import contextlib
    import io
    import subprocess
    import tempfile
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    _q = contextlib.redirect_stdout(io.StringIO())          # the lifecycle prints stay out of CI logs
    _qe = contextlib.redirect_stderr(io.StringIO())
    with tempfile.TemporaryDirectory() as project, _q, _qe:
        hd = ".agents/harness"
        # an unseeded project refuses apply; an unwired project fails check
        expect(apply(project, hd) == 1, "apply did not refuse an unseeded project")
        os.makedirs(os.path.join(project, hd))
        expect(check(project, hd, quiet=True) == 1, "an unwired project passed check (the false pass H3 exists to catch)")

        # a pre-existing unrelated hook + setting must survive the merge
        os.makedirs(os.path.join(project, ".claude"))
        pre = {"model": "opus", "hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo unrelated"}]}]}}
        json.dump(pre, open(_settings_path(project), "w"))

        expect(apply(project, hd) == 0, "apply failed on a seeded project")
        expect(check(project, hd, quiet=True) == 0, "a wired project failed check")
        s = json.load(open(_settings_path(project)))
        expect(s.get("model") == "opus", "unrelated top-level setting clobbered")
        flat = json.dumps(s)
        expect("echo unrelated" in flat, "unrelated hook entry clobbered")
        expect(flat.count("gate-signal") == 1, "gate entry missing or duplicated after apply")

        # idempotent: re-apply never duplicates
        expect(apply(project, hd) == 0, "re-apply failed")
        s2 = json.dumps(json.load(open(_settings_path(project))))
        expect(s2.count("gate-signal") == 1 and s2.count("emit-ledger") == 1, "re-apply duplicated entries")

        # duplicate-matcher idempotency (Simon/Scott): our command already living in a SECOND Write|Edit
        # group must not be re-added to the first. Hand-craft two PreToolUse Write|Edit groups, our gate in the 2nd.
        s_dup = json.load(open(_settings_path(project)))
        gate_cmd = _entries(hd)["PreToolUse"][0]
        s_dup["hooks"]["PreToolUse"] = [{"matcher": MATCHER, "hooks": []},
                                        {"matcher": MATCHER, "hooks": [{"type": "command", "command": gate_cmd}]}]
        json.dump(s_dup, open(_settings_path(project), "w"))
        expect(apply(project, hd) == 0, "apply failed against duplicate matcher groups")
        s3 = json.dumps(json.load(open(_settings_path(project))))
        expect(s3.count("gate-signal") == 1, "apply duplicated a command already present in a second matcher group")

        # the WIRED COPIES actually work from their installed location:
        gate = os.path.join(project, hd, "hooks", "gate-signal")
        r = subprocess.run([sys.executable, gate, "--hook"], input='{"tool_input":{"file_path":".agents/harness/signals/x/y.json"}}',
                           capture_output=True, text=True)
        expect(r.returncode == 2, "the wired gate did not DENY a protected write (exit {})".format(r.returncode))
        r = subprocess.run([sys.executable, gate, "--hook"], input='{"tool_input":{"file_path":"src/main.py"}}',
                           capture_output=True, text=True)
        expect(r.returncode == 0, "the wired gate blocked a benign write")
        r = subprocess.run([sys.executable, gate, "--hook"], input='{"tool_input":{"file_path":".claude/settings.json"}}',
                           capture_output=True, text=True)
        expect(r.returncode == 2, "the wired gate let a worker UNWIRE itself (settings write not denied)")
        # the copied cascade imports the PRIVATE kernel copy (no sibling lattice.py in .agents/harness/hooks/)
        prop = os.path.join(project, hd, "hooks", "propagate-staleness")
        r = subprocess.run([sys.executable, prop, "selftest"], capture_output=True, text=True, cwd=project)
        expect(r.returncode == 0, "the copied propagate-staleness failed from its wired location: {}".format(r.stderr[-200:]))

        # the WIRED gate-budget denies a write to a BLOCKED cell (the v0.4 stop-gate, from its installed location)
        gb = os.path.join(project, hd, "hooks", "gate-budget")
        expect(os.path.isfile(gb), "gate-budget was not copied by apply")
        _lat.scaffold(os.path.join(project, hd))                    # ensure a lattice exists in the wired project
        _lat.save(os.path.join(project, hd), {"cells": [{"layer": "spec", "scope": "task", "slug": "x",
                  "maturity": "defined", "blocked": True, "blocked_reason": "no-progress",
                  "asset_ref": ".agents/harness/spec/x.md"}]})
        r = subprocess.run([sys.executable, gb, "--hook"], input='{"tool_input":{"file_path":".agents/harness/spec/x.md"}}',
                           capture_output=True, text=True, cwd=project)
        expect(r.returncode == 2, "the wired gate-budget did not DENY a write to a blocked cell (exit {})".format(r.returncode))
        r = subprocess.run([sys.executable, gb, "--hook"], input='{"tool_input":{"file_path":".agents/harness/spec/other.md"}}',
                           capture_output=True, text=True, cwd=project)
        expect(r.returncode == 0, "the wired gate-budget blocked an unrelated write")

        # CV1 — DRIFT IS A HARD FAILURE, and re-apply heals it (the staleness-plugin's own staleness gate):
        lib = os.path.join(project, hd, "hooks", LIB_COPY[1])
        with open(lib, "a", encoding="utf-8") as f:
            f.write("\n# drift injected by selftest\n")          # the wired kernel now differs from the plugin's
        expect(check(project, hd, quiet=True) == 1, "check did not FAIL on a drifted wired kernel (CV1 regression)")
        expect(apply(project, hd) == 0 and check(project, hd, quiet=True) == 0, "re-apply did not heal the drift")
        expect(open(os.path.join(project, hd, "hooks", VERSION_FILE)).read().strip() == KERNEL_VERSION,
               "apply did not stamp the kernel version")

        # a malformed settings file is never touched
        open(_settings_path(project), "w").write("{not json")
        before = open(_settings_path(project)).read()
        expect(apply(project, hd) == 1, "apply did not refuse a malformed settings file")
        expect(open(_settings_path(project)).read() == before, "apply modified a malformed settings file")
        json.dump(pre, open(_settings_path(project), "w")); apply(project, hd)

        # unwire removes exactly ours
        expect(unwire(project, hd) == 0, "unwire failed")
        s3 = json.load(open(_settings_path(project)))
        flat3 = json.dumps(s3)
        expect("gate-signal" not in flat3 and "emit-ledger" not in flat3, "unwire left our entries")
        expect("echo unrelated" in flat3 and s3.get("model") == "opus", "unwire removed unrelated state")
        expect(not os.path.isfile(gate), "unwire left our copied files")
        expect(check(project, hd, quiet=True) == 1, "an unwired project passed check after unwire")
    if fails:
        sys.stderr.write("wire selftest: FAIL\n")
        for f in fails:
            sys.stderr.write("  - {}\n".format(f))
        return 1
    print("wire selftest: OK (unwired fails check / wired passes; merge preserves unrelated state; idempotent; "
          "refuses malformed settings; the installed gate-signal denies protected writes INCLUDING its own unwiring; "
          "the installed gate-budget denies a write to a blocked cell; the copied cascade runs on the private kernel "
          "copy; a drifted wired kernel FAILS check and re-apply heals it; unwire restores exactly)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if not argv or argv[0] not in ("plan", "apply", "check", "unwire"):
        print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
        return 2
    op = argv[0]
    project = argv[argv.index("--project") + 1] if "--project" in argv else "."
    hd = argv[argv.index("--harness-dir") + 1] if "--harness-dir" in argv else ".agents/harness"
    quiet = "--quiet" in argv
    if op == "plan":
        return plan(project, hd)
    if op == "apply":
        return apply(project, hd)
    if op == "check":
        return check(project, hd, quiet=quiet)
    return unwire(project, hd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
