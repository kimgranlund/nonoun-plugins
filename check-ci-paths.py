#!/usr/bin/env python3
"""check-ci-paths.py — every repo path referenced by .github/workflows/ci.yml must exist.

The 2026-06-05 → 06-10 outage (docs/ISSUES.md R-1) included workflow steps invoking
selftests of plugins that had moved out of the repo — nothing gated the workflow's own
path references, so the stale steps sat red for days. This check extracts path-shaped
tokens from the workflow (with env vars like `$PF` resolved from the `env:` block),
skips /tmp, globs' filenames, and URLs, and fails if any referenced file is absent.

A token is checked when it contains a `/` and ends in a source/doc suffix, OR when it
follows a `python3` invocation (which also catches the extensionless bins the real
outage referenced — `…/forge-lint`, `…/adia-scaffold`). It passes if it exists relative
to the repo root OR any env-var directory (covers `cd "$PF" && …`). For glob tokens only
the directory part is asserted.

Usage:  check-ci-paths.py [workflow.yml]   # default .github/workflows/ci.yml
        check-ci-paths.py selftest
Exit 0 = all referenced paths exist · 1 = missing path(s) · 2 = bad invocation.
Stdlib only (Python 3.8+).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WF = os.path.join(".github", "workflows", "ci.yml")
SUFFIXES = (".py", ".md", ".json", ".yml", ".yaml", ".js", ".css", ".html", ".sh")
ENV_RE = re.compile(r"(?m)^\s+([A-Z][A-Z0-9_]*):\s*([\w./-]+)\s*$")
TOKEN_SPLIT = re.compile(r"[\s;|&()<>]+")


def referenced_paths(text):
    """Path-shaped tokens from the workflow text, env-substituted. Returns (token, candidates)."""
    env = dict(ENV_RE.findall(text))
    out = []

    def add(tok):
        if not tok or "/" not in tok or "://" in tok or "@" in tok:
            return
        for k, v in env.items():
            tok = tok.replace("${%s}" % k, v).replace("$%s" % k, v)
        if tok.startswith(("/", "~", "-")) or "$" in tok:  # /tmp, absolute, flags, unresolved vars
            return
        if "*" in tok:                                      # glob: assert the directory part
            tok = os.path.dirname(tok.split("*", 1)[0])
            if not tok:
                return
        out.append((tok, [tok] + [os.path.join(v, tok) for v in env.values()]))

    for line in text.splitlines():
        # quotes are shell syntax, never path content — drop them everywhere first
        toks = [t for t in TOKEN_SPLIT.split(line.replace('"', "").replace("'", "")) if t]
        for i, tok in enumerate(toks):
            if tok in ("-c", "-m") and i and toks[i - 1].startswith("python"):
                break                                       # the rest of the line is inline code, not paths
            if tok.startswith("../"):
                continue                                    # cwd-relative parent path — not repo-checkable
            if "/" in tok and (tok.endswith(SUFFIXES) or "*" in tok):
                add(tok)
            elif tok == "python3" and i + 1 < len(toks):
                add(toks[i + 1])                            # the invoked script — incl. extensionless bins
    return out


def _created_dirs(text):
    """Dirs the workflow creates itself (`mkdir [-p] <dir>`) — paths written under these are build outputs
    (e.g. `_site/index.html` after `mkdir -p _site`), not repo inputs, so they must not be required to exist."""
    dirs = set()
    for m in re.finditer(r"mkdir\s+(?:-p\s+)?([^\s;|&]+)", text):
        d = m.group(1).strip().strip("\"'").rstrip("/")
        if d and not d.startswith(("/", "-", "$")):
            dirs.add(d)
    return dirs


def check(wf_path):
    text = open(wf_path, encoding="utf-8").read()
    created = _created_dirs(text)
    missing = []
    for raw, candidates in referenced_paths(text):
        if any(raw == d or raw.startswith(d + "/") for d in created):
            continue                                         # a path under a dir the workflow mkdir's — a build output
        if not any(os.path.exists(os.path.join(ROOT, c)) for c in candidates):
            missing.append((raw, candidates[0]))
    return missing


def _selftest():
    ok = True
    fake = (
        "    env:\n      G: tools/gates\n"
        "      - run: python3 \"$G/validate_plugin.py\" selftest\n"
        "      - run: python3 gone-plugin/bin/tool.py selftest\n"
        "      - run: python3 gone-plugin/bin/some-lint selftest\n"        # extensionless — the R-1 shape
        "      - run: python3 product-forge/bin/product-lint selftest\n"  # extensionless, exists
        "      - run: python3 tools/sync-gates.py --check\n"
        "      - run: test -f /tmp/demo/site/lib/sitemap.json\n"
        "      - run: for f in tools/corpus-reader/lib/components/*.js; do true; done\n"
        "      - run: python3 -c \"assert x == 'gone-dir/literal.css'\"\n"  # inline code, not a path
        "      - run: test -f ../outside.css\n"                             # parent-relative — skipped
    )
    refs = referenced_paths(fake)
    flagged = {cands[0] for _, cands in
               [r for r in refs if not any(os.path.exists(os.path.join(ROOT, c)) for c in r[1])]}
    for must_flag in ("gone-plugin/bin/tool.py", "gone-plugin/bin/some-lint"):
        if must_flag not in flagged:
            ok = False
            print(f"selftest: failed to flag {must_flag}", file=sys.stderr)
    for must_pass in ("validate_plugin", "product-lint", "sync-gates", "components",
                      "literal.css", "outside.css"):
        if any(must_pass in f for f in flagged):
            ok = False
            print(f"selftest: false-flagged something matching {must_pass!r}: {flagged}", file=sys.stderr)
    if any("/tmp" in t for t, _ in refs):
        ok = False
        print("selftest: /tmp paths must be skipped", file=sys.stderr)
    print("selftest: PASS" if ok else "selftest: FAIL")
    return 0 if ok else 1


def main(argv):
    if argv and argv[0] == "selftest":
        return _selftest()
    if argv:
        wfs = [argv[0]]
    else:
        wfdir = os.path.join(ROOT, ".github", "workflows")
        wfs = sorted(os.path.join(".github", "workflows", f) for f in os.listdir(wfdir)
                     if f.endswith((".yml", ".yaml"))) if os.path.isdir(wfdir) else []
        if not wfs:
            print("check-ci-paths: no workflow files under .github/workflows/", file=sys.stderr)
            return 2
    total = 0
    for wf in wfs:
        wf_abs = os.path.join(ROOT, wf)
        if not os.path.isfile(wf_abs):
            print(f"usage: check-ci-paths.py [workflow.yml] — not found: {wf}", file=sys.stderr)
            return 2
        for raw, resolved in check(wf_abs):
            print(f"  {raw} → {resolved} — referenced by {wf} but absent from the tree")
            total += 1
    print(f"RESULT: {'PASS' if not total else 'FAIL'} ({total} missing path(s) across {len(wfs)} workflow(s))")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
