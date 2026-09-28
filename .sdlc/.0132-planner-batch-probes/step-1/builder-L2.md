<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/planner.md: after rule 1's first sentence, added a sentence that says to run all of a step's probes in one Bash call, one `bash -c` per criterion, and to print each criterion's label, exit code, and at most the first 5 lines of its output. It also puts rule 11's un-negated guard runs in the same call. All existing sentences are unchanged.
- plugins/sdlc-lite/scripts/check.py: added `'one Bash call': ('agents/planner.md',),` to `PLAN_DEFECT_DOCS`, right after `'gates green'`.
- CLAUDE.md: extended the Decisions sentence that starts "The planner runs each criterion once before writing it" so it also covers the single batched Bash call, the label, the exit code, and the first 5 output lines.

## Checks
- All 11 acceptance criteria, each run with `bash -c`: all exited 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0.

## Notes
- The `.sdlc/0132-planner-batch-probes/` changes in git status were already there from the planning run. They are not part of this step.
- I did not run the negative control on a copy (phrase removed, entry kept). check.py passing with the entry shows the guard is wired in.
