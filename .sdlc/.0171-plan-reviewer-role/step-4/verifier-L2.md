<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `resolve plan-reviewer L1` equals "gpt-6-astra high": pass. Evidence: ran it, `test` exited 0.
- Astra `planner-L3.md` fixture gives "gpt-6.1-sol high": pass. Evidence: printed `gpt-6.1-sol high`, exit 0.
- Sol `planner-L2.md` fixture gives "gpt-6-astra high": pass. Evidence: printed `gpt-6-astra high`, exit 0. This is the negative case: no alternate when the models differ.
- Both plan-reviewer TOML files exist: pass. Evidence: `test -f` on both exited 0.
- Alternate `model = "gpt-6.1-sol"` and base `sandbox_mode = "read-only"`: pass. Evidence: both `grep -qx` matched, exit 0.
- models.json `plan-reviewer.L1 == ['gpt-6-astra','high']`: pass. Evidence: the python check exited 0. The diff adds only that one line, after `verifier`, and `verifier_alternates` is untouched.
- `test_plan_reviewer_alternate_follows_newest_planner`: pass. Evidence: "Ran 1 test, OK". Bite: copied the new selftest into a detached worktree at `$SDLC_BASE_SHA` and it went red (errors=1). Read the test body: it asserts the astra case gives `('gpt-6.1-sol','high',False)`, the sol case gives `('gpt-6-astra','high',False)`, the patched-empty-alternates case gives `('gpt-6-astra','high',True)`, and the alternate definition's model, effort and sandbox.
- `test_runner_records_plan_reviewer_alternate_agent`: pass. Evidence: "OK", and it printed the two response files `plan-reviewer-L1.request.response.json` and `plan-reviewer-L1-2.request.response.json`. Bite: red at base (failures=1). The test asserts the request agent is `sdlc-plan-reviewer-l1-alternate` with model `gpt-6.1-sol`. It asserts exit 0, a `model=gpt-6.1-sol` header, and a runs.jsonl record with `shared_with_builder` false. The negative control asserts `sdlc-plan-reviewer-l1` with `gpt-6-astra`.
- `grep -qF PAIRED codex_exchange.py`: pass. Evidence: exit 0. The diff at `codex_exchange.py` reads `if role in codex_roles.PAIRED and model != default_model:`.
- `grep -qF plan-reviewer instructions.md`: pass. Evidence: exit 0. The diff shows "a verifier or plan-reviewer alternate profile".
- docs count and table row: pass. Evidence: both greps exit 0. The diff shows "24 project agent definitions: 20 base ... four alternate", the `| Plan reviewer | Astra high |` row, and the added alternates sentences.
- SKILL.md name and HARNESS-NOTES count: pass. Evidence: both greps exit 0.
- (guard) `codex_roles.py generate --check`: pass. Evidence: printed "Codex agent definitions verified".
- (guard) full `codex-selftest.py`: pass. Evidence: "Ran 22 tests in 14.754s, OK", exit 0. The builder's claim that existing tests are unchanged matches the diff, which has only added lines in `codex-selftest.py`.
- (guard) changed-files allowlist: pass. Evidence: the pipeline exited 0. The non-agent files changed against base are `docs/codex-role-execution.md`, `HARNESS-NOTES.md`, `instructions.md`, `models.json`, `codex-selftest.py`, `codex_exchange.py`, `codex_roles.py` and `SKILL.md`, all in the allowlist. The rest are `adapters/codex/agents/*.toml`. The two new plan-reviewer TOMLs are also under that glob.

Extra checks:
- `python3 scripts/check-packaging.py` printed PASS.
- `python3 plugins/sdlc-lite/scripts/check.py` printed "ok: 19 role levels, 9 agents checked".
- `git diff --check` was clean.
- The throwaway worktree was removed (`git worktree list` shows only the main tree).

## Out of scope changes
None. The 22 existing TOMLs changed only by regeneration, since the prelude text lives in `instructions.md` (the diff stat is 30 files, all in scope). The builder's note that the `run.sh` comment around line 217 still describes only the verifier is left alone by design, since `run.sh` is not in this step's file list.

## For the next attempt
None
