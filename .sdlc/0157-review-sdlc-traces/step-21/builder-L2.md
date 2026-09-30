<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/review-traces/SKILL.md`: swapped the step 21 placeholder for two sections. `## 5. File` covers the model-call cap, what goes to report.md, the no-person rule, one AskUserQuestion round with the drafts batched four at a time, and filing with `tickets.py new bug` plus the handoff.md body. `## Report` lists the outputs.

## Checks
- AC1 `grep -qF 'AskUserQuestion'` and `grep -qF 'at most 4 options'`: pass
- AC2 `grep -qF 'tickets.py new bug'`: pass
- AC3 `grep -qF 'report.md'`: pass
- AC4 `grep -qF 'files nothing'` and `grep -qF 'SDLC_HEADLESS'`: pass
- AC5 `grep -qF 'clusters + findings + 1'`: pass
- (guard) scope command: pass
- `git diff --check` on the file: pass

## Notes
- The old placeholder heading was `## 5. Report and file`. The handoff asked for `## 5. File` and a closing `## Report`, so I replaced it with those two headings.
- I also sent two more things to report.md: findings dropped in stage 3 (with the reason) and drafts the user does not approve. Stages 2 and 3 already say these go to "the stage 5 report", so this matches them.
