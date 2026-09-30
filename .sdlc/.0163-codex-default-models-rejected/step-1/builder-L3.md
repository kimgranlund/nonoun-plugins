<!-- role=builder level=L3 model=opus effort=high recovered-from-log: run.sh was edited during this run and exited without writing the result -->
## Status
done

## Changes
- `plugins/sdlc-lite/adapters/codex/models.json`: every `gpt-6-sol` is now `gpt-6-astra` and each level keeps its effort. Scout L1 is still `gpt-6-luna` `high`. Added `"verifier_alternates": {}`.
- `plugins/sdlc-lite/scripts/codex_roles.py`:
  - New `config()` and `verifier_alternates()` accessors. `models()` now returns role entries only.
  - `definitions()` yields `sdlc-verifier-lN-alternate` only when the alternates map has an entry for that level's model.
  - `resolve()` returns `(model, effort, shared)`, and the CLI prints a third token `shared` when the verifier shares the builder's model.
  - `generate` deletes orphan `sdlc-*.toml` files, and `generate --check` reports them as drift.
  - No `gpt-6-*` literals remain in the file.
- `plugins/sdlc-lite/scripts/run.sh`:
  - The Codex resolve block reads `model effort shared`.
  - When shared, the result header gets ` shared_with_builder=yes`.
  - `runs.jsonl` gets a boolean `shared_with_builder`, which is false on the Claude path. The Claude defaults and the Claude verifier switch are unchanged.
- `plugins/sdlc-lite/scripts/codex-selftest.py`:
  - Replaced `test_verifier_uses_different_model` with `test_verifier_shares_builder_model_without_alternate`, `test_verifier_alternate_comes_from_config` and `test_runner_records_shared_verifier_model`.
  - The stub CLI has a new `verdict` mode that emits `## Verdict` / `pass`.
- `plugins/sdlc-lite/adapters/codex/agents/*.toml`: regenerated. 11 profiles changed from `gpt-6-sol` to `gpt-6-astra`. `sdlc-verifier-l1-alternate.toml`, `-l2-alternate.toml` and `-l3-alternate.toml` were deleted by `generate`.

## Checks
- **Red first:** I ran the three new selftests against the old code before the fix: 2 errors and 1 failure.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`: generated 19 definitions and removed the 3 alternates.
- **Negative control for the orphan check:** I added a dummy `sdlc-fake-l9.toml` and ran `generate --check`. It exited 2 with "generated agent drift: orphan …". I then removed the file.
- All acceptance criteria were run from the repo root with `SDLC_BASE_SHA=4198ff19…`, and every one passed:
  - `! grep -qF gpt-6-sol …/models.json`
  - `verifier_alternates` is a dict
  - (guard) every level keeps its effort compared with base
  - (guard) the scout luna line is unchanged
  - `! grep -qF gpt-6- …/codex_roles.py`
  - `resolve verifier L1` with an astra builder prints `gpt-6-astra medium shared`
  - In a temp copy with `{"gpt-6-astra": "gpt-6-terra"}`, `resolve verifier L1` prints exactly `gpt-6-terra medium`.
  - `! grep -rlF gpt-6-sol …/agents`
  - (guard) `generate --check`
  - (guard) no orphan agent files
  - `grep -qF shared_with_builder …/run.sh`
  - The three new tests and (guard) `test_definitions_match_shared_contracts`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: all 20 tests OK.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: PASS.
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: OK.
- `python3 plugins/sdlc-lite/scripts/check.py`: ok (18 role levels, 8 agents).
- `bash -n plugins/sdlc-lite/scripts/run.sh`: ok. `git diff --check`: ok.

## Notes
- No change was needed in `codex_exchange.py`. It still adds `-alternate` only when the resolved model differs from the default, so a shared verifier uses `sdlc-verifier-lN` and a configured alternate uses the generated `-alternate` profile.
- Step 2 (docs) still has stale references to the removed alternates and to `gpt-6-sol`:
  - `plugins/sdlc-lite/adapters/codex/instructions.md` line 22, the "alternate profiles that enforce a different model" sentence. It is embedded in every generated TOML, so it has to be regenerated after editing.
  - `docs/codex-role-execution.md`: "22 project agent definitions, including three alternate verifier models" (there are now 19). The live-run note on line 74 also names `sdlc-verifier-l1-alternate`.
  - `docs/validation/native-codex-smoke.json` hashes the deleted alternate TOMLs. It is historical evidence, and whether to leave it is step 2's call.
- The `models.json` defaults were changed and not run live. No live Codex run was made in this step.
