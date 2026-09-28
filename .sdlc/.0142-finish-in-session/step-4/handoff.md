## Task goal
Small related work gets finished in the session that found it. A new ticket exists only for work that is out of scope, large, or needs the user.

## Step 4: /fix fast lane skill
level: L2
### Do
1. Create `plugins/sdlc-lite/skills/fix/SKILL.md` with frontmatter `name: fix`, a `description:` (fast lane for a size-S item: a doc line, a lint tweak, one test, a one-file fix; the conductor writes the step handoff itself, runs builder L1 or L2 and verifier L1, and closes the ticket inline with `tickets.py close --reason`; no planner, no filer, no follow-up tickets; use for "quick fix", "small fix", a size-S ticket; NOT for work touching more than one file's behavior or needing a plan, which is /chain), `argument-hint: <ticket slug | one-line ask>`, and `allowed-tools:` with `Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*)`, `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*)`, `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*)`, `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/board.py:*)`, Read, Write, Grep, Glob, AskUserQuestion. Body: (1) size gate: S means docs, a lint tweak, one test, or a fix in one file with an obvious effect, provable by 1 to 3 checks; anything else → say so in one line and route to `/sdlc-lite:chain`; (2) handoff: `.sdlc/<slug>/handoff.md` exists (a ticket) or is created per handoff-format's free-text rule; write `.sdlc/<slug>/step-1/handoff.md` yourself per the step template (`## Task goal`, `## Step 1: <title>`, `level: L1` or `L2` per the builder rubric, `### Do`, `### Acceptance criteria` with 1 to 3 criteria, each a runnable command span red now or a `(guard)` green now, no `||`, no pinned sha), run `steps.py lint` on it and fix any refusal; never run `steps.py split`; (3) build and verify: `run.sh builder <level> <step handoff>`, `steps.py next` → `run.sh verifier L1`; a fail → one rebuild at the same level with the verifier's note under `## Previous attempt`; a second fail, a blocked builder, or `inherited` → stop, report, and offer /chain (the item was not size S); never bump, replan, or fix it yourself; (4) close: pass and ticket front matter → `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc close <slug> --reason "fixed in session by /fix: <one line>"`, no filer, no follow-ups; no ticket → nothing to close; (5) publish only after an AskUserQuestion approval as in /file step 4; report with `board.py --task <slug>`. Include the long-run rule in the chain's words (headless: foreground with the Bash `timeout` at 600000 or more, `SDLC_HEADLESS=1` launchers, never end the turn; interactive: `run_in_background: true`, wait for the completion notification, never poll with `sleep`), since check.py will guard it.
2. `plugins/sdlc-lite/agents/conductor.md`, Route every ask: `Size S (a doc line, a lint tweak, one test, a one-file fix) → /sdlc-lite:fix`, the fast lane with no planner, filer, or follow-up tickets; What you do yourself stays trivial edits only.
3. `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: extend the step 3 prose section: the `/fix` fast lane runs builder L1 or L2 (never higher) and verifier L1, one rebuild on a fail, no bump; a second fail hands the item to /chain.
4. `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the by-hand sentence from step 3 also names /fix (`step-1/`).
5. `plugins/sdlc-lite/scripts/check.py`: add `skills/fix/SKILL.md` to the long-run docs tuple (line 89) and `sdlc-lite:fix` in `agents/conductor.md` plus `fast lane` in `skills/fix/SKILL.md`, `agents/conductor.md`, and `skills/level-rubric/SKILL.md` to `FINISH_DOCS`.
6. Repo root `CLAUDE.md`: add `/fix` to the Launcher skills list with a short description.
### Acceptance criteria
- `test -f plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -q '^name: fix$' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -q '^description: ' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -q '^allowed-tools: ' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -q -- '--reason' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -qF 'steps.py lint' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -q 'sdlc-lite:fix' plugins/sdlc-lite/agents/conductor.md`
- `grep -qi 'fast lane' plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qF '/fix' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'skills/fix/SKILL.md' plugins/sdlc-lite/scripts/check.py`
- `grep -qF '/fix' CLAUDE.md`
- `d=$(mktemp -d); mkdir -p "$d/plugins"; cp -R plugins/sdlc-lite "$d/plugins/"; cp CLAUDE.md "$d/"; perl -pi -e 's/run_in_background/rib/g' "$d/plugins/sdlc-lite/skills/fix/SKILL.md"; out=$(python3 plugins/sdlc-lite/scripts/check.py "$d/plugins/sdlc-lite" 2>&1); rm -rf "$d"; printf "%s\n" "$out" | grep -q "skills/fix/SKILL.md.*run_in_background"`
- `d=$(mktemp -d); mkdir -p "$d/plugins"; cp -R plugins/sdlc-lite "$d/plugins/"; cp CLAUDE.md "$d/"; perl -pi -e 's/sdlc-lite:fix/sdlc-lite:fixx/g' "$d/plugins/sdlc-lite/agents/conductor.md"; out=$(python3 plugins/sdlc-lite/scripts/check.py "$d/plugins/sdlc-lite" 2>&1); rm -rf "$d"; printf "%s\n" "$out" | grep -q "agents/conductor.md.*sdlc-lite:fix"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` (this step extends check.py and the docs it guards; green at HEAD and it must stay green on the real tree; the full `check.sh` stays on the final step)
