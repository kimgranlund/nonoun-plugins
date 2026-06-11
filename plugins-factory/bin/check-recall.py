#!/usr/bin/env python3
"""check-recall.py — proactively catch brittle concept-regex patterns in the council-calibration checkers.

The council checkers (`check*.py` under each plugin's `evals/council-calibration/`) score a council
transcript by matching a corpus of regex patterns per planted defect. Those patterns develop *recall*
gaps: the council catches a defect but words it a way no pattern matches, so a run scores low — a
CHECKER miss, not a council miss. This bit three separate run-3 samples (the over-fleet A4/A6 fix,
the monolith MO6 "form" vs "format" fix), each found *reactively* after a run.

This harness finds them *before* a run does. Each checker has a co-located paraphrase corpus
(`evals/recall-corpus/<plugin>-<checker>.recall.json`) listing, per planted defect, the legitimate
ways a council might word it. The harness imports the checker, lowercases each paraphrase exactly as
the checker lowercases its transcript, and asserts every paraphrase matches ≥1 of that defect's
patterns. A miss = a brittle pattern, surfaced as a CI failure to fix before it costs a run.

It also enforces **coverage**: the corpus's defect keys must EQUAL the checker's PLANTED keys — every
planted defect carries recall paraphrases, and a renamed/added defect can't silently lose coverage.

Usage:
  check-recall.py [corpus.json ...]   # default: every evals/recall-corpus/*.recall.json
  check-recall.py selftest            # prove the harness catches a deliberately-brittle pattern

Exit 0 = every paraphrase matches + coverage complete; 1 = a brittle pattern or coverage gap.
Stdlib only; Python 3.8+.
"""
import glob
import importlib.util
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # bin → plugins-factory → repo
CORPUS_DIR = os.path.join(REPO_ROOT, "plugins-factory", "evals", "recall-corpus")


def _load_planted(checker_rel):
    """Import a checker module by repo-relative path and return its PLANTED dict (without running main())."""
    path = os.path.join(REPO_ROOT, checker_rel)
    spec = importlib.util.spec_from_file_location("_checker", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PLANTED


def check_corpus(corpus_path):
    """Return (ok, lines) — validate one checker's paraphrase corpus against its PLANTED patterns."""
    lines = []
    corpus = json.load(open(corpus_path, encoding="utf-8"))
    checker_rel = corpus["checker"]
    defects = corpus["defects"]
    try:
        planted = _load_planted(checker_rel)
    except (OSError, AttributeError, ImportError) as e:
        return False, [f"  FAIL  {os.path.basename(corpus_path)} — cannot load checker '{checker_rel}': {e}"]

    ok = True
    # coverage: corpus keys must equal planted keys (no missing recall coverage, no stale corpus key)
    missing = set(planted) - set(defects)
    stale = set(defects) - set(planted)
    if missing:
        ok = False
        for k in sorted(missing):
            lines.append(f"  FAIL  {checker_rel}: planted defect has NO recall paraphrases — {k}")
    if stale:
        ok = False
        for k in sorted(stale):
            lines.append(f"  FAIL  {checker_rel}: corpus defect not in checker PLANTED (renamed?) — {k}")

    # recall: every paraphrase must match ≥1 of its defect's patterns (lowercased, as the checker matches)
    total, matched = 0, 0
    for key, paraphrases in defects.items():
        if key not in planted:
            continue
        pats = planted[key]
        for ph in paraphrases:
            total += 1
            low = ph.lower()
            if any(re.search(p, low) for p in pats):
                matched += 1
            else:
                ok = False
                lines.append(f"  FAIL  {checker_rel}: paraphrase matches NO pattern for [{key}]\n"
                             f"          → \"{ph}\"")
    head = f"  {'PASS' if ok else 'FAIL'}  {os.path.relpath(checker_rel)} — {matched}/{total} paraphrases match, {len(defects)} defect(s) covered"
    return ok, [head] + lines


def main(argv):
    corpora = argv if argv else sorted(glob.glob(os.path.join(CORPUS_DIR, "*.recall.json")))
    if not corpora:
        print(f"RESULT: FAIL — no recall corpora found under {CORPUS_DIR}")
        return 1
    allok = True
    for c in corpora:
        ok, lines = check_corpus(c)
        for ln in lines:
            print(ln)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'} (checker-recall over {len(corpora)} checker(s))")
    return 0 if allok else 1


def selftest():
    """Prove the harness catches the exact bug class it exists for: a paraphrase a brittle pattern misses,
    a stale/missing coverage key, and a clean pass. No external state. Exit 0 = pass, 1 = fail."""
    import tempfile
    fails = []
    def check(cond, label):
        if not cond:
            fails.append(label)
    tmp = tempfile.mkdtemp(prefix="check-recall-selftest-")
    try:
        # a synthetic checker with a deliberately-narrow pattern ("format" — misses "form")
        checker = os.path.join(tmp, "fake_check.py")
        open(checker, "w", encoding="utf-8").write(
            'PLANTED = {"X gate checks the wrong thing": [r"format, not correctness"]}\n')
        global REPO_ROOT
        REPO_ROOT = tmp  # make repo-relative resolution point at the temp checker

        def corpus(defects):
            p = os.path.join(tmp, "c.recall.json")
            json.dump({"checker": "fake_check.py", "defects": defects}, open(p, "w", encoding="utf-8"))
            return p

        # 1. a paraphrase the brittle pattern MISSES → harness must FAIL (this is the whole point)
        ok, _ = check_corpus(corpus({"X gate checks the wrong thing": ["the harness verifies form, not correctness"]}))
        check(not ok, "harness did NOT catch the brittle pattern (form vs format)")
        # 2. a matching paraphrase → PASS
        ok, _ = check_corpus(corpus({"X gate checks the wrong thing": ["it checks format, not correctness"]}))
        check(ok, "harness failed a paraphrase that genuinely matches")
        # 3. a missing-coverage key → FAIL
        ok, _ = check_corpus(corpus({}))
        check(not ok, "harness did NOT flag a planted defect with no recall coverage")
        # 4. a stale corpus key → FAIL
        ok, _ = check_corpus(corpus({"X gate checks the wrong thing": ["it checks format, not correctness"],
                                     "Z defect not in checker": ["whatever"]}))
        check(not ok, "harness did NOT flag a stale corpus key")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        sys.stderr.write("check-recall selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("check-recall selftest: OK (catches brittle patterns, coverage gaps, and stale keys)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main(sys.argv[1:]))
