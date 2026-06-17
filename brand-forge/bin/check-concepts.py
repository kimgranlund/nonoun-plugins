#!/usr/bin/env python3
"""check-concepts.py — gate retired seat-vocabulary out of brand-forge's seat-defining surfaces.

The v0.4 reframe renamed the Muse seat (**provocateur → aspirational attractor**) and its job
(**"widen the options" → "supply the gravitational pull"**). That rename leaked the retired terms
into three docs because nothing gated a concept-rename the way `reference-lint` gates broken links.
This mechanizes the discipline the plugin's own thesis demands ("structure is mechanized; taste is
not"): a retired seat-term in a seat-defining surface (`agents/` · `skills/` · `commands/`) is a CI
failure.

Precision matters more than recall here. The retired terms are the seat NAME and seat JOB that
changed — NOT "provocation"/"provoke", which stay valid: a *provocation* is one shape the Muse's
gravitational pull can take (`agents/brand-muse.md`), and critics legitimately ask whether strategy
"provokes" work. Flagging the bare verb would false-positive on living vocabulary, so the gate keys
on the precise retired phrases, which have ~zero legitimate use.

Not scanned: `CHANGELOG.md` and `reviews/` (they RECORD the rename — history must name the old term),
and the gitignored `agents/.name-map.md` (critic bios). These live outside the seat surfaces anyway.

Usage:
  check-concepts.py [<brand-forge-dir>]   # default: the plugin this script lives in
  check-concepts.py selftest
Exit 0 = clean; 1 = a retired term found; 2 = usage error. Stdlib only, Python 3.8+.
"""
import os
import re
import sys

# (human label, pattern) — high-signal retired SEAT vocabulary, not the still-valid "provocation".
RETIRED = [
    ("`provocateur` — retired seat name (now: the aspirational attractor)",
     re.compile(r"provocateur", re.I)),
    ("`widen the options` — retired seat job (now: supply the gravitational pull)",
     re.compile(r"widen(?:s|ing)?\s+(?:the\s+)?options?\b", re.I)),
]
SCAN_DIRS = ("agents", "skills", "commands")          # the seat-defining surfaces
SKIP_RX = re.compile(r"\.name-map\.md$")              # gitignored critic bios (the only skip inside scope)


def scan(root):
    """Return a list of (rel_path, line_no, label, snippet) for every retired term found."""
    findings = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for fn in sorted(filenames):
                if not fn.endswith(".md") or SKIP_RX.search(fn):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                with open(full, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        for label, pat in RETIRED:
                            if pat.search(line):
                                findings.append((rel, i, label, line.strip()[:100]))
    return findings


def run(root):
    findings = scan(root)
    if findings:
        print("RESULT: FAIL — retired seat-vocabulary found (a concept-rename leaked; see ROADMAP):",
              file=sys.stderr)
        for rel, i, label, snip in findings:
            print(f"  {rel}:{i}  {label}\n      …{snip}", file=sys.stderr)
        return 1
    print("RESULT: PASS (no retired seat-vocabulary in agents/ · skills/ · commands/)")
    return 0


def selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as tmp:
        agents = os.path.join(tmp, "agents")
        os.makedirs(agents)
        # clean file using the CURRENT vocabulary, incl. the still-valid "a provocation"
        with open(os.path.join(agents, "brand-muse.md"), "w") as f:
            f.write("The aspirational attractor supplies the gravitational pull. A provocation is one "
                    "shape that pull can take; a critic may ask whether the work provokes anything.\n")
        expect(scan(tmp) == [], f"clean current vocabulary flagged (false positive): {scan(tmp)}")

        # a retired seat NAME re-introduced
        with open(os.path.join(agents, "bad-name.md"), "w") as f:
            f.write("The Muse is the studio's provocateur.\n")
        expect(any("provocateur" in lbl for _, _, lbl, _ in scan(tmp)), "missed retired 'provocateur'")

        # a retired seat JOB re-introduced
        with open(os.path.join(agents, "bad-job.md"), "w") as f:
            f.write("Its job is to widen the options the team considers.\n")
        expect(any("widen the options" in lbl for _, _, lbl, _ in scan(tmp)), "missed retired 'widen the options'")

        # the gitignored name-map is skipped even with a retired term
        with open(os.path.join(agents, ".name-map.md"), "w") as f:
            f.write("bio: known as a provocateur in the industry.\n")
        nm = [f for f in scan(tmp) if f[0].endswith(".name-map.md")]
        expect(nm == [], f".name-map.md was scanned (should be skipped): {nm}")

    if fails:
        sys.stderr.write("check-concepts selftest: FAIL\n")
        for m in fails:
            sys.stderr.write(f"  - {m}\n")
        return 1
    print("check-concepts selftest: OK (catches retired provocateur/widen-the-options; "
          "leaves the still-valid 'provocation'/'provokes' alone; skips the gitignored name-map)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if len(argv) > 1:
        print("usage: check-concepts.py [<brand-forge-dir>] | selftest", file=sys.stderr)
        return 2
    root = argv[0] if argv else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return run(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
