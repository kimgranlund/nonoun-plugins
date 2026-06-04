---
date: 2026-05-16
---

# Improvement Roadmap

For maintainers and contributors to this skill. Documents the highest- leverage improvements identified after authoring, ranked by impact. Update as items are completed or as new gaps surface.

## Meta-caveat

This skill was authored in a single session against a theoretical model. The 5-wave structure, cascade scoring, adversarial pass, and rubric dimensions are all **untested against real repos at the time of authoring**. The most valuable improvements are not new features — they're empirical validation of what's already here.

Resist the temptation to expand surface area (more rubric dimensions, more repo-type adaptations, more wave variants) before validating what's specified. Adding to an unmeasured system multiplies the unknowns.

---

## Priority 1 — Build an eval harness with a reference corpus

**Status:** Not started

**Leverage:** Highest. Unblocks every other improvement. Currently the skill has no objective signal for whether its output is good.

**Concrete work:**

1. Assemble a corpus of 5–10 reference repos covering diverse types:
   - One framework / library
   - One application
   - One CLI tool
   - One API service
   - One monorepo
   - One small (<10k LOC) and one large (100k+ LOC)
2. For each, have an experienced engineer produce a **ground-truth review**: ranked backlog (P0/P1/P2), tier-1 patterns, rubric scorecard. Capture rationale, not just the answer.
3. Build an eval runner that:
   - Invokes the skill end-to-end on each reference repo
   - Captures the produced deliverable tree
   - Scores agent output against the ground truth (recall, precision, ranking correlation)
4. Define an acceptance threshold (e.g., "top-3 P0s overlap ≥2 with ground truth; tier-1 patterns overlap ≥60%; rubric scores within ±1 of human assessment").

**Why this is #1:** Without it, every claim about the skill's quality is anecdotal. With it, the next two items become measurable rather than aesthetic. The eval harness also becomes a regression suite — future changes can be measured for impact.

**Related capabilities:** an eval-framework pattern for defining the harness; an evaluation-campaign orchestrator for running it at scale.

---

## Priority 2 — Calibrate the `priority_score` formula and cascade

**Status:** Specified but unvalidated

**Leverage:** High. The formula is the closest thing this skill has to a "correctness" property, and it's currently hand-wavy.

**The current spec** (from `wave-protocols.md` → Wave 4):

```text
priority_score =
    severity_weight       × blast_radius_weight
  × compounding_factor    × theme_anchor
  × rubric_dim_weight
```

**Known concerns:**

- Five-factor multiplicative scoring produces wild dynamic range. Items that score 0.7 × 0.7 × 1.0 × 1.0 × 0.7 ≈ 0.34 land far from items scoring 4 × 4 × 1.5 × 1.3 × 1.5 ≈ 47. Whether this matches human intuition for "priority distance" is unknown.
- Ties may be common after rounding; tie-breaking by effort is defined but unmeasured for frequency.
- The `rubric_dim_weight` knob is supposed to let repo-type adaptations steer prioritization. Whether weight changes actually shift the resulting ranking in expected ways needs verification.
- The cascade math (a P0 demotion bumping the weakest P1 to P2, etc.) can produce non-obvious final states with 12+ items and 5+ adversarial moves. Audit trail readability has not been tested under load.

**Concrete work:**

1. Run sensitivity analyses on the formula using eval-corpus outputs. Plot score distributions; identify dominating factors; measure tie frequency.
2. Consider simpler alternatives — e.g., a decision tree ("blocker + public-API → P0; major + cross-package → P1; …") that's more defensible in the Tier Boundary Decisions section.
3. Formalize the cascade as a state machine. The current prose instructions for adjudication-then-cascade work for the easy case; they may not survive a complex adversarial pass with simultaneous promotes, demotes, and removals.
4. Add invariant checks at the end of Wave 5c (cascade adjudication):
   - Cap counts hold exactly (3/3/6 or the override)
   - No finding silently vanished
   - Cascade history is traceable per item

---

## Priority 3 — Measure HITL gate friction and tune accordingly

**Status:** Specified at 3 gates per review

**Leverage:** Medium-high. Directly affects whether engineers actually use the skill or skip the gates that give it value.

**Known concerns:**

- Three gates is a lot. If engineers rubber-stamp or skip them, the discovery-confirms-rubric-confirms-cascade chain collapses and the skill becomes one-shot authoring with extra steps.
- Gate questions are currently open-ended ("Anything missing? Anything weighted wrong?"). Open questions take more cognitive load than confirm-or-edit prompts.
- No telemetry exists for which gates get engaged vs. skipped, or which questions get substantive answers.

**Concrete work:**

1. Instrument the skill (where possible) to capture: gate engagement rate, time-on-gate, edit-vs-confirm rate per question.
2. Watch 3–5 real reviews and observe where engineers hesitate, skip, or get frustrated. Note which gates surface useful adjustments vs. which feel like ceremony.
3. Test gate redesigns:
   - **Pre-filled defaults.** "I'll use these weights unless you change them. Press confirm or edit." (vs. "Please choose weights.")
   - **Async batching.** Could Gates #1 and #2 be combined into a single async review with both decisions, presented after Wave 1 + a fast Wave 3 sketch?
   - **Tiered HITL.** Full-gate mode for high-stakes reviews; auto- mode with logged decisions for low-stakes ones. Engineer audits decisions post-hoc rather than gating mid-flight.
4. Decide which gates are non-negotiable (the rubric gate is the strongest candidate — it shapes everything downstream) vs. which can become softer.

---

## Lower-priority items (not in the top 3)

The following are real but lower-leverage. Address only after the top three are complete and grounded in data.

- **Repo-type discovery robustness.** Wave 1's classifier is heuristic. Misclassification cascades. Improve with multi-signal voting and explicit confidence reporting.
- **Sub-agent prompt drift.** Wave 3 dispatches N agents with slightly different briefs. Calibration across agents may drift. Extract a shared core brief + per-dimension delta.
- **Exemplar freshness.** `exemplars.md` cites third-party projects whose patterns may shift. Add timestamps and a periodic verification protocol; consider replacing project-name anchors with abstract pattern descriptions.
- **Before/after sketch implementability.** Verify that an implementing agent has everything it needs from a P0's sketch to actually execute the change without re-discovering context.
- **Graceful degradation at HITL gates.** If the engineer at the gate is junior or distracted, the skill could surface red flags more aggressively, propose stronger defaults, or block on specific ambiguities while waving through others.
- **Output for non-engineering audiences.** The cover memo (`README.md` in the deliverable tree) is currently aimed at engineers. Leadership audiences may need different framing (effort + risk + roadmap impact, not severity + blast-radius).

---

## Anti-priorities (explicitly do not work on these)

- **More rubric dimensions.** The existing 11 aren't proven yet.
- **More repo-type adaptations.** The existing 10 haven't been validated for classification accuracy.
- **More wave variants.** The 5-wave structure is untested. Forking variants before validating the trunk multiplies unknowns.
- **Output-format alternatives** (e.g., consolidated 4-doc mode). Tempting but premature — wait for evidence that the granular tree underperforms before adding alternatives to maintain.

These can become priorities only **after** the eval harness shows specific gaps that more surface area would close.
