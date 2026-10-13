# Fixture: plan-doc run

A written fixture, not a recorded session. Date in the session: 2026-10-12.

Turn 1 user: Run the plan doc `docs/plans/export-csv.md` to completion. Goal: ship CSV export for the invoices page.
Turn 2 agent: Preflight passes. The plan doc has 5 steps; `plan-state.json` shows 0 done.
Turn 3 user: Standing rule: never push without asking me first.
Turn 4 user: Second rule: keep every commit under 200 changed lines.
Turn 5 agent: Step 1 (`export/schema.py`) is built and verified, pass.
Turn 6 agent: Step 2 needs a delimiter. Options: comma or semicolon.
Turn 7 user: Comma. Excel users in the US are the main readers.
Turn 8 agent: Recorded: user 2026-10-12 picks the comma delimiter. Step 2 is built and verified, pass.
Turn 9 agent: Step 3 first build failed: `test_export_dates` is red, the dates were local time.
Turn 10 agent: I chose UTC ISO 8601 dates, since the API already returns UTC. Step 3 rebuilt and verified, pass.
Turn 11 user: Fine. Skip the streaming writer for now, files are small.
Turn 12 agent: Recorded: user 2026-10-12 drops the streaming writer from scope.
Turn 13 agent: Step 4 (`export/view.py`) is building on branch `feat/export-csv`. 2 files are dirty.
Turn 14 agent: Open question: must the export include voided invoices?
Turn 15 user: I need to ask finance. Hold that, continue with step 4.
Turn 16 agent: Step 4 is built; the verifier has not run. Step 5 (docs) is not started.
Turn 17 user: I am about to compact. Next is the step 4 verify.

## Probe questions

1. Which delimiter does the export use? Expected: comma (turn 7).
2. May the agent push the branch after step 4 passes? Expected: no, ask first (turn 3).
3. How large may one commit be? Expected: under 200 changed lines (turn 4).
4. Is the streaming writer in scope? Expected: no, dropped by the user (turn 11).
5. What is the next action and what is still open? Expected: verify step 4; the voided-invoices question waits on finance (turns 14 to 17).
