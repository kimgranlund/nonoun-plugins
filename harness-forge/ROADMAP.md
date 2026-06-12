# harness-forge — Roadmap

Open structural work, in rough priority. v0.1 is the kernel + the operating roster, validated and selftested; the items below deepen it toward the full factory the foundations describe.

## v0.2 — close the operating loop in the user's project

- **The seed-into-loop gate installer.** `/harness-seed` currently scaffolds `.harness/` state; extend it to *wire the blocking gates into the user's worker loop* — install `gate-signal` as a PreToolUse(Write|Edit) deny on the protected verifier set, plus the budget/no-progress gate and the `emit-ledger` feedback hook, into the project's own `.claude/settings.json` (with the user's consent). The plugin session stays advisory; the user's autonomous loop gets the blocking enforcement the model requires.
- **`emit-ledger` + `propagate-staleness` as project hooks.** Ship the two remaining gateverb scripts (feedback that injects fast-check findings into the loop; the staleness cascade as a write-time graph effect) and the installer that wires them.
- **A real first-slice walkthrough.** A recorded end-to-end run (seed → scan → advance an `ontology` + `spec` + `rubric` slice to `validated` → distill) on a toy project, committed under `evals/` as the kernel's behavioral baseline.

## v0.2 — calibration (the catalog standard)

- **Council-calibration fixtures.** Planted-defect harnesses (a rubric-before-spec lattice; a worker-writable signal directory; an unearned-autonomy claim; a frozen/un-regenerating lattice) + concept-regex checkers, proving `harness-evaluate` and the `lattice-auditor` catch each — the calibration discipline the other catalog plugins carry, with the recall corpus gated by `check-recall.py`.
- **`bin/` behavioral gates in CI.** The three selftests already run; add a fixture that builds a `.harness/` with a planted partial-order violation and asserts `lattice.py validity` flags it (the gate proves itself on a real defect).

## v0.3 — the structural-critic council

- **A harness critic council.** The catalog's adversarial-review house style, but keyed to the model's failure-mode clusters (a verifier-integrity critic, a reward-hacking critic, a partial-order critic, an autonomy-trajectory critic, a budget/cost critic, a staleness critic, a naming-discipline critic) + an orchestrator — fanned out in parallel isolated contexts. Structural, not named-practitioner (that lens lives in `agent-ops`), to keep the boundary clean.

## v0.3+ — the kernel / kit / instance tiers

- **Family kits.** The foundations name three tiers — invariant machinery (kernel), family bindings (kit), accreted project state (instance). v0.1 is the kernel. Ship **kits**: a `harness-forge-kit-*` family binding (seed corpora, family rubrics, harness adapters) for a concrete domain (a research loop, a coding loop, a docs loop), imported as precedent and marked as such.
- **Harness adapters.** Pluggable verifier adapters (pytest, link-check, screenshot-diff, llm-judge) bound to rubric cells, so a cell's `validate` step routes to a real check by configuration, not by prose.
- **A `lattice render` view.** A derived, human-readable lattice grid (layers × scopes, color by maturity) — a status surface over `lattice.json`, the canonical state staying the JSON.

## Known limitations (v0.1)

- The blocking gates ship as `bin/` tools but are not yet auto-installed into the user's loop (the v0.2 installer).
- The probe-cost ranking falls back to a constant until the ledger accrues history (by design — measured, not estimated).
- No family kits yet — the kernel is domain-agnostic; cold-start precedent must be authored per project until kits land.
