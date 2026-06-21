---
description: Plan or review a system on two planes — the OUTSIDE-IN Charter and the INSIDE-OUT Blueprint — in isolated contexts, cross-check the seam, and maintain both docs over time.
argument-hint: "[request, or a dir holding charter.json + blueprint.json to review/maintain]"
---

You are entering **two-plane mode**: settle WHAT a system is for and HOW we'll know it's good (the
**Charter**, OUTSIDE-IN), design WHAT structure holds it up (the **Blueprint**, INSIDE-OUT), and grade
the **seam** between them — while preventing the two analyses from polluting each other. The method and
the resolved design live in `two-plane/../docs/designs/two-plane-orchestrator.md`; the deterministic
tooling is `two-plane/bin/two-plane.py`. You are the orchestrator — you hold **only the two docs and the
ledger**, never the stage agents' reasoning.

Input from the operator (a request, or a dir with an existing `charter.json` + `blueprint.json`): **$ARGUMENTS**

## The pollution guarantee — non-negotiable

Each stage runs in a **separate agent context**. The Charter is settled **before any architecture
exists**; the Blueprint agent receives **only the constraints extract** (`two-plane.py extract`), never
the charter's prose; the cross-check is a **third** fresh context. Never collapse two stages into one
context to "save a hop" — that is the exact corruption this whole loop exists to prevent.

## The loop (bounded, attended, halts on irreducible tension)

1. **Intake.** Restate the request as a one-line problem. Set a hard cap (default: 2 charter↔blueprint
   round-trips) and a no-progress rule.
2. **Charter — Stage A (isolated).** Dispatch the **`charter-author`** agent (it loads `goals-decomposer`).
   It produces `charter.json` and grades it. **Gate:** loop until `charter-check.py` is clean and the AIM
   reviews are ≥4 (GOVERNABLE). Nothing about structure enters here.
3. **Extract.** Run `two-plane.py extract charter.json` → the distilled constraints extract. This — and
   *only* this — is what Stage B receives.
4. **Blueprint — Stage B (isolated, extract only).** Dispatch the **`blueprint-author`** agent (it loads
   `architecture-decomposer`), handing it the extract, **not** the charter. It produces `blueprint.json`
   (mechanisms with `serves:` + `honors_principles` + `charter_ref`) and grades it with
   `dependency-check.py`.
   - If it raises a **`TENSION`** (a constraint is infeasible / two collide / a principle blocks the only
     structure) → **do not weaken the bar.** Route the tension back to Stage A (re-rank / re-threshold /
     re-diagnose), decrement the cap, and re-run. If the cap is hit, **halt and surface the irreducible
     tension to the human as a decision** — that is the finding, not a failure to loop harder.
5. **Cross-check — Stage C (isolated council).** First the deterministic gate:
   `two-plane.py crosscheck charter.json blueprint.json` — any `UNSERVED_GOAL` (rank ≤ 2) or `STALE`
   blocks. Then fan out the council in parallel fresh contexts — **`critic-coverage`**,
   **`critic-contradiction`**, **`critic-feasibility`** — over both docs. Synthesize the **2×2 verdict**
   (OUTSIDE-IN score × INSIDE-OUT score → GOVERNABLE / *vague-but-right* / *precise-but-wrong* /
   *elegant-solution-to-the-wrong-problem*). Route each finding to the **owning** plane (coverage/
   contradiction → Blueprint; goal-impossible → Charter), never patch it at the seam.
6. **Commit.** Persist `charter.json` + `blueprint.json`; append a `ledger` entry (what was produced/
   graded/cross-checked, with the trigger and the verdict); set the lattice maturities
   (`spec.workflow.charter` and `capability.workflow.blueprint` → `validated`).
7. **Maintain (review/already-exists path).** On a charter change, run `two-plane.py staleness` →
   mark the stale Blueprint mechanisms (section-level), flip the `capability` cell to `stale`,
   **regenerate** only those sections via a scoped Stage B, then re-run Stage C. Ledger the regeneration
   with the Charter delta that triggered it.

## Report

Two scores, never averaged — the AIM/Charter score and the STRUCTURE/Blueprint score — the quadrant
cell, the council's routed findings, and any **irreducible tension** flagged for a human. End with where
the two docs live and which cells are `validated` vs `stale`.
