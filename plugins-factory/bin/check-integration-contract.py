#!/usr/bin/env python3
"""check-integration-contract.py — the catalog's plugin INTEGRATION CONTRACT, as a checked property.

Every nonoun-plugins plugin integrates with a host harness (Claude Code) through the five primitives. The
catalog's integration invariants have been held by *convention + author discipline*; this gate mechanizes
the two that no other gate covers, so "a hardened, reliable, token-efficient integration" is **verified**,
not merely disciplined (the gap audit: validate_plugin/context-cost/trust-boundary/mcp-liveness/manifest-sync
already cover layout, the token budget, the trust guard, MCP liveness, and description sync — this gate fills
the rest).

  H · ENTRY/ROUTER THINNESS — a command is a thin typed entry point that ROUTES to a skill/agent/bin/
      references, and never re-contains methodology (the five-primitive law). Mechanized as: the body
      (frontmatter stripped) must (R) route — reference a real skill/agent on disk, a `${CLAUDE_PLUGIN_ROOT}/
      bin/` script, or a `references/` doc — AND (S) stay under the size budget (FAIL ≥ 4000 chars, WARN ≥
      2800). Calibrated on the real catalog: 37 commands, max body 3269; the skills they point at are ≥6993,
      so a re-contained method lands in skill territory and fails. Reinforces context-cost.py's token budget
      at the structural/routing level.

  I · ADVISORY BUNDLED HOOK (structural) — a plugin's OWN hooks.json hook must be advisory: it can never
      DENY a tool call. Only a PreToolUse hook can deny a call, so a bundled PreToolUse entry is the
      structural form of "bundled blocking" and FAILS here. (Blocking integration is legal ONLY by
      consent-wiring into the user's project — harness-forge's wire.py — never bundled.) The behavioral
      form — execute each --hook and assert exit 0 + no block decision under finding-triggering input — is
      the next increment (it executes plugin code, so it rides the check-mcp-liveness --trusted-source
      interlock). All five bundled hooks are PostToolUse-only today; this freezes that.

Modes:
  check-integration-contract.py plugin <dir>          # one plugin
  check-integration-contract.py marketplace <dir>     # every plugin in <dir>/.claude-plugin/marketplace.json
  check-integration-contract.py selftest              # prove the gate bites

Exit 0 = pass (WARNs allowed) · 1 = a contract violation · 2 = usage. Stdlib only; Python 3.8+. Clean-checkout-true.
"""
import json
import os
import re
import sys

# H — router thinness
ROUTER_SIZE_FAIL = 4000        # body chars; real catalog max is 3269, the skills they point at are >=6993
ROUTER_SIZE_WARN = 2800        # just above p90 (2711) — the four legitimately-heavy commands land here
_BIN_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/bin/|(?<![\w./-])bin/[\w./-]+")
_REFS_RE = re.compile(r"(?:skills/[a-z0-9-]+/)?references/\S+")
_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)

# I — advisory hook (structural): only PreToolUse can DENY a tool call, so a bundled PreToolUse is blocking.
DENYING_EVENTS = {"PreToolUse"}

# I — advisory hook (BEHAVIORAL): execute each --hook on finding-triggering input; it must exit 0 AND emit no
# block/deny decision. Executes plugin code, so it rides the I-12 exec interlock (the check-mcp-liveness pattern).
TRUST_FLAG = "--trusted-source"
TRUST_ENV = "PLUGINS_FACTORY_TRUST_EXEC"
_BLOCK_RE = re.compile(r'"(?:decision|permissionDecision)"\s*:\s*"(?:block|deny)"|"continue"\s*:\s*false')
# per-plugin worst-case fixture: (filename, content, file_path_override). Each hook reads differently — content,
# disk, or just the path string — so one payload can't trigger a finding in all; an unknown plugin gets the generic.
_GENERIC_FIX = ("contract-probe.md", "We embody the hero archetype; our mission statement is to grow revenue 30%.", None)
_HOOK_FIXTURES = {
    "brand-forge":     ("brand.md", "We embody the hero archetype. Our mission statement: win the category.", None),
    "product-forge":   ("prd.md", "Our product strategy is to grow revenue 30%. Make it hard to cancel.", None),
    "plugins-factory": ("plugin.json", '{"name":"x","version":"not-semver"}', None),
    "agent-ops":       ("CLAUDE.md", "# proj\n" + "\n".join("- detail line {}".format(i) for i in range(40)), None),
    "harness-forge":   (None, None, ".agents/harness/specs/first-slice.md"),   # path-shape only (plural layer dir advisory)
}


def _trust_ok(argv):
    return TRUST_FLAG in argv or os.environ.get(TRUST_ENV, "") not in ("", "0", "false", "False")


def _strip_frontmatter(text):
    return _FRONTMATTER_RE.sub("", text, count=1)


def _plugin_skills_agents(plugin_dir):
    skills = set()
    sk = os.path.join(plugin_dir, "skills")
    if os.path.isdir(sk):
        skills = {d for d in os.listdir(sk) if os.path.isdir(os.path.join(sk, d))}
    agents = set()
    ag = os.path.join(plugin_dir, "agents")
    if os.path.isdir(ag):
        agents = {os.path.splitext(f)[0] for f in os.listdir(ag) if f.endswith(".md")}
    return skills, agents


def _command_routes(body, skills, agents):
    """A command ROUTES if it references a real skill/agent on disk, a bin/ script, or a references/ doc —
    the three legitimate hand-off targets the real catalog uses (calibrated: all 37 commands route via one)."""
    if _BIN_RE.search(body) or _REFS_RE.search(body):
        return True
    for name in (skills | agents):
        if name and re.search(r"`" + re.escape(name) + r"`|(?<![\w-])" + re.escape(name) + r"(?![\w-])", body):
            return True
    return False


def check_command(path, skills, agents):
    """Return a list of (severity, message) for one command file. severity in {FAIL, WARN}."""
    out = []
    try:
        raw = open(path, encoding="utf-8").read()
    except OSError as e:
        return [("FAIL", "cannot read {}: {}".format(path, e))]
    body = _strip_frontmatter(raw).strip()
    n = len(body)
    rel = os.path.basename(path)
    if not _command_routes(body, skills, agents):
        out.append(("FAIL", "{}: routes to nothing — a command must hand off to a skill/agent, a "
                            "${{CLAUDE_PLUGIN_ROOT}}/bin/ script, or a references/ doc (it is inert, or "
                            "re-containing what a skill should hold)".format(rel)))
    if n >= ROUTER_SIZE_FAIL:
        out.append(("FAIL", "{}: body is {} chars (>= {}) — a command is a thin entry point; this is "
                            "skill-sized, the methodology belongs in a lazily-loaded skill".format(rel, n, ROUTER_SIZE_FAIL)))
    elif n >= ROUTER_SIZE_WARN:
        out.append(("WARN", "{}: body is {} chars (>= {}) — heavy for a router; confirm it points at a "
                            "skill rather than restating one".format(rel, n, ROUTER_SIZE_WARN)))
    return out


def check_hooks_static(plugin_dir):
    """Return a list of (severity, message): a BUNDLED hook must be advisory — never a PreToolUse (deny) entry."""
    out = []
    hp = os.path.join(plugin_dir, "hooks", "hooks.json")
    if not os.path.isfile(hp):
        return out
    try:
        h = json.load(open(hp, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [("FAIL", "hooks/hooks.json does not parse: {}".format(e))]
    hooks = h.get("hooks", h) if isinstance(h, dict) else {}
    advisory_token_seen = False
    for event, groups in (hooks.items() if isinstance(hooks, dict) else []):
        if event in DENYING_EVENTS:
            out.append(("FAIL", "hooks.json bundles a {} hook — only a {} hook can DENY a tool call, so a "
                                "bundled one is blocking integration; a plugin's own hook must be advisory "
                                "(blocking is legal only by consent-wiring into the user's project, never "
                                "bundled)".format(event, event)))
        for g in (groups if isinstance(groups, list) else [groups]):
            for hk in (g.get("hooks", []) if isinstance(g, dict) else []):
                cmd = hk.get("command", "") if isinstance(hk, dict) else ""
                if "--hook" in cmd or re.search(r"\bhook\b", cmd):
                    advisory_token_seen = True
    if hooks and not advisory_token_seen:
        out.append(("WARN", "hooks.json command(s) carry no advisory `--hook`/`hook` entry-point token — "
                            "confirm the bundled hook runs in advisory mode"))
    return out


def _commands_from_hooks(plugin_dir):
    hp = os.path.join(plugin_dir, "hooks", "hooks.json")
    cmds = []
    if os.path.isfile(hp):
        try:
            h = json.load(open(hp, encoding="utf-8"))
            for groups in ((h.get("hooks", h) or {}).values() if isinstance(h, dict) else []):
                for g in (groups if isinstance(groups, list) else [groups]):
                    for hk in (g.get("hooks", []) if isinstance(g, dict) else []):
                        if isinstance(hk, dict) and hk.get("command"):
                            cmds.append(hk["command"])
        except (OSError, json.JSONDecodeError):
            pass
    return cmds


def check_hook_behavioral(plugin_dir, name):
    """I (behavioral) — run each bundled --hook on worst-case (finding-triggering) input; it must exit 0 AND
    emit NO block/deny decision. Catches the exit-0-but-emits-a-block-decision escape the static pass can't.
    EXECUTES plugin code — callers gate this on the I-12 --trusted-source interlock."""
    import subprocess
    import tempfile
    out = []
    cmds = _commands_from_hooks(plugin_dir)
    if not cmds:
        return out
    root = os.path.abspath(plugin_dir)
    fname, content, fp_override = _HOOK_FIXTURES.get(name, _GENERIC_FIX)
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=root)
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, fname) if fname else fp_override
        if fname:
            open(fp, "w", encoding="utf-8").write(content or "")
        payload = json.dumps({"session_id": "contract-gate", "hook_event_name": "PostToolUse", "tool_name": "Write",
                              "tool_input": {"file_path": fp, "content": content or ""}, "tool_response": {"success": True}})
        for cmd in cmds:
            real = cmd.replace("${CLAUDE_PLUGIN_ROOT}", root)
            try:
                r = subprocess.run(real, shell=True, input=payload, capture_output=True, text=True, timeout=25, env=env)
            except (subprocess.SubprocessError, OSError) as e:
                out.append(("FAIL", "bundled hook did not run ({}): {}".format(cmd[:50], e)))
                continue
            if r.returncode != 0:
                out.append(("FAIL", "bundled hook exited {} on finding-triggering input — a non-zero PostToolUse is "
                                    "blocking feedback; a bundled hook must be advisory ({})".format(r.returncode, cmd[:50])))
            if _BLOCK_RE.search(r.stdout or ""):
                out.append(("FAIL", "bundled hook emitted a BLOCK/DENY decision — advisory hooks warn, never block "
                                    "(the exit-0-but-blocks escape) ({})".format(cmd[:50])))
            if not ((r.stdout or "") + (r.stderr or "")).strip():
                out.append(("WARN", "hook produced no output on its worst-case fixture — exit-0 verified, but not "
                                    "under a finding (the fixture may have drifted from the hook's smells) ({})".format(cmd[:50])))
    return out


def check_plugin(plugin_dir, name=None, behavioral=False):
    """Return (findings, name). findings: list of (severity, message)."""
    name = name or os.path.basename(os.path.abspath(plugin_dir))
    findings = []
    skills, agents = _plugin_skills_agents(plugin_dir)
    cmd_dir = os.path.join(plugin_dir, "commands")
    if os.path.isdir(cmd_dir):
        for f in sorted(os.listdir(cmd_dir)):
            if f.endswith(".md"):
                findings += check_command(os.path.join(cmd_dir, f), skills, agents)
    findings += check_hooks_static(plugin_dir)
    if behavioral:
        findings += check_hook_behavioral(plugin_dir, name)
    return findings, name


def _report(name, findings):
    fails = [m for s, m in findings if s == "FAIL"]
    warns = [m for s, m in findings if s == "WARN"]
    for m in fails:
        print("  FAIL  {}".format(m))
    for m in warns:
        print("  warn  {}".format(m))
    print("  {} — {} fail, {} warn".format(name, len(fails), len(warns)))
    return len(fails)


def cmd_plugin(plugin_dir, behavioral=False):
    findings, name = check_plugin(plugin_dir, behavioral=behavioral)
    rc = _report(name, findings)
    return 1 if rc else 0


def cmd_marketplace(root, behavioral=False):
    mp = os.path.join(root, ".claude-plugin", "marketplace.json")
    try:
        plugins = json.load(open(mp, encoding="utf-8")).get("plugins", [])
    except (OSError, json.JSONDecodeError) as e:
        print("RESULT: cannot read {}: {}".format(mp, e), file=sys.stderr)
        return 2
    total_fail, n = 0, 0
    for p in plugins:
        src = p.get("source", "")
        d = os.path.normpath(os.path.join(root, src)) if src.startswith(".") else os.path.join(root, p.get("name", ""))
        if not os.path.isdir(d):
            continue
        n += 1
        findings, name = check_plugin(d, p.get("name"), behavioral=behavioral)
        total_fail += _report(name, findings)
    note = " + behavioral hook exec" if behavioral else " (static; pass --trusted-source for the behavioral hook check)"
    print("RESULT: {} (integration-contract over {} plugin(s){}{})".format(
        "PASS" if total_fail == 0 else "FAIL", n, note, "" if total_fail == 0 else " — {} violation(s)".format(total_fail)))
    return 1 if total_fail else 0


def cmd_selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as tmp:
        # a plugin fixture: a skill + an agent on disk, a thin routing command, and an advisory hook.
        os.makedirs(os.path.join(tmp, "skills", "my-method"))
        os.makedirs(os.path.join(tmp, "agents"))
        open(os.path.join(tmp, "agents", "my-council.md"), "w").write("---\nname: my-council\n---\nx")
        os.makedirs(os.path.join(tmp, "commands"))
        os.makedirs(os.path.join(tmp, "hooks"))

        def cmd(fn, text):
            open(os.path.join(tmp, "commands", fn), "w").write(text)

        cmd("thin.md", "---\ndescription: x\n---\nInvoke the `my-method` skill to do the thing.")      # routes (skill) + small → PASS
        cmd("thin-bin.md", "---\nd: x\n---\nRun `python3 \"${CLAUDE_PLUGIN_ROOT}/bin/x.py\" go`.")      # routes (bin) → PASS
        cmd("inert.md", "---\nd: x\n---\nJust some prose that hands off to nothing at all, no target.")  # routes to nothing → FAIL
        cmd("fat.md", "---\nd: x\n---\nInvoke the `my-method` skill.\n" + ("methodology prose. " * 300))  # routes but >4000 → FAIL

        skills, agents = _plugin_skills_agents(tmp)
        expect(check_command(os.path.join(tmp, "commands", "thin.md"), skills, agents) == [],
               "a thin routing command was flagged")
        expect(check_command(os.path.join(tmp, "commands", "thin-bin.md"), skills, agents) == [],
               "a bin-routing command was flagged")
        inert = check_command(os.path.join(tmp, "commands", "inert.md"), skills, agents)
        expect(any(s == "FAIL" and "routes to nothing" in m for s, m in inert), "an inert command was not failed")
        fat = check_command(os.path.join(tmp, "commands", "fat.md"), skills, agents)
        expect(any(s == "FAIL" and "skill-sized" in m for s, m in fat), "a fat (>4000) command was not failed")

        # I — advisory hook: PostToolUse passes, a bundled PreToolUse fails.
        open(os.path.join(tmp, "hooks", "hooks.json"), "w").write(json.dumps(
            {"hooks": {"PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "bin/lint --hook"}]}]}}))
        expect(not any(s == "FAIL" for s, m in check_hooks_static(tmp)), "an advisory PostToolUse hook was failed")
        open(os.path.join(tmp, "hooks", "hooks.json"), "w").write(json.dumps(
            {"hooks": {"PreToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": "bin/gate --hook"}]}]}}))
        pre = check_hooks_static(tmp)
        expect(any(s == "FAIL" and "PreToolUse" in m for s, m in pre), "a bundled PreToolUse (blocking) hook was not failed")

        # whole-plugin: with the PostToolUse hook restored, the fixture has 2 FAILs (inert + fat), 0 from hooks.
        open(os.path.join(tmp, "hooks", "hooks.json"), "w").write(json.dumps(
            {"hooks": {"PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "bin/lint --hook"}]}]}}))
        findings, _ = check_plugin(tmp)
        expect(sum(1 for s, m in findings if s == "FAIL") == 2, "whole-plugin FAIL count wrong: {}".format(findings))

    # I (behavioral) — a hook that exits 0 + advises PASSES; one that exits 0 but emits a block decision, or
    # exits non-zero, FAILS. Self-authored fixtures (the selftest runs its OWN code → no --trusted-source needed).
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "bin"))
        os.makedirs(os.path.join(tmp, "hooks"))

        def hook_plugin(body):
            open(os.path.join(tmp, "bin", "hook.py"), "w").write("import sys, json\n" + body)
            open(os.path.join(tmp, "hooks", "hooks.json"), "w").write(json.dumps(
                {"hooks": {"PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command",
                 "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/bin/hook.py" --hook'}]}]}}))

        hook_plugin("sys.stdin.read(); print('advice: consider X'); sys.exit(0)")               # advisory → PASS
        expect(not any(s == "FAIL" for s, m in check_hook_behavioral(tmp, "x")), "an advisory hook (exit 0, advises) was failed")
        hook_plugin("sys.stdin.read(); print(json.dumps({'decision': 'block'})); sys.exit(0)")  # exit 0 BUT blocks → FAIL
        expect(any(s == "FAIL" and "BLOCK/DENY" in m for s, m in check_hook_behavioral(tmp, "x")), "an exit-0-but-blocks hook was not failed")
        hook_plugin("sys.stdin.read(); sys.exit(2)")                                            # non-zero → FAIL
        expect(any(s == "FAIL" and "exited 2" in m for s, m in check_hook_behavioral(tmp, "x")), "a non-zero-exit hook was not failed")
    expect(_trust_ok([TRUST_FLAG]), "interlock: --trusted-source did not authorize the behavioral check")
    expect(not _trust_ok([]), "interlock: the behavioral check ran without trust")

    if fails:
        sys.stderr.write("check-integration-contract selftest: FAIL\n")
        for f in fails:
            sys.stderr.write("  - {}\n".format(f))
        return 1
    print("check-integration-contract selftest: OK (router-thinness — a thin skill/bin-routing command passes, an "
          "inert command + a >4000-char fat command FAIL; advisory-hook static — a PostToolUse hook passes, a bundled "
          "PreToolUse FAILS; advisory-hook behavioral — an exit-0 advising hook passes, an exit-0-but-emits-block hook "
          "+ a non-zero-exit hook FAIL, gated by the I-12 trust interlock; whole-plugin aggregates)")
    return 0


def main(argv):
    behavioral = _trust_ok(argv)                          # I-12: the exec (behavioral) hook check is opt-in; static stays open
    args = [a for a in argv if a != TRUST_FLAG]
    if len(args) == 1 and args[0] == "selftest":
        return cmd_selftest()
    if len(args) == 2 and args[0] == "plugin":
        return cmd_plugin(args[1], behavioral)
    if len(args) == 2 and args[0] == "marketplace":
        return cmd_marketplace(args[1], behavioral)
    print("usage: check-integration-contract.py {plugin <dir> | marketplace <dir> | selftest} [--trusted-source]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
