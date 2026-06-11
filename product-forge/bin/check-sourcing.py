#!/usr/bin/env python3
"""check-sourcing.py — the provenance gate for product-forge.

product-forge's whole value proposition is GROUNDED authority, and its council renders named —
often living — practitioners. A fabricated quote or an unsourced claim is the worst failure mode.
This gate turns "everything is sourced" from author discipline into a verifiable property:

  - every knowledge-library reference — any `*.md` under `skills/<skill>/references/`, EXCEPT the
    rubric files under a `rubrics/` dir (scored references that intentionally carry no frontmatter) —
    MUST carry YAML frontmatter with `date`, `coverage`, and `primary_sources`;
  - every council critic (`agents/critic-*.md`) MUST be sourced — EITHER by carrying an inline source
    signal (an explicit Sourcing block, a URL, or a year citation) OR — because the critics' real
    identities, bios, and sources are deliberately obscured out of the repo — by having a complete
    provenance block in the git-ignored `agents/.name-map.md` (a `## <slug>` heading carrying both a
    `real_name:` and a `sources:` line). The guarantee is unchanged — nothing ships unsourced — but the
    attribution for an obscured critic lives in the name map, not in the committed agent file;
  - the council roster's stated critic count (`agents/product-council.md`, "Roster (N critics)") MUST
    match the number of `critic-*.md` files on disk, so the roster can't drift from the tree.

The library scope is **derived from the skill tree**, not a hard-coded list, so a newly-added skill's
references can't silently fall out of coverage (the failure the v0.2 red-team caught).

It does NOT verify a quote is accurate (only a human / web-fetch can) — but it guarantees nothing
ships unsourced. Run it in CI alongside validate_plugin.py / reference-lint.py.

agent-ops ships a `check-sourcing.py` of the same NAME but deliberately DIFFERENT scope — not a stale
copy (the two can't share code; each plugin is self-contained, zero cross-plugin deps; see ISSUES D-9).
agent-ops has no dated research library to gate, and its obscured critics each carry an INLINE
`.name-map.md` pointer (a source signal present in every checkout), so it needs neither the library
frontmatter check nor the FULL/PUBLIC-CHECKOUT split below. product-forge's surface is the superset
(library + a name-map-deferral design), so its gate is the richer one. The divergence is by design.

Two modes, decided by the tree being checked:
  - FULL (the name-map file is present — the maintainer's working tree): obscured critics must
    have a complete provenance block; incomplete blocks are failures.
  - PUBLIC CHECKOUT (the name-map is ABSENT **and** `git check-ignore` confirms it is deliberately
    excluded — every fresh clone / CI): critics without an inline signal DEFER to the name-map.
    Deferrals are reported, not failed — a public tree cannot carry their provenance by design, so
    the full provenance guarantee for obscured critics is enforced where the name-map lives (the
    maintainer's machine), and CI enforces everything it can see (library frontmatter, inline
    signals, roster-count integrity).
Outside a git context an absent name-map still fails — absence is only excused when git proves it
is intentional.

Usage:
  check-sourcing.py <plugin-dir>   # exit 0 if all sourced, 1 if any gap, 2 on bad invocation
  check-sourcing.py selftest
Stdlib only (Python 3.8+).
"""
import os
import re
import subprocess
import sys

REQUIRED_FM = ("date", "coverage", "primary_sources")
SOURCE_SIGNAL = re.compile(r"Sourcing|https?://|(?:19|20)\d\d")  # a Sourcing block, a URL, or a year
ROSTER_COUNT = re.compile(r"Roster\s*\((\d+)\s+critics?\)")


def _frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else None


def _library_refs(root):
    """Derive the knowledge-library reference set from the skill tree: every `*.md` under any
    `skills/<skill>/references/`, excluding files under a `rubrics/` dir (rubrics are scored
    references that carry no frontmatter by design). Deriving — rather than hard-coding a skill
    list — means a new skill's references are covered automatically."""
    skills_root = os.path.join(root, "skills")
    out = []
    if not os.path.isdir(skills_root):
        return out
    for skill in sorted(os.listdir(skills_root)):
        refdir = os.path.join(skills_root, skill, "references")
        for dp, _dirs, files in os.walk(refdir):
            if "rubrics" in dp.split(os.sep):  # rubrics carry no frontmatter by design
                continue
            for fn in sorted(files):
                if fn.endswith(".md"):
                    out.append(os.path.join(dp, fn))
    return out


def _namemap_provenance(agdir):
    """Slugs that have a COMPLETE provenance block in the git-ignored agents/.name-map.md —
    a `## <slug>` heading whose block carries both a `real_name:` and a `sources:` line. The map is
    intentionally absent from the repo (it holds the obscured real identities); when present it is the
    out-of-repo source-of-truth for a critic's attribution. Returns a set of slugs (empty if no map)."""
    nm = os.path.join(agdir, ".name-map.md")
    if not os.path.isfile(nm):
        return set()
    text = open(nm, encoding="utf-8", errors="replace").read()
    sourced = set()
    # split into per-critic blocks on "## <slug>" headings, keep the slug + its body
    parts = re.split(r"(?m)^##\s+(critic-[^\s—-]+(?:-[a-z])?)\b", text)
    # parts = [pre, slug1, body1, slug2, body2, ...]
    for i in range(1, len(parts) - 1, 2):
        slug, body = parts[i], parts[i + 1]
        if re.search(r"(?mi)^\s*-\s*\*\*real_name:\*\*", body) and \
           re.search(r"(?mi)^\s*-\s*\*\*sources:\*\*", body):
            sourced.add(slug)
    return sourced


def _deliberately_ignored(repo_dir, path):
    """True when git confirms `path` is excluded by ignore rules — i.e., this tree deliberately
    omits it (a public checkout / CI), as opposed to the file being lost. Works for absent paths
    (check-ignore evaluates the rules, not the filesystem); False outside a git context."""
    try:
        r = subprocess.run(["git", "-C", repo_dir, "check-ignore", "-q", "--", path],
                           capture_output=True, timeout=15)
        return r.returncode == 0
    except Exception:
        return False


def check(root):
    """Return (findings, deferred) — failures, plus critics whose provenance defers to the
    deliberately-absent name-map (public-checkout mode only; informational, never a failure)."""
    root = os.path.abspath(root)
    findings = []
    deferred = []
    for fp in _library_refs(root):
        rel = os.path.relpath(fp, root)
        fm = _frontmatter(open(fp, encoding="utf-8", errors="replace").read())
        if fm is None:
            findings.append((rel, "no YAML frontmatter (need date + coverage + primary_sources)"))
            continue
        missing = [k for k in REQUIRED_FM if not re.search(rf"(?m)^{k}\s*:", fm)]
        if missing:
            findings.append((rel, "missing frontmatter: " + ", ".join(missing)))
    agdir = os.path.join(root, "agents")
    namemap_path = os.path.join(agdir, ".name-map.md")
    public_checkout = (not os.path.isfile(namemap_path)
                       and _deliberately_ignored(agdir if os.path.isdir(agdir) else root, namemap_path))
    namemap_sourced = _namemap_provenance(agdir)
    critic_files = []
    if os.path.isdir(agdir):
        for fn in sorted(os.listdir(agdir)):
            if not (fn.startswith("critic-") and fn.endswith(".md")):
                continue
            critic_files.append(fn)
            slug = fn[:-3]  # strip ".md"
            text = open(os.path.join(agdir, fn), encoding="utf-8", errors="replace").read()
            # a critic is sourced by an inline signal OR by a complete name-map provenance block
            if not SOURCE_SIGNAL.search(text) and slug not in namemap_sourced:
                if public_checkout:
                    deferred.append(fn)  # provenance lives in the (deliberately absent) name-map
                else:
                    findings.append((os.path.join("agents", fn),
                                     "critic is unsourced: no inline source signal (Sourcing block / URL / "
                                     "year) and no complete provenance block (real_name + sources) in the "
                                     "git-ignored agents/.name-map.md"))
    # roster-count integrity: the council's stated count must match the critic files on disk
    council = os.path.join(agdir, "product-council.md")
    if critic_files and os.path.isfile(council):
        m = ROSTER_COUNT.search(open(council, encoding="utf-8", errors="replace").read())
        if m and int(m.group(1)) != len(critic_files):
            findings.append((os.path.join("agents", "product-council.md"),
                             f"roster says {m.group(1)} critics but {len(critic_files)} critic-*.md files exist"))
    return findings, deferred


def _selftest():
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        fl = os.path.join(d, "skills", "product-patterns", "references", "flows")
        os.makedirs(fl)
        open(os.path.join(fl, "good.md"), "w").write(
            "---\ndate: 2026-06-03\ncoverage: foundational\nprimary_sources:\n  - NN/g\n---\n# ok\n")
        open(os.path.join(fl, "bad.md"), "w").write("# no frontmatter here\n")
        # a rubric file must be EXEMPT — rubrics carry no frontmatter by design
        rb = os.path.join(d, "skills", "product-evaluate", "references", "rubrics")
        os.makedirs(rb)
        open(os.path.join(rb, "rubric-x.md"), "w").write("# Rubric — X\n\nNo frontmatter, by design.\n")
        ag = os.path.join(d, "agents")
        os.makedirs(ag)
        open(os.path.join(ag, "critic-sourced.md"), "w").write(
            "---\nname: critic-sourced\n---\nGrounded in <https://example.com> (2020).\n")
        open(os.path.join(ag, "critic-bare.md"), "w").write(
            "---\nname: critic-bare\n---\nNo source signal in this body.\n")
        # an obscured critic with NO inline signal but a complete name-map block → must be CLEAN
        open(os.path.join(ag, "critic-obs-c.md"), "w").write(
            "---\nname: critic-obs-c\n---\nObscured lens, no inline year or URL here.\n")
        # an obscured critic whose name-map block is INCOMPLETE (no sources) → must still be flagged
        open(os.path.join(ag, "critic-half-c.md"), "w").write(
            "---\nname: critic-half-c\n---\nObscured lens, no inline signal.\n")
        open(os.path.join(ag, ".name-map.md"), "w").write(
            '## critic-obs-c — "Obs C."\n\n- **real_name:** Some Person\n- **sources:** public talks.\n\n'
            '## critic-half-c — "Half C."\n\n- **real_name:** Other Person\n- **lens:** a lens, but no sources line.\n')
        # roster says 9 but only 4 critic-*.md files exist → must be flagged
        open(os.path.join(ag, "product-council.md"), "w").write("## Roster (9 critics) + sub-councils\n")
        rels = {r for r, _ in check(d)[0]}
        for expect_flag in ("skills/product-patterns/references/flows/bad.md",
                            os.path.join("agents", "critic-bare.md"),
                            os.path.join("agents", "critic-half-c.md"),
                            os.path.join("agents", "product-council.md")):
            if expect_flag not in rels:
                ok = False
                print(f"selftest: failed to flag {expect_flag}", file=sys.stderr)
        for expect_clean in ("skills/product-patterns/references/flows/good.md",
                            os.path.join("agents", "critic-sourced.md"),
                            os.path.join("agents", "critic-obs-c.md"),
                            "skills/product-evaluate/references/rubrics/rubric-x.md"):
            if expect_clean in rels:
                ok = False
                print(f"selftest: false-flagged {expect_clean}", file=sys.stderr)
    # PUBLIC-CHECKOUT mode: name-map ABSENT but git-ignored → obscured critics DEFER, not fail.
    # (Skipped silently when git is unavailable; CI exercises this mode on every clean clone.)
    try:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], capture_output=True, timeout=15, check=True)
            open(os.path.join(d, ".gitignore"), "w").write(".name-map.md\n")
            ag = os.path.join(d, "agents")
            os.makedirs(ag)
            open(os.path.join(ag, "critic-obs-c.md"), "w").write(
                "---\nname: critic-obs-c\n---\nObscured lens, no inline year or URL here.\n")
            findings, deferred = check(d)
            critic_flags = [r for r, _ in findings if r.startswith("agents")]
            if critic_flags:
                ok = False
                print(f"selftest: public-checkout mode flagged {critic_flags} (should defer)", file=sys.stderr)
            if deferred != ["critic-obs-c.md"]:
                ok = False
                print(f"selftest: public-checkout mode deferred {deferred} (expected critic-obs-c.md)", file=sys.stderr)
    except (OSError, subprocess.SubprocessError):
        pass  # no git here — the mode is integration-tested by every CI clean clone
    print("selftest: PASS" if ok else "selftest: FAIL")
    return 0 if ok else 1


def main(argv):
    if argv and argv[0] == "selftest":
        return _selftest()
    args = [a for a in argv if not a.startswith("-")]
    if len(args) != 1 or not os.path.isdir(args[0]):
        print("usage: check-sourcing.py <plugin-dir>", file=sys.stderr)
        return 2
    findings, deferred = check(args[0])
    for rel, why in findings:
        print(f"  {rel}: {why}")
    note = (f"; {len(deferred)} critic(s) defer provenance to the git-ignored name-map "
            f"(public checkout — run on the maintainer tree for the full gate)") if deferred else ""
    print(f"RESULT: {'PASS' if not findings else 'FAIL'} ({len(findings)} sourcing gap(s){note})")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
