<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 with reap cases (fake orphan listed by default and still alive, killed by `--kill`; live-parent match neither listed killable nor killed): pass. Evidence:
  - Built tree: 4 runs, each rc=0 and ending `gate_lock selftest: PASS`. The reap cases are at `plugins/sdlc-lite/scripts/gate_lock.py:430-489` and `:612-634`: double-fork orphan, `--older-than 0`, and a live-parent fake carrying the same matching name.
  - The check can go red. One-line mutated copies under `$SDLC_TMP_WORKTREES/mut`, each selftest rc=1 with the named miss:
    - list mode made to stop (`if not a.kill:` to `if False:`): `orphan: not listed by default or not left alone ... stopped pid 64645 (TERM)`.
    - `--kill` made a no-op that still reports TERM: `orphan: --kill did not stop it`, so the selftest checks the process is actually gone and not just the printed text.
    - orphans never listed (`elif age >= ...` to `elif False:`): `orphan: not listed by default or not left alone`.
    - parent check dropped in `leftovers` (`if not is_orphan(ppid):` to `if False:`, `PARENT-CHECK` line untouched): `live-parent: the process with a live parent was listed as stoppable`.
  - Pre-build tree (throwaway worktree at `$SDLC_BASE_SHA` 7353252, removed afterwards): `gate_lock.py reap --older-than 0` prints usage and exits 2. Its selftest exits 0 with 0 `no parent check` lines, and `grep -c 'PARENT-CHECK\|cmd_reap'` gives 0. So the reap cases are what discriminate, not the bare exit 0.
  - Independent hand run of the real script against four fakes I started, narrowed by `--match` to a random token and cleaned up by saved pid. The orphans were made by a dead parent (ppid 1 per `ps`), a different mechanism from the selftest's double fork.
    - `reap --older-than 0`: listed exactly the two orphans, printed `1 matching process(es) with a live parent skipped` and `nothing stopped`; all four still alive.
    - `reap` at the default threshold: `no leftover browser processes older than 30 min`.
    - `--older-than 0.1`: not listed at first, listed once `age 6s`.
    - `--kill`: `stopped pid 80205 (TERM)` and `stopped pid 80207 (KILL)` (the second ignores SIGTERM), 2.5 s elapsed, rc=0. Both dead; the live-parent fake and a token-only orphan that does not match the browser pattern stayed alive.
    - Second `--kill`: nothing left, rc=0.
  - The `not alive(l)` conjunct can bite: `proc_start` returns `None` for a child killed but not yet reaped (observed `before: True`, `after, unreaped: None`).
  - Steelman, dropped: "the `N matching process(es) with a live parent skipped` line lists live-parent processes". It is a count with no pid, and the requirement forbids listing them as killable; the selftest's `listed()` keys on `pid <n> ` (line 442).
- Negative control shown once (without the parent check the live-parent case fails): pass. Evidence:
  - `grep -c 'negative control observed (no parent check)'` on selftest stdout is 1 in all 4 runs. The line reads `gate_lock selftest: negative control observed (no parent check): live-parent: the process with a live parent was listed as stoppable, got "pid 55179 ...`.
  - The biting variable is `is_orphan` at line 264, which the selftest's mutant replaces with `return True` (line 627). The harness's own reparent wait uses inline logic (line 463), so the mutant does not weaken it.
  - The control's assertion can go red: a copy whose mutant write is made inert (`mutant.write_text(src)`) exits 1 with `negative control: with the parent check removed the live-parent case must fail, got []`.

## Out of scope changes
None. `git status` shows only `plugins/sdlc-lite/scripts/gate_lock.py` and `docs/references/sdlc-internals.md` modified, both named by the handoff, as an uncommitted working-tree diff against 7353252. No `builder-*.md` exists in the artifacts dir, so the diff was the claim under review.

Concerns examined and cleared, each with its check:
- `reap --match REGEX` is not in the handoff's flag list. It only narrows (`gate_lock.py:273`, `:320`): in the hand run an orphan carrying the token but no browser name was neither listed nor stopped. It is what keeps the selftest off real processes; a bare list-only `reap` on this machine shows 4 real orphaned `Google Chrome for Testing` processes, which I left alone.
- Docs entry: `git diff --word-diff` shows exactly one added sentence. Its claims match the observed behaviour (at least MIN minutes, default 30, TERM then KILL after 2 s, each pid printed, live parent never listed or stopped).
- No red-under-load re-run rule: a grep of added lines for `under.load|re-run|rerun|retry|flaky` matches only the `rerun with --kill` hint string.
- Dependents:
  - `python3 plugins/sdlc-lite/scripts/check.py` rc=0 in the tree and at base (item 34 pins phrases in both changed files).
  - `python3 scripts/check-packaging.py` reports PASS; `git diff --check` is clean.
  - `fanout.py` calls only `gate_lock.py run` (`:342`, `:2483`), whose path is unchanged and covered by selftest sections 1-5, so the fanout selftest and full `check.sh` were not run. `fanout.py:1888` `'reap'` is a temp dir name.
- Untracked `.sdlc/0304-gate-lock-reap/base-sha` and `verifier-L3.attempt.json` are runner artifacts. No fake processes were left behind (`ps` grep empty after every run).

## For the next attempt
None
