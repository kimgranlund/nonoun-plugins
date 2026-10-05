# Defect fixes 0.20.10

Four size S and M tickets, each routed to the solo lane by `steps.py lane` (it printed `solo` for T-0259, T-0260, T-0262 and T-0273). The builder was Sonnet 5.5 in the maintainer session; one batched verifier ran `scripts/run.sh verifier L3` and used Fable, a different model family. No version bump, push, tag, or publish.

| Ticket | Change | Regression test |
|---|---|---|
| T-0259 | `fanout.py`: an uncommitted handoff refusal names `git add -f <path>`; a plan whose start commit tracks `package.json` and whose gates never install prints a `note:` naming `npm ci && ...`; a red gate in a worktree with `package.json` and no `node_modules` appends the same hint. Documented in `docs/maintenance/sdlc-internals.md`. | `fanout.py selftest` case 20 |
| T-0260 | `run.sh`: a failed run whose log shows 429 or a session limit writes `<role>-<level>.limit` and prints `run.sh: session limit: resume with: <command>` (exit stays 1; a success removes the marker). `solo_run.py`: writes `solo.limit` and prints a resume hint. | `run-selftest.sh` case `session limit`; `solo_run.py selftest` |
| T-0262 | `tickets.py`: `outside_refs` also scans the ticket root with ignore rules off, so citations under a gitignored `.sdlc` are found, refused, and rewritable; `--force` prints `left refs to <folder> in <files>`. | `tickets.py selftest` `(u) refs` cases |
| T-0273 (new) | `codex-selftest.py` `test_fanout_uses_codex` checks the argv (role script, not the `claude` CLI) instead of a `claude` substring, so it passes under a path containing `claude`. | `codex-selftest.py CodexTests.test_fanout_uses_codex` |

## Red before, green after

- T-0273: before the fix the test failed in this worktree (path under `.claude/worktrees`) with `AssertionError: 'claude' unexpectedly found in "/Library/Developer/CommandLineTools/usr/bin/python3 /Users/kimgranlund/...`; after, `Ran 1 test ... OK`.
- T-0259: with the three production hunks neutralised, `fanout.py selftest` listed three case 20 misses; with them, `fanout selftest: PASS`.
- T-0262: with the ignore-off scan disabled, `tickets.py selftest` listed `(u) refs: a citation in a gitignored .sdlc refuses and names .sdlc/index.md: rc=0 ''` and the `--rewrite-refs` case; with it, `tickets selftest: PASS`.
- T-0260: with `limit_hint` disabled `solo_run.py selftest` failed `limit stop: ...`; with `limit_marker` returning early `run-selftest.sh` failed `session limit: no resume line on stderr`; restored, both print PASS.

## Checks

On the built tree: `fanout.py selftest`, `tickets.py selftest`, `solo_run.py selftest` and `run-selftest.sh` printed PASS; `check.py` printed `ok: 19 role levels, 9 agents checked`; `codex_roles.py generate --check` printed `Codex agent definitions verified`; `check-packaging.py` printed `PASS: catalog parity, identity, skill routes, hook isolation and context links`.

## Independent verification

`.sdlc/verify-defect-fixes-0.20.10/verifier-L3.md` (model fable, effort xhigh): verdict pass. It reran each selftest, reverted only the non-test hunks in a throwaway worktree and saw each regression test go red, and planted a fake codex driver to show the new T-0273 test is not vacuous. One non-blocking note: the 429 and `rate limit` patterns also match those words in prose inside a failed log, which leaves an advisory marker only (exit code unchanged, removed by a later success).

## Limitations

- Live 429 behaviour was not observed; the tests use a stub `claude` that prints a 429 line, so the real session-limit wording is matched by pattern only.
- The `npm ci` note is a heuristic (tracked `package.json`, no install word in any gate); it does not change the gate.
- Closing these tickets with the new scan listed the verify folder's own citations, so they were closed with `--rewrite-refs`, which rewrote the folder paths in the verifier's handoff, log, and result.
