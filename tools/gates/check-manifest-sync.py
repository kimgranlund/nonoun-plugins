#!/usr/bin/env python3
"""check-manifest-sync.py — fail when a plugin's declared state drifts from what it ships.

Mechanizes CLAUDE.md's "keep the four descriptions in sync — drift is a defect" rule and the
version<->CHANGELOG honesty the manifest validator can't see (it checks each manifest in isolation).
This is the gate that would have caught the brand-forge v0.1->v0.2 drift the 2026-06-03 red-team
found by hand: a description that named four commands while the directory shipped five, and a
CHANGELOG whose "Unreleased" features were already merged under the released version.

Four checks, per plugin:
  C1  version <-> CHANGELOG : plugin.json `version` equals the latest dated CHANGELOG release, and no
                             "## Unreleased" section carries shipped content (this repo has no
                             separate dist — the directory IS the release).
  C2  count claims         : every "N commands / N-critic / ..." count stated in the plugin.json
                             description, README, or this plugin's marketplace.json entry matches the
                             real directory count (commands/*.md, agents/critic-*.md). The CHANGELOG
                             is NOT scanned — its entries describe historical releases.
  C3  cited commands exist : every `/<prefix>-<name>` slash-command cited in those descriptions, whose
                             prefix matches a real command's prefix, resolves to a commands/*.md file.
  C4  enumeration complete : a parenthetical/bracketed list of >=3 same-prefix slash-commands is the
                             conventionally-complete command set; if it OMITS a command that ships, it's
                             the brand-forge drift (a description listing 6 of 7 commands) — now caught.

Usage:
  check-manifest-sync.py <plugin-dir> [--json]   # scan one plugin
  check-manifest-sync.py selftest                # synthetic clean + drifted fixtures prove it bites
Exit 0 = in sync · 1 = drift · 2 = bad invocation.
Stdlib only (Python 3.8+).
"""
import glob
import json
import os
import re
import shutil
import sys
import tempfile

VER_RE = re.compile(r"^##\s+\[?v?(\d+\.\d+\.\d+)", re.M)
UNREL_RE = re.compile(r"^##\s+\[?Unreleased\]?.*$(.*?)(?=^##\s|\Z)", re.M | re.S | re.I)
# Count claims: (regex capturing the number, noun, glob of the things counted). Only nouns terse
# plugin descriptions actually state numerically — commands and council critics — to keep signal high.
COUNT_CLAIMS = [
    (re.compile(r"(\d+)\s+(?:typed\s+)?(?:commands?|entry\s+points?)\b", re.I),
     "command", "commands/*.md"),
    (re.compile(r"(\d+)\s*-?\s*(?:[a-z]+[\s-]+){0,3}critics?\b", re.I),
     "critic", "agents/critic-*.md"),
]
# A slash-command citation starts at a token boundary (space, "(", backtick, line start) — the
# lookbehind rejects path fragments like `../adia-ui-factory` or `host.com/x/y` that merely contain a slash.
SLASH_CMD_RE = re.compile(r"(?<![\w./@-])/([a-z][a-z0-9]*(?:-[a-z0-9]+)+)")
# A parenthetical or bracketed group (non-nested) — a conventionally-complete command enumeration lives here.
PAREN_RE = re.compile(r"[(\[]([^()\[\]]+)[)\]]")


def _read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def _count(plugin_root, pattern):
    return len(glob.glob(os.path.join(plugin_root, pattern)))


def _description_sources(plugin_root):
    """The 'current-state' docs whose counts must match the tree — plugin.json description, README,
    and this plugin's marketplace.json entry. (The CHANGELOG is excluded: it narrates history.)"""
    out = []
    pj = os.path.join(plugin_root, ".claude-plugin", "plugin.json")
    if os.path.isfile(pj):
        try:
            out.append(("plugin.json", json.load(open(pj, encoding="utf-8")).get("description", "")))
        except (OSError, ValueError):
            pass
    readme = os.path.join(plugin_root, "README.md")
    if os.path.isfile(readme):
        out.append(("README.md", _read(readme)))
    mkt = os.path.join(os.path.dirname(plugin_root), ".claude-plugin", "marketplace.json")
    name = os.path.basename(plugin_root)
    if os.path.isfile(mkt):
        try:
            for e in json.load(open(mkt, encoding="utf-8")).get("plugins", []):
                if e.get("name") == name or e.get("source", "").rstrip("/").endswith("/" + name):
                    out.append(("marketplace.json", e.get("description", "")))
                    break
        except (OSError, ValueError):
            pass
    return out


def _plugin_names(plugin_root):
    """Sibling plugin names from the marketplace — a `/<name>` that is a plugin is a cross-plugin
    reference, never a command (catches the adia-ui-factory / adia-ui-forge shared-prefix case)."""
    mkt = os.path.join(os.path.dirname(plugin_root), ".claude-plugin", "marketplace.json")
    try:
        return {e.get("name", "") for e in json.load(open(mkt, encoding="utf-8")).get("plugins", [])}
    except (OSError, ValueError):
        return set()


def check(plugin_root):
    plugin_root = os.path.abspath(plugin_root)
    findings = []  # (code, detail)

    # C1 — version <-> CHANGELOG
    version = None
    pj = os.path.join(plugin_root, ".claude-plugin", "plugin.json")
    if os.path.isfile(pj):
        try:
            version = json.load(open(pj, encoding="utf-8")).get("version")
        except (OSError, ValueError):
            findings.append(("C1", "plugin.json is unreadable / not valid JSON"))
    cl = os.path.join(plugin_root, "CHANGELOG.md")
    if version and os.path.isfile(cl):
        text = _read(cl)
        m = VER_RE.search(text)
        if m and m.group(1) != version:
            findings.append(("C1", f"plugin.json version {version} != latest CHANGELOG release {m.group(1)}"))
        um = UNREL_RE.search(text)
        if um and re.search(r"^\s*[-*]\s+\S", um.group(1), re.M):
            findings.append(("C1", 'CHANGELOG has an "Unreleased" section with content — cut a dated '
                                   "release (this repo ships the working tree as the release)"))
    elif version and not os.path.isfile(cl):
        findings.append(("C1", "no CHANGELOG.md to corroborate the version"))

    # C2 — count claims match the tree
    actual = {noun: _count(plugin_root, pat) for _rx, noun, pat in COUNT_CLAIMS}
    c2_seen = set()
    for src, text in _description_sources(plugin_root):
        for rx, noun, _pat in COUNT_CLAIMS:
            for m in rx.finditer(text):
                claimed = int(m.group(1))
                key = (src, noun, claimed)
                if actual[noun] > 0 and claimed != actual[noun] and key not in c2_seen:
                    c2_seen.add(key)
                    findings.append(("C2", f'{src} claims {claimed} {noun}(s) ("{m.group(0).strip()}") '
                                           f"but the tree has {actual[noun]}"))

    # C3 — cited slash-commands resolve
    cmds = {os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(plugin_root, "commands", "*.md"))}
    prefixes = {c.split("-", 1)[0] for c in cmds if "-" in c}
    siblings = _plugin_names(plugin_root)
    c3_seen = set()
    if cmds:
        for src, text in _description_sources(plugin_root):
            for m in SLASH_CMD_RE.finditer(text):
                tok = m.group(1)
                if (tok.split("-", 1)[0] in prefixes and tok not in cmds
                        and tok not in siblings and tok not in c3_seen):
                    c3_seen.add(tok)
                    findings.append(("C3", f"{src} cites /{tok} but there is no commands/{tok}.md"))

    # C4 — enumeration completeness: a parenthetical/bracketed list of >=3 same-prefix slash-commands is
    # conventionally the COMPLETE command set; if it omits a command that ships, it's the brand-forge drift
    # (a manifest that listed 6 of 7 commands). Only fires on an explicit (a, b, c) run — not a prose mention
    # of one or two commands — so an intentional subset stated outside parens never trips it.
    c4_seen = set()
    if cmds:
        by_prefix_all = {}
        for c in cmds:
            by_prefix_all.setdefault(c.split("-", 1)[0], set()).add(c)
        for src, text in _description_sources(plugin_root):
            for grp in PAREN_RE.findall(text):
                listed = {m.group(1) for m in SLASH_CMD_RE.finditer(grp) if m.group(1) in cmds}
                by_prefix = {}
                for c in listed:
                    by_prefix.setdefault(c.split("-", 1)[0], set()).add(c)
                for pfx, enumed in by_prefix.items():
                    full = by_prefix_all.get(pfx, set())
                    missing = full - enumed
                    if len(enumed) >= 3 and missing and (src, pfx, frozenset(missing)) not in c4_seen:
                        c4_seen.add((src, pfx, frozenset(missing)))
                        findings.append(("C4", f"{src} has a ({len(enumed)}-command) parenthetical list that enumerates "
                                               f"{len(enumed)} of {len(full)} {pfx}-* commands but OMITS "
                                               f"{', '.join('/' + m for m in sorted(missing))} — a complete-looking list "
                                               f"that fell behind the directory (the brand-forge drift class)"))
    return findings


def _mk_plugin(root, version, changelog_latest, description, commands, critics, unreleased=False):
    os.makedirs(os.path.join(root, ".claude-plugin"))
    json.dump({"name": os.path.basename(root), "version": version, "description": description},
              open(os.path.join(root, ".claude-plugin", "plugin.json"), "w", encoding="utf-8"))
    os.makedirs(os.path.join(root, "commands"))
    for c in commands:
        open(os.path.join(root, "commands", c + ".md"), "w", encoding="utf-8").write("# " + c)
    if critics:
        os.makedirs(os.path.join(root, "agents"))
        for i in range(critics):
            open(os.path.join(root, "agents", f"critic-{i}.md"), "w", encoding="utf-8").write("# critic")
    body = "# Changelog\n\n"
    if unreleased:
        body += "## Unreleased\n\n- a shipped-but-undeclared feature\n\n"
    body += f"## {changelog_latest} — 2026-06-03\n\n- initial\n"
    open(os.path.join(root, "CHANGELOG.md"), "w", encoding="utf-8").write(body)
    open(os.path.join(root, "README.md"), "w", encoding="utf-8").write(description + "\n")


def selftest():
    tmp = tempfile.mkdtemp(prefix="manifest-sync-selftest-")
    fails = []
    try:
        clean = os.path.join(tmp, "clean-forge")
        _mk_plugin(clean, "1.0.0", "1.0.0",
                   "A demo with 2 typed commands (/clean-a, /clean-b) and a 3-critic council.",
                   ["clean-a", "clean-b"], 3)
        r = check(clean)
        if r:
            fails.append(f"clean plugin should pass, but flagged: {r}")

        drift = os.path.join(tmp, "drift-forge")
        _mk_plugin(drift, "0.1.0", "0.2.0",  # version != changelog (C1) + Unreleased content (C1)
                   "A demo with 4 typed commands (/drift-a, /drift-x) and a 5-critic council.",
                   ["drift-a", "drift-b"], 3, unreleased=True)  # claims 4 cmds/2 real, 5 critics/3 real (C2); /drift-x phantom (C3)
        codes = {c for c, _ in check(drift)}
        for need in ("C1", "C2", "C3"):
            if need not in codes:
                fails.append(f"drift plugin should raise {need}; got {sorted(codes)}")

        # C4 — a parenthetical list of >=3 commands that OMITS a shipped one (the brand-forge drift class)
        omit = os.path.join(tmp, "omit-forge")
        _mk_plugin(omit, "1.0.0", "1.0.0",
                   "Modes are typed commands (/omit-a, /omit-b, /omit-c).",   # lists 3, ships 4 → omits /omit-d
                   ["omit-a", "omit-b", "omit-c", "omit-d"], 0)
        ocodes = {c for c, _ in check(omit)}
        if "C4" not in ocodes:
            fails.append(f"omission plugin should raise C4 (a 3-of-4 parenthetical list); got {sorted(ocodes)}")
        # a COMPLETE parenthetical list of the same shape must NOT fire C4
        full = os.path.join(tmp, "full-forge")
        _mk_plugin(full, "1.0.0", "1.0.0",
                   "Modes are typed commands (/full-a, /full-b, /full-c).",   # lists 3, ships exactly those 3
                   ["full-a", "full-b", "full-c"], 0)
        if any(c == "C4" for c, _ in check(full)):
            fails.append("a complete parenthetical command list wrongly fired C4")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        sys.stderr.write("check-manifest-sync selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("check-manifest-sync selftest: OK")
    return 0


def main(argv):
    args = [a for a in argv if not a.startswith("-")]
    if args and args[0] == "selftest":
        return selftest()
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("usage: check-manifest-sync.py <plugin-dir> [--json] | selftest", file=sys.stderr)
        return 2
    findings = check(args[0])
    if "--json" in argv:
        print(json.dumps({"ok": not findings,
                          "findings": [{"check": c, "detail": d} for c, d in findings]}, indent=2))
    else:
        for c, d in findings:
            print(f"  [{c}] {d}")
        print(f"RESULT: {'PASS' if not findings else 'FAIL'} ({len(findings)} drift finding(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
