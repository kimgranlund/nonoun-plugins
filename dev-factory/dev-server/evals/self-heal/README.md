# self-heal — answer key

`replay.py` proves decision #123 ("full self-heal + new oracle"): a refuter-caught false pass is REPAIRED in code, not merely flagged. It seeds a deliberately hollow capability — `index.mjs` exports `deal` as a function (so it passes its own gate `typeof deal === 'function'`) but `deal(3)` returns `[]` (so it fails the hidden refute `deal(3).length === 3`) — plus an app integrator validated against it, then drives `dispatch.run_refuter` once and asserts the full loop.

| # | Asserts |
| --- | --- |
| **H1** | the false pass is CAUGHT (`run_refuter → False`) and the existing safety net still fires — one incident recorded, autonomy demoted to tier 0 |
| **H2** | the refute is FOLDED into the gate — the cell's `verify.mjs` now enforces `deal(3).length === 3`, the check the worker was gaming |
| **H3** | a FRESH independent refuter is re-armed — a different harness whose checks do NOT reuse the consumed ones; the verify-spec `generation` advances 0→1 |
| **H4** | the cell drops `validated → regenerating` (re-author against the tougher gate) AND its dependent app drops `validated → stale` (UN-SHIPPED) |
| **H5** | after re-authoring (re-validation), the cell RE-ENTERS the refuter frontier — the fresh oracle re-measures the new validation epoch (the loop closes; it is not a one-shot) |

The bounded backstop is the existing `no-progress → block` breaker (proven by `evals/stop-gate`): a cell that cannot pass the strengthened gate stops; it never loops forever. The "new oracle" deterministic floor is generic invariants (`verify_gen.fresh_refute`); the live path overrides it with planner-authored edge cases.

Needs `node` (the refuter runs a real harness); skips with exit 0 if node is absent. The mechanism is also unit-covered by `dev-server/verify_gen.py selftest` (the pure fold/re-arm transform) and `dispatch.py selftest`.
