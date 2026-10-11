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

## Rehearsal in this repo (`.sdlc/plan-doc-hardening/plan-doc.md`, two L1 steps, Sonnet low driver)
Result: `plan_done.py` exits 0 and prints `plan done` after six driver sessions and five stops. Step 1 (T-0436) was built by a solo, independently verified (pass, re-run once for the missing record), landed and merged. Step 2 (T-0437) was built by a solo (4a59f78c) and landed by hand-cherry-pick. No driver edited a product file, asked the user, or pushed. Dollars: no script prints a total; the one priced verifier re-run was about $0.07. Unverified: the crash drill and guardrail probes (design 8.1 items 3 and 4), and the `/tmp` scratch rehearsal (it cannot work, see 2).

Stops and their causes, each a rule or script gap, none a driver error:
1. A named teammate driver cannot spawn a named sub-agent. Fixed in `run-rules.md` (9e542876).
2. The host builds sub-agent worktrees from origin/main (a9d42334 after the push), not local HEAD. A claim commit that is not on origin is invisible to the solo, so `fanout.py land` refuses (T-0437). A driver started outside the plan's repository gets a worktree of the wrong repository.
3. `plan_done.py stop` leaves a sticky record; nothing clears it, so a resume needs hand removal of `plan-state.json`.
4. `dispatch.py recover --root .` rewrites about 25 old closed-ticket attempt files, which dirties main and blocks `git merge --ff-only`.
5. A non-fast-forward merge of the integration branch leaves `fanout/<date>` behind and the next `fanout.py prep` refuses.
6. A closed ticket landed with no verifier record on main (it sat in the abandoned solo worktree) makes `plan_done.py` read `no independent verifier pass`.
7. `plan_check.py` accepts only `K-<n>` ids in Done when; a `M-` id passes only if the target text is named. A measure command that prints `path:count` (git grep -c) is `unreadable`.
8. The ticket template defaults to size L2 and status proposed; the run rules do not say which fields to set from a step.
9. Earlier: a step already built has no rule (first run); the stop path itself worked.

Follow-up: one fix ticket for items 2 to 8 (T-0438).
