<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
fail

## Criteria
- #1 The report shows a run.sh chain and a solo run that finished on Codex with validated result files (results.py validate output included): fail. Evidence: the chain half holds. I reran `results.py validate --role <r>` on the copied `planner-L1.md`, `builder-L1.md`, `verifier-L1.md` and `verifier-L1-2.md`, and all four exit 0. Validating `verifier-L1.md` with `--role builder` exits 1 ("header role=verifier does not match --role builder"), so the check bites. Every copy under `docs/reports/codex-live-evidence/` is byte-identical to its original in `/tmp/codex-live-0316/.sdlc/greet/` except the two files with em dashes replaced (diffed line by line). The run rows have `backend codex`, the models and efforts the report gives, and the same durations (96174, 37638, 80298, 38429 ms). The solo half cannot be met as written. The solo row has `"file": ""`, and `results.py validate --role solo` exits 2 with "invalid choice: 'solo'" because `results.py` has no solo schema (`ROLES` at results.py:66). The solo run itself did finish on Codex: `role solo, model gpt-6.1-sol, effort low, backend codex, transport exec, exit_code 0, duration 81818 ms`, and `/tmp/codex-live-0316` reruns `python3 -B -m unittest discover -s tests` with 3 tests, OK. The report says plainly that no solo result file exists. This half is a plan defect, not a build defect.
- #2 Any failure is recorded with its log path and filed as a ticket: fail. Evidence: the "recorded with its log path" part holds. The failed first verifier is recorded with its original path `/tmp/codex-live-0316/.sdlc/greet/step-1/verifier-L1.log`, and the copied `verifier-L1.failed-attempt.log.txt` is identical to it. The "filed as a ticket" part does not. The report's last bullet says "none were filed" and lists three candidates. `git status --porcelain` shows no new ticket folder. Steelman: the builder could answer that solo may not file tickets. That rule is real (`plugins/sdlc-lite/agents/solo.md:57` says "Never publish, push, open a PR, or file a ticket"), but the parent or conductor can file them before close. The criterion is therefore satisfiable and still unmet, so the fail stands.
- #3 No model or effort value changed; `codex_roles.py generate --check` passes: pass. Evidence: `git diff --stat HEAD -- plugins/ scripts/` is empty, and `git status` shows only added files under `docs/reports/`. In this tree `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` printed "Codex agent definitions verified" and exited 0. Negative control: in a throwaway worktree at `$SDLC_BASE_SHA` I changed the first `"low"` in `adapters/codex/models.json` to `"medium"`. `generate --check` then exited 2 with "generated agent drift: .../sdlc-builder-l1.toml". The worktree was removed afterwards.

## Out of scope changes
None. All tracked changes are new files under `docs/reports/codex-live-evidence*`, which the ticket's Do names. The untracked `.sdlc/0316-codex-live-evidence/{base-sha,runs.jsonl,skips.md,verifier-L2.attempt.json}` are runner and lane records, not project changes. Other checks:
- `git diff --check HEAD`: no output.
- Em dash grep over the report and the evidence folder: no matches.
- Every local link in the report resolves; each was tested with `test -e`.

## For the next attempt
plan defect: #1 asks for the solo run to have validated result files, but `results.py` has no solo role (`--role solo` is an invalid choice) and `solo_run.py` writes none (solo row `"file": ""`). Only the chain half can pass. Reword #1 to require validated result files for the chain plus the solo `runs.jsonl` row with exit 0 and a rerun of its done check.
Still needed in the build: file the three failure candidates listed at the end of `docs/reports/codex-live-evidence.md` as tickets:
1. solo has no result file that can be validated.
2. The red-checkpoint was marked retrospective even though the builder recorded its controls before editing.
3. `loaded_context` shows `rollout absent` on `codex exec` runs.

The parent or conductor files them (solo.md:57 forbids solo from filing), and the report's last bullet should then be updated to cite the new ticket ids. The first verifier fail was caused by the operator, not the plugin; filing it is optional, but the report should say why it was not filed.
