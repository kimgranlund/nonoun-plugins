<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0163: Use gpt-6-astra for Codex defaults and make the verifier alternate configurable

## PR body
### Summary
On a ChatGPT account, Codex rejects `gpt-6-sol` and `gpt-6-luna` with status 400. `gpt-6-astra` works. This PR follows the user's 2026-09-29 decision:
- Every `gpt-6-sol` default becomes `gpt-6-astra`, with each level's effort kept.
- The Codex verifier's alternate model now comes from configuration. `codex_roles.resolve` used to hardcode a switch to `gpt-6-sol`, which the account rejects.
- With no alternate configured, the verifier keeps the builder's model and the runner records that they shared it.

### Changes
- `plugins/sdlc-lite/adapters/codex/models.json`:
  - Every `gpt-6-sol` becomes `gpt-6-astra`.
  - Scout L1 stays `gpt-6-luna`.
  - New top-level key `verifier_alternates`, empty by default. It maps a builder model to the model the verifier uses instead.
- `plugins/sdlc-lite/scripts/codex_roles.py`:
  - `models()` returns only role entries.
  - No `gpt-6-*` literals remain in the file.
  - `resolve` now returns `(model, effort, shared)`. It switches to a mapped alternate when one exists. Otherwise it keeps the builder's model and sets `shared`.
  - The `resolve` CLI prints a third token, `shared`, in that case.
  - `definitions()` emits a `sdlc-verifier-lN-alternate` profile only when the map has an entry for that level's model.
- `plugins/sdlc-lite/scripts/run.sh`:
  - When the verifier shares the builder's model, the result header gets `shared_with_builder=yes`.
  - `runs.jsonl` gets a boolean `shared_with_builder`, false on the Claude path.
  - Claude defaults and the Claude verifier switch are unchanged.
- `plugins/sdlc-lite/scripts/codex-selftest.py`:
  - The old `test_verifier_uses_different_model` is replaced by three tests:
    - `test_verifier_shares_builder_model_without_alternate`
    - `test_verifier_alternate_comes_from_config`
    - `test_runner_records_shared_verifier_model`
  - The stub CLI gains a `verdict` mode.
- Docs:
  - `skills/level-rubric/SKILL.md` and `plugins/sdlc-lite/HARNESS-NOTES.md` describe the configured-alternate and shared rule.
  - `docs/references/codex-role-execution.md` gets:
    - the agent count, now 19
    - the mapping table with Sol changed to Astra
    - the rewritten verifier paragraph
    - a dated 2026-09-29 note on the ChatGPT-account result
  - `adapters/codex/instructions.md` says the alternate profile exists only when `models.json` configures one.
- Generated agents:
  - `adapters/codex/agents/*.toml` were regenerated: 11 profiles changed to `gpt-6-astra`, and the 3 verifier alternate TOMLs were removed.
  - The 3 planner TOMLs were regenerated because they embed the level-rubric skill.
  - All 19 TOMLs were regenerated again for the `instructions.md` change.

### Verification
All three steps passed their verifiers.
- Step 1:
  - The three new selftests failed against the old code (2 errors, 1 failure) and pass now.
  - The verifier reran them in a throwaway worktree at the base SHA and saw the same failures.
  - The full `codex-selftest.py` ran 20 tests, all OK.
  - `run-selftest.sh` passed, `lifecycle-selftest.py` was OK, and `check.py` reported "ok: 18 role levels, 8 agents".
  - With an alternate configured in a temp copy (`gpt-6-astra` to `gpt-6-terra`), `resolve verifier L1` printed `gpt-6-terra medium`. With no alternate, it printed `gpt-6-astra medium shared`.
  - Negative control: a dummy orphan agent file made `generate --check` fail with "generated agent drift: orphan".
  - Neither the builder nor the verifier ran a live Codex run.
- Step 2:
  - The 8 grep criteria passed.
  - `bash plugins/sdlc-lite/scripts/check.sh` exited 0 after the planner TOMLs were regenerated. Shellcheck is not installed, so that part was skipped.
  - `python3 scripts/check-packaging.py` printed PASS, and `git diff --check` was clean.
  - The step-2 verifier inferred `check.sh` green from its last output lines. It did not capture the printed exit code.
- Step 3:
  - Both grep criteria were red at the base SHA and green on the built tree.
  - `generate --check` passed. A stale-generation control made it print "generated agent drift".
  - `check.py` passed.

Not verified: a role launched through `scripts/run.sh` with the Codex backend on a ChatGPT account, and API-key accounts. All evidence uses stub CLIs and direct output checks.

## Changelog entry
- Fixed: Codex role defaults now use `gpt-6-astra` where they used `gpt-6-sol`, which a ChatGPT account rejects. The Codex verifier's alternate model is now set by `verifier_alternates` in `adapters/codex/models.json`, empty by default. With no alternate, the verifier keeps the builder's model, and the result header and `runs.jsonl` record `shared_with_builder`. The three `sdlc-verifier-lN-alternate` agents are no longer generated.

## Follow-ups
- decide: Scout L1 still uses `gpt-6-luna`, which a ChatGPT account rejects, so Codex scout runs fail there until the user picks a replacement or accepts it.
- decide: No live `scripts/run.sh` run with the Codex backend on a ChatGPT account was made. The root AGENTS.md asks for a focused live run in a throwaway project for changed role behavior.
- note: `docs/reports/native-codex-smoke.json` hashes the deleted alternate TOMLs. It was left as historical evidence, and it may look stale next to the current agent set.
- note: Projects that installed the old agents keep stale `sdlc-verifier-lN-alternate` TOMLs in `.codex/agents/`, because `install` does not remove files it no longer generates. They are unused while no alternate is configured.
