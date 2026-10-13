<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Bind each Codex native exchange request to the profile fingerprint captured at dispatch, and refuse a normal response whose fingerprint is missing or differs, while `--failed`, ownership, duplicate, destination, cancellation, and timeout controls keep working.

## Step 1: Bind and enforce the profile fingerprint in the native exchange
level: L3
guard timeout: 300
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none.

Targets: `plugins/sdlc-lite/scripts/codex_exchange.py` (`_wait_for_agent`, `respond`), `plugins/sdlc-lite/scripts/run.sh` (the `runs.jsonl` jq expression near the `attempt_id` argument), `plugins/sdlc-lite/scripts/solo_run.py` (`build_record`), and the tests in `plugins/sdlc-lite/scripts/codex-selftest.py`. Write the three new tests first and run them before touching `codex_exchange.py`; keep the failing output for the builder result (handoff criterion 5).

Settled interface (evidence: `codex_exchange.py:53` builds the request with no binding, `codex_exchange.py:89` accepts any nonempty report, `codex_roles.py:117` `check_loaded(role, report, binding)` already classifies ready, refused, unknown):
- Request key `profile_fingerprint`: `codex_roles.fingerprint(agent)`, computed in `_wait_for_agent` after the `-alternate` suffix is decided and before the request file is written. An agent with no generated profile raises `ValueError` naming the agent before any request is published, on the same path as the existing "native exchange already exists" error.
- The waiter validates against its in-memory payload, never a recomputed fingerprint. On a response with `is_error` false and a nonblank report it calls `codex_roles.check_loaded(agent, report, payload['profile_fingerprint'])`; any status other than ready sets `failed`, stores the helper message in `error`, and exits 1 with request status `failed`.
- Request key `profile_check` written with the final status: `ready`, `refused`, `unknown`, or `not-checked` (a `--failed` response, a timeout, a cancel, an invalid response).
- A `--failed` response skips the fingerprint check. The request stores `error` as `native agent reported failure: ` plus the first nonblank line of the report; the result event keeps the full report in `result`.
- The result event gains `profile_fingerprint` and `profile_check`.
- `respond()` without `--failed` runs the same check against `payload['profile_fingerprint']` read from the request file, after the existing status, owner, destination, and empty-report checks so those keep their own messages. A request with no binding, or a status other than ready, raises `ValueError` with the helper message: CLI exit 2, no response file, request still `waiting`.
- `run.sh` adds both keys to the `runs.jsonl` line only when the result event has `profile_fingerprint`, so Claude records do not change. `solo_run.py` `build_record` does the same from `result`. Do not write `*.attempt.json` from the exchange: `run_lifecycle.py` owns that file in another process. The kept request file, which already carries `attempt_id`, plus the `runs.jsonl` line are the attempt records.

New tests in `CodexTests`, each using a real waiter subprocess and the `codex_exchange.py` CLI (the child pattern is `docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` lines 33 to 44; do not edit that file):
- `test_native_exchange_enforces_the_dispatched_profile_binding`: a report with no profile line and one with a stale line each get respond exit 2, no response file, and a request still `waiting`; the current fingerprint gets respond exit 0, exchange exit 0, status `received`, `profile_check` ready. One more case writes a response file directly (correct `request_id`, stale report, `is_error` false) and expects exchange exit 1, status `failed`, and `error` naming the refusal.
- `test_native_exchange_binding_survives_profile_change_after_dispatch`: the waiter child patches `codex_roles.fingerprint` to a fixed fake value before calling `wait_for_agent`, so the unpatched responder process computes a different live fingerprint. A report stating the fake value is accepted; a report stating the live value is refused with exit 2.
- `test_native_exchange_failed_response_needs_no_profile_line`: a `--failed` response with no profile line gets respond exit 0, exchange exit 1, status `failed`, the reason text in the request `error` and in the result event `result`.

Contract dependents, found with `git grep -n -E "codex_exchange|respond\(" -- plugins/sdlc-lite/scripts`: every existing normal response in `codex-selftest.py` has no profile line and goes red once the check lands. Prefix each with `profile: ` plus the request's `profile_fingerprint`: `test_native_exchange_preserves_runner_artifacts`, `test_conductor_exchange_needs_no_nested_cli` (the expected `result` gains the line), `test_runner_records_plan_reviewer_alternate_agent` (both exchanges, alternate and default agent), and the `solo_respond` default text used by the four `test_solo_native_*` tests (not its `failed=True` calls). Extend `test_native_exchange_preserves_runner_artifacts` and `test_solo_native_exchange_levels` to assert the request and the `runs.jsonl` line hold the same `profile_fingerprint` as `codex_roles.fingerprint(<agent>)`.

Left untouched on purpose: `lifecycle-selftest.py` has one `respond` call (line 93, in `test_recovery_preserves_evidence_and_rejects_late_native_report`); its request has no binding and must still fail on "owner is gone", which holds because the binding check runs last. `codex_exec.py` and `run_lifecycle.py` need no change. `run-selftest.sh` and the rest of `check.sh` belong to the `fanout.py land` gate.

The exchange checks the final report only. It does not prove a role checked its profile before editing; step 2 words that.
### Acceptance criteria
- (red) `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_native_exchange_enforces_the_dispatched_profile_binding CodexTests.test_native_exchange_binding_survives_profile_change_after_dispatch CodexTests.test_native_exchange_failed_response_needs_no_profile_line` exits 0 and its output says 3 tests ran.
- (red) `grep -q profile_fingerprint plugins/sdlc-lite/scripts/codex_exchange.py && grep -q profile_fingerprint plugins/sdlc-lite/scripts/run.sh && grep -q profile_fingerprint plugins/sdlc-lite/scripts/solo_run.py`
- The new assertions fail on the base exchange: after `git worktree add --detach "$SDLC_TMP_WORKTREES/0507-base-check" "$SDLC_BASE_SHA"` and `cp plugins/sdlc-lite/scripts/codex-selftest.py "$SDLC_TMP_WORKTREES/0507-base-check/plugins/sdlc-lite/scripts/codex-selftest.py"`, the run `! python3 "$SDLC_TMP_WORKTREES/0507-base-check/plugins/sdlc-lite/scripts/codex-selftest.py" CodexTests.test_native_exchange_enforces_the_dispatched_profile_binding` holds, and its output shows a failed assertion on the missing or stale case, not an import or attribute error. Use a fresh worktree name if that one exists.
- The builder result quotes the failing output of the three new tests from the run made before `codex_exchange.py` changed.
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_native_exchange_preserves_runner_artifacts CodexTests.test_conductor_exchange_needs_no_nested_cli CodexTests.test_runner_records_plan_reviewer_alternate_agent CodexTests.test_fingerprinted_report_passes_the_native_exchange_and_result_parser CodexTests.test_unanswered_native_request_fails_and_cleans_marker`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_solo_native_exchange_levels CodexTests.test_solo_native_response_failure CodexTests.test_solo_native_timeout CodexTests.test_solo_native_rerun_keeps_earlier_request`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py LifecycleTests.test_both_hosts_cancel_lock_retry_and_routing LifecycleTests.test_recovery_preserves_evidence_and_rejects_late_native_report LifecycleTests.test_sigkill_recovers_claude_but_codex_native_refuses`
- (guard) `python3 plugins/sdlc-lite/scripts/solo_run.py selftest`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^plugins/sdlc-lite/scripts/(codex_exchange\.py|codex-selftest\.py|run\.sh|solo_run\.py)$" | grep -q .`

## Step 2: Describe the binding, regenerate profiles, record evidence, gates green
level: L2
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: step 1.

Targets: `plugins/sdlc-lite/adapters/codex/instructions.md` (the "Profile handshake" paragraph and the two `codex_exchange.py` paragraphs above it), `docs/references/codex-role-execution.md` (the "Report envelope" section and the native transport paragraph), the generated `plugins/sdlc-lite/adapters/codex/agents/sdlc-*.toml`, and a new report. [creates: docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md]

Settled wording, in both documents:
- Each native request carries `profile_fingerprint`, the binding captured at dispatch. `codex_roles.py handshake --binding` takes that value from the request file.
- `codex_exchange.py` refuses a normal report whose first line is not `profile: <that binding>`: exit 2, no response written, the request stays waiting. The conductor then answers with `--failed` and the refusal message as the reason, and starts a fresh Codex session for a new run. It never edits the report to add the line.
- `--failed` needs no profile line.
- The pre-edit handshake stays a conductor instruction. Include the exact phrase "does not prove the role checked before it edited" for the final-report check, and say the fingerprint is self-reported.
- In `codex-role-execution.md`, name the two new `runs.jsonl` keys and the three new tests as the regression.

`instructions.md` is the prelude of every profile (`codex_roles.py` `instructions()`), so the edit changes all 28 fingerprints: run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` and never hand-edit a TOML.

Left untouched on purpose: `envelope_note` in `codex_roles.py`, `agents/solo.md`, and `skills/sdlc-lite/SKILL.md` tell the role or conductor what to send and stay accurate. `docs/references/sdlc-internals.md` does not mention the exchange (`grep -c codex_exchange` prints 0). `docs/reports/2026-10-12-sdlc-lite-astra-review.md` and its folder are immutable.

The report records the commands run and their results for the missing, stale, current, changed-after-dispatch, and `--failed` cases, the baseline failing output from step 1, and handoff criterion 7 as unverified: a fresh callable named-agent Codex run cannot run on this Claude host without nesting a CLI. No step here proves live Codex behavior.

Run every gate below and fix any red step 1 introduced. A gate already red at the build-start HEAD comes back as `inherited red`. The Progressive Context performance-contract link failure is out of scope. The rest of `check.sh` belongs to the `fanout.py land` gate.
### Acceptance criteria
- `grep -qF profile_fingerprint plugins/sdlc-lite/adapters/codex/instructions.md && grep -qF "does not prove the role checked before it edited" plugins/sdlc-lite/adapters/codex/instructions.md`
- `grep -qF profile_fingerprint docs/references/codex-role-execution.md`
- `grep -qF profile_fingerprint plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`
- `test -f docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md && grep -qi unverified docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- docs/reports/2026-10-12-sdlc-lite-astra-review docs/reports/2026-10-12-sdlc-lite-astra-review.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/scripts/(codex_exchange\.py|codex-selftest\.py|lifecycle-selftest\.py|run\.sh|solo_run\.py)|plugins/sdlc-lite/adapters/codex/instructions\.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml|docs/references/codex-role-execution\.md|docs/reports/2026-10-12-codex-exchange-fingerprint-binding(\.md|/.*))$" | grep -q .`

## Assumptions
- The exchange accepts a report with no profile line today: verified by a scratch probe (waiter subprocess plus the CLI) that got respond exit 0, and by finding F5 in `docs/reports/2026-10-12-sdlc-lite-astra-review.md`.
- Every agent the exchange can name has a generated fingerprint, conductor and alternates included: verified by `plugins/sdlc-lite/scripts/codex_roles.py` `definitions()`, which wraps every row in `with_fingerprint`, and by `codex_roles.py generate --check` passing with 28 profiles.
- `instructions.md` is embedded in every generated profile: verified by `codex_roles.py` `instructions()` (`prelude = (ADAPTER / 'instructions.md').read_text()`) and by "Profile handshake" appearing in `sdlc-conductor-l1.toml` and `sdlc-scout-l1.toml`.
- The `runs.jsonl` line is built from the last result event: verified by `run.sh:665` (`last_ev`) and the jq expression that reads `.usage` and `.transport` from it.
- The "relevant attempt record" is the kept request file plus the `runs.jsonl` line, not `*.attempt.json`: settled from `run_lifecycle.py:94`, which owns that file under its own lock in a parent process.
- Both enforcement points are wanted (the responder refuses early, the waiter is authoritative): settled from the handoff's Expected section and F5's "require the same binding when accepting a normal response".
- All guards are green at the base commit: verified by one probe run (focused tests 14s, 6s, 15s; `solo_run.py selftest` 30s; `codex-selftest.py` 52s; `lifecycle-selftest.py` 19s; packaging, `generate --check`, both scope guards, and the immutability diff exit 0). Guard timeouts are about three times those times, rounded up for a host at load 20.
- The plan text passes `steps.py lint`, `specgate.py check`, and `results.py validate --role planner` (with the runner's header line): verified on a scratch copy.
- The lane's broad `check.sh` gate runs at `fanout.py land`: inferred from the branch `fanout/wave54-b` and handoff criterion 6, which names only the two selftests and packaging.

## Risks
- The `(red)` test criterion is red today because the tests do not exist yet. The behavioral red is the base-worktree criterion, which runs after the build, plus the builder's quoted baseline output.
- I could not see the `generate --check` guard or the whole-suite guards go red: the worktree hook denied a scratch worktree in this planner session (`SDLC_TMP_WORKTREES` unset). The scope guards were seen red on fixtures and the immutability diff on an earlier commit.
- The base-worktree criterion needs `SDLC_TMP_WORKTREES` set for the verifier. If it is unset, the verifier reports that criterion unverified and relies on the builder's quoted baseline output.
- A refused response leaves the waiter waiting until the conductor answers with `--failed` or the timeout fires. That is deliberate, and step 2 documents it.
- Step 2 changes every Codex fingerprint, so a live Codex session holding old profiles is refused until it restarts. This is the intended effect of the binding.
- `run.sh` changes are covered here only through the Codex selftests; `run-selftest.sh` runs at the land gate.
- Handoff criterion 7 (a live named-agent Codex run) stays unverified on this host.
- Scratch probe files remain under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/.worktrees/tmp/0507-planner-L2`; nothing was deleted.
