#!/usr/bin/env python3
"""check-methods.py — the method-card schema gate for product-forge.

Every methodology playbook (a `*.md` under any `skills/<skill>/references/methods/`) is a runnable
process, and the plugin routes + scores it from a structured "method card" in its frontmatter. This
gate turns that card into a checked contract. Fields fall into two groups:

  TYPED (validated):
  - `phase`   — must be one of the seven process-spine phases;
  - `cadence` — must be one of {one-off, per-decision, recurring, continuous};
  - `domains` — must list taxonomy domains in 1–12;
  - `produces`— must be present AND non-empty (the artifact the method yields);
  - `rubric`  — must resolve to a real rubric in product-evaluate (the maker-judge link);
  - `de_risks`— OPTIONAL; if present, every value must be one of Marty C.'s four risks
                {value, usability, feasibility, viability}. (Methods that produce a decision or an
                artifact rather than de-risking a build-risk simply omit it.)

  DESCRIPTIVE (presence-checked only — free text by design):
  - `method` (a kebab id), `timebox`, `participants`, `inputs`.

Provenance fields (date / coverage / primary_sources) are enforced separately by check-sourcing.py.
The method-file scope is DERIVED from the skill tree (not a hard-coded list), so a new skill's
playbooks are covered automatically.

Usage:
  check-methods.py <plugin-dir>   # exit 0 if all cards valid, 1 if any gap, 2 on bad invocation
  check-methods.py selftest
Stdlib only (Python 3.8+).
"""
import os
import re
import sys

PHASES = {"discover", "frame", "decide", "structure", "make", "measure", "govern"}
CADENCES = {"one-off", "per-decision", "recurring", "continuous"}
RISKS = {"value", "usability", "feasibility", "viability"}
REQUIRED = ("method", "phase", "domains", "timebox", "cadence", "participants", "inputs", "produces", "rubric")


def _frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else None


def _method_files(root):
    """Every playbook: *.md under any skills/<skill>/references/methods/."""
    skills_root = os.path.join(root, "skills")
    out = []
    if not os.path.isdir(skills_root):
        return out
    for skill in sorted(os.listdir(skills_root)):
        mdir = os.path.join(skills_root, skill, "references", "methods")
        for dp, _dirs, files in os.walk(mdir):
            for fn in sorted(files):
                if fn.endswith(".md"):
                    out.append(os.path.join(dp, fn))
    return out


def _inline(fm, key):
    """The inline value after `key:` (empty string for a block-list field; None if the key is absent)."""
    m = re.search(rf"(?m)^{key}\s*:\s*(.*)$", fm)
    return m.group(1).strip() if m else None


def check(root):
    root = os.path.abspath(root)
    findings = []
    rubric_dir = os.path.join(root, "skills", "product-evaluate", "references", "rubrics")
    for fp in _method_files(root):
        rel = os.path.relpath(fp, root)
        fm = _frontmatter(open(fp, encoding="utf-8", errors="replace").read())
        if fm is None:
            findings.append((rel, "no YAML frontmatter / method card"))
            continue
        missing = [k for k in REQUIRED if not re.search(rf"(?m)^{k}\s*:", fm)]
        if missing:
            findings.append((rel, "missing card field(s): " + ", ".join(missing)))
        phase = _inline(fm, "phase")
        if phase and phase not in PHASES:
            findings.append((rel, f"phase '{phase}' not one of {sorted(PHASES)}"))
        cadence = _inline(fm, "cadence")
        if cadence and cadence not in CADENCES:
            findings.append((rel, f"cadence '{cadence}' not one of {sorted(CADENCES)}"))
        domains = _inline(fm, "domains")
        if domains:
            nums = re.findall(r"\d+", domains)
            if not nums:
                findings.append((rel, "domains must list taxonomy domains in 1-12"))
            elif any(not (1 <= int(n) <= 12) for n in nums):
                findings.append((rel, f"domains out of range 1-12: {domains}"))
        produces = _inline(fm, "produces")
        if produces is not None and not produces.strip().strip("\"'").strip():
            findings.append((rel, "produces is present but empty"))
        de = _inline(fm, "de_risks")
        if de:  # optional; validate only when present and non-empty
            tokens = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z-]*", de)]
            bad = [t for t in tokens if t not in RISKS]
            if bad:
                findings.append((rel, f"de_risks has non-risk value(s) {bad}; allowed: {sorted(RISKS)} (or omit)"))
        rubric = _inline(fm, "rubric")
        if rubric:
            rubric = rubric.strip().strip("\"'")
            if not os.path.isfile(os.path.join(rubric_dir, rubric + ".md")):
                findings.append((rel, f"rubric '{rubric}' does not resolve in product-evaluate"))
    return findings


def _selftest():
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        rb = os.path.join(d, "skills", "product-evaluate", "references", "rubrics")
        os.makedirs(rb)
        open(os.path.join(rb, "rubric-architecture.md"), "w").write("# Rubric — Architecture\n")
        mdir = os.path.join(d, "skills", "product-architecture", "references", "methods")
        os.makedirs(mdir)
        # good: de_risks present-and-valid; a sibling with de_risks omitted must also pass
        open(os.path.join(mdir, "good.md"), "w").write(
            "---\ndate: 2026-06-03\ncoverage: foundational\nprimary_sources:\n  - X\n"
            "method: good\nphase: structure\ndomains: [2, 4]\ntimebox: \"1 day\"\ncadence: one-off\n"
            "participants: [pm, designer]\ninputs: [a goal]\nproduces: a map\nde_risks: [usability]\n"
            "rubric: rubric-architecture\n---\n# Good\n")
        open(os.path.join(mdir, "good-no-derisk.md"), "w").write(
            "---\ndate: 2026-06-03\ncoverage: foundational\nprimary_sources:\n  - X\n"
            "method: good2\nphase: make\ndomains: [3]\ntimebox: \"hours\"\ncadence: recurring\n"
            "participants: [researcher]\ninputs: [a prototype]\nproduces: findings\nrubric: rubric-architecture\n---\n# Good2\n")
        # bad: phase invalid, cadence invalid, domains out of range, empty produces, de_risks non-risk,
        #      rubric missing, and a missing required field (no `timebox`)
        open(os.path.join(mdir, "bad.md"), "w").write(
            "---\nmethod: bad\nphase: brainstorm\ndomains: [13]\ncadence: banana\n"
            "participants: [pm]\ninputs: [x]\nproduces: \"\"\nde_risks: [purple]\nrubric: rubric-missing\n---\n# Bad\n")
        whys_by = {}
        for r, w in check(d):
            whys_by.setdefault(r, []).append(w)
        for clean in ("skills/product-architecture/references/methods/good.md",
                      "skills/product-architecture/references/methods/good-no-derisk.md"):
            if clean in whys_by:
                ok = False
                print(f"selftest: false-flagged {clean}: {whys_by[clean]}", file=sys.stderr)
        badw = " | ".join(whys_by.get("skills/product-architecture/references/methods/bad.md", []))
        for needle in ("phase", "cadence", "out of range", "produces is present but empty",
                       "non-risk value", "does not resolve", "missing card field"):
            if needle not in badw:
                ok = False
                print(f"selftest: bad.md missing expected finding '{needle}' (got: {badw})", file=sys.stderr)
    print("selftest: PASS" if ok else "selftest: FAIL")
    return 0 if ok else 1


def main(argv):
    if argv and argv[0] == "selftest":
        return _selftest()
    args = [a for a in argv if not a.startswith("-")]
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("usage: check-methods.py <plugin-dir>", file=sys.stderr)
        return 2
    findings = check(args[0])
    for rel, why in findings:
        print(f"  {rel}: {why}")
    print(f"RESULT: {'PASS' if not findings else 'FAIL'} ({len(findings)} method-card issue(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
