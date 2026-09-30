## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 19: review-traces skill: verify stage
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Fill `## 3. Verify` in `plugins/sdlc-lite/skills/review-traces/SKILL.md`: per finding kept by stage 2, write `.sdlc/<review task>/finding-<id>/handoff.md` from the fenced ```finding-step template, a step handoff per handoff-format: `## Task goal` (the review goal), `## Step 1: Reproduce finding <id>`, `level: L1`, `### Do` saying there is nothing to build, this step only reproduces the finding from its evidence, and `### Acceptance criteria` with one line per evidence entry rendered as a runnable check (`<evidence command>` in the template): a `{path, line}` entry becomes `sed -n '<line>p' <path> | grep -qF '<quoted text>'`, an `{attempt_id}` entry becomes `grep -q '<attempt_id>' <attempt.json path>`; lint it with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <that handoff>`, then run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh verifier L1` on it. A `fail` verdict drops the finding from the propose list; `pass` keeps it; no verdict reruns the verifier once, then drops. State that a finding whose evidence cannot be rendered as commands is dropped before any run.
### Acceptance criteria
- `grep -qF 'verifier L1' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'steps.py lint' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'drops the finding from the propose list' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- ````d=$(mktemp -d) && mkdir "$d/t" && awk '/^```finding-step$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | sed -e 's#<evidence command>#test -f README.md#' > "$d/t/planner-L1.md" && grep -q '^## Step 1: ' "$d/t/planner-L1.md" && grep -q '^level: L1$' "$d/t/planner-L1.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/t/planner-L1.md"````
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`
