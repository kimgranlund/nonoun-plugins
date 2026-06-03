---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Global `plan-vision` skill — Manifesto archetype (the product adaptation lineage for this file)."
  - "Marty C., *Inspired*, 2nd ed. (Wiley, 2017), ch. on product vision; and *Transformed: Moving to the Product Operating Model* (Wiley, 2024)."
  - "Richard R., *Good Strategy/Bad Strategy: The Difference and Why It Matters* (Crown Business, 2011) — the diagnosis-first spine."
---

# The Product Manifesto

This is the product adaptation of the **Manifesto** archetype from the global `plan-vision` skill — a peer authoring method, restated here for product strategy/vision memos rather than generic systems or architecture writing. A product manifesto is the largest of the four vision forms: it lays out a complete mental model of a product or direction — what it is when you strip it to atoms, the building blocks everything else composes from, the operating principles a team will not break, the phased path from here to the destination, and the single highest-leverage thing to get right first. The reader should finish holding the whole product in their head, and convinced it is inevitable.

> A product manifesto is not a roadmap with feelings attached. It argues a **way of seeing the product** — a thesis the reader probably does not hold yet — and then makes that thesis so well-decomposed it feels like the only sane decomposition. If the reader finishes knowing new features but thinking the same way, the manifesto failed; if they finish with the same facts but a changed model of what the product _is_, it worked.

## When to use it

Reach for the manifesto when you are proposing an entire product, platform, or strategic direction and the audience needs the full picture — founders aligning a company, a product leader resetting a portfolio, a team committing to a multi-year bet. It is the right form when a Reframe would underdevelop the argument (too much rides on the structure and the roadmap to leave them out) and when a Case-For would be too narrowly economic (you are arguing how to _think_ about the product, not just why it pays back). It is the wrong form for a single decision, a single feature, or a quarter's plan — those want a smaller archetype or a spec. Target ~2500–4500 words; below that, you are probably writing a Reframe and should say so.

## The structure

Seven movements, in order. Each constrains the next — the decomposition earns the primitives, the primitives earn the principles, the principles earn the roadmap.

1. **First-principles decomposition (the reduction).** Strip the product to what it _actually is_ when you remove tooling, category convention, and inherited feature-set. Two or three paragraphs, each ending on a sentence that rules something out. Land it in one blockquoted reduced definition — the kind that feels almost trivially true once stated but was not obvious before ("A note-taking app is a capture-and-retrieval system; everything else is composition around capture latency and recall trust"). Then one paragraph on what that reduction makes impossible.
2. **The N essential building blocks (3–7 primitives).** The named concepts the whole product composes from. One sentence framing — "everything else is composition of these" — then one paragraph per primitive: what it is, why it exists, and what follows from its existence. Name them opinionatedly ("Capture Latency," not "Input Performance"); the naming carries the argument.
3. **Platform foundation (usually 3 layers).** The infrastructure claim — the durable surfaces the product stands on (e.g. a data layer, a distribution layer, a trust/permissions layer). What each layer owns and why it is a layer and not a feature.
4. **Core principles (non-negotiable design constraints, 4–6).** Each stands alone, each opinionated, each stating what must be true and why. These are the product's physics, not its preferences.
5. **Operating principles (how the team works, day-to-day).** Shorter than the core principles — bold lead-in, one-paragraph explanation. How decisions get made, what the team optimizes for, what it refuses.
6. **Path forward (a phased roadmap, 3–4 phases with evocative names).** Each phase has a one-line goal, the activities/capabilities it unlocks, and a concrete, verifiable **milestone** that signals the phase is done. The phases should _unfold_ — each implies the next, not merely follows it.
7. **The one thing to get right first.** Two or three paragraphs naming the single highest-leverage decision — the thing the author would lean across the table to emphasize in person. This is where the manifesto's conviction lands hardest.

Close with a **distillation table** (reduced claim → implication) and a short italicized closing aphorism. The table is the argument re-expressed at maximum compression, not decoration.

## The voice discipline

**Thesis-first.** State the way-of-seeing in the subtitle and the reduction; do not bury it under a survey of the market. **Opinionated, not balanced.** The principles are non-negotiable, not options; when you acknowledge an alternative direction, it is to explain why it is wrong, not to be fair to it. A manifesto that gives every option equal weight is a survey, and a survey has no vision. **Physics-literal, not metaphorical.** If you invoke compounding, network effects, switching costs, or retention curves, it must be because the mechanism literally applies and you could compute with it — not because it sounds strategic. **Dense — every paragraph earns its place.** If a paragraph could appear in a manifesto for any product, cut it. The genre's signature quality is a lot of thinking per page. Manifestos can be written in the third-person abstract ("the product does X") which reads more like a physics paper than a pitch, and is usually stronger than a chest-beating "we."

## A short worked product example

**Product:** a developer-facing observability tool, drowning in a crowded "dashboards + alerts" category.

**Subtitle / thesis:** _Observability is a question-answering system, not a chart gallery — and the latency that matters is time-to-answer, not time-to-dashboard._

**Reduction:** Strip away the panels and the alert rules. An observability product exists for one moment: an engineer, mid-incident, asking "what changed?" Everything else is composition around how fast and how trustworthy the answer to that question is. → This rules out the entire "more chart types" roadmap; charts are an output of answering, not the product.

**The primitives (4):** (1) **The Question** — the unit of work is a question an engineer asks under stress, not a dashboard they configured calmly. (2) **Answer Latency** — the time from question to defensible answer; the one curve the whole product optimizes. (3) **Trust Surface** — why an engineer believes the answer at 3am without re-deriving it. (4) **Question Memory** — the system remembers what was asked and answered last incident, so the second occurrence is faster than the first.

**Core principle (one of four):** _No answer without provenance._ Every answer the product gives links to the raw signal it came from, because an untrusted answer under incident pressure is worse than no answer — it sends the engineer down a wrong path with false confidence.

**Path forward:** Phase A "Answer the obvious question" (auto-surface what changed in a deploy window; milestone: median time-to-first-answer under 60s on a real incident) → Phase B "Remember the question" → Phase C "Anticipate the question."

**The one thing to get right first:** Answer Latency on the single question "what changed?" If that one answer is fast and trusted, the product has a reason to exist that no dashboard gallery can copy; if it is slow or doubted, no number of panels will save it. Concentrate the first two quarters there and defer everything else.

Note how the form does the work: the reduction kills a whole category of roadmap before a single feature is debated, the primitives are named so the names carry the thesis, and the "one thing" leaves the reader knowing exactly where to push first.
