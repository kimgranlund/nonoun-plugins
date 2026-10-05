# Codex fanout live run

Recorded: 2026-10-04. One live run of `fanout.py run` with `SDLC_BACKEND=codex` and one size S ticket in one lane. It closes the limit "no Codex lane was run" from `docs/validation/fanout-solo-live-run.md` for the single-lane, size S case only.

## What ran

- Plugin code: commit `8684437` of this repository (`git rev-parse --short HEAD` in the worktree), plugin version 0.20.7. `codex --version`: `codex-cli 0.160.0`; `codex login status`: `Logged in using ChatGPT`.
- Throwaway project in a `mktemp -d` folder outside this repository, with a stub package `kit` (`kit/a.py`), a one-test suite, and one ticket stamped by `tickets.py new` and edited to size S: add `clamp(value, lo, hi)` to `kit/a.py` with tests. `codex_roles.py install` put the 28 generated agents under the project's `.codex/agents`. `steps.py lane .sdlc/clamp` printed `solo` (reason: size S decides before planning).
- Hidden check [`hidden.py`](codex-fanout-live-run/hidden.py), eight cases, kept beside the project and named in no prompt.
- Command, with every `CLAUDE_CODE_*`, `CLAUDE_PLUGIN_*`, `CLAUDECODE` and `SDLC_*` variable removed from the environment first, then `SDLC_BACKEND=codex SDLC_HEADLESS=1` set: `python3 <plugin>/scripts/fanout.py run --lanes-dir <dir>/lanes --integration fanout/codex --stagger 0 --gate "python3 -m unittest discover" a=T-0001`.

## Result

- Exit 0, 39 seconds (`start.txt` 22:56:22, `end.txt` 22:57:01). The lane printed `lane solo tier S`, the driver started, the lane commit `7d2205a`, the merge `0260403` and `close T-0001` (`a9f74bf`) are in [`integration-log.txt`](codex-fanout-live-run/integration-log.txt) and [`run-output.txt`](codex-fanout-live-run/run-output.txt).
- Hidden check on the integration tree: `hidden_check: 8/8 passed`, exit 0 ([`hidden-check.txt`](codex-fanout-live-run/hidden-check.txt)).
- The ticket closed with the skips guard live: [`skips.md`](codex-fanout-live-run/skips.md) holds the lane line and the planner and filer `## Skipped` entries that `steps.py lane` writes.
- The solo started through the wrapper on Codex. [`runs.jsonl`](codex-fanout-live-run/runs.jsonl) holds one record: `role` solo, `level` L1, `model` `gpt-6.1-sol`, `effort` low, `backend` codex, `transport` exec, `exit_code` 0, `duration_ms` 38032, `turns` 1, usage 106,994 input tokens (77,952 cached) and 663 output tokens, `cost_usd` null with `cost_reason` "codex reports no cost". The cost is null, not zero, as designed.
- The solo reported adding `clamp` and tests and running `python3 -m unittest discover -s tests` (3 tests passed), see [`lane-a-T-0001-log.txt`](codex-fanout-live-run/lane-a-T-0001-log.txt) and [`diff.txt`](codex-fanout-live-run/diff.txt).

## Limits

- The model and effort come from the run record the wrapper wrote (the tier table in `adapters/codex/models.json`), not from a Codex rollout. No rollout for this run was found under `~/.codex/sessions` (the newest file there was from 13:36 that day), so `agent_role` and `turn_context` were not read. The model is declared, not independently observed.
- The gate was vacuous. `python3 -m unittest discover` ran 0 tests, because the fixture's `tests/` folder is not a package, so the gate passed on nothing. The solo ran its own tests with `-s tests` and they passed, and the hidden check ran outside the lane, so delivery is shown, but the gate is not.
- The fanout report line says `Lane for T-0001: solo (tier S: sonnet low)` although the Codex tier ran (`report.md`). That label is a display defect in `fanout.py`'s report text; the run record has the right model.
- Scope: one lane, one size S ticket, one run, one machine. The size M path, the batched verifier for tiers M and L, parallel lanes, the lane cap and the stagger were not exercised on Codex here.
- Cost is unknown: Codex reports none. Only token counts exist.
- Not a conductor run. The conductor start on Codex is in `docs/validation/codex-conductor-solo-live-run.md`.
- Trailing whitespace was stripped from the copied evidence files so `git diff --check` passes; nothing else in them was edited.
