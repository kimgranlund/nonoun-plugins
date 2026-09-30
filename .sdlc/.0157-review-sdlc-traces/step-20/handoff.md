## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 20: review-traces skill: propose stage
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Fill `## 4. Propose` in `plugins/sdlc-lite/skills/review-traces/SKILL.md`: write `.sdlc/<review task>/propose/handoff.md` from the fenced ```propose-handoff template: `## Goal` (one ticket draft per confirmed sdlc-lite finding), `## Context` listing per finding its id, detector, summary, evidence paths, the diagnose result path, and the verify result path, and per ticket the required lines `Repro:` (steps from the evidence), `Expected:`, `Actual:` (quoted verbatim from the finding summary and evidence), and `Red check:` (one command that fails today and passes once the defect is fixed: a `traces.py selftest` case, a script selftest case, or a fixture), and `## Constraints` (drafts only, one `## Step` per ticket at level L1, no code, no filing). Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh planner L2` on it once; each `## Step` of the result is one draft: its title is the ticket title, its Do the ticket body, its acceptance criteria the red check.
### Acceptance criteria
- `grep -qF 'planner L2' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- ````awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Repro:' && awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Expected:' && awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Actual:' && awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Red check:'````
- `grep -qF 'quoted verbatim' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`
