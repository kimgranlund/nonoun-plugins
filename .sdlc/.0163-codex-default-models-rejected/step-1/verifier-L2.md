<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `! grep -qF gpt-6-sol plugins/sdlc-lite/adapters/codex/models.json`: pass. Evidence: rc=0. The base `models.json` had `gpt-6-sol` (count 1 in the throwaway worktree at `$SDLC_BASE_SHA`), so the check can go red.
- `verifier_alternates` is a dict: pass. Evidence: python check rc=0.
- (guard) every level keeps its effort against `$SDLC_BASE_SHA`: pass. Evidence: the python guard exited 0. The diff shows the efforts unchanged.
- (guard) scout L1 line: pass. Evidence: `grep -qF '"scout": {"L1": ["gpt-6-luna", "high"]}'` rc=0.
- `! grep -qF gpt-6- plugins/sdlc-lite/scripts/codex_roles.py`: pass. Evidence: rc=0. The diff removes the literals.
- Resolve with a builder header `model=gpt-6-astra` prints `gpt-6-astra medium shared`: pass. Evidence: the `test "$(…)" = "gpt-6-astra medium shared"` check exited 0.
- Configured alternate `{"gpt-6-astra":"gpt-6-terra"}` in a temp copy prints exactly `gpt-6-terra medium`: pass. Evidence: observed output `[gpt-6-terra medium]`, rc=0.
- `! grep -rlF gpt-6-sol plugins/sdlc-lite/adapters/codex/agents`: pass. Evidence: rc=0. `git status` shows the three `-alternate` TOMLs deleted.
- (guard) `codex_roles.py generate --check`: pass. Evidence: "Codex agent definitions verified".
- (guard) no orphan agent files: pass. Evidence: the python check exited 0 on the built tree. Negative control: with a dummy `sdlc-fake-l9.toml` added, the check exited 1, and `generate --check` printed "generated agent drift: orphan …sdlc-fake-l9.toml". I removed the dummy afterwards.
- `grep -qF shared_with_builder plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: rc=0. The diff shows `shared_note` added to the header and the `--argjson shared_with_builder` field in the `runs.jsonl` record.
- `CodexTests.test_verifier_shares_builder_model_without_alternate`: pass. Evidence: "Ran 1 test … OK". I copied the new selftest into a throwaway worktree at `$SDLC_BASE_SHA`, where it ended with `FAILED (errors=1)`.
- `CodexTests.test_verifier_alternate_comes_from_config`: pass. Evidence: "OK" on the built tree, and `FAILED (errors=1)` at base.
- `CodexTests.test_runner_records_shared_verifier_model`: pass. Evidence: "OK" on the built tree, and `FAILED (failures=1)` at base. This is a real `run.sh verifier L1` run through the stub CLI. It asserts the header contains `shared_with_builder=yes` and the `runs.jsonl` record has `shared_with_builder` true.
- (guard) `CodexTests.test_definitions_match_shared_contracts`: pass. Evidence: "OK".
- Builder's claim that all 20 tests pass: pass. Evidence: I ran the full `codex-selftest.py` and got "Ran 20 tests … OK". `run-selftest.sh` printed PASS, `lifecycle-selftest.py` printed OK, and `check.py` printed "ok: 18 role levels, 8 agents checked". `git diff --check` was clean.

I steelmanned each pass. The `models()` change and `runs.jsonl` field are covered by the passing suites. The Claude path is unchanged in the `run.sh` diff (`shared_with_builder` stays `false` there).

## Out of scope changes
None. Every changed file is one the step named. The 11 regenerated TOMLs and the 3 deleted alternate TOMLs come from the step's item 4.

## For the next attempt
None. The builder's note about stale docs (`instructions.md`, `docs/references/codex-role-execution.md`, `docs/reports/native-codex-smoke.json`) belongs to step 2, which the handoff says covers docs. I did not run a live Codex run, because the criteria don't call for one.
