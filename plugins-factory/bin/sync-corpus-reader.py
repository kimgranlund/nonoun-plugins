#!/usr/bin/env python3
"""Sync the canonical corpus-reader into the plugins that vendor it.

The single source of truth is `plugins-factory/bin/corpus-reader/`. brand-forge and
product-forge ship their own *copy* (vendored), because cross-plugin symlinks do NOT
survive plugin install — installed plugins are copied into a version-keyed cache and
cannot reference files outside their own directory (plugin-architecture.md). So each
plugin carries the reader; this script keeps the copies byte-identical to the source.

    python3 bin/sync-corpus-reader.py            # copy source → each vendored target
    python3 bin/sync-corpus-reader.py --check    # exit 1 if any copy drifts (CI gate)

Vendored copies are GENERATED — never hand-edit one. Edit the source, then re-sync.
Generated/per-consumer files (the example corpus, the generated sitemap) are not copied.
"""
import hashlib
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent              # …/plugins-factory/bin
SRC = HERE / "corpus-reader"
ROOT = HERE.parent.parent                            # the marketplace root
TARGETS = [
    ROOT / "brand-forge" / "bin" / "corpus-reader",
    ROOT / "product-forge" / "bin" / "corpus-reader",
]

SKIP_DIRS = {"brand-corpus", "__pycache__", ".git"}   # example corpus is per-consumer
SKIP_FILES = {"sitemap.json", ".DS_Store"}            # sitemap.json is generated per-consumer


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


def main():
    check = "--check" in sys.argv
    if not SRC.is_dir():
        print(f"error: source not found: {SRC}", file=sys.stderr)
        sys.exit(2)
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

        if drift or sec:
            if drift:
                print("corpus-reader drift — run `python3 bin/sync-corpus-reader.py` to fix:")
                for d in drift:
                    print(f"  {d}")
            if sec:
                print("corpus-reader security wiring regressed (source):")
                for s in sec:
                    print(f"  {s}")
            print(f"RESULT: FAIL ({len(drift)} drift, {len(sec)} security)")
            sys.exit(1)
        print(
            f"RESULT: PASS (corpus-reader in sync across {len(TARGETS)} plugin(s); "
            f"{len(files)} files each; DOMPurify + SRI wiring intact)"
        )
        return

    for tgt in TARGETS:
        print(f"  synced → {tgt.relative_to(ROOT)} ({len(files)} files)")
    print(f"corpus-reader synced from {SRC.relative_to(ROOT)} into {len(TARGETS)} plugin(s)")


if __name__ == "__main__":
    main()
