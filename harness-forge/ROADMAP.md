# harness-forge — Roadmap

Open structural work, in rough priority. v0.2 is the kernel + the operating roster + the consent-wired loop, validated and selftested; the items below deepen it toward the full factory the foundations describe.

## v0.2 — close the operating loop in the user's project

- ~~**The seed-into-loop gate installer.**~~ **Shipped in 0.2.0** — `bin/wire.py` (plan/apply/check/unwire, consent-gated, idempotent, self-protecting) + `/harness-seed` step 4. Still open from this line: the **budget/no-progress gate** as a wired hook (today budgets are policy the orchestrator enforces; a Stop-hook that halts a loop on budget exhaustion / repeated failure signatures is unbuilt).
- ~~**`emit-ledger` + `propagate-staleness` as project hooks.**~~ **Shipped in 0.2.0** — both gateverb species, selftested, wired by the installer.
- ~~**A real first-slice walkthrough.**~~ **Shipped in 0.2.1** — `evals/first-slice-walkthrough/replay.py` (CI) + `RUN.md`; it caught the seed's circular-verifier deadlock at authoring time. Still open: stamp default `budget` fields at seed (the positive-control baseline's one real weakness, H5).

## v0.2 — calibration (the catalog standard)

- ~~**Council-calibration fixtures.**~~ **Shipped in 0.2.1** — `evals/calibration/`: four planted-defect fixtures + `check_fixtures.py` (the gates catch each defect; a clean control passes) + five judge baselines in `runs/` gated by `check_baselines.py` (concept recall, incl. the injection-quoted-not-obeyed assertion).
- ~~**`bin/` behavioral gates in CI.**~~ **Shipped in 0.2.1** — the planted partial-order violation is `fixtures/rubric-before-spec/` (caught by `lattice.py check`); the failing-verifier-does-not-advance case is in `validate.py selftest`; the walkthrough is the end-to-end positive.

## v0.3 — the structural-critic council

- ~~**A harness critic council.**~~ **Shipped in 0.3.0** — the 7 structural critics + the `harness-council` orchestrator + `/harness-council`, with a live calibration run recorded against the unearned-autonomy fixture. Still open: convene the council against the remaining three fixtures (one live baseline exists; N=4 is the full set), and a `/harness-council` lens-subset smoke in CI.

## v0.3+ — the kernel / kit / instance tiers

- **Family kits.** The foundations name three tiers — invariant machinery (kernel), family bindings (kit), accreted project state (instance). v0.1 is the kernel. Ship **kits**: a `harness-forge-kit-*` family binding (seed corpora, family rubrics, harness adapters) for a concrete domain (a research loop, a coding loop, a docs loop), imported as precedent and marked as such.
- **Harness adapters.** `bin/validate.py` (v0.1.1) already runs a cell's verifier *command* and mints the signal from its exit status — the runner exists. Add pluggable, named verifier adapters (pytest, link-check, screenshot-diff, llm-judge) bound to rubric cells by configuration, so a cell's `validate` step selects a real check by name, not by the operator typing the command each time.
- **A `lattice render` view.** A derived, human-readable lattice grid (layers × scopes, color by maturity) — a status surface over `lattice.json`, the canonical state staying the JSON.

## Known limitations (v0.2)

- The blocking gates are installed **only by consent** (`wire.py apply`, offered by `/harness-seed`) — an unwired project's protection is the worker's narrow tool scope plus discipline, and `wire.py check` says which state you're in. A worker holding `Bash` can still route around any path-glob gate; keep workers Bash-less.
- The wired hook copies in `.harness/hooks/` refresh on re-`apply`, not automatically on plugin update (`wire.py check` WARNs on drift).
- The probe-cost ranking falls back to a constant until the ledger accrues history (by design — measured, not estimated).
- No family kits yet — the kernel is domain-agnostic; cold-start precedent must be authored per project until kits land.
