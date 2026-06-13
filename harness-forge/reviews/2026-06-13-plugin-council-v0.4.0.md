# harness-forge — plugins-factory council red-team (v0.4.0, the bounded loop)

The 9-critic **plugins-factory** council, run cold in parallel isolated contexts against v0.4.0 — the third dogfood red-team, scoped to the highest-risk surface the catalog has shipped: an autonomous loop that edits files (`/harness-run`) + a new wired blocking hook (`gate-budget`). The agent IDs below are this run's real dispatch handles (the evidenced-artifact discipline from the 0.3.1 CV3 fold).

| Critic | Lens | Dispatch ID | Headline |
| --- | --- | --- | --- |
| Boris C. | context cost | `a0667cc70bac75c53` | the orchestrator is a `while`-loop wearing an agent's always-on description |
| Steve Y. | granularity / naming | `ac273b49bfb1221d6` | `block`/`unblock` are off the operation vocab the plugin's own thesis polices |
| Elon M. | delete-first | `a885e777e794eece7` | the loop is a script; the eval proves it runs agent-free |
| Charity M. | observability | `a7cbe16fd4745862e` | the running loop is a black box; the block decision is unledgered |
| Andrej K. | verifiable or vibes | `aea3fea7481227f08` | "bounded by construction" is half code (per-cell), half prose (global) |
| Simon W. | blast radius | `a40d9a5c1c9ba7f78` | the global caps are prose; `gate-budget` enforces none of them |
| Scott W. | illegal states | `acf1d88b38b375ef9` | `blocked_reason` without `blocked` is a representable illegal state |
| Chip H. | determinism boundary | `ae71f2b9e3cddabd9` | loop termination is a computation routed to inference |
| David F. | packaging / CI | `a569b4e129ef36f65` | the un-CI'd global-cap half of "bounded" is sold as evidenced, undisclosed |

## Verdict: the per-cell breaker is real; "bounded by construction" overclaims the global caps. Make the global bound code.

The convergent PASS, stated by name across the panel: the **per-cell** stop-gate is genuinely wired and behaviorally proven — `evals/stop-gate/check.py` drives detect → block → rank-drop → deny from the *installed* hook with no model in the loop, and the critics credited it unprompted. The packaging (P4/P5/P8), manifest sync, fail-open polarity of both blocking hooks, and the `gate-budget` path-match were each **refuted as defects with evidence** by the critics who chased them.

## CC1 — The convergent Critical: the GLOBAL caps are prose, not code (Andrej · Simon · Chip · David; Charity adjacent)

Four critics independently grepped `bin/` and the hook wiring and found the same hole: `max-cells`, `max-iterations`, and `wall-clock` exist only in `agents/harness-builder.md` and `commands/harness-run.md` as instructions the *orchestrator model* "ticks" in its own context. There is **no code counter, no `time` deadline, no `Stop`/`SubagentStop` hook** — `gate-budget` keys solely on the per-cell `blocked` flag. So the terminator of an unattended loop is a model counting and comparing: the exact CV4 pattern (a computation routed to inference) that 0.3.1 fixed for the *detector*, restated at the loop level — the point of maximum blast radius. Chip's sharpest cut: `skills/harness-build/SKILL.md` says *"Three pieces, all code"* when the middle piece (the orchestrator running the loop under caps) is a model agent.

→ **Fixed (the mechanism, not just the claim).** `bin/run-budget.py` (new, selftested) persists `.harness/run/budget.json` `{start_ts, deadline_ts, max_iterations, max_cells}` at loop start; **`gate-budget` now also denies *every* worker write once the run budget is exhausted** — `now > deadline_ts` (wall-clock, pure code, no counter), or ledger-counted `validate` events since `start_ts` ≥ `max_iterations`, or validated-since-start ≥ `max_cells`. The global ceiling is now a thing the loop *physically cannot write past*, enforced by the same hook as the per-cell stop. `evals/global-bound/` proves an exhausted run denies a write with **no model agent** — the eval Chip said "cannot be written," made writable by building the mechanism. The honest-scope is applied precisely until/where code doesn't reach (the orchestrator still *decides* to stop gracefully; the gate is the hard floor it can't exceed).

## CC2 — Charity's Critical: the running loop is unobservable, and the block decision is unledgered

`/harness-run` surfaces nothing until it halts; `gate-budget`'s denials are mute (exit 2 + stderr, no event/counter); and the loop's most important decision — `lattice.py block` — **leaves no trace in either ledger path** (it's a Bash subprocess, so `ledger.append` isn't called and the `Write|Edit`-only `emit-ledger` never sees it). `/harness-status` was deferred from 0.3.1 to the release *after* the loop that needs it.

→ **Fixed.** `lattice.py block`/`unblock` now ledger the event (the halt decision is recorded); `gate-budget` denials append a countable `deny` event; **`/harness-status`** ships (a cheap, no-agent read: maturity histogram + frontier + last-N ledger + wiring/drift verdict + run-budget status + gate-fire count); and the MCP `scan_frontier` now excludes/marks blocked cells (it had been advertising a blocked cell as open work, contradicting `rank`).

## Converged Majors → dispositions

- **Steve W. (Critical, in his lens) — `block`/`unblock` are off the closed `operation` vocab** the plugin's self-hosting naming thesis is built to forbid; `council` was added as a ledgered ontology revision in 0.3.0, these weren't. → **Fixed:** added to `schemas/naming.schema.json`'s `operation` vocab as a ledgered revision; the `block` *object* vocab disambiguated from the `block` *verb*.
- **Scott W. — `blocked_reason` without `blocked` is a representable illegal state.** → **Fixed (band-aid) + ROADMAP:** `lattice.py check()` now flags a `blocked_reason` with no `blocked`; the full discriminated-union refactor (`block: {reason}`, making it unconstructable — the same move already roadmapped for signal/maturity) is ROADMAP.
- **Elon M. (Critical, in his lens) — "the orchestrator is a script."** → **Partially refuted, core accepted.** The loop genuinely needs an agent for the `Task` dispatch of fresh-context advancers (a `bin/` script can't spawn sub-agents — the deletion would lose the Ralph-discipline isolation). But his *core* — the caps must be code, not the agent's prose — **is** CC1, and it's fixed there. The orchestrator stays; its global caps are now mechanically enforced by `gate-budget` + `run-budget.py`, so its description earns its keep (it manages a real, code-bounded run). Boris C.'s always-on-cost concern is disclosed, not deleted.
- **Simon W. / David F. doc fixes:** the `/harness-seed` consent step named "three hook copies" → now **four**, naming `gate-budget` (a blocking hook the user approves into their settings); `wire.py`'s usage docstring "WARNs on drift" → "fails on drift" + the vestigial `warns` list removed (the 0.3.1 CV1 fix made drift a hard exit-1).

## Refuted with evidence (the council did its own work)

The two-blocking-hooks-brick-the-loop risk (both fail open on parse/missing-lattice/unmapped-path — Simon); the `gate-budget` suffix over-match (full-path tail, not a basename — Scott); the drift gate covers all 5 wired copies (David, who then flagged the *selftest* only drifts `_lattice.py` — folded as a hook-drift selftest case); manifest sync, version, and counts clean (Scott, David).

## The honest framing the panel kept invoking

The plugin already holds itself to "say which state you're in; don't overclaim mechanical" (for `wire.py check`) and "don't read judge-baselined as judge-verified" (CV3). The panel's lesson: apply it to *every* safety slogan. After this fold, "bounded by construction" is true where code reaches (per-cell + the wall-clock/iteration/cell global ceiling) and scoped where it doesn't (the orchestrator's graceful stop is its discipline; the gate is the floor).
