<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1 (evidence files exist and are non-empty, report exists): pass. Evidence: I ran the loop as written. All 10 files under `docs/reports/reorg-apply-live-run/` are non-empty and `docs/reports/reorg-apply-live-run.md` exists.
- Criterion 2 (apply output and dry-run listing greps): pass. Evidence: the full grep chain printed `c2ok`. It covers `final check: pass`, 2 `^commit ` lines, the move line, both `claude-response.md:60` rewrites, no `plugin-compatibility.md:9` rewrite and no `claude-response.md:55` rewrite. `dry-run.txt` has 23 `^rewrite` lines, which is 19 for batch `references` plus 4 for batch `other`, matching the expected listing. It has the `batch 1: references` and `batch 2: other` headers.
- Criterion 3 (refusals): pass. Evidence: `refuse-digest.txt` matches `^reorg.py: refused: digest mismatch` and `refuse-approve.txt` matches `^reorg.py: refused: `.
- Criterion 4 (README links): pass. Evidence: `(reports/reorg-apply-live-run.md)` is in `docs/README.md` and `(../reports/reorg-apply-live-run.md)` is in `docs/repo-onboarding/README.md`.
- Criterion 5 (no "not built" or stale status text): pass. Evidence: the grep chain printed `c5ok`. The `reorganization.md` status line now reads "Apply is built in `reorg.py` by T-0233 ... Glob classification and `onboard plan` are not built."
- Criterion 6 (Open findings outcome column and `reorg.py` mentions): pass. Evidence: rows N1, N2, N3, N5, N8, N9 and N15 each match `| (Settled|Not applicable): `, and both docs name `reorg.py`. The grep chain printed `c6ok`.
- Criterion 7 (`REORG_NEEDS` and check.py): pass. Evidence: `REORG_NEEDS` is in `check.py`. `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` printed `ok: 19 role levels, 9 agents checked` with rc 0.
  - The diff shows docstring item 38 and a `REORG_NEEDS` block that mirrors item 30.
  - The block has an in-line negative control for every phrase in every file. The control reports "negative control not flagged" if a removed phrase goes unflagged, and none were reported on this run.
  - The builder separately saw a flag when it removed `--approve` from the procedure.
- Criterion 8 (no em dash or trailing whitespace in the 5 files): pass. Evidence: run through `bash -c`, the command printed `c8ok`. My first zsh attempt failed only because the unquoted `$fs` did not word-split.
- Guard `check.sh`: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` exited rc=0. The tail shows `run selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`. The log has no `FAIL` lines. check.sh now calls `reorg.py selftest`.
- Guard `scripts/check-packaging.py`: pass. Evidence: it printed `PASS: catalog parity, identity, skill routes, hook isolation and context links`, rc 0.
- Guard `git diff --check`: pass. Evidence: it printed `diffcheck_ok`.
- Guard scope: pass. Evidence: both scope checks printed `guardscope_ok`.

Other checks:
- **Report claims against evidence.**
  - `follow.txt` has 19 lines, matching the report's "19 lines, followed the rename".
  - `links.txt` shows 838 checked and 12 broken both before and after, with the same set.
  - The report states the clone HEAD `56e99a4d...` and says the managed-block refresh was proven by the selftest only.
  - It records the `design.md:368` and `:370` limit.
  - Files carrying `sdlc-lite:managed:start` are `docs/repo-onboarding/design.md` and `docs/reports/onboard-live-run.md`, neither of which is among the rewritten files. The "selftest only" claim holds.
- **Steelman.** I considered failing the criteria for `reorg.py` being untracked and for the builder's `git add -N` on the report files. The handoff says reorg.py is uncommitted, and the guard's untracked allowlist includes it. `git add -N` is an index-only change that item 32 of `check.py` needs in order to resolve the links. Builder note 1 explains it. Dropped.
- **Not re-run.** I did not re-run the live clone or the pre-build baseline. The evidence files are the recorded output of that run, and the dry-run and apply listings and the refusal texts are self-consistent.

## Out of scope changes
None. `git diff --name-only $SDLC_BASE_SHA` and the untracked list, excluding `.sdlc`, stay inside the allowed set. `.sdlc/0233-reorg-apply/handoff.md` is modified, but `.sdlc` is excluded from the scope guard and is the ticket's own record.

## For the next attempt
None
