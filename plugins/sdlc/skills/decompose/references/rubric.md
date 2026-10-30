# Rubric — a decomposition (the skill's output)

> Scores a cleared decomposition (node tree + action set + host map + manifest) for soundness and
> hand-off readiness. The mechanical coverage gate is `scripts/coverage_check.py` (D1); D2–D6 are the
> judgement the script cannot do. Scale 1–5; `[gate]` = mechanically checkable, `[review]` = judgement
> with cited evidence. 2026-06-26.

| # | Dimension | Type | What it checks | 1 (fail) → 3 (adequate) → 5 (excellent) |
|---|---|---|---|---|
| D1 | Coverage gate | [gate] | `coverage_check.py` exits 0 — no `UNHOSTED` / `DANGLING` / `UNJUSTIFIED-LEAF` | 1: script red or not run · 3: exit 0 · 5: exit 0 with every host and `justify` explicit |
| D2 | Plane independence | [review] | The two planes were derived separately (the action set is not read off the node tree) | 1: one plane copied from the other (map is tautological) · 3: mostly independent · 5: demonstrably independent — the planes contradicted and the contradictions were resolved |
| D3 | MECE | [review] | Parts mutually exclusive (no overlap) and collectively exhaustive (no gap) | 1: overlapping or gappy · 3: mostly · 5: every part disjoint; the children fully describe the parent |
| D4 | Granularity | [review] | Every leaf/action is one-responsibility/one-owner — neither over- nor under-decomposed | 1: leaves hide seams, or split past an owner · 3: mostly right · 5: each part directly buildable/assignable, none manufacturing coordination cost |
| D5 | Grounding | [review] | Nodes name real responsibilities; actions name real needs — not the intended implementation | 1: invented parts / solution smuggled in · 3: mostly grounded · 5: every node a real responsibility, every action a real need |
| D6 | Hand-off readiness | [review] | Structure → SPEC/LLD and actions → acceptance/tests, with no reshaping | 1: not authorable · 3: usable · 5: feeds the spec family directly |

**Gate to promote:** D1 **and** D3 must each score ≥ 3 — a decomposition that fails the coverage script,
or isn't MECE, is not sound regardless of the rest.

**Top failure to look for first:** a plane read off the other (D2). It passes the coverage script
*trivially* — the host map is a tautology — while the cross-check has learned nothing. The deterministic
gate cannot catch this; the reviewer must.
