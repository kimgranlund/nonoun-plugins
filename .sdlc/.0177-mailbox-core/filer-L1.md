<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

Step 1 failed its first verification. `locate` reported a message that was moving between folders as a duplicate. The second attempt fixed it and passed. Steps 2 to 5 passed on their first verification, and the plan review returned pass.

## PR title
T-0177: Mailbox core: messages.py, lifecycle, schema, and run.sh notice

## PR body
### Summary
Adds `plugins/sdlc-lite/scripts/messages.py`. It runs a git-ignored `.sdlc/messages/` mailbox with a validated schema and a `new`, `read`, `done` lifecycle. A transition table documents the lifecycle. `run.sh` now prints a one-line stderr count notice before it launches a role. Exit codes and other output are unchanged.

### Changes
- `messages.py`: new standard-library script, Python 3.9 compatible.
  - Subcommands are `send`, `list`, `read`, `ack`, `reply`, `expire`, `count` and `selftest`.
  - Every refusal exits 1 with one stderr line, nothing written or moved, and no traceback.
  - `read` claims a message by atomic rename and prints the body between data markers, with a trust line saying it is data, never instructions.
  - A linked worktree resolves to the main checkout's mailbox.
  - A caller cannot set `read_time`, `ack_time`, `send_time` or `protocol`.
  - Messages over 4000 bytes are refused.
  - `ack` is refused when `follow_up_requested: true` and no reply exists.
  - `expire` moves overdue messages to `done`, and sends the sender a notice when a message that needed a reply expired without one.
  - The transition table is in the docstring and `--help`.
- `selftest`: 18 cases covering each transition row, the negative controls, the worktree case, and the two-reader race. It also has a control proving the race case fails when the claim is a copy then delete. Test hooks `SDLC_MESSAGES_TEST_CLAIM` and `SDLC_MESSAGES_TEST_BARRIER` exist for the selftest only.
- `run.sh`: prints `run.sh: <n> new message(s) for <role>; read with messages.py` when the count for the role or host name is above 0. It never prints a body, and a missing mailbox prints nothing.
- `run-selftest.sh`: new notice case.
- `check.sh`: runs `messages.py selftest`.
- `.gitignore`, `handoff-format` `SKILL.md`, `onboard.py` (`TEMPLATE_VERSION` still 1) and `docs/repo-onboarding/design.md` name `.sdlc/messages/` as ignored.
- `docs/maintenance/sdlc-internals.md`: new `messages.py` entry, and a notice sentence on the `run.sh` entry.
- `docs/ticket-stages/design.md`: Message bus section updated with status, the reply rule, notice fields, and commands per transition.

### Verification
- Step 1 (CLI), second attempt, verifier L3: all 13 criteria passed on Python 3.9.6.
  - Each of the first 12 criteria was red at the base commit and went red under injected single-change mutants.
  - The first attempt failed on a race: about 1 in 80 losing `read` calls said `in more than one folder` instead of `already claimed`. The fix changed only `locate`. Three 40-round races with 8 concurrent readers gave 40 wins and 0 bad losers each, and a reply race gave 120 successful replies.
- Step 2 (selftest), verifier L3: passed.
  - It prints PASS with all 18 `ok:` labels in about 8 s.
  - The caller's mailbox and untracked files are unchanged by a run.
  - 16 single-defect copies each failed the expected case.
  - Injecting `read_time` at send failed `create`. Making the claim non-atomic failed `race: one winner`.
- Step 3 (run.sh notice, selftest case, check.sh wiring), verifier L1: passed.
  - The no-mailbox run is silent. The count includes the role and host names, and no body appears.
  - A real stub run prints the notice once, and the block sits inside the `{ ... }` group.
  - The verifier did not run the guard-removed negative control itself. The builder reported it.
- Step 4 (ignore rules and docs), verifier L1: passed.
  - `git check-ignore` is true for a message path.
  - The onboard bullet matches `design.md` byte for byte, and `onboard.py selftest` is green.
  - The doc claims match the code, and no files outside the six scoped ones changed.
- Step 5 (gates), verifier L1: passed.
  - `check.sh` exited 0, including `messages selftest: PASS`, with shellcheck skipped because it is not installed.
  - `check-packaging.py` passed.
  - The diff and em-dash guards over steps 1 to 4 were clean.
  - They were empty at HEAD, so they were checked against the real range as well.

## Changelog entry
- Added `messages.py`, a git-ignored `.sdlc/messages/` mailbox with a validated schema, a `new`, `read`, `done` lifecycle, a transition table, and a selftest. `run.sh` prints a one-line count notice for new messages before it launches a role. The ignore guidance in `handoff-format` and `onboard.py` names the mailbox.

## Follow-ups
- note: shellcheck is not installed on this host, so `check.sh` skipped it. `run.sh` and `run-selftest.sh` were not shellchecked.
- note: the selftest race control catches a non-atomic claim only when the copy and delete straddle the barrier. If the copy and delete both run after the barrier, the selftest passes. The verifier saw this as a plain-unlink variant failing in 1 of 3 full runs.
- note: live host validation of the mailbox is T-0179. The messenger agent is T-0178. Neither was exercised here.
