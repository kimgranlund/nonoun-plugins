## Task goal
`/sdlc-lite:report` prints a short executive summary of the current agent thread by default, and the named views (tasks, signals, needs, context, cost, children, identity, evidence, full) on request, from records and the transcript, with no model call in the collector.

## Step 3: Loose ends
level: L1
### Do
- In `plugins/sdlc-lite/skills/report/SKILL.md` (line 22) and `plugins/sdlc-lite/skills/report/references/views.md` (line 9, the `summary` row), describe the summary as `report.py` prints it: state, needs, now, next, grade, plus `recent` and `unknown` lines when they are not empty, still at most 8 lines. Change only those two lines.
### Acceptance criteria
- (red) `grep -F "at most 8 lines" plugins/sdlc-lite/skills/report/SKILL.md | grep -F "recent" | grep -qF "unknown" && grep -E "^\| \`summary\`" plugins/sdlc-lite/skills/report/references/views.md | grep -F "recent" | grep -qF "unknown"`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 scripts/check-packaging.py`
