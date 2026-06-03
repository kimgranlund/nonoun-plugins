---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "P. Jonathon Phillips, Carina A. Hahn, Peter C. Fontana, et al. *Four Principles of Explainable Artificial Intelligence.* NIST Interagency Report (NISTIR) 8312, September 2021. DOI 10.6028/NIST.IR.8312. https://nvlpubs.nist.gov/nistpubs/ir/2021/nist.ir.8312.pdf"
  - "Megan Chan. \"Explainable AI in Chat Interfaces.\" Nielsen Norman Group, 2025-12-12. https://www.nngroup.com/articles/explainable-ai"
  - "Regulation (EU) 2016/679 (GDPR), Articles 13–15 & 22 — information about, and safeguards on, solely-automated decisions ('meaningful information about the logic involved'). https://gdpr-info.eu/art-22-gdpr/"
---

# Explainability & Transparency

A system that affects a user owes them an account of _why_ — why this recommendation, this ranking, this denial, this answer. Explainability is the discipline of supplying that account honestly. This reference covers the spectrum from the everyday "why am I seeing this?" affordance to algorithmic-decision transparency, citations and provenance, and the single hardest distinction in the field: the difference between a **true explanation** (one that reflects how the system actually reached the output) and a **plausible rationalization** (a fluent story generated _about_ the output after the fact, which looks like transparency and isn't). It hardens the citations/honest-framing material in `ai-ux/uncertainty-citations.md` — that file is about calibrating confidence; this one is about the structural honesty of the _reasons_ the product gives. The load-bearing claim: **an explanation's job is to let the user verify or contest the decision — not to make them feel comfortable with it.** Comfort without verifiability is rationalization.

> The standard to hold onto, from NIST's four principles: an explanation must satisfy **explanation accuracy** — it must "correctly reflect the reason for generating the output" and "the system's process for generating the output." A reason that sounds good but doesn't reflect the actual process fails this principle even if the user is satisfied by it. Plausibility is not accuracy.

Explainability has one well-grounded government standard (NIST), strong legal scaffolding (GDPR), and one important recent reversal in the AI-UX literature (NN/g's caution against reasoning-trace "explanations"). The reversal is labeled where it bites — it is a single-source-but-named finding and a deliberate course-correction on the older "explainability = show the steps" intuition.

---

## NIST's four principles, as design checks

NISTIR 8312 (2021) gives the cleanest decomposition of what a good explanation must do. Treat each as a check.

| Principle (NIST) | What it requires | The check |
| --- | --- | --- |
| **Explanation** | The system delivers "accompanying evidence or reason(s) for... outputs." | Is there a reason at all — or does the output arrive bare, take-it-or-leave-it? |
| **Meaningful** | The explanation is "understandable to the individual user." | Can _this_ user act on it — or is it jargon, a coefficient dump, or a 40-page policy? |
| **Explanation accuracy** | The explanation "correctly reflects the system's process for generating the output." | Does the reason given match how the decision was actually made — or is it a comforting story? |
| **Knowledge limits** | The system "only operates under conditions for which it was designed" and signals when it reaches them. | Does it say "I don't know / this is outside what I can judge" — or answer confidently regardless? |

The two that products routinely fail are **explanation accuracy** and **knowledge limits**. Accuracy is hard because the honest explanation of a complex model is often unsatisfying, so teams reach for a tidier story that isn't true. Knowledge limits are hard because admitting "I can't reliably judge this" feels like a product weakness — but a system with no stated limits implicitly claims omniscience, and every confident-but-wrong output then reads as a betrayal. NIST is explicit that "meaningful" and "accurate" can be in tension: the most accurate explanation may not be the most understandable, and resolving that tension _honestly_ (simplify without distorting) is the craft.

---

## "Why am I seeing this?" — the everyday explanation

The most common explanation surface is not a regulated decision; it is the ranked feed, the recommendation, the "suggested for you," the ad. The pattern is a per-item affordance that answers, in the user's terms, why this item is here and what would change it.

```text
A good "why am I seeing this" answers three things:

  WHY THIS   — the specific signals: "Because you saved 3 hiking posts"
               (not "based on your activity" — name the actual driver)
  WHO DECIDED— is this organic, ranked, sponsored, or paid placement?
               (provenance: an ad labeled as an ad, ranking labeled as ranking)
  WHAT NOW   — a control that changes it: "See fewer like this" / "Why?" → adjust
               (explanation without a lever is just narration)
```

The tell of a good one: it names a _specific, true_ signal and offers a _working_ control. The tell of a bad one: "Based on your interests and activity" — a non-answer that explains nothing and changes nothing, present to look transparent rather than to be. An explanation the user can't act on is decoration; sponsored content not labeled as sponsored is a provenance failure (and, for ads, often a legal one).

---

## Algorithmic-decision transparency

When the system makes a consequential decision _about_ a person — a loan denied, an application screened, content removed, an account flagged — the explanation stakes rise sharply, and so does the legal scaffolding. GDPR Articles 13–15 require, for solely-automated decisions with legal/significant effect, that the person be given "meaningful information about the logic involved," and Article 22(3) guarantees the right to "obtain human intervention," to "express his or her point of view," and to "contest the decision." The design implications:

- **Meaningful, not technical.** "Meaningful information about the logic" means a human-understandable account of the main factors and how they weighed — not the model weights, and not "an algorithm decided." Name the principal reasons in terms the person can respond to.
- **Contestable.** A consequential automated decision needs a route to human review — and the human must have authority to actually change the outcome, not rubber-stamp it. An "appeal" that returns the same automated answer is not contestability.
- **Actionable.** The best decision explanations are _counterfactual_: "you were declined because income was below X; with income above X the decision changes." This tells the person what to do, which is what they actually want from a "why."

> Labeled caveat on the "right to explanation." Whether GDPR confers a hard, standalone "right to explanation" of a specific decision is genuinely contested among legal scholars — Article 22 itself doesn't use the phrase; the obligation is assembled from Articles 13–15's "meaningful information about the logic" plus Recital 71. Treat "meaningful information about the logic and a route to contest" as the durable, citable design requirement; treat "a legally guaranteed per-decision explanation" as a contested interpretation, not settled fact.

---

## True explanation vs. plausible rationalization

This is the distinction the whole file turns on, and the one most likely to be gotten wrong _while trying to do the right thing_. The intuition "make the AI show its reasoning" is natural — and, per the most recent NN/g research, often counterproductive for generative systems. Chan's explainable-AI guidance advises designers to "avoid using step-by-step explanations that imply certainty or transparency," because such "explanations are often unfaithful to the model's actual computation": a generated reasoning trace can omit the real drivers, and can change its story when the user pushes back. A walkthrough that _looks_ like an audit of the model's thinking is frequently a plausible narrative produced _about_ a conclusion — which fails NIST's explanation-accuracy principle while manufacturing exactly the overtrust that explainability is supposed to prevent.

|  | True explanation | Plausible rationalization |
| --- | --- | --- |
| **Relationship to the output** | Reflects how the output was actually produced | Generated after the fact, _about_ the output |
| **Under challenge** | Stable — the reasons don't shift when questioned | Often shifts to re-justify the same conclusion |
| **What it enables** | Verification and contest | Comfort and compliance |
| **NIST test** | Passes explanation accuracy | Fails it, however fluent |
| **Honest substitute (NN/g)** | — | Replace with verifiable sources + stated limits |

NN/g's recommended substitute is the practical move: instead of a fictionalized internal monologue, give the user the two things they can actually check — **the sources behind the claim** (provenance the user can follow; see `ai-ux/uncertainty-citations.md`) and **an honest statement of the system's limits** (NIST's knowledge-limits principle). The discipline: prefer a verifiable, modest "here's what this is based on and here's what I can't judge" over a confident, unverifiable "here's my reasoning." (Labeled: the anti-reasoning-trace finding is NN/g, Dec 2025 — recent and single-source-but-named; it tempers, not forbids, reasoning UI, and is the current best-sourced position.)

---

## Citations and provenance

Provenance is explanation's most checkable form: a claim with a source the user can follow is a reason they can verify themselves. The mechanics — place the source next to the claim, link to the relevant part, style it distinctly, name it (not just "Source"), and set the expectation that sources can be wrong — are covered in `ai-ux/uncertainty-citations.md`. The transparency-specific point here: **a citation is only an explanation if it actually supports the claim and the user can reach it.** A decorative, authoritative-looking source that doesn't resolve, or doesn't actually back the assertion, is a rationalization in citation costume — it raises perceived trust without earning it, which is the precise failure this whole reference exists to catch.

---

## Anti-patterns

- **Reason-free output.** A ranking, recommendation, or decision delivered bare, with no "why" at all — fails NIST's first principle outright.
- **The non-explanation.** "Based on your interests and activity" / "an algorithm decided" — present to look transparent, explaining nothing the user can act on (fails "meaningful").
- **Rationalization-as-transparency.** A fluent step-by-step that reads like the model's reasoning but is a post-hoc story (fails "explanation accuracy"; NN/g flags it directly) — overtrust dressed as openness.
- **Omniscient silence.** A system that never says "I don't know" or "this is outside what I can judge" — no knowledge limits, so every confident error is a betrayal.
- **Uncontestable decision.** A consequential automated decision with no route to a human who can actually change it — an "appeal" that re-runs the same algorithm.
- **Decorative citation.** A source that doesn't resolve or doesn't support the claim, present to manufacture trust (see `uncertainty-citations.md`).
- **Unlabeled provenance.** Sponsored or paid placement shown without a "sponsored" label — a provenance failure and often an ad-disclosure violation.

---

## The scoring test: is the explanation true, or just comforting?

1. **There is a reason, and it's meaningful.** Does the system give a reason the _user_ can understand and act on — or arrive bare, or hide behind jargon / "based on your activity"? (NIST: explanation + meaningful.)
2. **The reason is accurate.** Does the explanation reflect how the output was actually produced — or is it a plausible story generated about it? Does it stay stable when challenged? (NIST: explanation accuracy; NN/g on unfaithful reasoning traces.)
3. **Limits are stated.** Does the system signal when a question is outside what it can reliably judge — or claim implicit omniscience? (NIST: knowledge limits.)
4. **Consequential decisions are contestable.** For decisions _about_ a person, is there meaningful information about the logic and a route to human review with authority to change it? (GDPR Arts. 13–15, 22.)
5. **Provenance is checkable and honest.** Are citations real, supporting, reachable, and is paid/sponsored content labeled — or are sources decorative and placement disguised?

A product passes when a user can find out why the system did what it did, in terms they can act on, with reasons that actually reflect the process and limits the system honestly admits — and can contest the decisions that matter. It fails when the "explanation" is a comforting story the user can't verify, a non-answer that explains nothing, or a confident output from a system that never admits it might be out of its depth.

---

## One labeled caveat

NIST's four principles and the quoted phrasings ("accompanying evidence or reason(s)," "understandable to the individual user," "correctly reflect... the system's process," "only operates under conditions for which it was designed") are from NISTIR 8312 (Phillips et al., Sept 2021). The GDPR "meaningful information about the logic involved" obligation is Articles 13–15; the human-intervention / contest safeguards are Article 22(3). Whether GDPR confers a hard standalone **right to explanation** of an individual decision is genuinely contested in the legal literature (Article 22 omits the phrase; it is assembled from Arts. 13–15 + Recital 71) — treat "meaningful logic + a route to contest" as durable and "guaranteed per-decision explanation" as contested. The caution against step-by-step reasoning traces as faithful explanation is NN/g (Chan, Dec 2025) — recent, single-source-but-named, and a deliberate reversal of earlier "show the steps" intuition; it tempers reasoning UI rather than forbidding it. Citation mechanics are detailed in the sibling file `ai-ux/uncertainty-citations.md`.
