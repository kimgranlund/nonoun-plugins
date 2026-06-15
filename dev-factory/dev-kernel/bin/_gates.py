#!/usr/bin/env python3
"""_gates.py — shared machinery for dev-factory's protective PreToolUse gates (private lib).

The immutable/rewritable boundary (TDD §14.1) is realized by hooks that DENY a worker's write to
verifier assets — not by a sentence in a doc. Published reward-hacking rates run to double-digit
percentages of rollouts; the first and strongest defense is mechanical: signals, rubrics, the ledger,
the hooks, and the kernel schemas are deny-on-write to worker agents, so a worker cannot grade its own
homework or rewrite the audit trail. This module carries the protected-path matching, the PreToolUse
payload parsing, and the deny mechanism the four gate scripts (gate-signal / gate-verifier / gate-ledger
/ gate-naming) share.

These gates are NEVER bundled as a plugin PreToolUse hook (that would block a shared session — the
integration-contract law). They are CONSENT-WIRED into the user's autonomous worker loop / each worker
worktree by the server's wiring, where a non-zero exit denies the write.

Stdlib only; Python 3.8+.
"""
import fnmatch
import json
import os
import sys

NS = ".agents/dev-factory"

# The immutable side of the boundary (§14.1), path-segment-anchored. `signals/` is THE reward-hack
# defense; the ledger is append-only audit; the wiring (.claude/settings.json) is protected so a wired
# worker cannot unwire its own gate.
SIGNALS = [f"{NS}/signals/*"]
VERIFIER = [
    f"{NS}/signals/*",
    f"{NS}/rubric/*",
    f"{NS}/hooks/*",
    f"{NS}/run/*",
    f"{NS}/*/*/verify.mjs",     # a cell's per-cell critic harness ({layer}/{slug}/verify.mjs) — the gate a worker
    f"{NS}/lattice.json",       # authors code to PASS but must never write (else it grades its own homework)
    f"{NS}/*.schema.json",
    ".claude/settings.json",
]
LEDGER = [f"{NS}/ledger/*", f"{NS}/coordination/index.jsonl"]


def is_protected(path, globs):
    """True if `path` matches a protected glob at a path-segment boundary (root-relative or after any
    `/`) — never on a bare basename, so a user's own docs/lattice.json stays writable."""
    if not path:
        return False
    p = path.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    # normalize an absolute path that contains the namespace to its repo-relative tail
    for glob in globs:
        anchor = glob.split("/")[0]
        idx = p.find(anchor + "/") if anchor.endswith("*") is False else -1
        cand = p
        if (anchor + "/") in p:
            cand = p[p.index(anchor + "/"):]
        if fnmatch.fnmatch(cand, glob) or fnmatch.fnmatch(p, glob) or fnmatch.fnmatch(p, "*/" + glob):
            return True
    return False


def read_payload():
    """Parse a PreToolUse hook payload from stdin. Returns (tool_name, path, command). On an UNPARSEABLE
    payload returns (None, None, None) — `tool is None` is the parse-failure sentinel callers MUST treat as
    fail-CLOSED (deny): a malformed payload is the one case where the gate is blind to the write target, so
    it must never allow. (A successfully parsed payload always yields a string tool, possibly "".)"""
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None, None, None
    tool = data.get("tool_name") or data.get("tool") or ""
    ti = data.get("tool_input") or data.get("toolInput") or {}
    path = ti.get("file_path") or ti.get("path") or ti.get("notebook_path") or ""
    command = ti.get("command") or ""
    return tool, path, command


def deny(reason):
    """Emit the PreToolUse deny, maximally compatible across hook regimes: the structured JSON decision
    on stdout (the form current headless Claude reads — verified against the June-2026 docs) AND exit 2
    with the reason on stderr (the exit-code convention the catalog gates + selftests use). A worker's
    protected write is blocked under either runtime."""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "deny", "permissionDecisionReason": reason}}))
    sys.stderr.write(reason + "\n")
    return 2


# Bash verbs that MUTATE a file. The redirect heuristic is BEST-EFFORT defense-in-depth — robust shell
# analysis is undecidable, so the real floor is that the looping worker (cell-advancer) carries no Bash tool
# at all (frontmatter tool-scope). This list is deliberately the genuine file-MUTATING verbs only: it does
# NOT include interpreter flags like `-c`/`-e`, which over-match legitimate READS a Bash-carrying agent
# (cell-validator shelling a verifier) runs over protected paths — e.g. `python3 -c 'open("…/lattice.json").read()'`
# or `grep -e validated …/signals/…`. A false-deny on the validator's reads is worse than the residual
# inline-interpreter-write evasion, which the no-Bash tool-scope on the *forging* worker already closes.
_BASH_WRITE_VERBS = (">", "tee ", "rm ", "cp ", "mv ", "dd ", "sed -i", "install ", "truncate", "ln ")


def path_gate_verdict(tool, path, command, globs, what):
    """Pure verdict for a protected-path gate: returns (allow: bool, reason: str|None). Separated from
    stdin/emission so the selftest can prove the fail-closed + Bash-evasion behavior without a subprocess.
    Fails CLOSED on an unparseable payload (`tool is None`) — the gate must never allow a write it cannot
    inspect."""
    if tool is None:
        return False, "unparseable PreToolUse payload; failing closed (the gate cannot verify the write target, so it must not allow)"
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit") and is_protected(path, globs):
        return False, (f"{path} is a protected {what} (immutable boundary). "
                       f"Only the validation path / single-writer server may write it")
    if tool == "Bash" and command:
        for g in globs:
            base = g.replace("/*", "").replace("*", "")
            if base and base in command and any(v in command for v in _BASH_WRITE_VERBS):
                return False, f"shell command touches protected {what} ({base})"
    return True, None


def run_path_gate(name, globs, argv, what):
    """The standard --hook / check / selftest dispatch for a protected-path gate."""
    if argv and argv[0] == "selftest":
        return _selftest_path_gate(name, globs, what)
    if argv and argv[0] == "--hook":
        tool, path, command = read_payload()
        allow, reason = path_gate_verdict(tool, path, command, globs, what)
        return 0 if allow else deny(f"{name}: DENIED — {reason}.")
    if argv and argv[0] == "check":
        path = argv[1] if len(argv) > 1 else ""
        return 1 if is_protected(path, globs) else 0
    sys.stderr.write(f"usage: {name} --hook | check <path> | selftest\n")
    return 2


def _selftest_path_gate(name, globs, what):
    fails = []
    # a protected path is caught; a sibling user path is not
    protected_example = globs[0].replace("/*", "/x.json").replace("*.schema.json", "cell.schema.json")
    if not is_protected(protected_example, globs):
        fails.append(f"missed a protected {what}: {protected_example}")
    if is_protected("src/app/main.ts", globs):
        fails.append("false-positive on a user source path")
    if is_protected("docs/examples/lattice.json", globs) and "lattice.json" not in name:
        # docs/examples/lattice.json must NOT be protected (only the real .agents/.../lattice.json is)
        fails.append("false-positive on a user doc that merely shares a basename")
    # fail-CLOSED on a malformed payload (the gate is blind to the target → must deny, never allow)
    if path_gate_verdict(None, None, None, globs, what)[0]:
        fails.append("FAIL-OPEN on an unparseable payload (must fail closed)")
    # a well-formed non-write tool (Read) on a protected path is still allowed (no false-deny)
    if not path_gate_verdict("Read", protected_example, "", globs, what)[0]:
        fails.append("false-deny on a Read of a protected path")
    # a Bash evasion (cp/mv/sed -i) that mutates a protected path is caught (not just >/tee/rm)
    base0 = globs[0].replace("/*", "").replace("*", "")
    if base0 and path_gate_verdict("Bash", None, f"cp /tmp/forged {base0}x", globs, what)[0]:
        fails.append("Bash cp-evasion into a protected path was allowed")
    # but a legitimate READ of a protected path via an interpreter flag is NOT a write — must be allowed
    if base0 and not path_gate_verdict("Bash", None, f"python3 -c 'open(\"{base0}x\").read()'", globs, what)[0]:
        fails.append(f"false-deny on a Bash READ of a protected path ({base0}x)")
    if base0 and not path_gate_verdict("Bash", None, f"grep -e validated {base0}x", globs, what)[0]:
        fails.append("false-deny on a `grep -e` read of a protected path")
    if fails:
        sys.stderr.write(f"{name} selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print(f"{name} selftest: OK (denies a worker write to a protected {what}; leaves user paths writable)")
    return 0
