## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 18: review-traces skill: ingest, detect, and diagnose stages
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/skills/review-traces/SKILL.md` in the shape of `skills/dig/SKILL.md`: frontmatter (`name: review-traces`; `description:` one sentence saying it reviews a project's sdlc run traces for waste and bugs caused by sdlc-lite with no model call in the ingest and detect stages, then diagnoses, verifies, proposes, and files each confirmed finding as a ticket after approval; `argument-hint: "<repo> [--lanes-dir DIR]... [--max N]"`; `allowed-tools:` Bash for `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traces.py`, `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh`, `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py`, and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py`, plus Read, Write, Grep, Glob, AskUserQuestion), the Codex host line every skill carries (it names `../sdlc-lite/SKILL.md`), the `SDLC_ROUTING_REASON` line, and a review task dir `.sdlc/<review task>/` created from the arguments per handoff-format. Sections: `## 1. Ingest and detect` (run `traces.py ingest <repo> [--lanes-dir DIR]...`, then `traces.py detect`, then `traces.py clusters --max N` with N from `--max`, default 5; these spend no model call), and `## 2. Diagnose` (per cluster write `.sdlc/<review task>/cluster-<k>/handoff.md` from the fenced ```cluster-question template with `## Goal`, `## Context` listing the cluster's finding ids, summaries, and evidence paths, `## Question` asking for the cause layer (sdlc-lite, project, host, task text) and the plugin file or rule at fault, and the sentence `Read only the evidence paths listed above; nothing else.`; run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh archaeologist L1` on it, or `scout L1` when the question is where a rule lives; read the result's `## Summary` for the layer and file; keep only findings whose layer is sdlc-lite for stage 3, the rest go to the stage 5 report). Leave placeholders for sections 3 to 5, which steps 19 to 21 fill.
### Acceptance criteria
- `head -1 plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -qx -- '---'`
- `grep -q '^name: review-traces$' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF '../sdlc-lite/SKILL.md' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'archaeologist L1' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'scout L1' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'clusters --max' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'traces.py ingest' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'traces.py detect' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- ````awk '/^```cluster-question$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^## Question$'````
- ````awk '/^```cluster-question$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -qF 'Read only the evidence paths listed above; nothing else.'````
- `grep -qF 'SDLC_ROUTING_REASON' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`
