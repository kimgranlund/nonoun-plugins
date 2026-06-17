#!/usr/bin/env python3
"""check-bake-safety.py — assert a baked single-file corpus-reader is XSS-safe and integrity-pinned.

`build-sitemap.py --bake` inlines a corpus's markdown + the reader's JS into ONE self-contained
`reader.html` that runs on `file://`. Inlining untrusted markdown into a `<script>` data island and a
`<script type="module">` bundle is exactly where a script-context escape (`</script>`) or a live
`<script>alert(...)>` would break out — so the bake's safety is load-bearing and must be gated.

This was a 495-char inline `python3 -c` one-liner in ci.yml — unreadable in a diff and untestable in
isolation (the 2026-06-11 audit's P1-3). Extracted here as a named gate with one message per check and
a `selftest` that proves it FAILS on an injected escape, per PLAN.md's "new gates prove themselves".

Six checks over a baked reader.html:
  C1  the corpus markdown was inlined            (`window.CORPUS_FILES = {`)
  C2  the data island has no `</script>` escape  (untrusted content can't break out of the script)
  C3  the module bundle has no `</script>` escape
  C4  the CDN libs keep Subresource Integrity     (>= 6 `integrity="sha384-`)
  C5  DOMPurify is wired                           (`purify.min.js`)
  C6  no live injected script                      (no `<script>alert(`)

Usage:
  check-bake-safety.py <reader.html> [--emit-bundle <path>]   # validate; optionally write the module bundle for `node --check`
  check-bake-safety.py selftest                                # prove it passes a safe bake and fails an injected one
Stdlib only (Python 3.8+).
"""
import re
import sys

_DATA_RE = re.compile(r"<script>\n(window\.CORPUS = .*?)\n</script>", re.S)
_BUNDLE_RE = re.compile(r'<script type="module">\n(.*?)\n</script>', re.S)


def check(html):
    """Return (ok, findings, bundle). `findings` is a list of (id, message) for each FAILED check;
    `bundle` is the extracted module JS (or None) for an optional downstream `node --check`."""
    findings = []
    data_m = _DATA_RE.search(html)
    bundle_m = _BUNDLE_RE.search(html)
    data = data_m.group(1) if data_m else None
    bundle = bundle_m.group(1) if bundle_m else None

    if "window.CORPUS_FILES = {" not in html:
        findings.append(("C1", "corpus markdown not inlined (no `window.CORPUS_FILES = {`) — not a baked single file?"))
    if data is None:
        findings.append(("C2", "could not find the inlined data island (`<script>\\nwindow.CORPUS = …\\n</script>`)"))
    elif "</script>" in data:
        findings.append(("C2", "the data island contains a `</script>` — untrusted content can break out of the script context"))
    if bundle is None:
        findings.append(("C3", "could not find the module bundle (`<script type=\"module\">…</script>`)"))
    elif "</script>" in bundle:
        findings.append(("C3", "the module bundle contains a `</script>` script-context escape"))
    sri = html.count('integrity="sha384-')
    if sri < 6:
        findings.append(("C4", f"too few Subresource Integrity hashes ({sri} < 6) — CDN libs not pinned"))
    if "purify.min.js" not in html:
        findings.append(("C5", "DOMPurify (`purify.min.js`) is not wired — untrusted markdown would render unsanitized"))
    if "<script>alert(" in html:
        findings.append(("C6", "a live `<script>alert(` is present — an injected script survived the bake"))
    return (not findings, findings, bundle)


def _run(path, emit):
    try:
        html = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"  cannot read {path}: {e}")
        print("RESULT: FAIL")
        return 1
    ok, findings, bundle = check(html)
    for cid, msg in findings:
        print(f"  [{cid}] {msg}")
    if ok and emit and bundle is not None:
        open(emit, "w", encoding="utf-8").write(bundle)
        print(f"  wrote module bundle → {emit} (for `node --check`)")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} ({len(findings)} safety gap(s)) — {path}")
    return 0 if ok else 1


# A minimal safe baked reader (matches build-sitemap.py --bake's structure) for the selftest.
_SAFE = (
    "<!doctype html><head>\n"
    + "".join(f'<link rel="stylesheet" href="https://cdn/{i}.css" integrity="sha384-AAA{i}" crossorigin>\n' for i in range(6))
    + '<script src="https://cdn/purify.min.js" integrity="sha384-PUR" crossorigin></script>\n'
    "</head><body>\n"
    "<script>\n"
    'window.CORPUS = {"a":1};\n'
    'window.CORPUS_FILES = {"a.md":"hello world"};\n'
    "</script>\n"
    '<script type="module">\n'
    "const x = 1; export {};\n"
    "</script>\n"
    "</body>\n"
)


def selftest():
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    # 1. a safe bake passes
    ok, findings, bundle = check(_SAFE)
    expect(ok, f"safe bake was flagged: {findings}")
    expect(bundle is not None and "const x = 1" in bundle, "module bundle not extracted from a safe bake")
    # 2. an injected `</script>` in the inlined data is caught (the core XSS escape)
    ok, findings, _ = check(_SAFE.replace('"hello world"', '"hi</script><script>alert(1)//"'))
    expect(not ok and any(c == "C2" for c, _ in findings), "did NOT catch a `</script>` escape in the data island")
    # 3. a live injected alert is caught
    ok, findings, _ = check(_SAFE + "<script>alert(document.cookie)</script>")
    expect(not ok and any(c == "C6" for c, _ in findings), "did NOT catch a live `<script>alert(`")
    # 4. stripped SRI is caught
    ok, findings, _ = check(_SAFE.replace('integrity="sha384-AAA', 'data-x="'))
    expect(not ok and any(c == "C4" for c, _ in findings), "did NOT catch stripped SRI hashes")
    # 5. removed DOMPurify is caught
    ok, findings, _ = check(_SAFE.replace("purify.min.js", "harmless.js"))
    expect(not ok and any(c == "C5" for c, _ in findings), "did NOT catch a missing DOMPurify")

    if fails:
        sys.stderr.write("check-bake-safety selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("check-bake-safety selftest: OK (passes a safe bake; catches </script> escape, live alert, stripped SRI, missing DOMPurify)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if not argv:
        print("usage: check-bake-safety.py <reader.html> [--emit-bundle <path>]  |  selftest", file=sys.stderr)
        return 2
    emit = None
    if "--emit-bundle" in argv:
        i = argv.index("--emit-bundle")
        emit = argv[i + 1] if i + 1 < len(argv) else None
    return _run(argv[0], emit)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
