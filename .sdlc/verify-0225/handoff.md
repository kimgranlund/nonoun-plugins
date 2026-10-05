# Verify T-0225: solo cost capture

## Goal
Independently verify `git diff main...HEAD` on branch solo-cost (T-0225): `scripts/solo_run.py` starts the solo agent and records its cost, so the budget gate and the board count the default lane.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0, and it can fail: inject each of three defects in a throwaway copy of the script (record a missing cost as zero, write no record when the session crashes, change a tier's effort) and show the selftest exits non-zero for each. Do not edit the branch's file.
2. `solo_run.py run` appends one `role solo` line to `<task-dir>/runs.jsonl` in the run.sh record shape (ts, role, level L1..L3, model, effort, cost_usd, usage, duration_ms, turns, attempt_id, backend, transport, routing_reason); `cost_usd` is the result's `total_cost_usd`, and it is null with `cost_reason`, never zero, when the result has no usage, no result event exists, or the backend is Codex. A refusal (bad tier, bad backend, no handoff.md) writes nothing.
3. `budget.py` counts the solo record without a change to its spend logic: a solo cost of 8.5 on a budget of 10 reports `warn` at 85 percent, two such runs report `over`, and a null-cost solo record is counted in `unmetered_runs`. Check by running `budget.py` and `board.py` against a seeded ticket, not only by reading the selftest.
4. `agents/solo.md` names `solo_run.py` as the start path and keeps the raw command as a labelled fallback; the tier table is unchanged and agrees with `fanout.py` SOLO_TIERS and `solo_run.py` TIERS. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and its item 25 fails when a tier, a required phrase in solo_run.py, or the solo.md mention is changed (show each).
5. `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (run it once); `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0; the three regenerated `adapters/codex/agents/sdlc-solo-l*.toml` match `agents/solo.md`.
6. `docs/validation/solo-cost-live-run.md`: every number and claim (0.1315212 equals the result event's total_cost_usd, exit 0, 3/3, 9 turns, 14996 ms, 1163 output tokens, budget status 0.13 of 5 at 2 percent, board cell `$0.13/$5 2%`, model `claude-sonnet-5-5`, 18 seconds) is backed by a committed file under `docs/validation/solo-cost-live-run/`; none of those files is gitignored (`git check-ignore`); `docs/README.md` links the record; no em dash appears in the changed text files; `git diff --check main..HEAD` is clean.
7. Scope: the branch changes no model or effort default, does not touch `fanout.py`, `steps.py`, `tickets.py` or `run.sh`, and `docs/maintenance/sdlc-internals.md` states honestly that fanout solo lanes are not metered yet.

Report each criterion pass or fail with the command and its output, then a verdict.
