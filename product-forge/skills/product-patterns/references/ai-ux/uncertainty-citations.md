---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Page Laubheimer, 'AI Hallucinations: What Designers Need to Know', Nielsen Norman Group (nngroup.com/articles/ai-hallucinations), 2025-02-07"
  - "Megan Chan, 'Explainable AI in Chat Interfaces', Nielsen Norman Group (nngroup.com/articles/explainable-ai), 2025-12-12"
  - "Georgia Kenderova, Maria Rosala & Tanner Kohler, '10 Guidelines for Designing Your Site's AI Chatbots', Nielsen Norman Group (nngroup.com/articles/ai-chatbots-design-guidelines), 2026-04-24"
---

# Uncertainty, Citations & Honest Framing

A generative model is confidently wrong on a schedule no other software component is. It produces fluent, plausible output whether or not the underlying claim is true, and the fluency itself is a trust signal the user cannot help reading. This reference is about closing the gap between how _certain_ the output sounds and how _reliable_ it actually is: surfacing confidence and uncertainty, attaching citations the user can check, surfacing errors and hallucinations rather than hiding them, and framing the product's capabilities honestly. The goal is **calibrated trust** — the user trusting the AI exactly as much as it deserves on this particular output, neither blindly nor cynically.

> The framing to hold onto, from NN/g: a hallucination is "output data that seems plausible but is incorrect or nonsensical" — presented "with unwarranted confidence." The design problem is not that the model is sometimes wrong; all systems err. It is that the model is wrong _without changing its tone_, so the interface has to supply the doubt the output omits.

This is an **emerging area**, but a comparatively well-grounded one: NN/g has published specific, named-author research on hallucinations, explainability, and chatbot disclaimers. Where a recommendation rests on a single study or a single source's framing, it is labeled.

---

## Surfacing uncertainty

The model's confidence in its prose is not evidence of correctness, so the interface must add an honest signal. NN/g's hallucinations research (Laubheimer) gives three concrete forms, in descending order of precision:

1. **First-person uncertainty language.** Phrasings like "I'm not completely sure, but…" — NN/g found this "more effective than generalized uncertainty statements." Hedge in the voice of the assistant, on the specific claim, not in a blanket disclaimer.
2. **Numeric confidence.** A rating such as "68% likely" alongside the output, useful "particularly in high-stakes domains like healthcare and law" — but only meaningful when the underlying probabilities are real and comparable, not invented.
3. **Categorical confidence.** "High / Medium / Low" labels when precise percentages "aren't reliable," explicitly to avoid "false precision."

A fourth technique NN/g names is **consistency checking**: generate multiple responses to the same prompt and flag disagreement, since "discrepancy can be brought to the user's attention." Divergent answers are themselves an honest uncertainty signal.

| Lever | Good — honest signal | Bad — false signal |
| --- | --- | --- |
| **Where the hedge lives** | On the specific uncertain claim, in first person | A blanket "AI may make mistakes" in the footer |
| **Numeric confidence** | Shown only when probabilities are real | A fabricated "94% confident" that means nothing |
| **Categorical fallback** | High/Med/Low when precision is unwarranted | False precision ("87.3%") the model cannot back |
| **Disagreement** | Surface when multiple generations diverge | Silently pick one and present it as settled |

---

## Citations and sources

Citations let the user verify rather than trust — but only if they actually resolve and actually support the claim, and AI-generated citations frequently do neither. NN/g (Chan) is blunt: "citations are often hallucinated and point to nonexistent URLs," and even real links may "lead to unreliable sources or to unrelated articles that do not actually support the claim." The implication is not "skip citations" — it is "design them so the user can and will check." NN/g's specific recommendations:

- **Place the source next to the claim it supports** — not in a lump at the end — so the user can map evidence to assertion.
- **Link to the relevant part of the source** to "reduce the interaction cost" of verifying.
- **Style citations distinctly** from the main response so they read as checkable references, not decoration.
- **Avoid vague link labels** like "Source"; name what the link is.
- **Set realistic expectations** by indicating that sources may be inaccurate — because a citation also functions as a (sometimes false) trust signal.

```text
The deadline moved to March 14.¹                    ← claim
   └─ ¹ [Project kickoff notes → "Timeline" section]   ← source next to claim,
                                                          links to the exact part,
                                                          named (not just "Source")
```

The trap to avoid: a citation _raises_ perceived trust whether or not it is real. An interface that shows authoritative-looking sources the user never clicks has manufactured confidence, not earned it. Design citations to be _checked_, and make checking cheap.

---

## Surfacing errors and hallucinations

Because the model will be confidently wrong, the interface should encourage verification at the moments it matters and degrade honestly when it does not know. NN/g's load-bearing finding on disclaimers: generic small-print warnings become "background clutter" and "fail to change user behavior." Honest error-surfacing is therefore specific, contextual, and paired with an action — not a blanket banner. NN/g's chatbot guidelines reinforce placement: a disclaimer should sit "prominently in the main interface, ideally near the input box," use "clear, direct language," and be "paired with an action" the user can take.

| Lever | Good — honest about error | Bad — hiding error |
| --- | --- | --- |
| **Disclaimer** | Specific, contextual, near the input, with an action | Generic footer fine-print that becomes clutter |
| **When unsure** | "I couldn't find a reliable source for this" | A confident invented answer |
| **Verification** | Prompts the user to check high-stakes claims | Presents everything with equal, total confidence |
| **Recovery** | An easy path to correct or report a wrong answer | No way to flag or fix an error |

---

## "Show your work" — a grounded caution

The instinct to make the AI explain its reasoning — a step-by-step "here's how I arrived at this" — is intuitive and, per the most recent NN/g research, **often counterproductive**. Chan's explainable-AI guidance advises designers to "avoid using step-by-step explanations that imply certainty or transparency," because "explanations are often unfaithful to the model's actual computation": the walkthrough may omit real factors or adjust its justification when the user pushes back. A reasoning trace that looks like an audit of the model's thinking is frequently a plausible story generated _about_ a conclusion, not the cause of it — and presenting it as transparency manufactures exactly the overtrust the rest of this reference fights.

NN/g's recommended substitute is to "use alternative explanation strategies, such as providing relevant sources and clarifying the model's limitations." In other words: replace the fictionalized internal monologue with the two things a user can actually verify — **the sources behind the claim** and **an honest statement of what the system can't do.** This is a single-source-but-named finding (NN/g, Dec 2025) and a recent reversal of earlier "explainability = show the steps" intuition; flag it as such, but it is the current best-sourced position and it should temper any "add a reasoning panel" instinct.

---

## Honest capability framing

Calibrated trust starts before the first answer, in how the product describes itself. NN/g recommends using "onboarding, tooltips, and empty states to honestly communicate what the AI is good at and where it might struggle" — naming the domains where it is reliable and the ones where it is still weak. The failure mode is a product whose marketing and empty state promise omniscience, so every confident-but-wrong answer reads as a betrayal rather than a known limitation. Underclaiming has a cost too — a capable tool described so timidly that users never try its strengths — but in practice overclaiming is the dominant and more damaging error, because it converts the model's inevitable mistakes into broken promises.

---

## Anti-patterns

- **Uniform confidence.** Every answer delivered in the same assured tone, regardless of how shaky the underlying claim is — the fluency-as-truth trap.
- **Decorative citations.** Authoritative-looking sources that don't resolve, don't support the claim, or sit in an end-lump the user never checks — manufactured trust.
- **False precision.** A numeric "94% confident" with no real probability behind it — a fabricated stat, worse than no number.
- **Footer fine-print.** A generic "AI can make mistakes" disclaimer that NN/g shows becomes background clutter and changes no behavior.
- **Reasoning-as-proof.** A step-by-step explanation presented as a faithful account of the model's computation when it is a post-hoc narration (NN/g) — overtrust dressed as transparency.
- **Capability overclaim.** Onboarding and marketing that promise more than the model delivers, turning every error into a broken promise.

---

## The scoring test: is trust calibrated or manufactured?

1. **Uncertainty is visible and honest.** Does the UI signal when the model is unsure — in first person, on the specific claim, with confidence levels only where the probabilities are real? Or is everything delivered with uniform confidence?
2. **Citations are checkable.** Are sources placed next to the claims they support, linked to the relevant part, distinctly styled, and named — or are they decorative end-matter the user never verifies?
3. **Errors surface, don't hide.** When the model doesn't know, does it say so? Are disclaimers specific, contextual, and actionable rather than generic fine-print?
4. **No reasoning theater.** Does the product avoid presenting a step-by-step "chain of thought" as a faithful explanation, favoring verifiable sources and honest limits instead (NN/g)?
5. **Honest capability framing.** Do onboarding and empty states name what the AI is good and bad at — or do they promise omniscience the model can't deliver?

A product passes when a careful user ends up trusting it _exactly as much as it deserves_ on each answer — checking the shaky claims, relying on the solid ones. It fails when fluent prose, decorative citations, or a plausible reasoning trace manufacture more confidence than the output has earned.
