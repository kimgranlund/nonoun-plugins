<!-- role=verifier level=L2 model=fable effort=medium -->
All checks ran; writing the verdict now.

## Verdict
pass

## Criteria
- `selftest` prints `tickets selftest: PASS` and exits 0: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` → `tickets selftest: PASS`, `rc=0`. The check can go red: with the warnings guard disabled in a throwaway worktree it printed `tickets selftest: FAIL, these did not bite: (b) open warnings refuse... (b) refusal wrote nothing...`, rc 1.
- Fixture by hand, Warnings `None`: pass. Evidence: `new feature parent "Parent"` then `close parent` → stdout `T-0001 done; 2 follow-up ticket(s): add-retry-to-fetch, document-the-flag`, rc 0; `grep -l '^from: T-0001' $R/*/handoff.md | wc -l` → 2; `grep '^status: done' $R/parent/handoff.md` → `status: done     # proposed | ...`, rc 0; `check` → `ok: 3 tickets, roadmap current`, rc 0. New ticket T-0002 has `type: idea`, `status: proposed`, `from: T-0001` right after `created:`, and Context `Follow-up from T-0001 (parent/filer-L1.md):` + bullet text.
- Same fixture with Warnings `step-2 verifier fail`: pass. Evidence: `close parent` rc 1, stderr `parent: filer warnings are open, not closing (rerun with --force to override):\nstep-2 verifier fail`; handoff still `status: proposed`; `$R` held only `parent` and `roadmap.md` (1 dir). `close parent --force` → rc 0, `T-0001 done; 2 follow-up ticket(s): ...`, two ticket dirs created.
- Negative control (warnings guard always passes → selftest FAIL): pass. Evidence: in `git worktree add <tmp> HEAD` with the modified file copied in, selftest was green; after `sed` to `if False and not is_none(warnings) and not force:` (line 336) selftest printed `FAIL, these did not bite: (b) open warnings refuse...; (b) refusal wrote nothing...`, rc 1. Worktree removed; `git status` unchanged afterwards. (A first NC attempt in a bare temp dir crashed on template lookup because templates resolve relative to the script's path; that was my setup, not the code.)
- `git diff --stat` touches only `plugins/sdlc-lite/scripts/tickets.py`: pass. Evidence: `git diff --stat` → `plugins/sdlc-lite/scripts/tickets.py | 246 +++--`, 1 file changed. `git status --short` shows only that file modified plus the untracked `.sdlc/0003-filer-follow-ups-to-tickets/` task dir (the chain's own artifacts).

Additional observed runs (Do-list items): `close nothere` refuses rc 1 naming the missing handoff; prose follow-ups refuse rc 1 with the prose echoed, handoff md5 unchanged, no ticket dir; second close on a done ticket refuses rc 1 with `already closed`, no new dir; regenerated roadmap lists `T-0001 ... 🟢 done` and `T-0002 one ... ⏳ proposed`. `scripts/check.sh` all green (role levels, selftest, tickets selftest, shellcheck, plugin validate). At HEAD, `close` is an invalid argparse choice (rc 2), so the feature is new in this diff. Selftest (a) closes a handoff whose body has a `status:` line and asserts byte-identity outside the front matter (tickets.py:544-547), covering plan risk 4; case (h) sets mtimes with `os.utime` (tickets.py:499-505, 596-605).

## Out of scope changes
None. Only `plugins/sdlc-lite/scripts/tickets.py` is modified; `.sdlc/0003-filer-follow-ups-to-tickets/` is the untracked task folder for this chain, not a code change.

## For the next attempt
None.
