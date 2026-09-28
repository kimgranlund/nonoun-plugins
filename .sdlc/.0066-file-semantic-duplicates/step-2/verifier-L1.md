<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1, both strings in `skills/file/SKILL.md`: pass. Evidence: the grep pair exited 0 (`c1=0`), and the diff shows `likely duplicate` and `open T-NNNN` in steps 3.1 and 3.2.
- Criterion 2, check.py guard bites: pass. Evidence: on a temp copy check.py exited 0. After `sed 's/likely duplicate/likely dupe/g'` it exited 1 and printed `FAIL skills/file/SKILL.md: missing "likely duplicate"`. The temp copy also carries the builder's `open T-NNNN` check; only `likely duplicate` was broken in this run, and that alone made it go red.
- Criterion 3, `likely duplicate` in `.claude/agents/sdlc-lite-author.md`: pass. Evidence: the grep exited 0. The diff extends the sync sentence to cover the dry run's `open T-NNNN` listing and the /file likely duplicate step.
- Observable (`skills/file/SKILL.md` steps 3.2, 3.3, 3.5, 3.6): pass. Evidence, from the diff:
  - Step 3.2 compares each follow-up against the dry run's `open T-NNNN` lines and marks matches `likely duplicate of T-NNNN`, naming the id. It uses the T-0047 vs T-0002 example.
  - Step 3.3 leaves likely duplicates out of the recommended set and adds `--skip`.
  - Step 3.5 excludes them from the unattended set and `--skip`s their indices.
  - Step 3.6 reports the likely duplicates with the matching T-NNNN each.
  - I read this from the diff; it describes session instructions, not runtime output.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: rc=0, with the order, fanout, run and hook selftests all reporting PASS. It ended with `ok: shellcheck` and `ok: plugin validate`.

## Out of scope changes
`CLAUDE.md`, `plugins/sdlc-lite/scripts/tickets.py` and `plugins/sdlc-lite/skills/ticket/SKILL.md` are modified in the working tree but are not in this step's Do list. They look like step 1's uncommitted work: the step-2 SKILL.md text depends on the dry run's `open T-NNNN` output that tickets.py provides. I did not inspect their diffs.

## For the next attempt
None
