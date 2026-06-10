#!/usr/bin/env python3
"""reference-lint.py — fail on internal markdown references that don't resolve on disk.

Catches the regression class a manifest validator can't see: a doc/command path that points at a
renamed or absent file. This is the gate that would have caught the two stale-reference regressions
the 2026-06-02 build-time red-team found by hand — `scripts/validate_plugin.py` after the tooling
moved to `bin/`, and `eval-as-*.md` after the critic personas became `agents/critic-*.md`.

It scans the LIVE component/reference docs (skips narrative history: reviews/, ROADMAP, CHANGELOG,
and any git-ignored content — e.g. bundled example corpora that never ship) and, for each backtick-
or link-wrapped token that looks like an INTERNAL file reference, checks it resolves relative to the
plugin root, the file's own dir, or ${CLAUDE_PLUGIN_ROOT}. Illustrative example paths, globs,
placeholders, and URLs are skipped, so a clean tree lints clean.

A reference whose TARGET is deliberately git-ignored (e.g. the obscured-critic
`agents/.name-map.md`) is exempt from the resolve requirement: such files are by design absent
from a fresh checkout, so requiring them on disk would make the gate green locally and
permanently red in CI. The exemption only applies when `git check-ignore` confirms the path is
ignored — outside a git context the strict behavior is unchanged.

Usage:
  reference-lint.py <plugin-dir> [--json]
Exit 0 = every internal reference resolves · 1 = unresolved reference(s) · 2 = bad invocation.
Stdlib only (Python 3.8+).
"""
import json
import os
import re
import subprocess
import sys

EXTS = (".md", ".py", ".json")
PLUGIN_DIRS = {"references", "agents", "skills", "commands", "hooks", "bin", "evals"}
PLUGIN_ROOT_VAR = "${CLAUDE_PLUGIN_ROOT}/"
# Pedagogical examples in rubric/foundation prose — not real internal refs.
ILLUSTRATIVE_STEMS = {"foo", "bar", "baz", "qux", "example", "example-a", "example-b",
                      "sample", "my-plugin", "my-skill", "some-skill", "other-skill"}
ILLUSTRATIVE_DIRS = {"shared-types", "core-types", "shared-utils", "examples",
                     "my-plugin", "plugins", "my-marketplace"}

# Hard rules — always flagged, even inside a code fence, because they are known-bad for THIS plugin.
HARD_RULES = [
    (re.compile(r"scripts/[\w./-]+\.py"),
     "path under scripts/ — this plugin's executables ship in bin/"),
    (re.compile(r"eval-as-\w+\.md"),
     "eval-as-*.md — the critic personas are now agents/critic-*.md"),
    (re.compile(r"skills-studio/references/"),
     "cross-plugin skills-studio/references/ path — co-locate or point at the bundled copy"),
]

TOKEN_RE = re.compile(r"`([^`\n]+)`|\]\(([^)\s]+)\)")  # `code spans` and [md](links)
SKIP_BASENAMES = {"ROADMAP.md", "CHANGELOG.md"}        # narrative — may quote bad paths as examples


def _candidate(tok):
    """Normalize a token; return a path string if it looks like an internal file ref, else None."""
    t = tok.strip().strip("'\"")
    t = t.split("#", 1)[0]                     # drop #anchor
    t = re.sub(r":\d+(?:-\d+)?$", "", t)       # drop :line / :line-range suffix
    if not t.endswith(EXTS):
        return None
    if "://" in t or any(c in t for c in "*<>[] ") or t.startswith("/") or t.startswith("~"):
        return None                            # URL, glob, placeholder, whitespace, absolute
    probe = t[len(PLUGIN_ROOT_VAR):] if t.startswith(PLUGIN_ROOT_VAR) else t
    if probe.startswith("${"):                 # e.g. ${CLAUDE_PLUGIN_DATA}/...
        return None
    segs = probe.lstrip("./").split("/")
    stem = os.path.splitext(segs[-1])[0]
    if stem in ILLUSTRATIVE_STEMS or any(s in ILLUSTRATIVE_DIRS for s in segs):
        return None                            # pedagogical example, not a real ref
    if probe.startswith("./") or probe.startswith("../"):
        return t                               # file-dir-relative
    return t if segs[0] in PLUGIN_DIRS else None  # first segment is a real plugin dir


def _ref_paths(tok, plugin_root, file_dir):
    """The absolute path(s) a token may denote — plugin-root-relative OR skill-local."""
    if tok.startswith(PLUGIN_ROOT_VAR):
        rel, bases = tok[len(PLUGIN_ROOT_VAR):], [plugin_root]
    elif tok.startswith("./") or tok.startswith("../"):
        rel, bases = tok, [file_dir]
    else:
        rel, bases = tok, [plugin_root, file_dir]
    return [os.path.normpath(os.path.join(b, rel)) for b in bases]


def _resolves(tok, plugin_root, file_dir):
    """A bare `dir/file` may be plugin-root-relative OR skill-local — accept either."""
    return any(os.path.exists(p) for p in _ref_paths(tok, plugin_root, file_dir))


def _deliberately_ignored(plugin_root, paths):
    """True when git confirms any candidate path is excluded by ignore rules — the tree
    deliberately omits it (works for absent paths: check-ignore evaluates rules, not the fs).
    False outside a git context, so non-repo lints keep the strict behavior."""
    for p in paths:
        try:
            r = subprocess.run(["git", "-C", plugin_root, "check-ignore", "-q", "--", p],
                               capture_output=True, timeout=15)
            if r.returncode == 0:
                return True
        except Exception:
            return False
    return False


def _git_ignored(plugin_root):
    """(ignored_dirs, ignored_files) as abs paths under plugin_root.

    Git-ignored content (e.g. a bundled example corpus) never ships and is absent
    in CI, so it must not gate. Empty sets when git is unavailable or this is not a
    repo — the linter then scans everything, as before.
    """
    dirs, files = set(), set()
    try:
        out = subprocess.run(
            ["git", "-C", plugin_root, "ls-files", "--others", "--ignored",
             "--exclude-standard", "--directory"],
            capture_output=True, text=True, check=True, timeout=15).stdout
    except Exception:
        return dirs, files
    for line in out.splitlines():
        entry = line.strip()
        if not entry:
            continue
        ap = os.path.normpath(os.path.join(plugin_root, entry))
        (dirs if entry.endswith("/") else files).add(ap)
    return dirs, files


def lint(plugin_root):
    plugin_root = os.path.abspath(plugin_root)
    ignored_dirs, ignored_files = _git_ignored(plugin_root)
    findings = []
    for dirpath, dirnames, files in os.walk(plugin_root):
        dirnames[:] = [d for d in dirnames if d not in ("reviews", ".git")
                       and os.path.normpath(os.path.join(dirpath, d)) not in ignored_dirs]
        for fn in sorted(files):
            if not fn.endswith(".md") or fn in SKIP_BASENAMES:
                continue
            fp = os.path.join(dirpath, fn)
            if os.path.normpath(fp) in ignored_files:
                continue
            rel = os.path.relpath(fp, plugin_root)
            file_dir = os.path.dirname(fp)
            in_fence = False
            for i, line in enumerate(open(fp, encoding="utf-8", errors="replace"), 1):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                seen = set()
                for rule, why in HARD_RULES:          # hard rules: always, even in a fence
                    for m in rule.finditer(line):
                        key = m.group(0)
                        if key not in seen:
                            seen.add(key)
                            findings.append((rel, i, key, why))
                if in_fence:
                    continue
                for m in TOKEN_RE.finditer(line):     # general resolve check: live prose only
                    raw = m.group(1) or m.group(2)
                    cand = _candidate(raw)
                    if cand and cand not in seen and not _resolves(cand, plugin_root, file_dir):
                        seen.add(cand)
                        if _deliberately_ignored(plugin_root, _ref_paths(cand, plugin_root, file_dir)):
                            continue  # by-design-local target (git-ignored) — absent in a fresh checkout
                        findings.append((rel, i, cand, "does not resolve on disk"))
    return findings


def main(argv):
    args = [a for a in argv if not a.startswith("-")]
    as_json = "--json" in argv
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("usage: reference-lint.py <plugin-dir> [--json]", file=sys.stderr)
        return 2
    findings = lint(args[0])
    if as_json:
        print(json.dumps({"ok": not findings,
                          "findings": [{"file": f, "line": ln, "ref": r, "why": w}
                                       for f, ln, r, w in findings]}, indent=2))
    else:
        for f, ln, r, w in findings:
            print(f"  {f}:{ln}: `{r}` — {w}")
        print(f"RESULT: {'PASS' if not findings else 'FAIL'} "
              f"({len(findings)} unresolved reference(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
