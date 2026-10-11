# Plan-doc executor live run, goal 002 (2026-10-11)

Driver: Sonnet high, one background sub-agent, started with the `/goal complete build and verify <plan-doc.md>` line. Plan: `.sdlc/plan-reliability-docs/plan-doc.md`. Tree base: 0eba072f.

## Result
Stopped at step 1 with exit 4 and state written, about 5 to 6 minutes, 9 driver turns, one solo sub-agent (about 100k tokens, no dollar figure reported). The plan was stale: goal 002's steps were built by T-0411 to T-0417 after the plan was written, so step 1's solo found every field, note and selftest label already present and made no change. The stop line named the cause and the resume command. Nothing was built twice, nothing pushed, no product file edited by the driver. Design section 8.1 item 5 (a plan that builds work) is therefore not exercised; items 2 to 4 (rehearsal, crash drill, guardrail probes) are not run: unverified.

## What the run showed
1. Stop behavior works as designed: a plan defect stopped the run with state written instead of improvising.
2. Gap: a step already built has no rule. The driver rightly refused to close it itself; the executor needs a rule for "step already satisfied" (verifier or `plan_done` check on the red criterion being green before any build).
3. Gap: a named teammate cannot spawn a named sub-agent ("Teammates cannot spawn other teammates"); the run rules say to spawn the printed JSON unchanged. The driver dropped `name` and the spawn gate accepted it. Any step will hit this when the driver is itself a sub-agent.
4. Gap: the run reports no dollars; the final record lacks the cost figure the design requires.
5. `fanout.py prep` printed `run_in_background: true` with `SDLC_HEADLESS` empty; harmless here.

Files: `.sdlc/plan-reliability-docs/plan-state.json`, ticket T-0435 (closed, no work).
