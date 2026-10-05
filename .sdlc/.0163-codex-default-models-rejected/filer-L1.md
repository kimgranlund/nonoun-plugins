<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None. Steps 1 and 2 both have a verifier verdict of pass. Two things to know:
- The step 1 builder result is marked "recovered-from-log": `run.sh` was edited during that run and exited without writing the result. The verifier still passed step 1 from its own checks.
- No live Codex run through `scripts/run.sh` was made. Only stub-CLI checks ran, so the change is not confirmed on a ChatGPT account.

## PR title
T-0163: Use gpt-6-astra for Codex defaults and make the verifier alternate configurable

## PR body
### Summary
On a ChatGPT account, Codex rejects `gpt-6-sol` and `gpt-6-luna` with a 400 and accepts `gpt-6-astra`. This change follows the user's 2026-09-29 decision. Every `gpt-6-sol` default becomes `gpt-6-astra`, with each level's effort kept.

`codex_roles.resolve` used to hardcode a switch to `gpt-6-sol` for the verifier after an Astra build, which the account rejects. That switch now comes from configuration, and the runner records when verification shares the builder's model.

### Changes
- `plugins/sdlc-lite/adapters/codex/models.json`:
  - Every `gpt-6-sol` is now `gpt-6-astra`, with efforts unchanged.
  - Scout L1 stays `gpt-6-luna` `high`. It is outside the decision.
  - New top-level `"verifier_alternates": {}` maps a builder model to the verifier's alternate model. It is empty by default.
- `plugins/sdlc-lite/scripts/codex_roles.py`:
  - No `gpt-6-*` literals remain in the file.
  - New `config()` and `verifier_alternates()` accessors. `models()` returns role entries only.
  - `definitions()` yields `sdlc-verifier-lN-alternate` only when the map has an entry for that level's model.
  - `resolve()` returns `(model, effort, shared)`. The CLI prints a third token `shared` when the verifier keeps the builder's model.
  - `generate` removes orphan `sdlc-*.toml` files, and `generate --check` reports them as drift.
- `plugins/sdlc-lite/scripts/run.sh`:
  - The Codex path adds `shared_with_builder=yes` to the result header when shared.
  - The `runs.jsonl` record gets a boolean `shared_with_builder`, false on the Claude path.
  - Claude defaults and the Claude verifier switch are unchanged.
- `plugins/sdlc-lite/scripts/codex-selftest.py`:
  - `test_verifier_uses_different_model` is replaced by `test_verifier_shares_builder_model_without_alternate`, `test_verifier_alternate_comes_from_config` and `test_runner_records_shared_verifier_model`.
  - The stub CLI has a new `verdict` mode.
- `plugins/sdlc-lite/adapters/codex/agents/*.toml`:
  - 11 profiles moved from Sol to Astra.
  - The three `sdlc-verifier-lN-alternate` files are deleted.
  - The three planner TOMLs are regenerated because they embed the level-rubric skill body.
- Docs:
  - `plugins/sdlc-lite/skills/level-rubric/SKILL.md` and `plugins/sdlc-lite/HARNESS-NOTES.md` describe the configured-alternate and shared-model rule.
  - `docs/codex-role-execution.md` has a new agent count (19), an Astra mapping table, and a dated ChatGPT-account note (2026-09-29, Codex CLI 0.154.0).

### Verification
- Step 1 (verifier L2, pass):
  - Every acceptance criterion was run. That covers no `gpt-6-sol` in `models.json`, efforts unchanged against the base SHA, and the scout line unchanged. It also covers `resolve` printing `gpt-6-astra medium shared`, and `gpt-6-terra medium` when a temp copy maps Astra to Terra. `generate --check` and the orphan-file check were run as well.
  - The three new selftests fail at the base SHA (errors or failure) and pass on the built tree. That is the red-then-green evidence.
  - Negative control: a dummy `sdlc-fake-l9.toml` made the orphan check and `generate --check` fail.
  - Full `codex-selftest.py` ran 20 tests OK. `run-selftest.sh` printed PASS, `lifecycle-selftest.py` printed OK, and `check.py` printed ok (18 role levels, 8 agents).
- Step 2 (verifier L1, pass):
  - The 8 grep criteria passed.
  - `check.sh` failed on its first run because the generated planner agents were stale after the SKILL.md edit. It went green after regeneration. The verifier ran it twice and inferred green from the final output lines ("run selftest: PASS", "hook selftest: PASS", "ok: plugin validate"). It did not capture the exit code.
  - `scripts/check-packaging.py` printed PASS, and `git diff --check` was clean.
  - The verifier ran no negative controls for the grep checks.
- shellcheck is not installed, so `check.sh` skipped it.
- Not verified: a live role run through `scripts/run.sh` with the Codex backend on a ChatGPT account. An API-key account was also not tested.

## Changelog entry
Fixed: Codex default models now use `gpt-6-astra` in place of `gpt-6-sol`, which ChatGPT accounts reject. The Codex verifier's alternate model is read from `verifier_alternates` in `adapters/codex/models.json`. When none is configured, the verifier keeps the builder's model and the run is recorded with `shared_with_builder`. Scout L1 still uses `gpt-6-luna`.

## Follow-ups
- decide: Scout L1 still uses `gpt-6-luna`, which the ChatGPT account rejects, so Codex scout runs keep failing until the user picks a replacement.
- fix-now: `plugins/sdlc-lite/adapters/codex/instructions.md` line 22 still mentions "alternate profiles that enforce a different model". The step 1 builder flagged it and it is embedded in every generated TOML, so edit it and regenerate. No step artifact shows it was changed.
- fix-now: `docs/codex-role-execution.md` line 74 still names `sdlc-verifier-l1-alternate` in the live-run note. The step 1 builder flagged it, and the step 2 artifacts do not show it changed.
- note: `docs/reports/native-codex-smoke.json` hashes the three deleted alternate TOMLs. It is historical evidence and was left untouched.
- note: Projects that installed the old agents keep stale `sdlc-verifier-lN-alternate` TOMLs in `.codex/agents/`, because `install` does not remove them. They are unused while no alternate is configured.
- note: A focused live Codex run through `scripts/run.sh` in a throwaway project is still needed, per root AGENTS.md. Only stub CLIs were used here.
