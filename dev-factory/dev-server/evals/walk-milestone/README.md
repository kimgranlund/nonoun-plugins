# Walk milestone — the answer key

`replay.py` is the **Walk-phase milestone** (TDD §19): proof that the *factory* — not a human — can drive
a vertical slice to `done`. Where Crawl showed a human driving one cell through the API, Walk turns the
30s heartbeat on at Tier 1 and lets it run: the compass selects, the dispatcher provisions a worktree +
runs a worker + invokes the critic, the lease recovers crashes — all bounded by a budget it *surfaces*
rather than burns. Passing this is the precondition the trust ladder reads to permit **Tier 2**.

Answer key (kept outside the fixture so a cold judge run stays honest):

| Check | Claim |
|---|---|
| **W1** | both tickets reach `done` driven only by `heartbeat.on_tick()` — the replay calls no transitions after triage; every claim/dispatch/validate/close is the loop's. |
| **W2** | **readiness order** holds: ticket B (whose dependency is A's target cell) is *not* dispatched until A's cell validates. The compass gates on the partial order, in code. |
| **W3** | **bounded by construction**: an exhausted window (past deadline) HALTS dispatch — the loop surfaces the ceiling, it does not burn through it (the spec's Failure 4; harness-forge's I-9 arming discipline, dev-native). |
| **W4** | **no reward-hack**: a worker cannot forge a signal mid-run (`gate-signal` denies it); every validated cell carries a critic-minted signal; false-pass is honestly `unmeasured` (no refuter incident), never a fake 0%. |

## Unattended, by construction

The heartbeat calls the **same** `api.transition_ticket` a human drag does — the loop is the scheduler
calling the API, not a parallel code path. So "unattended" is the same gated, ledgered, single-writer
path, just triggered by the clock. The replay proves it by calling *only* `on_tick()` after the operator
triages the tickets to `active`.

## The DispatchAdapter (OD-003)

Two adapters ship: the deterministic **`MockAdapter`** (a real subprocess, no live model — what this
milestone and CI use) and the live **`HeadlessClaudeAdapter`**, pinned against the June-2026 Claude Code
docs (`claude -p --add-dir <worktree> --allowedTools … --permission-mode acceptEdits --max-turns N
--max-budget-usd N --output-format stream-json --settings <gates>`). The dispatcher wires the dev-kernel
gates into each worktree's `.claude/settings.json`, so the immutable boundary is active *inside* the
worker run; gate denials emit the structured `permissionDecision: deny` (and exit 2) for cross-runtime
compatibility.

## Run it

```bash
python3 dev-factory/dev-server/evals/walk-milestone/replay.py   # exit 0 = Walk met
```

Stdlib + `sqlite3` only — the MockAdapter needs no FastAPI and no live model.
