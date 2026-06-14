---
description: Rank the gap set — priority ≈ (risk × unlock) ÷ probe-cost, subject to dependency readiness — and name the single next cell to advance.
argument-hint: "[optional: --dir .agents/harness]"
---

Pick the next cell. **$ARGUMENTS**

Run `python3 "${CLAUDE_PLUGIN_ROOT}/bin/lattice.py" rank --dir .agents/harness` — it filters the gap set by **dependency readiness** (the partial order: a rubric is not selectable before its spec validates; a cell binds only to a validated verifier) and orders the survivors by `(risk × unlock) ÷ probe-cost`. Probe cost is read from the ledger once history exists, not estimated.

Invoke **`harness-build`** to confirm the top cell against the **trajectory rule**: advance depth-first along the current thin slice until it validates; widen (new layers, larger scope) only from validated footholds, and rescan the full modality axis at every widening. Selecting a second `defined` cell while the first slice still lacks signal is grid-filling — the enterprise-architecture pathology where everything is specified and nothing is real.

Output one cell-id and the smallest scope that will yield decisive signal, then hand to `/harness-advance`. The probe is sized to the assumption, not the ambition.
