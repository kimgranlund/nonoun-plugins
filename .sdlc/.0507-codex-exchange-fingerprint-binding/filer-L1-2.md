<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- Handoff criterion 7 is unverified. It asks for a fresh callable named-agent Codex run that completes the bound exchange. That run can't happen on this Claude host without nesting a CLI. The new dated report marks it unverified. The fingerprint cases were checked only with real waiter subprocesses and the `codex_exchange.py` CLI.
- Step 1 criterion 3 was met by a substitute. `git worktree add` was denied by `block-stray-worktree.sh` because `SDLC_TMP_WORKTREES` was unset. Builder and verifier used a `git archive` export of base `07a5c289` instead. `cmp` showed its `codex_exchange.py` matched the base byte for byte. Each new test failed there on a real assertion.
- The full `check.sh` was not run. It is left to the `fanout.py land` gate. `dispatch.py selftest` was run by the step 1 verifier and passed.
- Steps 1, 2 and 3 all passed verification. There is no `process-deviations.md` in the artifacts dir or any step folder, so there are no process deviations.

## PR title
T-0507: bug: Codex exchange: enforce the dispatched profile binding

## PR body
### Summary
A native Codex exchange request now carries the profile fingerprint captured at dispatch. A normal response is accepted only if its profile line matches that fingerprint. Before this change, missing, stale and current fingerprints all exited 0 and recorded `received`. Fixes finding F5 of the Astra review.

### Changes
- `plugins/sdlc-lite/scripts/codex_exchange.py`:
  - `_wait_for_agent` computes `codex_roles.fingerprint(agent)` after the `-alternate` suffix is decided and stores it as `profile_fingerprint` in the request.
  - The waiter checks a normal response against that stored value with `codex_roles.check_loaded`. Any status other than ready fails the request with the helper message.
  - `respond()` runs the same check last, so a missing or stale profile line exits 2 and leaves the request `waiting`.
  - An agent with no generated profile raises `ValueError` before any request is published.
  - `--failed` skips the check and keeps the first-line reason in `error`. Its `profile_check` is `not-checked`.
  - Validation uses the dispatched binding, not a recomputed one, so profile files changed after dispatch do not move the target.
  - A whitespace slip on line 56 (`context =`) was restored in step 3.
- `plugins/sdlc-lite/scripts/run.sh` and `plugins/sdlc-lite/scripts/solo_run.py`: `runs.jsonl` records gain `profile_fingerprint` and `profile_check`, only when the result event carries them. Claude records are unchanged.
- `plugins/sdlc-lite/scripts/codex-selftest.py`:
  - Three new subprocess tests: binding enforced, binding survives a profile change after dispatch, and `--failed` needs no profile line.
  - Existing normal responses now carry the request's profile line.
- `plugins/sdlc-lite/adapters/codex/instructions.md` and `docs/references/codex-role-execution.md`:
  - Describe the binding, the exit 2 refusal, and the `--failed` path.
  - State that the final-report check "does not prove the role checked before it edited" and that the fingerprint is self-reported.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-*.toml`: all 28 regenerated with `codex_roles.py generate`, not hand-edited. Every Codex fingerprint changes, so a live Codex session holding old profiles is refused until it restarts.
- `docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md`: new dated evidence report. The Astra review report is unchanged.

### Verification
- Step 1, red then green:
  - Controls were recorded red before the first edit (`redck.py record`, 2 controls).
  - With only the selftest edited, the three new tests failed (`FAILED (failures=3)`). After the change they pass (`Ran 3 tests`, `OK`).
  - On the exported base tree each new test fails on a real assertion, for example `0 != 2 : a report with a missing profile line must be refused`.
- Step 1 guards, all passing:
  - five existing `CodexTests`
  - four `test_solo_native_*` tests
  - `lifecycle-selftest.py` (6 tests)
  - `solo_run.py selftest`
  - `dispatch.py selftest`
  - scope limited to the four target files, and `git diff --check`
- Step 2 gates, all passing: `codex_roles.py generate --check`, `codex-selftest.py`, `lifecycle-selftest.py`, `scripts/check-packaging.py`, `git diff --check`, and an unchanged Astra review report. Scope held to the planned file set.
- By-hand run of the five cases against a real waiter and the CLI:
  - missing: exit 2, request stays `waiting`
  - stale: exit 2
  - current: exit 0, `profile_check: ready`
  - changed after dispatch: live fingerprint refused, dispatched binding accepted
  - `--failed`: waiter exits 1, reason kept
- Step 3: the grep criterion passes and was shown to go red on the reverted line. Four `CodexTests` pass, and `py_compile` is clean.
- Not verified: a live Codex named-agent run (criterion 7). The full `check.sh` is left to the land gate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: the Codex native exchange now binds each request to the profile fingerprint captured at dispatch and refuses normal responses whose fingerprint is missing or stale. `--failed` responses are still accepted without a profile line. `runs.jsonl` records `profile_fingerprint` and `profile_check` for native runs.

## Follow-ups
- decide: Criterion 7 (a live named-agent Codex run completing the bound exchange) is unverified; someone must run it on a Codex host, or accept the offline subprocess evidence.
- note: `block-stray-worktree.sh` denies `git worktree add` inside role sessions because the hook sees no `SDLC_TMP_WORKTREES`. A planner brief should phrase a base-tree check as a `git archive` recipe instead.
- note: The new report quotes the live fingerprint `0.22.5+e27be4736593` for `sdlc-scout-l1`. Any later edit to `instructions.md` changes it, so the report stays dated evidence and is not rewritten.
