## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 21: review-traces skill: file stage and the model-call cap
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Fill `## 5. File` and a closing `## Report` in `plugins/sdlc-lite/skills/review-traces/SKILL.md`: one AskUserQuestion round over the drafts, at most 4 options per question (batch the drafts four at a time, recommendation first); each approved draft is filed with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py new bug <slug> "<title>"` (numbered mode follows `<root>/config`) and its `handoff.md` body gets the draft's Repro, Expected, Actual, Context (evidence paths, diagnose and verify result paths), and Constraints (the red check lands before or with the fix); findings whose layer is not sdlc-lite go to `.sdlc/<review task>/report.md` (one section per finding: layer, evidence, diagnose summary) and are never filed; a session with no person present (`SDLC_HEADLESS=1`, a fanout lane, or `claude -p`) writes every draft to `report.md` and files nothing. State the model-call cap: at most `clusters + findings + 1` role runs per review (one archaeologist or scout per cluster, one verifier per finding, one planner), bounded by `--max N`; the ingest and detect stages spend none. The `## Report` lists the findings path, the clusters, the drafts filed with their ticket ids, and the report.md path.
### Acceptance criteria
- `grep -qF 'AskUserQuestion' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'at most 4 options' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'tickets.py new bug' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'report.md' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'files nothing' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'SDLC_HEADLESS' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'clusters + findings + 1' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`
