<!-- role=builder level=L1 model=sonnet effort=low -->
All criteria pass except criterion 4 (single-file-changed check), which fails due to pre-existing planning artifacts already dirty in the tree before this step began, not caused by this step's edit.

## Status
done

## Changes
.claude/agents/sdlc-lite-author.md: appended two sentences to the "Plan-defect route" bullet mirroring planner.md rules 11 and 12 ("a `(guard)` is a check that can go red... before writing it" and "a file other lanes also change... checked by membership or structure...").

## Checks
- `grep -n "membership or structure" .claude/agents/sdlc-lite-author.md`: match found, pass.
- `grep -n "can go red" .claude/agents/sdlc-lite-author.md`: match found, pass.
- `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md`: exits 1, pass.
- `git diff HEAD -- .claude/agents/sdlc-lite-author.md | grep -c '^-[^-]'`: 0, pass.
- `git diff --stat HEAD | awk '{print $1}'`: lists `.claude/agents/sdlc-lite-author.md` and `.sdlc/0134-mirror-the-extended-planner-rules/handoff.md`; `git ls-files --others --exclude-standard` lists `.sdlc/0134-mirror-the-extended-planner-rules/planner-L1.md`, `runs.jsonl`, `step-1/`. I confirmed via a scoped `git stash push -u -- .claude/agents/sdlc-lite-author.md` (then `apply`/`drop` of that same entry) that `.sdlc/0134-mirror-the-extended-planner-rules/handoff.md` and the untracked planner artifacts were already present in the tree before my edit — they are the planner's own output from producing this step, not something I touched. Criterion as literally run fails, but not because of anything this step did.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0, pass.

## Notes
Criterion 4's `awk '{print $1}'` list is not scoped to just my file only because the working tree already carried the planner's uncommitted output (`.sdlc/0134-mirror-the-extended-planner-rules/handoff.md` modified, `planner-L1.md`, `runs.jsonl`, `step-1/` untracked) before this step started — verified this predates my change. I did not touch any file outside `.claude/agents/sdlc-lite-author.md`. Verifier should treat this pre-existing planning-pipeline dirt as expected state, not a step-1 defect.
