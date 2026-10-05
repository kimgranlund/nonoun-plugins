## Task goal
Independently verify four small defect fixes in one commit, 65c37f2 (pre-build base 2c839cf). Tickets: .sdlc/.0259-fanout-gate-preflight, .sdlc/.0260-solo-session-limit-resume, .sdlc/.0262-close-citation-scan-gaps, .sdlc/.0273-codex-selftest-claude-path (read each handoff.md). Each regression test must fail without its fix and pass with it.

## Step 1: Verify the four fixes
level: L3

### Do
- T-0259 (scripts/fanout.py): an uncommitted handoff refusal now names the force-add of the ignored path; a plan whose start commit tracks package.json and whose gates never install prints a `note:` naming `npm ci`; a red gate in a worktree with package.json and no node_modules appends a hint. Test: fanout selftest case 20. Docs: docs/maintenance/sdlc-internals.md.
- T-0260 (scripts/run.sh, scripts/solo_run.py): a failed run whose log shows 429 or a session limit writes `<role>-<level>.limit` and prints `run.sh: session limit: resume with: ...` (exit stays 1); solo_run.py writes `solo.limit` and prints a resume hint. Tests: run-selftest.sh case `session limit` and solo_run.py selftest.
- T-0262 (scripts/tickets.py): `outside_refs` also scans the ticket root with ignore rules off so citations under a gitignored `.sdlc` are found, refused, and rewritable; `--force` prints `left refs to ...`. Test: tickets.py selftest `(u) refs` cases.
- T-0273 (scripts/codex-selftest.py): `test_fanout_uses_codex` now checks argv (role script, and not the claude CLI) instead of a `claude` substring, so it passes when the repo path contains `claude`. This worktree lives under `.claude/worktrees`, which is the repro.
To show red before, work in a throwaway worktree under `$SDLC_TMP_WORKTREES` at HEAD, revert only the non-test hunks of each fix there (the `deps_note` call, the red-gate hint and the force-add wording in fanout.py; the `limit_marker` function body in run.sh and the `limit_hint` call in solo_run.py; the ignore-off scan block in `outside_refs`), run the matching selftest, and say what you did. For T-0273 run the OLD test body from base 2c839cf in this path and note that it fails.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `python3 plugins/sdlc-lite/scripts/solo_run.py selftest`
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_fanout_uses_codex`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- Each of the four regression tests goes red with its fix reverted (observed, not read).

## Builder note
The builder (Sonnet) saw red then green for each. Treat that as an unverified claim.
