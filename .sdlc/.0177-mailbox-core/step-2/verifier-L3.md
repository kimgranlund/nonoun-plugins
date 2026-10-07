<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- Criterion 1 (selftest prints PASS and all 18 `ok:` labels): pass. Evidence:
  - Ran the criterion command verbatim on the built tree: exit 0. Raw output is 18 `ok:` lines then `messages selftest: PASS`; a `diff` against the handoff's label list shows the order is identical.
  - Red at the pre-build commit: in a throwaway worktree at `$SDLC_BASE_SHA` the same command exits 2 (`invalid choice: 'selftest'`).
  - Three timed runs took 8.3 s, 8.1 s and 8.7 s, under the 60 s limit. A run where case 17 takes its 10 s barrier-timeout path would still be far under.
  - Every case was seen red: 16 single-defect copies (one per case 2 to 15, 17 and 18) each exited 1 with `messages selftest: FAIL: <the expected case>`. Cases 1 and 16 are covered under criterion 3.
  - Stability: the race verdict function ran 190 times in rename mode on an identical copy, one winner every time. In copy-delete mode, 20 of 20 verdicts failed with a torn probe (19 two-winner, 1 split).
- Criterion 2 (caller's mailbox and untracked files unchanged by selftest): pass. Evidence:
  - Ran the command verbatim: exit 0. The main checkout's `.sdlc/messages` does not exist before or after, and the untracked list is the same.
  - Bites on the comparison itself: in a throwaway standalone repo under `$SDLC_TMP_WORKTREES`, the unmodified copy gives exit 0. A copy whose selftest also runs one `send` in the caller's cwd exits 0 from selftest but the criterion exits 1.
  - No `messages-selftest-*` temp dirs were left behind.
  - With `SDLC_MESSAGES_TEST_CLAIM=copy-delete` and `SDLC_MESSAGES_TEST_BARRIER` set in the caller's environment, selftest still passes, so the hooks are dropped outside the race cases.
- Criterion 3 (Observable, two injected defects on temp copies): pass. Evidence:
  - (a1) `compose` sets `read_time` to `stamp(now)`: exit 1, `messages selftest: FAIL: create: ... exited 1: messages.py: read_time is set in new/`.
  - (a2) `deliver` sets `read_time` after validation: exit 1, `messages selftest: FAIL: create: created message: read_time is '2026-10-01T07:13:44.665429Z', expected ''`.
  - (b1) the hook test in `claim()` becomes `if True:`, so the default claim is the copy-delete claim as the Do defines it: exit 1, `messages selftest: FAIL: race: one winner: while a reader was held inside its claim the message sat in [('new', 'bob'), ('read', 'bob')] ... the claim is not atomic`.
  - (b2) default path becomes copy, barrier, plain `os.unlink`: exit 1, `FAIL: race: one winner`, same torn-claim reason.
  - Limit observed, not a fail: with the copy and delete placed after the barrier, the selftest catches it only sometimes. The plain-unlink variant failed `race: one winner` in 1 of 3 full runs and passed in 2; the variant that ignores FileNotFoundError failed in 3 of 3.
  - Steelman of that limit as a fail reason: the Do puts the barrier between the copy and the delete, and a window after the barrier cannot be held open by the prescribed mechanism. The rebuttal holds, so I dropped it. The builder's own note on this is confirmed.
  - Second dropped finding: case 17 accepts a "split" refusal as well as two winners, where the Do says "(two winners)". It still requires a failing verdict and a torn probe; requiring two winners outright would have flaked in the 1 of 20 split run above.
- Criterion 4 (file exists, no em dash): pass. Evidence:
  - Command verbatim: exit 0; the file has 0 non-ASCII lines.
  - Bites: a copy with one em dash appended exits 1, and a missing path exits 1.
- Criterion 5 (guard, only `messages.py` changed outside `.sdlc`): pass. Evidence:
  - Command verbatim: exit 0 with empty `out`. The raw input list is the single line `plugins/sdlc-lite/scripts/messages.py`.
  - Bites: with a different allowed path in the `grep -vxF`, the same pipeline exits 1.

## Out of scope changes
None.
- `git status --short` shows only `plugins/sdlc-lite/scripts/messages.py` modified, plus the runner's untracked files under `.sdlc/0177-mailbox-core/step-2/`.
- `git diff --check "$SDLC_BASE_SHA"` exits 0.
- Inside `messages.py`, the diff to step 1's code is limited to the docstring, three imports, `barrier()`, the `claim()` hook, and the `selftest` registration.
- Neighbors: `git grep "messages\.py"` finds only `docs/specs/ticket-stages/design.md`; no script, `check.sh` or `check.py` depends on it.
- Step 1's criteria 1 to 11, rerun on the built tree: 11 of 11 exit 0.
- Hooks observed on the real file: a lone `read` with the barrier set exits 1 with `barrier timeout` after 10 s and leaves the message in `new/`; an unknown `SDLC_MESSAGES_TEST_CLAIM` value keeps the rename (3 of 3 one-winner verdicts).

## For the next attempt
None
