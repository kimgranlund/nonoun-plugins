#!/usr/bin/env python3
"""Sync the canonical corpus-reader into the plugins that vendor it.

The single source of truth is `tools/corpus-reader/` — repo-root build tooling alongside
`gen-index.py`, relocated out of plugins-factory in D-14/I-11 (the reader serves the *maker*
plugins, not the judge). brand-forge and product-forge ship their own *copy* (vendored), because
cross-plugin symlinks do NOT survive plugin install — installed plugins are copied into a
version-keyed cache and cannot reference files outside their own directory (plugin-architecture.md).
So each plugin carries the reader; this script keeps the copies byte-identical to the source.

    python3 tools/sync-corpus-reader.py            # copy source → each vendored target
    python3 tools/sync-corpus-reader.py --check    # exit 1 if any copy drifts (CI gate)
    python3 tools/sync-corpus-reader.py --changelog "what changed"   # log a reader change
    python3 tools/sync-corpus-reader.py --fingerprint                # print the code fingerprint

Vendored copies are GENERATED — never hand-edit one. Edit the source, then re-sync.
Generated/per-consumer files (the example corpus, the generated sitemap) are not copied.

The reader ships its own README.md + CHANGELOG.md. The CHANGELOG cannot be allowed to go
stale: `--check` (a CI gate) computes a sha256 over the reader's behavior-bearing source
(its code, not the docs) and fails if it differs from the `<!-- source-fingerprint: … -->`
marker recorded by the last CHANGELOG entry. Any code change therefore trips CI until it is
logged with `--changelog "…"`, which prepends a dated entry and refreshes the marker.
"""
import datetime
import hashlib
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent              # …/tools
SRC = HERE / "corpus-reader"                         # …/tools/corpus-reader (the canonical source)
ROOT = HERE.parent                                   # the marketplace root (tools/ → root)
TARGETS = [
    ROOT / "brand-forge" / "bin" / "corpus-reader",
    ROOT / "product-forge" / "bin" / "corpus-reader",
]

SKIP_DIRS = {"brand-corpus", "__pycache__", ".git"}   # example corpus is per-consumer
SKIP_FILES = {"sitemap.json", ".DS_Store"}            # sitemap.json is generated per-consumer

CHANGELOG = SRC / "CHANGELOG.md"
CODE_SUFFIXES = {".html", ".css", ".js", ".py"}        # behavior-bearing source (not docs / sitemap)
FINGERPRINT_RE = re.compile(r"<!--\s*source-fingerprint:\s*([0-9a-f]{64})\s*-->")


def source_files():
    out = []
    for p in sorted(SRC.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(SRC)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        out.append(rel)
    return out


def _digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def source_fingerprint():
    """sha256 over the reader's behavior-bearing source — its code (.html/.css/.js/.py),
    NOT README, CHANGELOG, the generated sitemap, or the example corpus. Any code change
    moves it, so the CHANGELOG's recorded marker can be diffed against it to catch a
    changelog that fell behind the code."""
    h = hashlib.sha256()
    code = []
    for p in SRC.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(SRC)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() in CODE_SUFFIXES:
            code.append((rel.as_posix(), p))
    for relposix, p in sorted(code):
        h.update(relposix.encode("utf-8") + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def changelog_marker():
    if not CHANGELOG.is_file():
        return None
    m = FINGERPRINT_RE.search(CHANGELOG.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def add_changelog_entry(summary):
    """Prepend a dated entry to the reader's CHANGELOG.md and refresh the source-fingerprint
    marker so `--check` passes again. The maintained path for logging a reader change."""
    if not CHANGELOG.is_file():
        sys.exit(f"error: {CHANGELOG} not found — create it first (see the reader README)")
    text = CHANGELOG.read_text(encoding="utf-8")
    if not FINGERPRINT_RE.search(text):
        sys.exit("error: CHANGELOG.md has no <!-- source-fingerprint: … --> marker to refresh")
    fp = source_fingerprint()
    today = datetime.date.today().isoformat()
    text = FINGERPRINT_RE.sub(f"<!-- source-fingerprint: {fp} -->", text, count=1)
    entry = f"## {today} — {summary}\n\n"
    m = re.search(r"^## ", text, re.MULTILINE)
    text = (text[: m.start()] + entry + text[m.start():]) if m else (text.rstrip() + "\n\n" + entry)
    CHANGELOG.write_text(text, encoding="utf-8")
    print(f"logged: {today} — {summary}")
    print(f"fingerprint refreshed → {fp[:16]}…  (run --check to confirm)")


def main():
    argv = sys.argv[1:]
    if not SRC.is_dir():
        print(f"error: source not found: {SRC}", file=sys.stderr)
        sys.exit(2)
    if "--fingerprint" in argv:
        print(source_fingerprint())
        return
    if "--changelog" in argv:
        i = argv.index("--changelog")
        summary = (argv[i + 1] if i + 1 < len(argv) else "").strip()
        if not summary:
            sys.exit('usage: sync-corpus-reader.py --changelog "<summary of the change>"')
        add_changelog_entry(summary)
        return
    check = "--check" in argv
    files = source_files()
    drift = []

    for tgt in TARGETS:
        plugin = tgt.parent.parent.name
        for rel in files:
            s, d = SRC / rel, tgt / rel
            if check:
                if _digest(s) != _digest(d):
                    drift.append(f"{plugin}: out-of-date or missing  bin/corpus-reader/{rel}")
            else:
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
        # flag stale files present in a copy but no longer in the source
        if check and tgt.is_dir():
            wanted = set(files)
            for p in tgt.rglob("*"):
                if p.is_dir():
                    continue
                rel = p.relative_to(tgt)
                if any(part in SKIP_DIRS for part in rel.parts) or p.name in SKIP_FILES:
                    continue
                if rel not in wanted:
                    drift.append(f"{plugin}: stale (not in source)  bin/corpus-reader/{rel}")

    if check:
        # Security-wiring guard: the reader renders UNTRUSTED corpus markdown, so the
        # XSS hardening must never silently regress. (Copies == source after the drift
        # check, so asserting the source is sufficient.)
        sec = []
        idx = (SRC / "index.html").read_text(encoding="utf-8")
        page = (SRC / "lib" / "components" / "cr-ui-page.js").read_text(encoding="utf-8")
        if "purify.min.js" not in idx:
            sec.append("index.html: DOMPurify <script> missing")
        if idx.count('integrity="sha384-') < 6:
            sec.append("index.html: fewer than 6 Subresource-Integrity (sha384) tags")
        if "DOMPurify.sanitize" not in page:
            sec.append("lib/components/cr-ui-page.js: rendered markdown is not DOMPurify-sanitized (XSS hardening regressed)")

        # Freshness guard: the CHANGELOG must not fall behind the reader's code.
        stale = []
        marker = changelog_marker()
        if marker is None:
            stale.append("CHANGELOG.md missing or has no <!-- source-fingerprint: … --> marker")
        elif marker != source_fingerprint():
            stale.append('reader code changed since the last CHANGELOG entry — log it: '
                         '`python3 tools/sync-corpus-reader.py --changelog "<summary>"`')

        if drift or sec or stale:
            if drift:
                print("corpus-reader drift — run `python3 tools/sync-corpus-reader.py` to fix:")
                for d in drift:
                    print(f"  {d}")
            if sec:
                print("corpus-reader security wiring regressed (source):")
                for s in sec:
                    print(f"  {s}")
            if stale:
                print("corpus-reader CHANGELOG is stale:")
                for s in stale:
                    print(f"  {s}")
            print(f"RESULT: FAIL ({len(drift)} drift, {len(sec)} security, {len(stale)} stale)")
            sys.exit(1)
        print(
            f"RESULT: PASS (corpus-reader in sync across {len(TARGETS)} plugin(s); "
            f"{len(files)} files each; DOMPurify + SRI wiring intact; CHANGELOG current)"
        )
        return

    for tgt in TARGETS:
        print(f"  synced → {tgt.relative_to(ROOT)} ({len(files)} files)")
    print(f"corpus-reader synced from {SRC.relative_to(ROOT)} into {len(TARGETS)} plugin(s)")


if __name__ == "__main__":
    main()
