---
description: Scan the modality axis at the lattice's frontier scope — surface the open/stale cells (the gap set). Detects gaps; does not rank them.
argument-hint: "[optional: --dir .agents/harness]"
---

Scan the frontier. **$ARGUMENTS**

Run `python3 "${CLAUDE_PLUGIN_ROOT}/bin/lattice.py" scan --dir .agents/harness` — it sweeps the nine modality layers at the lattice's frontier scope and returns every cell whose maturity is open (`absent` / `defined` / `instantiated`) or `stale`. This is a deterministic graph computation, so it is a script, never inference.

Then invoke **`harness-build`** to read the gap set as a wavefront: a missing **whole layer** (no `rubric` at this scope, no `ledger` schema) is a higher-order gap than a missing slug. Completeness tells you what is missing; it does not tell you what is real — that is `/harness-next`'s job. Do not start filling cells here; scanning detects, ranking selects.

Note any `stale` cells: an upstream change flipped them, and a stale asset actively misdirects every consumer that trusts it — they are not optional cleanup.
