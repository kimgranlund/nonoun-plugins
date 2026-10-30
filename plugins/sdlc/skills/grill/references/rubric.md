# Rubric — ratified design (the skill's output)

> Scores a "Ratified Design" (DECISION SPACE · AXES · DECISIONS · GROUNDING · OPEN · RATIFIED DESIGN) for
> whether grilling derived the load-bearing decisions from both axes and stopped at the right place.
> Scale 1–5; `[gate]` = mechanically checkable, `[review]` = judgement with cited evidence. 2026-06-28.

| # | Dimension | Type | What it checks | 1 (fail) → 3 (adequate) → 5 (excellent) |
|---|---|---|---|---|
| D1 | Both-planes coverage | [gate] | DECISIONS name forks on **both** Structural `[S]` and Mechanism `[M]` axes | 1: one plane only (all `[S]` or all `[M]`) · 3: both present, one thin · 5: both planes fully worked, every decision axis-tagged |
| D2 | Decision leverage | [review] | The forks grilled were the highest-cascade / load-bearing ones, asked in leverage order | 1: trivia asked, a cascading fork left to default · 3: mostly load-bearing · 5: every round the highest-leverage open forks, none silently defaulted |
| D3 | Option grounding | [gate] | Every option was concrete — traceable to a codebase / catalog / token / constraint fact | 1: abstract forks (rubber-stampable) · 3: mostly grounded · 5: every option anchored to a named fact, GROUNDING section cites them |
| D4 | Cascade discipline | [review] | Each round's answers visibly **reshaped** the next round's surface (not a pre-planned checklist) | 1: flat questionnaire, rounds independent · 3: some reshaping · 5: every round derived from the prior answers; the cascade is explicit |
| D5 | Convergence | [gate] | Grilling stopped at a settled surface — no over-grilling, no load-bearing fork left unhosted | 1: over-grilled past convergence OR a cascading fork reached handoff open · 3: roughly right · 5: stopped exactly at settled; deferred forks each carry a default |
| D6 | Handoff readiness | [review] | `decompose` could run **both** planes from the Ratified Design without re-grilling | 1: a load-bearing fork still open · 3: usable with gaps · 5: both planes decomposable verbatim, structure + mechanisms named |

**Gate to promote:** D1, D3, D5 must each score ≥ 3. A ratified design that grills only one plane (D1),
asks the author to commit to abstract options (D3), or stops short / over-grills (D5) is worse than no
grilling — it launders an under-explored design as a settled one.

**Checker exception (D1 · D3 · D5):** no script ships. D1's grep-trivial slice — both `[S]` and `[M]`
tags present — certifies nothing: one token of each would pass while a whole plane ships hollow, so the
gate is both planes *worked*, a read. D3's fact-traceability and D5's settled-surface call are meaning
no grep can reach. They gate by adversarial read with cited evidence; `[gate]` here marks the must-pass
promote bar, not a machine check.

**Top failure to look for first:** running a single axis (D1) — a Structural-only or Mechanism-only
session looks thorough but ships the blindness of the plane it skipped; and abstract, ungrounded options
(D3) that get rubber-stamped, deferring the decision under the appearance of making it.
