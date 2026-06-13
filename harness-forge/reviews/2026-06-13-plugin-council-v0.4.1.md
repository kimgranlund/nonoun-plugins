# harness-forge — focused council on the v0.4.1 fix (verify the global-bound mechanism)

A **focused** plugins-factory red-team (5 critics whose lenses own the new safety-critical code) against v0.4.1 — the release that fixed the v0.4.0 convergent Critical (the autonomous loop's global caps were prose). The discipline: *you do not let the author's own fix to a convergent Critical ship unreviewed.* It found a genuine Critical the three prior councils could not have seen — the mechanism is new in 0.4.1.

| Critic | Lens | Dispatch ID | Headline |
| --- | --- | --- | --- |
| Chip H. | determinism boundary | `a53093ea38d87917a` | enforcement moved to code; the bound is now *armed* by inference (the must-run `start`) |
| Simon W. | blast radius | `a48456cd3fa173aa5` | **the budget file is writable by the worker the gate bounds — not in the protected set** |
| Scott W. | illegal states | `aec30229356248715` | `budget.json` is the only durable `.harness/` state with no schema and no `check` |
| Andrej K. | verifiable or vibes | `ac22a4e3cc76591cc` | the eval starts the budget in-process; it proves *enforcement*, not *bounding* |
| Charity M. | observability | `a83fd777574e3b044` | the dashboard shows the numerators, not the caps — a coroner, not a monitor |

## Verdict: the wall-clock enforcement is real and credited; the fix relocated the determinism gap rather than closing it, and left the bound's own file unprotected.

## CC1 — Critical (Simon): the budget file is not protected → a worker can lift its own ceiling

`gate-signal`'s `DEFAULT_PROTECTED` covers signals, rubrics, hooks, the ledger, `lattice.json`, and the wiring — but **not `.harness/run/budget.json`**, the file whose contents decide whether *every* write in the project is allowed. The advancer (tools: `Edit, Write`) can write it a far-future `deadline_ts` + null caps → `run_budget_exhausted` returns never-exhausted → `gate-budget` waves every write through. The bound is enforced by a file the bounded agent can edit. → **Fixed (one line):** `.harness/run/*` added to `DEFAULT_PROTECTED` (segment-anchored, so a user's own `run/` dir stays writable); selftest asserts `.harness/run/budget.json` is deny-on-write. The budget file is now a verifier asset like the signals it gates.

## CC2 — the arming gap (Chip Critical + Andrej Major): enforcement is code, initialization is inference

`gate-budget` only denies once a budget exists; the orchestrator must call `run-budget.py start` at step 0. Skip it (context rot, an injected "skip step 0", or forgetting) → no budget → fail-open → unbounded. The v0.4.0 pattern moved one inch: *enforcement* was prose, now *initialization* is. And `evals/global-bound/check.py` starts the budget **in-process** — so it proves "given a started budget, the gate enforces it," not "the loop is bounded"; the claim "physically cannot write past its budget" hides the precondition "*once a budget is started*." → **Fixed by scoping + hardening, not by pretending it's fully mechanical** (the gate genuinely cannot distinguish a loop-write from manual editing, so it cannot fail-closed without a budget): every "cannot write past its budget" claim now carries the precondition "once a run is armed — the orchestrator arms it (discipline); the gate enforces it (code)"; `run_budget_start` rejects a **vacuous** budget (all-null caps — there must be a real cap); the eval now drives the **CLI** and asserts the no-budget state surfaces as *unbounded*; and `/harness-status` **alarms** when a budget is absent.

## CC3 — Major (Scott): the run budget is untyped

`budget.json` is the only durable `.harness/` state with no schema and no `check()` — permitting deadline-before-start, zero/negative/string caps (→ `TypeError` → fail-open → silently unbounded), non-ISO deadlines. → **Fixed:** new `schemas/run-budget.schema.json` (the 5th schema); `lattice.py check` validates `budget.json` when present (types, `deadline ≥ start`, caps ≥ 1); `run_budget_start` rejects bad values at the writer. The ISO-timestamp comparisons now **parse** (offset-robust) instead of string-lexicographic (Scott M2).

## CC4 — Major (Charity): the dashboard omits the caps

`/harness-status` showed iterations/cells *so-far* but never the caps, so it could show "7 iterations" with no hint the cap is 8 — and "no active run budget" read benign when it could mean "running unbounded now." → **Fixed:** `run_budget_exhausted`'s detail carries `max_iterations`/`max_cells`; the dashboard renders `7/8 iterations · 3/8 cells · 4m to deadline` and **alarms** on a missing budget. Streaming (a push signal) and a run-budget liveness/PID marker (the stale-budget-after-crash case) are ROADMAP.

## Credited as genuinely fixed (the council's PASS)

The block decision is ledgered; the gate-fire count is wired correctly end-to-end (Charity traced it — "not observability theater"); `scan_frontier` marks blocked cells; the **wall-clock axis is real and ungameable by a miscounting agent**; `gate-budget` fails *open* correctly on every error path (a stop-gate that bricked on a hiccup is worse than the runaway); the deny-event append cannot fail the hook or recurse. The v0.4.0 "global caps are prose" finding is dead at the enforcement layer.

## Tamper-evidence (Simon M1, partial)

The orchestrator can still `clear`/`start` its own budget (it genuinely needs to end runs) — fully mechanizing that is ROADMAP. 0.4.2 makes a *reset of an active budget* tamper-evident: `run_budget_start` over an unexhausted active run ledgers a `budget-reset` event with a distinct actor, so a self-extending loop is at least visible in the append-only trail.
