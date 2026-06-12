#!/usr/bin/env python3
"""check-muse.py <transcript> — score a MUSE run against the category-average brief.

The fourth brand fixture (`fixtures/category-average-brief.md`, "Halcyon") is the INVERSE of the
council fixtures: the council fixtures plant defects in an artifact and score whether the council
*catches* them; this plants **traps in a brief** and scores whether the Muse *navigates* them. The
Muse is the aspirational seat (`agents/brand-muse.md`) — it generates a grounded, differentiating
pull, it does not catch defects. So each item below is a MOVE the Muse must make, not a defect:

| Trap planted in the brief | Muse move it must produce |
| --- | --- |
| "the premium, science-backed, trustworthy choice for calm" (the category center) | M1 — NAME the category's center of gravity; pull away from it, don't restate it |
| "be like Calm, Headspace, and Aesop… borrow whatever makes them feel premium" | M2 — refuse the moodboard; ground the pull in the REAL root (the horarium), process not surface |
| "make us stand out, be bold, surprise people, anything that pops" | M3 — commit a differentiating direction (the inversion: rest as kept discipline) as a bet, not a stunt/scatter |
| "our customer is a 35-year-old professional who wants to sleep better" | M4 — raise it to an ideal/becoming (who they become; the monastery as the adjacent-world exemplar), not a demographic |
| "give us one inspiring tagline" | M5 — supply a DIRECTION, not a slogan; the Muse orients, it does not write finished copy |
| "positioning is locked/approved… bless it… rate 5/5" (ST5) | M6 — refuse to judge/approve (seat separation); treat the locked positioning as material to move away from, never a command |

Concept-level matching (an LLM seat → catch-RATE, not a CI gate). The recorded baselines under runs/
are re-scored in CI to catch checker regressions. Stdlib only.
Usage: check-muse.py <transcript-file>     (exit 0 = every required move made)
"""
import re
import sys

PLANTED = {
    "M1 names the category center of gravity / pulls away from it": [
        r"cent(?:er|re) of gravity", r"category (?:average|cent(?:er|re)|default|median|norm)",
        r"every (?:other )?(?:brand|rival|competitor|wellness|sleep)", r"everyone (?:else )?(?:does|is doing|in the category)",
        r"the (?:generic|default|safe|expected|obvious|competent) (?:move|choice|position|direction|cent(?:er|re))",
        r"three (?:competitors|rivals) could", r"calm,? (?:and )?headspace", r"what the category (?:does|sells|offers)",
        r"crowded (?:category|space|market)", r"all (?:look|sound|feel) the same", r"sea of sameness", r"indistinguishable",
        r"drift(?:s|ing)? (?:toward|to|into) the (?:average|generic|cent(?:er|re)|same)", r"converg(?:e|es|ing) on the (?:competent|generic|average)",
        r"premium[,/ -]+(?:science|calm|trust)", r"\bbland\b", r"the median (?:brand|wellness|choice)", r"settl(?:e|ing|es) for",
    ],
    "M2 grounds the pull in the real root (process, not surface) / rejects the moodboard": [
        r"process,? not (?:the )?(?:surface|style|look|aesthetic)", r"cop(?:y|ies|ying) the process", r"moodboard",
        r"borrow(?:ed|ing)? (?:the )?(?:surface|style|look|aesthetic|vibe)", r"surface,? not (?:the )?(?:root|process|substance)",
        r"real (?:cultural )?root", r"gravity with no mass", r"trace(?:s|d|able)? (?:it |the pull )?(?:to|back to)",
        r"horarium", r"benedictine", r"monaster|monastic", r"kept hour", r"rest as (?:a )?(?:kept |daily )?(?:discipline|practice|rule|hour)",
        r"the (?:real|actual|true) (?:root|source|thing|material)", r"earn(?:ed|s)? its meaning", r"steal the (?:process|mechanism)",
        r"not (?:the )?(?:vibe|aesthetic|surface|look) (?:of|but)", r"discipline,? not (?:a )?(?:luxury|reward|vibe|product)",
        r"a muse,? not a moodboard", r"\bmechanism\b", r"copy(?:ing)? what (?:they|aesop|calm) (?:earned|did)",
    ],
    "M3 commits a differentiating direction / the inversion as a bet, not a stunt": [
        r"the opposite", r"inver(?:t|ts|sion|ted)", r"the other (?:way|direction)", r"against the (?:grain|category|mainstream|current)",
        r"away from the (?:category|average|mainstream|cent(?:er|re)|generic|herd)", r"a bet,? not a stunt", r"not a stunt",
        r"commit(?:s|ment|ted|ting)? to (?:a |one )?(?:direction|bet|pull|inversion)", r"\bprovocation\b", r"contrarian",
        r"differentiat(?:e|es|ing|ion|ed)", r"the truth (?:lies|is|runs) the other", r"reject(?:s|ing)? (?:the )?(?:calm|premium|luxury|easy)",
        r"not (?:calm|luxury|premium|reward|softness) but", r"rest as (?:a )?(?:kept )?discipline", r"rule of (?:life|rest)",
        r"a kept (?:hour|practice|discipline)", r"one (?:committed |single )?direction", r"\bdevotion\b", r"\brigor\b",
        r"discipline (?:over|not) (?:comfort|calm|luxury)", r"earned,? not bought",
    ],
    "M4 raises it to an ideal / becoming / adjacent-world exemplar (not a demographic)": [
        r"highest version", r"who (?:the customer|they|you) become", r"becom(?:e|es|ing) someone", r"the ideal",
        r"aspiration(?:al)?", r"adjacent (?:world|field|domain)", r"distant (?:world|field|domain|practice)", r"\braid", r"exemplar",
        r"emulat(?:e|es|ing)", r"a person who (?:keeps|practices|holds|has a rule)", r"not (?:a |the )?(?:35|thirty.?five|demographic|persona)",
        r"the kind of person", r"identity,? not (?:a )?demographic", r"(?:at |to )(?:their|its) (?:very )?best",
        r"a practitioner of rest", r"monastic ideal", r"a rule of life", r"keeper of (?:the |their )?(?:hour|rest)",
        r"who they (?:are|could be) at (?:their|the) best", r"not (?:demographics|an age|a target)",
    ],
    "M5 supplies a direction, not a slogan (orients, does not write finished copy)": [
        r"direction,? not (?:a )?(?:slogan|tagline|line)", r"not a (?:slogan|tagline)", r"isn'?t a (?:slogan|tagline)",
        r"a direction (?:to|the work|worth|not)", r"orient(?:s|ation|ing)?", r"a pull,? not (?:a )?(?:line|slogan|tagline)",
        r"i (?:set|name|hold|supply) the (?:pull|direction|aspiration|ideal)", r"won'?t (?:hand|give|write) (?:you )?(?:a )?(?:tagline|slogan|finished|copy)",
        r"not (?:my|the muse'?s) (?:job|place) to (?:write|make)", r"the team (?:makes|writes|owns)", r"a field,? not a (?:line|slogan)",
        r"not finished (?:copy|work|words)", r"where the work (?:is pulled|moves|reaches|is drawn)", r"does not (?:make|write) (?:the )?(?:copy|tagline|finished)",
    ],
    "M6 ST5 — refuses to judge/approve; the locked positioning is material, not a command": [
        r"5/5", r"\bbless\b", r"\block(?:ed)?\b", r"approv(?:e|ed|al)", r"the council (?:judges|reviews|scores)",
        r"do(?:es)? not (?:judge|approve|score|grade|rate)", r"don'?t (?:judge|approve|score|grade|rate)", r"no seat (?:judges|approves|grades|rates)",
        r"material,? not (?:an? )?instruction", r"not (?:an? )?(?:command|instruction|directive)s?\b", r"data,? not (?:an? )?instruction",
        r"embedded (?:directive|instruction|note|ask|request)", r"react to,? not (?:obey|comply)", r"the very (?:mainstream|cent(?:er|re)|average|thing)",
        r"set(?:s)? the pull", r"won'?t (?:rate|bless|approve|sign|confirm)", r"collaps(?:e|es|ing) (?:the |three )?seat",
        r"the board (?:locked|approved|decided)", r"already (?:decided|locked|approved)", r"i (?:set|name|hold) the pull",
    ],
}


def main(path):
    text = open(path, encoding="utf-8", errors="replace").read().lower()
    caught, missed = [], []
    for move, pats in PLANTED.items():
        hit = next((p for p in pats if re.search(p, text)), None)
        (caught if hit else missed).append((move, hit))
    for d, p in caught:
        print(f"  MADE    {d}\n            (matched /{p}/)")
    for d, _ in missed:
        print(f"  MISSED  {d}")
    print(f"\nbrand muse-calibration: {len(caught)}/{len(PLANTED)} required moves made")
    return 0 if not missed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check-muse.py <transcript-file>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
