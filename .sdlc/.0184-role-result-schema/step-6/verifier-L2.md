<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Required-strings loop (`## Environment`, `## Commands`, `## Evidence`, `## Limits`, `run.sh builder L1`, `exit 3`, `exit 0`, `rebuild L1`, `verify L1`, `invalid result`): pass. Evidence: I ran the loop on `docs/reports/role-result-schema-live-run.md` and nothing printed as MISSING. I checked that the strings sit in the right sections by reading the doc. The check can go red because `grep -qF` on an absent string exits 1, but I did not run a negative control.
- Date regex `2026-[0-9]{2}-[0-9]{2}`: pass. Evidence: grep matched (c2ok). The doc has `2026-10-01` under `## Environment`, as the Do requires.
- (guard) allowed-files check: pass. Evidence: I ran the full guard command from the handoff and it printed c3ok. The only new file outside `.sdlc` is the doc. I did not run it in a worktree at the base SHA. Every other changed file is on the allow-list and belongs to earlier steps.
- Do requirement: the live evidence is real and matches the doc. Evidence:
  - Arm 1 (malformed rerun): in the kept probe project, `.sdlc/t/step-1/builder-L1-2.md` is exactly the header plus `## Changes` and `greet.sh: echo hello world`, with no `## Status`.
  - Its `builder-L1-2.attempt.json` has `"exit_code": 3` and `"status": "failed"`.
  - `run.sh:464-468` emits `run.sh: $role result ... ; see $result` and runs `exit 3` when `results.py validate` fails.
  - I reran `steps.py next` on `t`: `rebuild L1` with the reason `builder-L1-2.md has no done/blocked under ## Status`. That matches the doc.
  - Arm 1 (first try): `t/step-1/builder-L1.md` has `## Status done` plus a Notes section saying the model ignored the override. The doc records this honestly and reruns once, as the Do allows.
  - Arm 2 (structural): `t2/step-1` has its own handoff, a `runs.jsonl` line and a headerless `builder-L1.md`. `steps.py next` printed `invalid result: ... first line is not a <!-- role=... --> header`, then `reason: the newest result does not match its results.py schema; stop and ask the user`.
  - Arm 3 (normal): `steps.py next` on `t3` printed `verify L1`.
  - Environment: `claude --version` printed `2.1.286 (Claude Code)`, `sw_vers` printed `26.6.2`, and `git rev-parse --short HEAD` printed `f45649e`. The SHA-256 hashes of `run.sh`, `results.py` and `steps.py` match the doc's truncated hashes.
  - Housekeeping: `grep -c "—"` on the doc gave 0 em dashes, and `git diff --check` was clean.
  - Limits: the section states the Codex arm is unverified and that the run was one model at one level.
- Builder claims: accepted, each confirmed by the checks above. The builder's note that the throwaway project still exists is also true, since I listed it.

## Out of scope changes
None. The only file this step added outside `.sdlc` is `docs/reports/role-result-schema-live-run.md`. The other modified files come from earlier steps and are on the guard's allow-list. The throwaway project outside the repo is left over, and the builder disclosed it.

## For the next attempt
None.
