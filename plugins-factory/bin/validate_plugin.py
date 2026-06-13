#!/usr/bin/env python3
"""validate_plugin.py — static validator for Claude Code plugin.json + marketplace.json.

Reproduces the DOCUMENTED static checks of `claude plugin validate` in-repo, so the gate runs
without the CLI guaranteed present (see references/plugin-architecture.md). It NEVER installs,
runs, or imports the plugin — purely static manifest/frontmatter analysis (a P9 property of this
tool itself; the 2026-06-02 build-time red-team confirmed the inert posture and drove the
loader-rule + layout-depth + hooks-parse checks below).

Subcommands:
  plugin <path>        Validate a plugin dir (containing .claude-plugin/plugin.json) or a plugin.json.
  marketplace <path>   Validate a .claude-plugin/marketplace.json (or a dir containing one).
  selftest             Run built-in good/bad fixtures; exit 0 iff the validator logic is correct.
  hook                 PostToolUse advisory mode: read the event JSON on stdin, validate a written
                       plugin.json / marketplace.json, print findings, and ALWAYS exit 0 (never blocks).

Checks (ERROR -> exit 1 · warn -> advisory unless --strict):
  PLUGIN (manifest)
    - valid JSON; `name` present, kebab-case, no spaces (ERROR)
    - `version` (if present) is semver (ERROR)
    - component path fields are `./`-relative with NO `..` traversal (ERROR on `..`);
      absolute / `~` / UNC / drive-relative paths flagged (warn — won't resolve after install)
    - `userConfig` options each carry `title` (str), `type` (string|number|boolean|directory|file),
      and `description` (str) — all three required (ERROR; mirrors `claude plugin install`, which
      rejects the install otherwise); non-bool `sensitive`/`required`/`multiple` warn
  PLUGIN (layout — when given a dir)
    - .claude-plugin/ purity: a component dir anywhere under .claude-plugin/ (even nested) ERRORs
      (it will silently NOT load); other subdirs of .claude-plugin/ warn
    - declared component paths that don't exist on disk ERROR (declared-but-absent)
    - hooks/hooks.json and .mcp.json, if present, must parse (a malformed hooks.json blocks the
      WHOLE plugin) (ERROR)
    - LOADER RULE: a bundled agents/*.md whose frontmatter declares `hooks`, `mcpServers`, or
      `permissionMode` ERRORs (the loader forbids it — capability smuggling; rubric P9 / ST3)
    - FRONTMATTER FLOW-COLLECTION TRAP: a command/agent/skill frontmatter value that opens an
      unquoted `[`/`{` flow collection and is unterminated or has trailing tokens (e.g.
      `argument-hint: [spa|ssr] [app name]`) ERRORs — YAML fails to parse and the loader silently
      drops the WHOLE frontmatter block; a clean collection in a string key (description/
      argument-hint/name/title) warns (quote it)
    - a root CLAUDE.md won't load as context (warn)
  MARKETPLACE
    - valid JSON; `name` kebab + not reserved (ERROR); `owner.name` present (ERROR)
    - `plugins[]` present; each entry has `name` (kebab) + `source` (ERROR)
    - any string value in a `source` (string or object, any key) containing `..` ERRORs
    - no duplicate plugin names (ERROR); unknown object-source type warns

Usage:
  validate_plugin.py plugin <path> [--strict] [--json]
  validate_plugin.py marketplace <path> [--strict] [--json]
  validate_plugin.py selftest
Exit 0 = valid (no errors; no warnings under --strict) · 1 = invalid · 2 = bad invocation.
Stdlib only (Python 3.9+).
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import tempfile

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
# frontmatter top-level key (no leading whitespace, before the colon)
FM_KEY = re.compile(r"^([A-Za-z_][\w-]*)\s*:")
# top-level frontmatter `key: value` with an inline (non-empty) scalar value
FM_KEYVAL = re.compile(r"^([A-Za-z_][\w-]*):[ \t]+(\S.*?)[ \t]*$")
LOADER_FORBIDDEN = {"hooks", "mcpServers", "permissionMode"}

# userConfig option schema (MCPB user_config form, mirrored by `claude plugin validate`):
# each option REQUIRES `title` (str), `type` (enum below), and `description` (str).
USERCONFIG_TYPES = {"string", "number", "boolean", "directory", "file"}
# frontmatter keys whose value is meant to be a plain string — a flow collection ([…]/{…}) there
# is a smell (parsed as a list/map) even when it parses; flagged as a warning.
SCALAR_FM_KEYS = {"description", "argument-hint", "name", "title"}

COMPONENT_PATH_FIELDS = [
    "skills", "commands", "agents", "hooks", "mcpServers",
    "outputStyles", "lspServers",
]
COMPONENT_DIRS = {"skills", "commands", "agents", "hooks", "output-styles", "themes", "monitors"}

RESERVED_MARKETPLACE_NAMES = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
    "anthropic-marketplace", "anthropic-plugins", "agent-skills", "anthropic-agent-skills",
    "knowledge-work-plugins", "life-sciences", "claude-for-legal",
    "claude-for-financial-services", "financial-services-plugins", "official-claude-plugins",
}
KNOWN_SOURCE_TYPES = {"github", "url", "git-subdir", "npm"}


# ----------------------------------------------------------------------------- path helpers
def _has_traversal(p: str) -> bool:
    return ".." in p.replace("\\", "/").split("/")


def _is_absolute(p: str) -> bool:
    """POSIX-absolute, Windows drive-absolute/relative, UNC, or ~-rooted — none resolve in the cache."""
    return (
        p.startswith("/")
        or p.startswith("~")
        or p.startswith("\\\\")                      # UNC
        or re.match(r"^[A-Za-z]:", p) is not None    # C:\... or C:rel
    )


def _iter_path_values(val):
    if isinstance(val, str):
        yield val
    elif isinstance(val, list):
        for item in val:
            if isinstance(item, str):
                yield item


def _iter_strings(obj):
    """Yield every string value nested anywhere in obj (for exhaustive `..` scanning)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_strings(v)


def _agent_declares_illegal(frontmatter_text: str):
    """Return the sorted list of loader-forbidden top-level keys present in an agent's frontmatter."""
    found = set()
    for line in frontmatter_text.splitlines():
        m = FM_KEY.match(line)
        if m and m.group(1) in LOADER_FORBIDDEN:
            found.add(m.group(1))
    return sorted(found)


def _extract_frontmatter(text: str) -> str:
    """Return the YAML frontmatter block (between the first two `---` fences), or ''."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    out = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        out.append(line)
    return "\n".join(out)


def _flow_trap_severity(value: str):
    """Classify an unquoted frontmatter scalar for the YAML flow-collection trap.

    A value that opens a flow collection (`[` or `{`) is parsed as a list/map, never a string. If
    that collection is unterminated, or has any trailing tokens after its matching close, the YAML
    parser raises "Unexpected token" and the loader drops the ENTIRE frontmatter block (every field
    silently lost). Quoting the value fixes it.

      `[a|b] [c]`  -> 'error'  (trailing `[c]` after the first `]`)
      `[a|b`       -> 'error'  (never closed)
      `[a|b]`      -> 'warn'   (clean collection, but a string was intended)
      `"[a|b] [c]"`-> None     (already quoted — safe)
    Returns None | 'warn' | 'error'.
    """
    v = value.strip()
    if not v or v[0] in ("\"", "'") or v[0] not in "[{":
        return None
    depth, in_str, end = 0, None, -1
    for i, c in enumerate(v):
        if in_str:
            if c == in_str:
                in_str = None
        elif c in ("\"", "'"):
            in_str = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return "error"
    return "error" if v[end + 1:].strip() else "warn"


def _frontmatter_traps(fm_text: str, rel: str):
    """Scan a frontmatter block for the flow-collection trap. Returns (errors, warnings)."""
    errors, warnings = [], []
    for line in fm_text.splitlines():
        m = FM_KEYVAL.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        sev = _flow_trap_severity(val)
        if sev == "error":
            errors.append(f"`{rel}` frontmatter `{key}:` opens a YAML flow collection that is "
                          f"unterminated or has trailing tokens — the parser fails and the WHOLE "
                          f"frontmatter block is silently dropped at load; quote the value")
        elif sev == "warn" and key in SCALAR_FM_KEYS:
            warnings.append(f"`{rel}` frontmatter `{key}:` value starts with `[`/`{{` so it parses "
                            f"as a list/map, not a string — quote it")
    return errors, warnings


def _validate_user_config(uc):
    """Validate the `userConfig` block against the option schema enforced by `claude plugin
    install` / `claude plugin validate`. Returns (errors, warnings)."""
    errors, warnings = [], []
    if uc is None:
        return errors, warnings
    if not isinstance(uc, dict):
        return (["`userConfig` must be an object (option-name -> option-schema)"], [])
    for key, opt in uc.items():
        loc = f"userConfig.{key}"
        if not isinstance(opt, dict):
            errors.append(f"{loc} must be an object")
            continue
        title = opt.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{loc} missing required string `title` — rejected at install; the "
                          f"enable-time prompt has no label without it")
        typ = opt.get("type")
        if not isinstance(typ, str) or typ not in USERCONFIG_TYPES:
            errors.append(f"{loc}.type must be one of {sorted(USERCONFIG_TYPES)}: got {typ!r}")
        desc = opt.get("description")
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{loc} missing required string `description`")
        for boolfield in ("sensitive", "required", "multiple"):
            if boolfield in opt and not isinstance(opt[boolfield], bool):
                warnings.append(f"{loc}.{boolfield} should be a boolean: got {opt[boolfield]!r}")
    return errors, warnings


# ----------------------------------------------------------------------------- layout (dir-mode)
def _check_layout(plugin_dir, data):
    errors, warnings = [], []

    # .claude-plugin/ purity — recursive: a component dir at ANY depth silently won't load.
    cp = os.path.join(plugin_dir, ".claude-plugin")
    if os.path.isdir(cp):
        for root, dirs, _files in os.walk(cp):
            for d in dirs:
                if d in COMPONENT_DIRS:
                    rel = os.path.relpath(os.path.join(root, d), plugin_dir)
                    errors.append(f"component dir `{rel}` is inside .claude-plugin/ "
                                  f"(it will silently NOT load — move to the plugin root)")
                elif root == cp:
                    warnings.append(f".claude-plugin/ should hold only plugin.json; found subdir `{d}/`")

    # declared component paths must exist on disk (declared-but-absent silently provides nothing).
    for field in COMPONENT_PATH_FIELDS:
        for p in _iter_path_values(data.get(field, None) or []):
            if p.startswith("./") and not _has_traversal(p) and not _is_absolute(p):
                if not os.path.exists(os.path.join(plugin_dir, p)):
                    errors.append(f"`{field}` declares `{p}` but it does not exist on disk")

    # hooks/hooks.json + .mcp.json must parse — a malformed hooks.json blocks the WHOLE plugin.
    for rel in ("hooks/hooks.json", ".mcp.json"):
        fp = os.path.join(plugin_dir, rel)
        if os.path.isfile(fp):
            try:
                json.load(open(fp, encoding="utf-8"))
            except json.JSONDecodeError as e:
                sev = "blocks the ENTIRE plugin from loading" if rel.endswith("hooks.json") else "won't load"
                errors.append(f"`{rel}` is malformed JSON ({sev}): {e}")

    # LOADER RULE: a bundled agent may not declare hooks / mcpServers / permissionMode.
    agents_dir = os.path.join(plugin_dir, "agents")
    if os.path.isdir(agents_dir):
        for entry in sorted(os.listdir(agents_dir)):
            if entry.startswith(".") or not entry.endswith(".md"):  # skip dotfiles (e.g. a git-ignored .name-map.md)
                continue
            try:
                text = open(os.path.join(agents_dir, entry), encoding="utf-8").read()
            except OSError:
                continue
            illegal = _agent_declares_illegal(_extract_frontmatter(text))
            if illegal:
                errors.append(f"agent `agents/{entry}` declares loader-forbidden field(s) "
                              f"{illegal} — plugin-shipped agents cannot carry hooks/mcpServers/permissionMode")

    # FRONTMATTER FLOW-COLLECTION TRAP — an unquoted `key: [..]`/`{..}` value that is unterminated
    # or carries trailing tokens (e.g. `argument-hint: [spa|ssr] [app name]`) makes the YAML parser
    # fail; the loader then drops the WHOLE frontmatter block (description/argument-hint lost). This
    # is invisible to a path/JSON check, which is how it shipped — so scan every component's md.
    fm_targets = []
    for sub in ("commands", "agents"):
        d = os.path.join(plugin_dir, sub)
        if os.path.isdir(d):
            for entry in sorted(os.listdir(d)):
                if entry.endswith(".md") and not entry.startswith("."):  # skip dotfiles
                    fm_targets.append((os.path.join(d, entry), f"{sub}/{entry}"))
    skills_dir = os.path.join(plugin_dir, "skills")
    if os.path.isdir(skills_dir):
        for entry in sorted(os.listdir(skills_dir)):
            sm = os.path.join(skills_dir, entry, "SKILL.md")
            if os.path.isfile(sm):
                fm_targets.append((sm, f"skills/{entry}/SKILL.md"))
    for fp, rel in fm_targets:
        try:
            text = open(fp, encoding="utf-8").read()
        except OSError:
            continue
        e_fm, w_fm = _frontmatter_traps(_extract_frontmatter(text), rel)
        errors += e_fm
        warnings += w_fm

    # COMMAND ↔ SKILL slug collision — commands AND skills both resolve as `/<plugin>:<slug>`
    # (plugin-architecture.md §Namespacing). A command and a skill that share a slug collide: the
    # skill claims the namespace and the command is unreachable ("Unknown command: /<plugin>:<slug>").
    def _dir_slugs(sub, is_skill=False):
        d = os.path.join(plugin_dir, sub)
        if not os.path.isdir(d):
            return set()
        if is_skill:
            return {n for n in os.listdir(d) if not n.startswith(".") and os.path.isfile(os.path.join(d, n, "SKILL.md"))}
        return {os.path.splitext(n)[0] for n in os.listdir(d) if n.endswith(".md") and not n.startswith(".")}
    for slug in sorted(_dir_slugs("commands") & _dir_slugs("skills", is_skill=True)):
        errors.append(f"command `commands/{slug}.md` and skill `skills/{slug}/` share the slug "
                      f"`{slug}`: both resolve to `/<plugin>:{slug}`, so the skill shadows the command "
                      f"and `/{slug}` is unreachable — rename one (commands are verbs; skills are domains)")

    if os.path.isfile(os.path.join(plugin_dir, "CLAUDE.md")):
        warnings.append("a root CLAUDE.md is NOT loaded as plugin context — ship instructions as a skill")

    return errors, warnings


# ----------------------------------------------------------------------------- validators (pure-ish)
def validate_plugin_manifest(data, plugin_dir=None):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return (["manifest is not a JSON object"], [])

    name = data.get("name")
    if not name:
        errors.append("missing required field `name`")
    elif not isinstance(name, str) or not KEBAB.match(name):
        errors.append(f"`name` must be kebab-case (no spaces/uppercase): got {name!r}")

    ver = data.get("version")
    if ver is not None and not (isinstance(ver, str) and SEMVER.match(ver)):
        errors.append(f"`version` must be semver MAJOR.MINOR.PATCH: got {ver!r}")

    for field in COMPONENT_PATH_FIELDS:
        if field not in data:
            continue
        for p in _iter_path_values(data[field]):
            if _has_traversal(p):
                errors.append(f"`{field}` path escapes the plugin root (contains `..`): {p!r}")
            elif _is_absolute(p):
                warnings.append(f"`{field}` uses a non-relative path (won't resolve after install): {p!r}")
            elif not p.startswith("./"):
                warnings.append(f"`{field}` path should be `./`-relative: {p!r}")

    e_uc, w_uc = _validate_user_config(data.get("userConfig"))
    errors += e_uc
    warnings += w_uc

    if plugin_dir and os.path.isdir(plugin_dir):
        e2, w2 = _check_layout(plugin_dir, data)
        errors += e2
        warnings += w2

    return (errors, warnings)


def validate_marketplace_manifest(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return (["marketplace is not a JSON object"], [])

    name = data.get("name")
    if not name:
        errors.append("missing required field `name`")
    elif not isinstance(name, str) or not KEBAB.match(name):
        errors.append(f"marketplace `name` must be kebab-case: got {name!r}")
    elif name in RESERVED_MARKETPLACE_NAMES:
        errors.append(f"marketplace `name` is reserved and cannot be used: {name!r}")

    owner = data.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        errors.append("missing required `owner.name`")

    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append("`plugins` must be a non-empty array")
        return (errors, warnings)

    seen = set()
    for i, entry in enumerate(plugins):
        if not isinstance(entry, dict):
            errors.append(f"plugins[{i}] is not an object")
            continue
        pname = entry.get("name")
        if not pname:
            errors.append(f"plugins[{i}] missing `name`")
        else:
            if not (isinstance(pname, str) and KEBAB.match(pname)):
                errors.append(f"plugins[{i}].name must be kebab-case: got {pname!r}")
            if pname in seen:
                errors.append(f"duplicate plugin name in marketplace: {pname!r}")
            seen.add(pname)
        src = entry.get("source")
        if src is None:
            errors.append(f"plugins[{i}] ({pname!r}) missing `source`")
        else:
            if isinstance(src, str) and not src.startswith("./") and not isinstance(src, dict):
                warnings.append(f"plugins[{i}].source string should be a `./`-relative path: {src!r}")
            if isinstance(src, dict):
                stype = src.get("source")
                if stype not in KNOWN_SOURCE_TYPES:
                    warnings.append(f"plugins[{i}].source has an unknown type {stype!r} "
                                    f"(known: {sorted(KNOWN_SOURCE_TYPES)})")
            # exhaustive `..` scan over every string anywhere in the source (string or nested object)
            for s in _iter_strings(src):
                if _has_traversal(s):
                    errors.append(f"plugins[{i}].source contains a `..` path: {s!r}")
                    break
    return (errors, warnings)


# Critic personas are reused across the catalog's councils by design (the same named practitioner, a
# different per-plugin lens). Reuse means two plugins ship an `agents/critic-<name>.md` with the SAME
# frontmatter `name:`. Claude Code resolves a BARE agent name with a SILENT DROP — "if two files declare
# the same name, it keeps one and discards the other without warning" — so co-enabling two such plugins
# makes one critic vanish. The fix (I-10): every council orchestrator dispatches its critics by the
# plugin-SCOPED name (`<plugin>:critic-<name>`), which addresses each plugin's agent unambiguously. These
# four collisions are known + intentional; ANY OTHER cross-plugin agent-name collision is an accident.
KNOWN_AGENT_REUSE = {"critic-andrej-k", "critic-boris-c", "critic-garry-t", "critic-simon-w"}


def _agent_names(plugin_dir):
    """Every frontmatter `name:` under <plugin_dir>/agents/ (dotfiles like .name-map.md skipped)."""
    out = []
    adir = os.path.join(plugin_dir, "agents")
    if not os.path.isdir(adir):
        return out
    for fn in sorted(os.listdir(adir)):
        if not fn.endswith(".md") or fn.startswith("."):
            continue
        try:
            head = open(os.path.join(adir, fn), encoding="utf-8").read(4096)
        except OSError:
            continue
        m = re.search(r"^name:\s*(.+?)\s*$", head, re.M)
        if m:
            out.append(m.group(1).strip())
    return out


def check_cross_plugin_agents(market, base):
    """Cross-plugin agent-`name` collision check (marketplace scope). Known persona-reuse → warning
    (must be dispatched scoped); any other collision → error (a silent-drop accident)."""
    errors, warnings = [], []
    if not isinstance(market, dict) or not isinstance(market.get("plugins"), list):
        return errors, warnings
    byname = {}
    for entry in market["plugins"]:
        if not isinstance(entry, dict):
            continue
        pname = entry.get("name")
        src = entry.get("source")
        rel = src[2:] if isinstance(src, str) and src.startswith("./") else (src if isinstance(src, str) else pname)
        pdir = os.path.join(base, rel) if rel else None
        if not pdir or not os.path.isdir(pdir):
            continue
        for aname in _agent_names(pdir):
            byname.setdefault(aname, set()).add(pname or rel)
    for aname, plugins in sorted(byname.items()):
        if len(plugins) < 2:
            continue
        who = ", ".join(sorted(plugins))
        if aname in KNOWN_AGENT_REUSE:
            warnings.append(f"agent `{aname}` is shared across [{who}] (known persona reuse) — each council "
                            f"MUST dispatch it scoped as `<plugin>:{aname}`, never bare (Claude Code silently "
                            f"drops one of two same-named agents)")
        else:
            errors.append(f"agent name `{aname}` collides across [{who}] — a bare-name dispatch silently drops "
                          f"one. Make it unique, or (if intentional persona reuse) add it to KNOWN_AGENT_REUSE "
                          f"and ensure every orchestrator dispatches it scoped.")
    return errors, warnings


# ----------------------------------------------------------------------------- file loading
def _load_plugin_json(path):
    if os.path.isdir(path):
        cand = os.path.join(path, ".claude-plugin", "plugin.json")
        if not os.path.isfile(cand):
            cand2 = os.path.join(path, "plugin.json")
            cand = cand2 if os.path.isfile(cand2) else cand
        return json.load(open(cand, encoding="utf-8")), path
    data = json.load(open(path, encoding="utf-8"))
    plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    return data, plugin_dir


def _load_marketplace_json(path):
    if os.path.isdir(path):
        cand = os.path.join(path, ".claude-plugin", "marketplace.json")
        if not os.path.isfile(cand):
            cand2 = os.path.join(path, "marketplace.json")
            cand = cand2 if os.path.isfile(cand2) else cand
        return json.load(open(cand, encoding="utf-8"))
    return json.load(open(path, encoding="utf-8"))


def _report(kind, errors, warnings, strict, as_json):
    ok = not errors and not (strict and warnings)
    if as_json:
        print(json.dumps({"kind": kind, "ok": ok, "errors": errors, "warnings": warnings}, indent=2))
    else:
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  warn:  {w}")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} ({len(errors)} error(s), {len(warnings)} warning(s))")
    return 0 if ok else 1


# ----------------------------------------------------------------------------- selftest
def _selftest():
    cases = []  # (label, kind, payload, expect_errors)

    good_plugin = {"name": "design-system", "version": "1.2.0", "description": "x",
                   "skills": "./skills/", "commands": ["./commands/build.md"]}
    cases += [
        ("good plugin", "plugin", good_plugin, False),
        ("plugin missing name", "plugin", {"version": "1.0.0"}, True),
        ("plugin non-kebab name", "plugin", {"name": "Design System"}, True),
        ("plugin bad semver", "plugin", {"name": "x", "version": "1.0"}, True),
        ("plugin `..` path", "plugin", {"name": "x", "skills": "../shared/skills/"}, True),
        ("plugin `foo/../bar` mid-segment", "plugin", {"name": "x", "agents": "./a/../b/"}, True),
        ("plugin tilde path is warn", "plugin", {"name": "x", "agents": ["~/a.md"]}, False),
        ("userConfig good", "plugin",
         {"name": "x", "userConfig": {"k": {"title": "K", "type": "directory", "description": "d"}}}, False),
        ("userConfig missing title", "plugin",
         {"name": "x", "userConfig": {"k": {"type": "directory", "description": "d"}}}, True),
        ("userConfig missing description", "plugin",
         {"name": "x", "userConfig": {"k": {"title": "K", "type": "string"}}}, True),
        ("userConfig bad type", "plugin",
         {"name": "x", "userConfig": {"k": {"title": "K", "type": "folder", "description": "d"}}}, True),
        ("userConfig not an object", "plugin", {"name": "x", "userConfig": []}, True),
    ]
    good_mkt = {"name": "my-marketplace", "owner": {"name": "Kim"},
                "plugins": [{"name": "design-system", "source": "./plugins/ds"},
                            {"name": "repo-ops", "source": {"source": "github", "repo": "k/repo-ops"}}]}
    cases += [
        ("good marketplace", "marketplace", good_mkt, False),
        ("mkt reserved name", "marketplace",
         {"name": "anthropic-plugins", "owner": {"name": "K"}, "plugins": [{"name": "p", "source": "./p"}]}, True),
        ("mkt missing owner", "marketplace",
         {"name": "m", "plugins": [{"name": "p", "source": "./p"}]}, True),
        ("mkt duplicate plugin", "marketplace",
         {"name": "m", "owner": {"name": "K"},
          "plugins": [{"name": "p", "source": "./a"}, {"name": "p", "source": "./b"}]}, True),
        ("mkt source `..` string", "marketplace",
         {"name": "m", "owner": {"name": "K"}, "plugins": [{"name": "p", "source": "../escape"}]}, True),
        ("mkt source `..` in nested key", "marketplace",
         {"name": "m", "owner": {"name": "K"},
          "plugins": [{"name": "p", "source": {"source": "git-subdir", "url": "k/r", "path": "../escape"}}]}, True),
    ]

    failures = []
    for label, kind, payload, expect_err in cases:
        errs, _ = (validate_plugin_manifest(payload) if kind == "plugin"
                   else validate_marketplace_manifest(payload))
        if bool(errs) != expect_err:
            failures.append(f"{label}: expected_errors={expect_err} got={errs}")

    # loader-rule unit test (pure function)
    if _agent_declares_illegal("name: a\nmcpServers:\n  x: y\n") != ["mcpServers"]:
        failures.append("loader-rule: failed to flag mcpServers in agent frontmatter")
    if _agent_declares_illegal("name: a\ndescription: ok\n") != []:
        failures.append("loader-rule: false-positive on a clean agent")

    # flow-collection-trap unit tests (pure function)
    _flow_cases = {
        "[spa|ssr] [app name]": "error",   # trailing tokens after the first `]`
        "[a|b": "error",                    # never closed
        "[what to build]": "warn",          # clean collection, string intended
        '"[a|b] [c]"': None,                # already quoted
        "just a string": None,              # plain scalar
    }
    for raw, expect in _flow_cases.items():
        if _flow_trap_severity(raw) != expect:
            failures.append(f"flow-trap: {raw!r} -> {_flow_trap_severity(raw)!r}, expected {expect!r}")

    # on-disk layout fixtures (exercise the dir branch the payload tests can't reach)
    tmp = tempfile.mkdtemp(prefix="plugins-factory-selftest-")
    try:
        # nested component dir inside .claude-plugin/ must ERROR
        os.makedirs(os.path.join(tmp, ".claude-plugin", "sub", "skills"))
        open(os.path.join(tmp, ".claude-plugin", "plugin.json"), "w").write("{}")
        errs, _ = validate_plugin_manifest({"name": "x"}, tmp)
        if not errs:
            failures.append("layout: nested .claude-plugin/sub/skills not caught")
        # declared-but-absent component path must ERROR
        errs, _ = validate_plugin_manifest({"name": "x", "skills": "./skills/"}, tmp)
        if not any("does not exist" in e for e in errs):
            failures.append("layout: declared-but-absent skills/ not caught")
        # agent smuggling mcpServers must ERROR
        tmp2 = tempfile.mkdtemp(prefix="plugins-factory-selftest-")
        os.makedirs(os.path.join(tmp2, "agents"))
        open(os.path.join(tmp2, "agents", "bad.md"), "w").write("---\nname: bad\nmcpServers:\n  s: 1\n---\nbody\n")
        errs, _ = validate_plugin_manifest({"name": "x"}, tmp2)
        if not any("loader-forbidden" in e for e in errs):
            failures.append("layout: agent declaring mcpServers not caught")
        _rmtree(tmp2)

        # command ↔ skill slug collision must ERROR (the /<plugin>:<slug> shadowing class)
        tmp3 = tempfile.mkdtemp(prefix="plugins-factory-selftest-")
        os.makedirs(os.path.join(tmp3, "commands"))
        os.makedirs(os.path.join(tmp3, "skills", "evaluate"))
        open(os.path.join(tmp3, "commands", "evaluate.md"), "w").write("---\ndescription: x\n---\nbody\n")
        open(os.path.join(tmp3, "skills", "evaluate", "SKILL.md"), "w").write("---\nname: evaluate\ndescription: x\n---\nbody\n")
        errs, _ = validate_plugin_manifest({"name": "x"}, tmp3)
        if not any("share the slug" in e for e in errs):
            failures.append("layout: command↔skill slug collision not caught")
        _rmtree(tmp3)

        # command frontmatter flow-collection trap must ERROR; a quoted value must be clean
        tmp4 = tempfile.mkdtemp(prefix="plugins-factory-selftest-")
        os.makedirs(os.path.join(tmp4, "commands"))
        bad = os.path.join(tmp4, "commands", "bad.md")
        open(bad, "w").write("---\ndescription: d\nargument-hint: [spa|ssr] [app name]\n---\nbody\n")
        errs, _ = validate_plugin_manifest({"name": "x"}, tmp4)
        if not any("flow collection" in e for e in errs):
            failures.append("layout: command frontmatter flow-collection trap not caught")
        open(bad, "w").write('---\ndescription: d\nargument-hint: "[spa|ssr] [app name]"\n---\nbody\n')
        errs, _ = validate_plugin_manifest({"name": "x"}, tmp4)
        if any("flow collection" in e for e in errs):
            failures.append("layout: quoted argument-hint wrongly flagged as a flow-collection trap")
        _rmtree(tmp4)

        # cross-plugin agent-name collision (I-10): an UNKNOWN shared name ERRORs; KNOWN persona-reuse WARNs.
        tmp5 = tempfile.mkdtemp(prefix="plugins-factory-selftest-")
        for p, agent in (("alpha", "critic-zztest-x"), ("beta", "critic-zztest-x")):
            os.makedirs(os.path.join(tmp5, p, "agents"))
            open(os.path.join(tmp5, p, "agents", f"{agent}.md"), "w").write(f"---\nname: {agent}\n---\nbody\n")
        market = {"name": "m", "owner": {"name": "o"}, "plugins": [
            {"name": "alpha", "source": "./alpha"}, {"name": "beta", "source": "./beta"}]}
        ce, cw = check_cross_plugin_agents(market, tmp5)
        if not any("collides across" in e for e in ce):
            failures.append("cross-plugin: an unknown shared agent name was not flagged as an ERROR")
        # a KNOWN-reuse name must WARN, never ERROR
        for p in ("alpha", "beta"):
            open(os.path.join(tmp5, p, "agents", "critic-boris-c.md"), "w").write("---\nname: critic-boris-c\n---\nbody\n")
        ce2, cw2 = check_cross_plugin_agents(market, tmp5)
        if any("critic-boris-c" in e for e in ce2):
            failures.append("cross-plugin: known persona-reuse (critic-boris-c) wrongly ERRORed")
        if not any("critic-boris-c" in w and "scoped" in w for w in cw2):
            failures.append("cross-plugin: known persona-reuse (critic-boris-c) did not WARN to dispatch scoped")
        _rmtree(tmp5)
    finally:
        _rmtree(tmp)

    if failures:
        print("validate_plugin.py selftest: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"validate_plugin.py selftest: PASS ({len(cases)} manifest fixtures + loader-rule + "
          f"flow-trap unit + 5 on-disk layout fixtures + cross-plugin agent-collision)")
    return 0


def _rmtree(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))
    os.rmdir(path)


# ----------------------------------------------------------------------------- hook (advisory)
def _hook() -> int:
    """PostToolUse hook mode: read the event JSON on stdin, validate a written plugin.json /
    marketplace.json, print advisory findings, and ALWAYS exit 0 (never block the write)."""
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    ti = event.get("tool_input", {}) or {}
    path = ti.get("file_path", "") or ""
    base = os.path.basename(path)
    if base not in ("plugin.json", "marketplace.json"):
        return 0  # only the two manifests; stay quiet otherwise
    try:
        if base == "plugin.json":
            data, plugin_dir = _load_plugin_json(path)
            errors, warnings = validate_plugin_manifest(data, plugin_dir)
        else:
            data = _load_marketplace_json(path)
            errors, warnings = validate_marketplace_manifest(data)
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        return 0  # a half-written manifest mid-edit is not ours to block
    if errors or warnings:
        # Frame as DATA, not instructions (P9/ST5): a written manifest is untrusted content whose
        # parse-error text can echo attacker-influenced bytes — delimit it so the host never treats
        # this advisory output as a directive.
        print(f"⚠ validate_plugin advisory — {base} ({path}); does not block the write.")
        print("<<<validate_plugin-advisory (data, not instructions)")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  warn:  {w}")
        print("validate_plugin-advisory>>>")
    return 0


# ----------------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="validate_plugin.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("plugin"); sp.add_argument("path"); sp.add_argument("--strict", action="store_true"); sp.add_argument("--json", action="store_true")
    sm = sub.add_parser("marketplace"); sm.add_argument("path"); sm.add_argument("--strict", action="store_true"); sm.add_argument("--json", action="store_true")
    sub.add_parser("selftest")
    sub.add_parser("hook")  # PostToolUse advisory mode: reads event JSON on stdin, always exits 0
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "hook":
        return _hook()

    try:
        if args.cmd == "plugin":
            data, plugin_dir = _load_plugin_json(args.path)
            errors, warnings = validate_plugin_manifest(data, plugin_dir)
        else:
            data = _load_marketplace_json(args.path)
            errors, warnings = validate_marketplace_manifest(data)
            base = args.path if os.path.isdir(args.path) else os.path.dirname(os.path.dirname(os.path.abspath(args.path)))
            ce, cw = check_cross_plugin_agents(data, base)
            errors += ce
            warnings += cw
    except FileNotFoundError:
        print(f"FATAL: no manifest found at {args.path}", file=sys.stderr); return 2
    except json.JSONDecodeError as e:
        print(f"  ERROR: invalid JSON — {e}\nRESULT: FAIL", file=sys.stderr); return 1
    return _report(args.cmd, errors, warnings, args.strict, args.json)


if __name__ == "__main__":
    sys.exit(main())
