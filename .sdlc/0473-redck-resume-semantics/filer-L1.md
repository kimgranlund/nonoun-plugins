<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0473: redck: phase against the working tree, bind to an ancestor base

## PR body
Summary
- `redck.py` now gives a second builder on a branch that already holds the first builder's commits `pre-edit` (at record) or `preserved` (at audit), where it used to give `retrospective` or `missing`. A control from a different lineage is still refused.
- This covers T-0470 finding 6 (`docs/reports/2026-10-12-maison-wave-7b-mechanics.md`, item 6).

Changes
- `plugins/sdlc-lite/scripts/redck.py`:
  - `dirty_paths` diffs against HEAD, not the base. The phase is read against the working tree.
  - `cmd_record` stores `at_sha` (HEAD, or None outside git) on each control entry.
  - A new `same_lineage` helper binds a control whose `base_sha` is the current base or an ancestor of HEAD. Answers are cached per sha within one audit.
  - In `span_status`, an own pre-edit control that is not red defers to an earlier same-lineage pre-edit red (`preserved` or `prelude-changed`) before it returns `green-baseline`.
  - The docstring and the retrospective stderr reason are updated.
- `plugins/sdlc-lite/scripts/redck.py` selftest: the old "different base sha no longer binds the original" check is replaced by T2. T1, T3, T4 and T5 are new and run in a second repo so the shared repo's `out.txt` and dirty-set checks stay valid.
- `docs/references/sdlc-internals.md`: the `scripts/redck.py` paragraph is rewritten to cover the HEAD-based phase, `at_sha`, and ancestor binding.

Verification
- Verifier L2 verdict: pass on all 12 criteria.
- Observed red: the builder added the T-0473 cases first and ran selftest before the fix. It failed on the T1, T2, T4 and T5 titles. The builder ran `redck record` before its first edit.
- Verifier mutants:
  - Reducing `same_lineage` to equality fails T2 and T4.
  - Making `same_lineage` always true fails only T3, the not-an-ancestor control.
  - Returning `green-baseline` before the earlier-red lookup fails only T4.
  - A copy of the base-sha scripts prints no T-0473 lines.
- Green after the fix:
  - `redck.py selftest` passes, 29 ok lines. Only the old line-394 check changed its verdict.
  - `check.py` passes.
  - `git diff --check` is clean.
  - The scope guard passes: only the two files above differ outside `.sdlc`.
  - `bash plugins/sdlc-lite/scripts/check.sh` exits 0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- redck: `record` reads the phase against the working tree at HEAD and stores `at_sha`. `audit` binds a control whose base is the current base or an ancestor of HEAD. An own pre-edit green control defers to an earlier same-lineage pre-edit red. A second builder on the same branch now gets `pre-edit` or `preserved`.

## Follow-ups
- note: `plugins/sdlc-lite/agents/builder.md:28`, its generated `builder-L*.md` files and the Codex TOMLs still say a second `record` "is only a base control and is stored as retrospective". That is now partly stale. The handoff forbade prompt wording changes, so it was left alone; revise it in a prompt-wording ticket.
- note: `cmd_record` still exits 1 on a green span. That was outside the three rules and left unchanged.
