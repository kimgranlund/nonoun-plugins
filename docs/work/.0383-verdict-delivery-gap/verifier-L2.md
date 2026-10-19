<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- (guard) `python3 plugins/sdlc-lite/scripts/dispatch.py selftest | tail -1 | grep -q 'PASS'`, with section 11 holding the five fault-injection cases: pass. Evidence: on the built tree `dispatch.py selftest` exited 0 and its last line was `dispatch selftest: PASS`. All section 11 lines are `ok:` (lines 342 to 359), covering these cases:
  - "record then verdict message"
  - "a poller that is not listening is named on stderr with the Monitor route"
  - "duplicate delivery: deliver after sent resends nothing"
  - "duplicate delivery: a crash between send and mark (state sending) marks sent without a second message"
  - "attempt left running after a report: status names it report-written-unrecorded"
  - "an unregistered receiver: PENDING on stderr" plus "after registering, deliver sends the pending verdict exactly once"
  - "a failed sub-agent and an invalid report each deliver failed and invalid"

  To show the check can go red, I copied the new dispatch.py into a throwaway worktree at base d85d9eef and broke one piece at a time:
  - NC1: removed `deliver_quietly` from record's success path. rc=1 and 14 `FAIL:` lines, including record-then-message, the T-0297 fixture, the idle-poller warning and duplicate delivery.
  - NC2: disabled the prior-send lookup. rc=1 with `FAIL: duplicate delivery: a crash between send and mark ...`.
  - NC3: removed the `report-written-unrecorded` suffix. rc=1 with `FAIL: attempt left running after a report ...`.
  - NC4: disabled the pending-delivery status line. rc=1 with `FAIL: a pending delivery shows in status`.

  No process-deviations.md exists. This is a solo lane with no builder report, so failing-first rests on these controls and on the base run.
- (guard) The `grep -c 'T-0297 fixture: the verdict is in the mailbox at the record moment'` line: pass. Evidence:
  - Built tree: prints `1`, and the line is `ok: T-0297 fixture: the verdict is in the mailbox at the record moment, not minutes later (gap under 5 s, was about 7 minutes)`.
  - Base worktree at d85d9eef: prints `0`.
  - The NC1 run turned it into `FAIL:`, so `record` itself is what delivers the message.
  - Real CLI run in a scratch repo: `send_time: 2026-10-08T23:02:34.742827Z` and the delivery `sent_at` of `23:02:34.858` came from the same `record` call.
- `prepare --notify <receiver> [--notify-re <id>]` writes `notify`, and with no `--notify` there is no key, message or delivery record: pass. Evidence:
  - Real CLI in a scratch repo: `dispatch.py prepare --notify codex verifier L1 .sdlc/t/handoff.md` exited 0, and the dispatch JSON has `notify: codex` and `notify_re: ''`.
  - Base: `unrecognized arguments: --notify`.
  - Selftest `ok: control: a dispatch with no --notify sends no message and writes no delivery record` checks `'notify' not in got0` and that no `.delivery.json` exists. It went red under NC1.
  - Selftest `ok: prepare refuses a malformed receiver name`.
- `dispatch.py deliver <dispatch file>` is idempotent and never reruns the role, and `status` shows `report-written-unrecorded` and `verdict-delivery-pending`: pass. Evidence from the real CLI in the scratch repo:
  - Before record, `status` printed `verifier-L1 orphaned verifier-L1 parent_pid=90482 report-written-unrecorded`.
  - `deliver` before record printed `UNRECORDED ... run: python3 .../dispatch.py record ...` with rc=5 and 0 messages.
  - `record` printed rc=0 and `pass sent to codex`, leaving 1 message.
  - `deliver` twice: both rc=0 with `already sent ... nothing resent`. Still 1 message, `runs.jsonl` still 1 line, attempt `completed`.

  `verdict-delivery-pending to ghost` is shown by the selftest case `a pending delivery shows in status`, which went red under NC4. Base has no `deliver` subcommand (`invalid choice: 'deliver'`).
- The idle-poller route is documented: pass. Evidence:
  - `grep -c 'Monitor' plugins/sdlc-lite/scripts/messages.py` prints 1. That alone does not bite, because base also prints 1: the edit extended an existing line.
  - The content check that does bite: `grep -c 'new/<receiver>'` in messages.py is 18 now against 17 at HEAD. The new sentence (messages.py diff line 362) reads "A conductor `Monitor` over `new/<receiver>` is a supported route ... (maison T-0283; a measured route, not a plugin guarantee)".
  - `grep -c 'Monitor\` over \`new/<receiver>\`' docs/references/sdlc-internals.md` is 1 now and 0 at HEAD. The new paragraph names it as a supported route with the 24-second against 4 to 10 minute measurement and says the Codex path is unverified.
- (guard) The gate commands: pass. Evidence: each exited 0 on the built tree.
  - `check.py`: rc=0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
  - `tickets.py --root .sdlc check`: rc=0. Its only output is a flat-layout warning.
  - `messages.py selftest`: rc=0, `messages selftest: PASS`.
  - `codex_roles.py generate --check`: rc=0, `Codex agent definitions verified`.
  - `claude_roles.py generate --check`: rc=0, `Claude agent definitions verified (22 files)`.
  - `bash plugins/sdlc-lite/scripts/check.sh`: rc=0. Run, hook and hook live probe selftests PASS, shellcheck and plugin validate ok, `docs_check: 0 errors`.

  Contract dependents of the changed `status` output: board.py (`dispatch.status(task, True)`) and supervisor.py (`status --orphans`, first token only) still parse it. The new suffix trails the line, and the pending line cannot appear in orphans mode because it comes after the `continue` at dispatch.py:428. `board.py selftest` PASS and `supervisor.py selftest` PASS.
- Unverified by design, Codex host behavior and a live Claude idle-poller rerun: pass. Evidence: both are declared unverified. sdlc-internals.md says "this path is Claude-only and Codex behavior is unverified", and messages.py marks the Monitor route as "not a plugin guarantee". `prepare` still refuses when `SDLC_BACKEND != claude` (dispatch.py:507). No live poller rerun was claimed, and none was run here.

Steelman check on the one weak spot: I drafted a fail for "`grep -c 'Monitor'` prints 1 at base too, so the criterion is vacuous". The rebuttal holds: the criterion pairs that grep with "name the conductor Monitor over `new/<receiver>` as a measured route", and the content greps above do bite (17 to 18 in messages.py, 0 to 1 in the doc). Dropped.

## Out of scope changes
- `.sdlc/0383-verdict-delivery-gap/handoff.md` gained an `## Acceptance criteria` section, read in `git diff`. The ticket had none, and the lane needed runnable criteria. It changes no code or behavior, so I dismissed it.
- `plugins/sdlc-lite/skills/verify/SKILL.md` gained one parenthetical in step 3 documenting `--notify` and `deliver`, read in `git diff`. This makes the new flag reachable from the verify launcher, which is the Do's intent. `check.sh` plugin validate and docs_check pass, so I dismissed it.
- The untracked `base-sha`, `runs.jsonl` and `verifier-L2.attempt.json` are run records.
- Otherwise none.

## For the next attempt
None
