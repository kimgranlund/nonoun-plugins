<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- Merge commit `46c554b` "Merge fanout/night-2026-09-29-fanout (T-0152)" on `fanout/night-2026-09-29`. Parents: `8cec9d1` (integration) and `8a6900b` (lane).
- `docs/maintenance/sdlc-internals.md`: two conflicts resolved, both lanes kept.
  - `scripts/tickets.py` paragraph: HEAD's `depends` `file:`/`cap:` text plus the lane's `external_branch:` sentence.
  - `scripts/fanout.py` paragraph: the lane's external-lane text (`<lane>@<branch>=...` usage and semantics) plus HEAD's `reap-tmp-worktrees.sh` step after the driver.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: conflict resolved by taking the lane's extended "Ids are allocated" rule (with `external_branch`) and keeping HEAD's `depends:` rule line.
- `plugins/sdlc-lite/scripts/fanout.py`: selftest conflict resolved by keeping both cases. HEAD's reap case stays as case 11, and the lane's external-lane case is renumbered to case 12, in both the code comment and the module docstring.
- Auto-merged with no conflict: `plugins/sdlc-lite/scripts/tickets.py`, `plugins/sdlc-lite/skills/fanout/SKILL.md`, `.sdlc/0152-external-lane-owners/**`.

## Checks
- Pre-merge: `git status --short` showed no tracked changes, only the untracked `.sdlc/merge-t-0152/`.
- `bash plugins/sdlc-lite/scripts/check.sh` on the resolved tree before the commit: rc=0. Every selftest passed, including "fanout selftest: PASS". Log: `.sdlc/merge-t-0152/step-1/check-merged.log`.
- `bash plugins/sdlc-lite/scripts/check.sh` in `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD^1`: rc=0. Log: `check-base.log`. Worktree removed afterwards.
- Comparing the two logs: 196 `ok:` lines each. The only non-`ok:` differences are temp paths, timings, and one DeprecationWarning (`steps.py` escape sequence) that appears in the base run only. No new findings.
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`: pass.
- `git merge-base --is-ancestor fanout/night-2026-09-29-fanout HEAD`: pass.
- (guard) `! git rev-parse -q --verify MERGE_HEAD`: pass.
- (guard) diff-tree `--cc` conflict-marker grep: pass.
- `git diff --check HEAD^1 HEAD -- docs plugins`: clean.

## Notes
- The merged external-lane path in `fanout.run_ticket` returns before the driver, so the tmp-prefix reap only runs for regular lanes. That matches both lanes' docs.
- The check logs are left as untracked files in the artifacts dir. Nothing was pushed.
