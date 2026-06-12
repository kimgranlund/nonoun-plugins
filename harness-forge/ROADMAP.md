# harness-forge — Roadmap

Open structural work, in rough priority. v0.2 is the kernel + the operating roster + the consent-wired loop, validated and selftested; the items below deepen it toward the full factory the foundations describe.

## v0.2 — close the operating loop in the user's project

- ~~**The seed-into-loop gate installer.**~~ **Shipped in 0.2.0** — `bin/wire.py` (plan/apply/check/unwire, consent-gated, idempotent, self-protecting) + `/harness-seed` step 4. Still open from this line: the **budget/no-progress gate** as a wired hook (today budgets are policy the orchestrator enforces; a Stop-hook that halts a loop on budget exhaustion / repeated failure signatures is unbuilt).
- ~~**`emit-ledger` + `propagate-staleness` as project hooks.**~~ **Shipped in 0.2.0** — both gateverb species, selftested, wired by the installer.
- **A real first-slice walkthrough.** A recorded end-to-end run (seed → scan → advance an `ontology` + `spec` + `rubric` slice to `validated` → distill) on a toy project, committed under `evals/` as the kernel's behavioral baseline.

## v0.2 — calibration (the catalog standard)

- **Council-calibration fixtures.** Planted-defect harnesses (a rubric-before-spec lattice; a worker-writable signal directory; an unearned-autonomy claim; a frozen/un-regenerating lattice) + concept-regex checkers, proving `harness-evaluate` and the `harness-auditor` catch each — the calibration discipline the other catalog plugins carry, with the recall corpus gated by `check-recall.py`.
- **`bin/` behavioral gates in CI.** The kernel selftests already run (naming · lattice incl. `check` · ledger · validate · harness-hook · gate-signal · lattice-mcp); add a fixture that builds a `.harness/` with a planted partial-order violation and asserts `lattice.py validity`/`check` flags it (the gate proves itself on a real defect), and one where `validate.py` runs a deliberately failing verifier and asserts the cell does **not** advance.

## v0.3 — the structural-critic council

- **A harness critic council.** The catalog's adversarial-review house style, but keyed to the model's failure-mode clusters (a verifier-integrity critic, a reward-hacking critic, a partial-order critic, an autonomy-trajectory critic, a budget/cost critic, a staleness critic, a naming-discipline critic) + an orchestrator — fanned out in parallel isolated contexts. Structural, not named-practitioner (that lens lives in `agent-ops`), to keep the boundary clean.

## v0.3+ — the kernel / kit / instance tiers

- **Family kits.** The foundations name three tiers — invariant machinery (kernel), family bindings (kit), accreted project state (instance). v0.1 is the kernel. Ship **kits**: a `harness-forge-kit-*` family binding (seed corpora, family rubrics, harness adapters) for a concrete domain (a research loop, a coding loop, a docs loop), imported as precedent and marked as such.
- **Harness adapters.** `bin/validate.py` (v0.1.1) already runs a cell's verifier *command* and mints the signal from its exit status — the runner exists. Add pluggable, named verifier adapters (pytest, link-check, screenshot-diff, llm-judge) bound to rubric cells by configuration, so a cell's `validate` step selects a real check by name, not by the operator typing the command each time.
- **A `lattice render` view.** A derived, human-readable lattice grid (layers × scopes, color by maturity) — a status surface over `lattice.json`, the canonical state staying the JSON.

## Known limitations (v0.2)

- The blocking gates are installed **only by consent** (`wire.py apply`, offered by `/harness-seed`) — an unwired project's protection is the worker's narrow tool scope plus discipline, and `wire.py check` says which state you're in. A worker holding `Bash` can still route around any path-glob gate; keep workers Bash-less.
- The wired hook copies in `.harness/hooks/` refresh on re-`apply`, not automatically on plugin update (`wire.py check` WARNs on drift).
- The probe-cost ranking falls back to a constant until the ledger accrues history (by design — measured, not estimated).
- No family kits yet — the kernel is domain-agnostic; cold-start precedent must be authored per project until kits land.
