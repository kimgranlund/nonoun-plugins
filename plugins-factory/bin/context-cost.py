#!/usr/bin/env python3
"""context-cost.py — measure a plugin's ALWAYS-ON context cost (the P6 Context-Economy audit).

The holistic rubric's P6 (`references/rubrics/plugins-holistic.md`) names this script directly:
"Test (always-on audit): read `claude plugin details` (or `context-cost.py` when available). Is
always-on cost dominated by anything other than terse skill/command descriptions?" A plugin charges
standing context to EVERY session just by being enabled — but only its *advertisements* load eagerly:
each agent / command / skill is announced by its frontmatter `description` (+ a command's
`argument-hint`). The bodies — SKILL.md prose, references, agent/command instructions — load on
invocation (progressive disclosure), so they are NOT always-on and are excluded here.

P6 is a `[review]` `[hypothesis]` dimension, not a `[gate]`: whether a cost is *justified* is a
judgment the council makes, not a regex. So this tool's job is to make the cost VISIBLE (the rubric's
prerequisite) and to flag the two mechanical smells the rubric calls out — a single description that
DOMINATES, and a description so long it is a body smuggled into an advertisement. It hard-fails only on
the unarguable cases (a >2KB description, or an explicit `--budget` breach); everything else is a
reported WARN, never a CI failure on a legitimately rich description.

What it reports per plugin: total always-on chars + an estimated token count (chars/4), a per-category
breakdown (agent / command / skill), the heaviest components with their share of the total, and whether
an MCP server is wired (its live tool-definition cost is real but not statically countable here — see
`check-mcp-liveness.py` for the served tool count).

Usage:
  context-cost.py plugin <dir>        [--warn-desc N] [--max-desc N] [--budget N]
  context-cost.py marketplace <dir>   [--warn-desc N] [--max-desc N] [--budget N]
  context-cost.py selftest
Defaults: --warn-desc 1024 (the conventional terseness budget) · --max-desc 2048 (a body, not an ad) ·
--budget off (per-plugin always-on char ceiling; opt-in).
Exit 0 = within budget (WARNs don't fail); 1 = a description exceeds --max-desc or a plugin exceeds --budget.
Stdlib only; Python 3.8+.
"""
import glob
import json
import os
import re
import sys
import tempfile

WARN_DESC = 1024   # over this, a description is carrying body weight into always-on context (reported, non-failing)
MAX_DESC = 2048    # over this, it is unarguably a body smuggled into an advertisement (FAIL)
DOMINATE = 0.25    # a single component over this share of a plugin's always-on cost is a domination smell (WARN)

_KEY_RE = re.compile(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$")


def frontmatter(path):
    """Parse a markdown file's YAML frontmatter into {key: scalar}, honoring folded/literal block
    scalars (`description: >` with indented continuation lines — the dominant description format here)."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return {}
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    lines = m.group(1).split("\n")
    out, i = {}, 0
    while i < len(lines):
        km = _KEY_RE.match(lines[i])
        if not km:
            i += 1
            continue
        indent, key, val = len(km.group(1)), km.group(2), km.group(3)
        if val.strip() in (">", "|", ">-", "|-", ">+", "|+"):   # block scalar — gather more-indented lines
            i += 1
            buf = []
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    buf.append("")
                    i += 1
                    continue
                if (len(nxt) - len(nxt.lstrip())) <= indent:
                    break
                buf.append(nxt.strip())
                i += 1
            out[key] = " ".join(b for b in buf if b)
        else:
            out[key] = val.strip().strip("\"'")
            i += 1
    return out


def components(plugin_dir):
    """The eagerly-advertised components: list of (category, name, advertised_char_cost)."""
    rows = []
    for f in sorted(glob.glob(os.path.join(plugin_dir, "agents", "*.md"))):
        if os.path.basename(f).startswith("."):     # e.g. the git-ignored .name-map.md
            continue
        rows.append(("agent", os.path.basename(f), len(frontmatter(f).get("description", ""))))
    for f in sorted(glob.glob(os.path.join(plugin_dir, "commands", "*.md"))):
        fm = frontmatter(f)
        rows.append(("command", os.path.basename(f), len(fm.get("description", "")) + len(fm.get("argument-hint", ""))))
    for f in sorted(glob.glob(os.path.join(plugin_dir, "skills", "*", "SKILL.md"))):
        rows.append(("skill", os.path.basename(os.path.dirname(f)), len(frontmatter(f).get("description", ""))))
    return rows


def audit(plugin_dir, warn_desc=WARN_DESC, max_desc=MAX_DESC, budget=None):
    """Return (summary dict, findings). findings is a list of (level, message); level in {WARN, FAIL}."""
    rows = components(plugin_dir)
    total = sum(c for _, _, c in rows)
    by_cat = {}
    for cat, _, c in rows:
        by_cat[cat] = by_cat.get(cat, 0) + c
    mcp = 0
    mcp_path = os.path.join(plugin_dir, ".mcp.json")
    if os.path.isfile(mcp_path):
        try:
            mcp = len(json.load(open(mcp_path, encoding="utf-8")).get("mcpServers", {}))
        except (OSError, ValueError):
            mcp = -1   # present but unparsable

    findings = []
    for cat, name, c in rows:
        if c > max_desc:
            findings.append(("FAIL", f"{cat} {name}: description is {c} chars (> --max-desc {max_desc}) — a body, not an advertisement; it taxes every session"))
        elif c > warn_desc:
            findings.append(("WARN", f"{cat} {name}: description is {c} chars (> {warn_desc}) — heavy; trim toward a terse what+when"))
    if total and rows:
        biggest = max(rows, key=lambda r: r[2])
        # Domination is the rubric's "VERBOSE description dominating" — so the dominating component must
        # itself be substantial (a terse description ruling a trivial budget is not a cost smell).
        if biggest[2] >= 400 and biggest[2] / total > DOMINATE:
            findings.append(("WARN", f"{biggest[0]} {biggest[1]} is {biggest[2] / total:.0%} of always-on cost — one component dominates the budget (P6 'verbose description dominating')"))
    if budget is not None and total > budget:
        findings.append(("FAIL", f"always-on total {total} chars exceeds --budget {budget}"))

    summary = {"total": total, "tokens": total // 4, "by_cat": by_cat, "n": len(rows), "mcp": mcp,
               "top": sorted(rows, key=lambda r: -r[2])[:5]}
    return summary, findings


def _report(name, plugin_dir, warn_desc, max_desc, budget):
    s, findings = audit(plugin_dir, warn_desc, max_desc, budget)
    cats = "  ".join(f"{c}={v:,}" for c, v in sorted(s["by_cat"].items())) or "(none)"
    mcp = "" if s["mcp"] == 0 else (f"  +MCP×{s['mcp']} (live tool-defs not counted — see check-mcp-liveness)" if s["mcp"] > 0 else "  +MCP (unparsable)")
    print(f"  {name}: always-on ≈ {s['total']:,} chars (~{s['tokens']:,} tok) over {s['n']} components{mcp}")
    print(f"      by category: {cats}")
    if s["top"] and s["total"]:
        print("      heaviest:    " + "  ".join(f"{cat}/{nm} {c}c ({c / s['total']:.0%})" for cat, nm, c in s["top"] if c))
    for level, msg in findings:
        print(f"      [{level}] {msg}")
    return not any(level == "FAIL" for level, _ in findings)


def cmd_plugin(plugin_dir, warn_desc, max_desc, budget):
    if not os.path.isdir(plugin_dir):
        print(f"RESULT: FAIL — not a directory: {plugin_dir}")
        return 1
    ok = _report(os.path.basename(plugin_dir.rstrip(os.sep)) or plugin_dir, plugin_dir, warn_desc, max_desc, budget)
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} (context-cost) — {plugin_dir}")
    return 0 if ok else 1


def cmd_marketplace(path, warn_desc, max_desc, budget):
    mpath = os.path.join(path, ".claude-plugin", "marketplace.json")
    if not os.path.isfile(mpath):
        print(f"RESULT: FAIL — no marketplace.json at {mpath}")
        return 1
    entries = json.load(open(mpath, encoding="utf-8")).get("plugins", [])
    allok, grand = True, 0
    for e in entries:
        src = e.get("source", "")
        rel = src[2:] if src.startswith("./") else src
        pdir = os.path.join(path, rel)
        if not os.path.isdir(pdir):
            continue
        allok = _report(e.get("name", rel), pdir, warn_desc, max_desc, budget) and allok
        grand += audit(pdir, warn_desc, max_desc, budget)[0]["total"]
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'} (context-cost) — catalog always-on ≈ {grand:,} chars (~{grand // 4:,} tok)")
    return 0 if allok else 1


def _mk(root, rel, desc, key="description", extra=""):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(f"---\nname: {os.path.basename(rel)}\n{key}: >\n  {desc}\n{extra}---\n\n# body\n")


def cmd_selftest():
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        # Known sizes: an agent (40), a command desc (30) + argument-hint (10), a skill (50).
        _mk(tmp, "agents/critic-a.md", "x" * 40)
        _mk(tmp, "commands/cmd-a.md", "y" * 30, extra="argument-hint: " + "z" * 10 + "\n")
        _mk(tmp, "skills/foo/SKILL.md", "w" * 50)
        s, findings = audit(tmp)
        expect(s["total"] == 40 + 40 + 50, f"measurement wrong: total={s['total']} (expected 130)")
        expect(s["by_cat"] == {"agent": 40, "command": 40, "skill": 50}, f"per-category wrong: {s['by_cat']}")
        expect(s["tokens"] == 130 // 4, f"token estimate wrong: {s['tokens']}")
        expect(not findings, f"a terse plugin produced findings: {findings}")

    # FAIL on a >max_desc description (a body in an advertisement).
    with tempfile.TemporaryDirectory() as tmp:
        _mk(tmp, "agents/critic-big.md", "B" * 2500)
        _, findings = audit(tmp)
        expect(any(lv == "FAIL" for lv, _ in findings), "did NOT fail a 2500-char description (> max-desc 2048)")

    # WARN (not FAIL) on an over-1024 but under-2048 description — a legitimately rich description.
    with tempfile.TemporaryDirectory() as tmp:
        _mk(tmp, "skills/rich/SKILL.md", "R" * 1500)
        _, findings = audit(tmp)
        expect(any(lv == "WARN" for lv, _ in findings), "did NOT warn a 1500-char description")
        expect(not any(lv == "FAIL" for lv, _ in findings), "WRONGLY failed a 1500-char description (should WARN only)")

    # Domination WARN: one component is most of the always-on cost.
    with tempfile.TemporaryDirectory() as tmp:
        _mk(tmp, "agents/critic-fat.md", "F" * 900)
        _mk(tmp, "commands/cmd-thin.md", "t" * 20)
        _, findings = audit(tmp)
        expect(any(lv == "WARN" and "dominates" in m for lv, m in findings), "did NOT flag a dominating component")

    # Opt-in --budget breach FAILs even with terse descriptions.
    with tempfile.TemporaryDirectory() as tmp:
        _mk(tmp, "agents/critic-a.md", "x" * 200)
        _, findings = audit(tmp, budget=100)
        expect(any(lv == "FAIL" and "budget" in m for lv, m in findings), "did NOT fail an explicit --budget breach")

    if fails:
        sys.stderr.write("context-cost selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("context-cost selftest: OK (measures always-on cost incl. folded block scalars; FAILs a 2KB body-"
          "description and a --budget breach; WARNs a rich description + a dominating component; terse passes clean)")
    return 0


def _flag(argv, name, default):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            try:
                return int(argv[i + 1])
            except ValueError:
                pass
    return default


def main(argv):
    if len(argv) == 1 and argv[0] == "selftest":
        return cmd_selftest()
    warn_desc = _flag(argv, "--warn-desc", WARN_DESC)
    max_desc = _flag(argv, "--max-desc", MAX_DESC)
    budget = _flag(argv, "--budget", None)
    pos = [a for a in argv if not a.startswith("--") and not a.lstrip("-").isdigit()]
    if len(pos) == 2 and pos[0] == "plugin":
        return cmd_plugin(pos[1], warn_desc, max_desc, budget)
    if len(pos) == 2 and pos[0] == "marketplace":
        return cmd_marketplace(pos[1], warn_desc, max_desc, budget)
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip() if "Usage:" in __doc__ else "usage error", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
