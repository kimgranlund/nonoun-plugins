<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout42/c/plugins/sdlc-lite/scripts/redck.py: four rule changes:
  - `dirty_paths(top, d)` now diffs against HEAD, not the base.
  - `cmd_record` stores `at_sha` (from `git rev-parse HEAD`, None outside git).
  - A new `same_lineage` helper binds a control whose base is the current base or an ancestor of HEAD. It caches the answer per sha for one audit; `cmd_audit` passes the cache into `span_status`.
  - In `span_status`, an own pre-edit control that is not red now defers to an earlier attempt's pre-edit red (`preserved` or `prelude-changed`) before falling back to `green-baseline`.

  The docstring's phase and binding text was rewritten (it now contains `at_sha` and `ancestor of HEAD`). The retrospective stderr reason now reads "differ from HEAD". Selftest: T2 replaces the old line-394 check, and T1, T3, T4 and T5 run in a second repo, `repo2`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout42/c/docs/references/sdlc-internals.md: the `scripts/redck.py` paragraph now covers:
  - the phase read against HEAD;
  - `at_sha`;
  - binding to the current base or an ancestor of HEAD;
  - `preserved` when this attempt's own pre-edit control is green;
  - the updated selftest coverage list.

## Checks
- `python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite/scripts/redck.py record .sdlc/0473-redck-resume-semantics/step-1/handoff.md`, run before the first edit: exit 0, "recorded 5 pre-edit control(s) red".
- Observed red: I added the T-0473 cases first, then ran `python3 plugins/sdlc-lite/scripts/redck.py selftest` before the fix. It exited 1:
  ```
  redck selftest: FAIL, these did not hold:
    - T-0473: base moved to HEAD, no A3 control: the A1 original on an ancestor base is preserved
    - T-0473: base kept, A1 work committed: the A3 record is pre-edit at a clean tree and stores at_sha
    - T-0473: an own pre-edit green defers to an earlier same-lineage pre-edit red: preserved
    - T-0473: work committed after the base with no earlier red is green-baseline (control)
  ```
  The other 25 checks printed `ok`, including T3 (`a control whose base is not an ancestor of HEAD is not bound (control)`).
- `python3 plugins/sdlc-lite/scripts/redck.py selftest` after the fix: PASS, exit 0, all 29 checks ok.
- The five `selftest 2>/dev/null | grep -qxF 'ok: T-0473: ...'` criteria (T1, T2, T3, T4, T5): each exit 0.
- Docstring and doc criterion (`'at_sha'` and `'ancestor of HEAD'` in `redck.__doc__`, plus `at_sha` in the sdlc-internals redck section): exit 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0.
- `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/redck.py docs/references/sdlc-internals.md`: exit 0, no output.
- Scope guard (`test -z "$( ... | grep -vxF -e redck.py -e sdlc-internals.md)"`): exit 0.
- `bash plugins/sdlc-lite/scripts/check.sh`, with SDLC_BASE_SHA set to 4694d0cd: exit 0.

## Notes
- Only the check named in the handoff (the old line 394) changed its verdict. Every other existing check kept its verdict.
- T4 commits `out.txt` in `repo2`, and T5 also needs to commit `out.txt`. So T4 ends with `git rm out.txt` and a commit, which keeps T5's base-to-HEAD commit meaningful with the literal `out.txt` name.
- As the handoff says, the stale wording in `agents/builder.md:28` ("a second `record` ... is stored as retrospective") and its generated copies is left untouched.
