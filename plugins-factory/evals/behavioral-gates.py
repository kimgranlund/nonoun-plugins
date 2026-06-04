#!/usr/bin/env python3
"""behavioral-gates.py — does the harness catch a bad plugin?

Builds throwaway fixture plugins, each carrying ONE known structural defect, runs the bin/ gates
against them, and asserts the defect is caught — plus a golden CLEAN fixture that must pass every
gate. This is the integration counterpart to each gate's own `selftest`: a selftest proves one gate's
logic in isolation; this proves the **harness as a whole** catches the defect classes a real bad
plugin exhibits.

It is the deterministic half of the behavioral-eval suite in ROADMAP.md. The other half — calibrating
whether the critic *council* surfaces the right architecture findings — is non-deterministic (an LLM
panel) and is not a CI gate; it stays a documented manual eval.

Usage: behavioral-gates.py     (exit 0 = the clean fixture passes every gate AND every defect is caught)
Stdlib only (Python 3.8+).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

BIN = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin"))


def _w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _manifest(d, **over):
    m = {"name": "fixture", "version": "1.0.0", "description": "A fixture plugin."}
    m.update(over)
    _w(os.path.join(d, ".claude-plugin", "plugin.json"), json.dumps(m))


def _command(d, slug):
    _w(os.path.join(d, "commands", slug + ".md"), f"---\ndescription: do {slug}\n---\nbody\n")


def _skill(d, slug, body="body"):
    _w(os.path.join(d, "skills", slug, "SKILL.md"), f"---\nname: {slug}\ndescription: the {slug}\n---\n{body}\n")


def _changelog(d, version="1.0.0"):
    _w(os.path.join(d, "CHANGELOG.md"), f"# Changelog\n\n## {version} — 2026-01-01\n\n- initial\n")


# ---- fixture builders: each leaves a plugin dir with exactly one defect (or none, for clean) ----
def build_clean(d):
    _manifest(d); _command(d, "build"); _skill(d, "methodology"); _changelog(d)


def build_cross_plugin_dep(d):                       # P4 — illegal `../` dependency
    _manifest(d, skills="../shared/"); _changelog(d)


def build_command_skill_collision(d):                # P7 — one slug defined as both command + skill
    _manifest(d); _command(d, "review"); _skill(d, "review"); _changelog(d)


def build_agent_smuggles_mcp(d):                     # P9 — agent declares loader-forbidden field
    _manifest(d); _command(d, "build")
    _w(os.path.join(d, "agents", "actor.md"), "---\nname: actor\nmcpServers:\n  s: 1\n---\nbody\n")
    _changelog(d)


def build_version_drift(d):                          # P8 — version != latest CHANGELOG release
    _manifest(d, version="0.1.0"); _command(d, "build"); _changelog(d, version="0.2.0")


def build_count_drift(d):                            # P5 — description count claim != real count
    _manifest(d); _command(d, "build")               # one command on disk
    _w(os.path.join(d, "README.md"), "# fixture\n\nDriven by 3 typed commands.\n")  # claims three
    _changelog(d)


def build_dangling_ref(d):                           # P2/P8 — a reference that doesn't resolve
    _manifest(d); _command(d, "build")
    _skill(d, "methodology", body="See [the method](references/gone.md) for detail.")
    _changelog(d)


def _run(script, plugin_dir):
    argv = {"validate_plugin.py": ["plugin", plugin_dir, "--strict"]}.get(script, [plugin_dir])
    r = subprocess.run([sys.executable, os.path.join(BIN, script), *argv], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# (label, builder, gate, expected substring in the failure) — each defect must make its gate FAIL
DEFECTS = [
    ("cross-plugin-dep",        build_cross_plugin_dep,        "validate_plugin.py",     "escapes"),
    ("command-skill-collision", build_command_skill_collision, "validate_plugin.py",     "share the slug"),
    ("agent-smuggles-mcp",      build_agent_smuggles_mcp,      "validate_plugin.py",     "loader-forbidden"),
    ("version-changelog-drift", build_version_drift,           "check-manifest-sync.py", "latest CHANGELOG"),
    ("description-count-drift", build_count_drift,             "check-manifest-sync.py", "claims 3"),
    ("dangling-reference",      build_dangling_ref,            "reference-lint.py",      "does not resolve"),
]
ALL_GATES = ["validate_plugin.py", "reference-lint.py", "check-manifest-sync.py"]


def main():
    fails = []

    # 1) the golden CLEAN fixture must PASS every gate
    tmp = tempfile.mkdtemp(prefix="pf-eval-clean-")
    try:
        build_clean(tmp)
        for g in ALL_GATES:
            rc, out = _run(g, tmp)
            if rc != 0:
                fails.append(f"clean fixture: {g} should PASS but failed —\n    {out.strip()}")
            else:
                print(f"  clean -> {g}: PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2) each defective fixture must be CAUGHT by its gate (non-zero exit + the expected signal)
    for label, build, gate, substr in DEFECTS:
        tmp = tempfile.mkdtemp(prefix=f"pf-eval-{label}-")
        try:
            build(tmp)
            rc, out = _run(gate, tmp)
            if rc == 0:
                fails.append(f"{label}: {gate} should have FAILED, but passed")
            elif substr not in out:
                fails.append(f"{label}: {gate} failed without the expected signal '{substr}' —\n    {out.strip()}")
            else:
                print(f"  {label} -> {gate}: caught ('{substr}')")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        print("behavioral-gates: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print(f"behavioral-gates: PASS (clean fixture passes {len(ALL_GATES)} gates; {len(DEFECTS)} defect classes caught)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
