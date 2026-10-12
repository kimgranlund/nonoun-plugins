#!/usr/bin/env python3
"""potency_lint.py — mechanical triage for linguistic anti-patterns in a prompt artifact.

Surfaces the SURFACE-LEVEL smells that are regex-detectable — prohibition density (§5),
vague quantifiers and salience inflation (§8), and hedges (§4/§11). It is triage, not a
verdict: it cannot see whether a line *instantiates* or merely *describes* (that is the
[review] judgment, L1). Fenced ``` code blocks are skipped, but prose examples and
counter-examples will still trip it — read the flagged lines, don't obey the count.

Subject-noun exclusion (2026-07-04): an artifact whose OWN name contains a word in the
vague-quantifier set (a skill about writing *briefs* trips `brief`) would be permanently
red on that category through no fault of its prose — proven live by a real-artifact
shakedown (15/16 hits on one file were its own subject noun). The vague check therefore
skips exact-word matches of the artifact's own name tokens (frontmatter `name:`, the
bundle dir for a SKILL.md, or the file stem). Derived forms still count — `briefly`
flags even when the subject is `brief`.

Usage:  python3 potency_lint.py <file>
        python3 potency_lint.py selftest   # fixture-locked proof of the counters
Exit 0 = every category within budget.  Exit 1 = at least one budget exceeded.
"""
import re
import sys
from pathlib import Path

# (label, compiled regex, budget) — a category flags when its hit count exceeds budget.
HEDGE = re.compile(r"\b(please try to|try to|should probably|might want to|if possible|"
                   r"when you can|as much as possible|feel free to|it'?s important to|"
                   r"as best you can|do your best)\b", re.I)
PROHIBITION = re.compile(r"\b(do not|don'?t|never|avoid|refrain from|must not|do without)\b", re.I)
NEVER = re.compile(r"\bnever\b", re.I)
VAGUE = re.compile(r"\b(brief(?:ly)?|concise(?:ly)?|a few|several|reasonably|fairly|short(?:ly)?|"
                   r"tiny|as needed|as appropriate(?:ly)?|appropriately|properly|robustly|"
                   r"thorough(?:ly)?|a bit|or so|and so on|etc\.?)\b", re.I)
# Hard-emphasis WORDS + bang-runs are inflation (gated). Bold is counted separately and only
# reported: bolding a named handle is naming (§6), not shouting — a doc-wide bold budget would
# false-flag any well-structured prompt. The human reads the bold count and judges.
HARD_EMPHASIS = re.compile(r"\b(IMPORTANT|CRITICAL|CAUTION|WARNING|ATTENTION|URGENT|MANDATORY|"
                           r"CAREFUL|REMEMBER)\b|!{2,}")
BOLD = re.compile(r"\*\*[^*\n]+\*\*")                                   # informational only
MODAL = re.compile(r"\b(MUST NOT|MUST|SHALL|SHOULD|SHOULD NOT|MAY)\b")  # informational only

BUDGETS = {"hedges": 0, "prohibitions": 5, "NEVER (hard-gate cap)": 3,
           "vague quantifiers": 3, "hard-emphasis markers": 3}


CATS = (("hedges", HEDGE), ("prohibitions", PROHIBITION), ("NEVER (hard-gate cap)", NEVER),
        ("vague quantifiers", VAGUE), ("hard-emphasis markers", HARD_EMPHASIS))


def subject_tokens(path):
    """The artifact's own name tokens — the words its title legitimately owns, exempt from the
    vague-quantifier count as exact words. Sources, most-authoritative first: the frontmatter
    `name:` field; the bundle directory when the file is a SKILL.md; the file stem otherwise.
    Tokens under 3 chars are dropped (never exempt 'a'/'to')."""
    p = Path(path)
    names = []
    try:
        head = p.read_text(encoding="utf-8", errors="ignore")[:2000]
        m = re.search(r"^name:\s*(.+?)\s*$", head, re.M)
        if m:
            names.append(m.group(1))
    except OSError:
        pass
    names.append(p.parent.name if p.name.upper() == "SKILL.MD" else p.stem)
    toks = set()
    for name in names:
        for t in re.split(r"[-_\s]+", name.lower()):
            if len(t) >= 3:
                toks.add(t)
    return frozenset(toks)


def scan(text, vague_exclude=frozenset()):
    # Count OCCURRENCES (not matching lines): the budgets are density counts — one line
    # with six `Never`s is six, not one. Samples keep one entry per matching line for display.
    # `vague_exclude`: exact words (the artifact's own subject tokens) skipped in the VAGUE
    # count only — derived forms ('briefly' vs subject 'brief') still count.
    counts = {label: 0 for label, _ in CATS}
    samples = {label: [] for label, _ in CATS}
    excluded_vague = 0
    modal_count = bold_count = 0
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().lstrip(">").lstrip().startswith("```"):  # plain or blockquoted (> ```) fence
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        modal_count += sum(1 for _ in MODAL.finditer(line))
        bold_count += sum(1 for _ in BOLD.finditer(line))
        for label, rx in CATS:
            if label == "vague quantifiers" and vague_exclude:
                hits = [m for m in rx.finditer(line)]
                kept = [m for m in hits if m.group(0).lower() not in vague_exclude]
                excluded_vague += len(hits) - len(kept)
                c = len(kept)
            else:
                c = sum(1 for _ in rx.finditer(line))
            if c:
                counts[label] += c
                samples[label].append((n, line.strip()[:88]))
    return counts, samples, modal_count, bold_count, excluded_vague


# --- selftest fixtures ---------------------------------------------------------------------------
# DIRTY: every category present in a KNOWN quantity, each over its budget — the selftest asserts the
# exact counts, so a regex or fence-handling drift changes a number and the test bites. The fenced
# block at the bottom is a negative control: its smells must add zero.
_SELFTEST_DIRTY = """Please try to keep the output brief, and do your best.
IMPORTANT: never write outside the repo. Never overwrite user files. Never skip checks.
Do not delete branches. Don't force-push. Avoid rebases. Never bypass review.
Add a few tests, several docs, and clean up as needed.
CRITICAL!! REMEMBER: check twice. You MUST run the **linter**.
```
NEVER IMPORTANT don't avoid briefly   (fenced -- must not count)
```
"""
# expected occurrence counts for the dirty fixture (all five categories over budget)
_SELFTEST_DIRTY_EXPECT = {"hedges": 2, "prohibitions": 7, "NEVER (hard-gate cap)": 4,
                          "vague quantifiers": 4, "hard-emphasis markers": 4}
_SELFTEST_DIRTY_MODALS, _SELFTEST_DIRTY_BOLD = 1, 1
# CLEAN: the reverse control — instantiating prose with zero smells; must NOT be flagged.
_SELFTEST_CLEAN = """The agent validates every write path against the project root before writing.
Run the linter, read each flagged line, and fix the failing layer at its source.
Done when the lint budget holds and every load-bearing line instantiates the behavior.
"""


def selftest():
    """Fixture-locked proof: known counts on a dirty prompt (bites when any counter drifts),
    a fenced-block negative control, and a clean prompt that must pass every budget."""
    errs = []
    counts, _samples, modals, bold, _excl = scan(_SELFTEST_DIRTY)
    for label, want in _SELFTEST_DIRTY_EXPECT.items():
        if counts[label] != want:
            errs.append("dirty fixture: %s counted %d, expected %d" % (label, counts[label], want))
    for label, budget in BUDGETS.items():
        if counts[label] <= budget:
            errs.append("dirty fixture does NOT trip '%s' (%d <= budget %d) — the lint would not bite"
                        % (label, counts[label], budget))
    if modals != _SELFTEST_DIRTY_MODALS:
        errs.append("dirty fixture: modal count %d, expected %d" % (modals, _SELFTEST_DIRTY_MODALS))
    if bold != _SELFTEST_DIRTY_BOLD:
        errs.append("dirty fixture: bold count %d, expected %d" % (bold, _SELFTEST_DIRTY_BOLD))
    # fenced negative control: stripping the fence must RAISE the counts (proves the skip is live)
    unfenced = _SELFTEST_DIRTY.replace("```\n", "")
    counts_uf, _, _, _, _ = scan(unfenced)
    if not (counts_uf["NEVER (hard-gate cap)"] > counts["NEVER (hard-gate cap)"]
            and counts_uf["prohibitions"] > counts["prohibitions"]):
        errs.append("fence skip dead: fenced smells were counted (fenced %s vs unfenced %s)"
                    % (counts, counts_uf))
    # reverse control: a clean prompt is NOT flagged — zero hits, every budget holds
    counts_c, _, modals_c, bold_c, _ = scan(_SELFTEST_CLEAN)
    for label, budget in BUDGETS.items():
        if counts_c[label] != 0:
            errs.append("clean fixture wrongly flagged: %s = %d (expected 0)" % (label, counts_c[label]))
        if counts_c[label] > budget:
            errs.append("clean fixture over budget on %s" % label)
    # subject-noun exclusion (2026-07-04): the artifact's own name word must not count as vague,
    # while a derived form still does — and with NO exclusion, behavior is byte-identical to before.
    subj_text = ("The design brief opens with the problem. A brief names its audience.\n"
                 "Every brief cites its PRD. Keep the summary briefly worded.\n")
    counts_x, _, _, _, excl_x = scan(subj_text, vague_exclude=frozenset({"brief"}))
    if counts_x["vague quantifiers"] != 1 or excl_x != 3:
        errs.append("subject-noun exclusion wrong: expected 1 kept ('briefly') + 3 excluded "
                    "('brief' x3), got %d kept + %d excluded"
                    % (counts_x["vague quantifiers"], excl_x))
    counts_nx, _, _, _, excl_nx = scan(subj_text)
    if counts_nx["vague quantifiers"] != 4 or excl_nx != 0:
        errs.append("no-exclusion baseline drifted: expected 4 vague hits, 0 excluded, got %d/%d"
                    % (counts_nx["vague quantifiers"], excl_nx))
    # derivation: a bundle SKILL.md inherits its dir's tokens; the noun 'brief' lands in the set
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "prd-to-product-design-brief"
        d.mkdir()
        f = d / "SKILL.md"
        f.write_text("---\nname: prd-to-product-design-brief\n---\nbody\n", encoding="utf-8")
        toks = subject_tokens(f)
        if "brief" not in toks or "design" not in toks:
            errs.append("subject_tokens derivation wrong for a bundle SKILL.md: %s" % sorted(toks))
        if "to" in toks:
            errs.append("subject_tokens must drop sub-3-char tokens ('to' leaked): %s" % sorted(toks))
    if errs:
        print("potency_lint selftest: FAIL (%d)" % len(errs))
        for e in errs:
            print("  - " + e)
        return 1
    print("potency_lint selftest: OK — dirty fixture counted exactly (hedges %d, prohibitions %d, "
          "NEVER %d, vague %d, emphasis %d; all five over budget), fenced block skipped, "
          "clean fixture zero-flagged, subject-noun exclusion exempts the exact name word only "
          "(derived forms still count; no-exclusion baseline byte-identical)"
          % tuple(_SELFTEST_DIRTY_EXPECT[k] for k in
          ("hedges", "prohibitions", "NEVER (hard-gate cap)", "vague quantifiers",
           "hard-emphasis markers")))
    return 0


def main(argv):
    if len(argv) == 2 and argv[1] == "selftest":
        return selftest()
    if len(argv) != 2:
        print("usage: potency_lint.py <file>|selftest")
        return 2
    p = Path(argv[1])
    if not p.is_file():
        print(f"no such file: {argv[1]}")
        return 2
    exclude = subject_tokens(p)
    counts, samples, modal_count, bold_count, excluded_vague = scan(
        p.read_text(encoding="utf-8", errors="ignore"), vague_exclude=exclude)

    print(f"== potency lint: {p.name} ==")
    if excluded_vague:
        print(f"[info] subject-noun exclusion: {excluded_vague} vague hit(s) skipped as the "
              f"artifact's own name word(s) ({', '.join(sorted(t for t in exclude if VAGUE.fullmatch(t)))})")
    failed = False
    for label, budget in BUDGETS.items():
        n_hits = counts[label]
        over = n_hits > budget
        failed = failed or over
        mark = "OVER" if over else "ok"
        print(f"[{mark:>4}] {label}: {n_hits} (budget {budget})")
        for n, snippet in samples[label][:6]:
            print(f"         L{n}: {snippet}")
        if len(samples[label]) > 6:
            print(f"         … +{len(samples[label]) - 6} more lines")
    print(f"[info] RFC modals (MUST/SHOULD/MAY): {modal_count} "
          f"— load-bearing at the gates, inflates if scattered")
    print(f"[info] bold spans: {bold_count} — naming a handle is fine; scattered **bold** is shouting (§8)")
    print(f"-- {'SMELLS OVER BUDGET — audit the flagged lines' if failed else 'within budget'} --")
    print("   (triage only: it cannot judge instantiate-vs-describe — that is L1, a [review] call.)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
