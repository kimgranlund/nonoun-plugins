#!/usr/bin/env python3
"""replay.py — drive the brand-guidelines machinery end to end on the recorded Meridian ledger.

A behavioral proof (CI-replayable, no model agent): the interactive 2×2 (propose options → designer
picks A/B/C/D + comments) PRODUCED `meridian.ledger.json`; this replays the deterministic half the
catalog can gate — validate → coverage (6/6) → coherence → assemble → **corpus-provenance clean** →
project a brand-spec card. It proves the loop closes on a realistic, coherent brand (with a superseded
first color pass that the restrained palette replaces, and a `constrains` coherence edge), and doubles
as the worked example. Exit 0 = the loop closes; 1 = a step broke. Stdlib only; Python 3.8+.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.normpath(os.path.join(HERE, "..", "..", "bin"))
GL = os.path.join(BIN, "guidelines-ledger")
CP = os.path.join(BIN, "corpus-provenance")
LEDGER = os.path.join(HERE, "meridian.ledger.json")


def _run(*args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


def main():
    fails = []

    def expect(c, m):
        if not c:
            fails.append(m)

    r = _run(GL, "validate", LEDGER)
    expect(r.returncode == 0, f"ledger does not validate: {r.stderr.strip()}")

    r = _run(GL, "coverage", LEDGER)
    expect("6/6 domains resolved" in r.stdout, f"not all six domains resolved (supersession honored?): {r.stdout.strip()}")

    r = _run(GL, "coherence", LEDGER)
    expect(r.returncode == 0 and "constrains" in r.stdout, f"coherence did not surface the constrains edge: {r.stdout.strip()}")

    d = tempfile.mkdtemp(prefix="guidelines-walkthrough-")
    try:
        os.makedirs(os.path.join(d, "00-sources"))
        ledger_in_corpus = os.path.join(d, "00-sources", "guidelines-elicitation.json")
        shutil.copy(LEDGER, ledger_in_corpus)

        r = _run(GL, "assemble", ledger_in_corpus, "--out", d, "--apply")
        expect(r.returncode == 0, f"assemble failed: {r.stderr.strip()}")
        for layer, dom in (("03-identity", "mark"), ("04-expression", "color"), ("04-expression", "type"),
                           ("04-expression", "expression"), ("05-voice", "voice"), ("07-guidelines", "governance")):
            expect(os.path.isfile(os.path.join(d, layer, f"{dom}.md")), f"assemble did not write {layer}/{dom}.md")
        # the superseded loud color must NOT survive into the assembled doc; the restrained gold tell must
        color_doc = os.path.join(d, "04-expression", "color.md")
        if os.path.isfile(color_doc):
            txt = open(color_doc).read()
            expect("foredge-gold" in txt, "assembled color doc lost the live (restrained) choice")
            expect("jewel-tone" not in txt, "assembled color doc kept the SUPERSEDED loud choice")

        r = _run(CP, d)
        expect(r.returncode == 0, f"corpus-provenance is not clean on the assembled corpus: {r.stdout.strip()} {r.stderr.strip()}")

        card = os.path.join(d, "meridian.brand.json")
        r = _run(GL, "card", ledger_in_corpus, "--idea", "The pleasure of permanence in a disposable age.", "-o", card)
        expect(os.path.isfile(card), "brand-spec card was not projected")
        if os.path.isfile(card):
            c = json.load(open(card))
            expect(len(c.get("rules", [])) >= 6, "projected card has fewer than the six domain rules")
            expect(c["strategy"]["brand_idea"].startswith("The pleasure of permanence"), "card lost the brand idea")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    if fails:
        sys.stderr.write("guidelines-walkthrough: FAIL\n")
        for m in fails:
            sys.stderr.write(f"  - {m}\n")
        return 1
    print("guidelines-walkthrough: OK (Meridian ledger → validate → 6/6 coverage → coherence (constrains) → "
          "assemble [superseded loud color dropped, restrained kept] → corpus-provenance clean → brand-spec card; "
          "the loop closes end to end on a realistic brand)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
