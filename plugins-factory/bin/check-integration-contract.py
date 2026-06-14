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


def check_plugin(plugin_dir, name=None):
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


def cmd_plugin(plugin_dir):
    findings, name = check_plugin(plugin_dir)
    rc = _report(name, findings)
    return 1 if rc else 0


def cmd_marketplace(root):
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
        findings, name = check_plugin(d, p.get("name"))
        total_fail += _report(name, findings)
    print("RESULT: {} (integration-contract over {} plugin(s){})".format(
        "PASS" if total_fail == 0 else "FAIL", n, "" if total_fail == 0 else " — {} violation(s)".format(total_fail)))
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

    if fails:
        sys.stderr.write("check-integration-contract selftest: FAIL\n")
        for f in fails:
            sys.stderr.write("  - {}\n".format(f))
        return 1
    print("check-integration-contract selftest: OK (router-thinness — a thin skill/bin-routing command passes, "
          "an inert command + a >4000-char fat command FAIL; advisory-hook — a PostToolUse hook passes, a bundled "
          "PreToolUse blocking hook FAILS; whole-plugin aggregates)")
    return 0


def main(argv):
    if len(argv) == 1 and argv[0] == "selftest":
        return cmd_selftest()
    if len(argv) == 2 and argv[0] == "plugin":
        return cmd_plugin(argv[1])
    if len(argv) == 2 and argv[0] == "marketplace":
        return cmd_marketplace(argv[1])
    print("usage: check-integration-contract.py {plugin <dir> | marketplace <dir> | selftest}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
