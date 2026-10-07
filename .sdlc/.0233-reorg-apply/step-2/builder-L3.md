<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/reports/reorg-apply-live-run.md` (new): the live-run report, with `Recorded:`, what ran, results and limits. Each claim names its evidence file. It records the clone's HEAD `56e99a4db400fed029bcb6358c2421047ec4695b`, the layout commit `49be510d` and the base `0b58bd23`.
- `docs/reports/reorg-apply-live-run/` (new, 10 files): `plan.json`, `clone-layout.txt`, `dry-run.txt`, `apply.txt`, `git-log.txt`, `follow.txt`, `links.txt`, `refuse-digest.txt`, `refuse-approve.txt`, `selftest.txt`.
- `docs/repo-onboarding/reorganization.md`: v0.7 status line saying apply is built in `reorg.py` (T-0233) and glob classification and `onboard plan` are not. Changed line 5, the Mechanics, Classification and User decisions rows, and the Plan, Digest, Approve, Apply, Refusals and Final check sections, which now describe the built behavior and point to `reorg.py`'s header. "Validation required before shipping" is renamed "Validation" and gains a Selftest gate column. The Open findings table gains an Outcome column with Settled or Not applicable for N1, N2, N3, N5, N8, N9 and N15. The `git log --follow` assumption now cites the report.
- `docs/repo-onboarding/reorganization-plan-procedure.md`: the status line, the line-5 sentence and Step 3 now describe the built `reorg.py` with the `--dry-run` and `--approve <digest>` commands. No "not built" is left.
- `docs/repo-onboarding/README.md`: lines 3, 6 and 7 updated, and the report added under Evidence.
- `docs/README.md`: one line for the report, after the inventory report line.
- `plugins/sdlc-lite/scripts/check.py`: docstring item 38 and a `REORG_NEEDS` / `reorg_bad` block that copies item 30, with a negative control for each phrase in each file.

## Checks
- Live run in a clone of HEAD `0b58bd23` in a temp folder outside the repository, with a layout commit that has empty Homes and three frozen paths:
  - **Dry run:** exit 0. It listed 19 rewrites for batch `references`, 4 for batch `other` and 2 baseline links. This is exactly the listing the handoff expected; there was no refusal and no finding.
  - **Apply with that digest:** exit 0, printing `commit 240bf77c… references`, `commit 56e99a4d… other` and `final check: pass`.
  - **Apply listing vs dry-run listing:** identical, checked with `diff` after leaving out the commit and final-check lines.
- `rename_refs.py links` in the clone before and after the apply: 838 checked and 12 broken both times, the same set.
- `git log --follow` on `docs/references/codex-role-execution.md`: 19 lines, so Git followed the rename. The file has 87 lines and 4 were rewritten.
- Refusals, in a second clone reset to `49be510d`:
  - Editing `docs/sdlc-lite/pillars.md` after the dry run and applying with the old digest printed `reorg.py: refused: digest mismatch…` and exited 1.
  - Applying with no `--approve` printed `reorg.py: refused: no --approve…` and exited 1.
  - HEAD was unchanged both times.
- `reorg.py selftest`: 30 `ok` lines, then `reorg selftest: PASS`.
- Acceptance criteria 1 to 8: all PASS, run as written through `bash -c`. For criterion 8, I confirmed separately that the em-dash pattern does match an em dash.
- Negative control for `REORG_NEEDS`: with `--approve` removed from the procedure, check.py printed `FAIL check.py: reorganization apply: procedure missing "--approve"`. File restored; check.py then printed `ok`.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 in 513 s, including `reorg selftest: PASS`.
- (guard) `python3 scripts/check-packaging.py`: PASS.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`: exit 0.
- (guard) Scope check (only allowed paths changed or untracked): exit 0.

## Notes
1. I ran `git add -N` (intent-to-add, no commit) on the new report and its evidence folder. Without it, check.py item 32 failed: `rename_refs.py links` only resolves links to tracked files, so the 4 new links to the untracked report counted as broken. `reorg.py` is still untracked, as step 1 left it.
2. I removed trailing spaces from two blank commit-message lines in `git-log.txt`. Nothing else in the evidence was edited. Temp paths in the refusal files show as `<clone2>`.
3. The clone's commits were made under a Git identity set only in the clone (`builder`); the report says so.
4. The managed-block hash refresh is proven by the selftest's `managed` gate only: no rewritten file holds a `sdlc-lite:managed:start` marker. The report says this.
5. `docs/docs-schema/design.md:368` and `:370` were rewritten in the clone because they are repo-root path tokens. The report records this as a limit. In this repo, `design.md:364` was left unchanged as the handoff asked.
6. The temp clones are removed. I created no git worktree.
