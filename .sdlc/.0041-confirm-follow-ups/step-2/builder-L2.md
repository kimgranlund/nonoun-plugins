<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/file/SKILL.md`: step 3 now has six numbered substeps in this order: dry run (the force-close flow is kept, and `--force` is added to later calls only if approved), drop follow-ups the artifacts already answer with a reason each, AskUserQuestion multiSelect with the recommended set first, `close --skip`, an unattended default that is stated in the report, and the report itself. The "only if ticket front matter" guard is kept.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: added `[--dry-run] [--skip N[,N...]]` to the `argument-hint` close form. Item 4 now describes dry-run, `--skip`, the automatic duplicate skip (normalized title or slug), and that `--reason` combines with neither.
- `CLAUDE.md`: the tickets.py bullet's `close` description now covers `--dry-run`, `--skip`, the duplicate auto-skip, and that `/file` runs the dry run and confirms first.
- `.claude/agents/sdlc-lite-author.md`: line 16 has a new sync rule for dry-run, skip, and duplicate skipping across tickets.py, the /ticket skill, the /file skill, and CLAUDE.md.

## Checks
- `grep -- '--dry-run'` across the 4 files: matches in all 4.
- `grep -- '--skip'` across the 3 files: matches in all 3.
- `git diff --stat`: `agents/filer.md` is not listed.
- `git diff -U0 | grep '^+' | grep -c '—'`: prints 0.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0, including the steps and run selftests, shellcheck, and plugin validate.

## Notes
- `git diff --stat` also lists `tickets.py` and `.sdlc/0041-confirm-follow-ups/handoff.md`. Both were already changed before this step (step 1's work), and I did not edit them.
- The acceptance criterion about the order of `/file` step 3 was checked by reading the file, not by a command.
