## Task goal
`messenger` is a required declared agent for Claude and Codex that polls `messages/new/<harness>` every 10 seconds through `messages.py` and notifies its parent, with `check.py` coverage that fails when the agent file or its Codex mapping is missing.

## Step 2: Level-rubric note, Codex execution doc, and AGENTS guidance
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.

1. `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: add a short prose section `## Session agents (not run.sh roles)` after the `## Single-level roles` table.
   - It states:
     - The `conductor` and the `messenger` are session agents.
     - The messenger is not a `run.sh` role. Its Claude model `claude-haiku-4-5` is pinned in its own front matter, and its Codex agent `sdlc-messenger-l1` comes from `adapters/codex/models.json`.
     - `run.sh` has no messenger case.
   - Write it as prose, never as a table row. `check.py`'s rubric parser reads any line shaped like a `| <name> | L1 | <model effort> |` row as a role level and would flag `messenger:L1` as missing from run.sh.
   - The planner, plan-reviewer, and conductor agents preload this skill, so run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` afterwards. That regenerates `sdlc-planner-l1/l2/l3`, `sdlc-plan-reviewer-l1`, `sdlc-plan-reviewer-l1-alternate`, and `sdlc-conductor-l1` TOMLs; these are contract dependents.
2. `docs/codex-role-execution.md`:
   - Add a table row `| Messenger | Terra 5.6 low | | | | |` after the Conductor row.
   - Change the count sentence to `There are 25 project agent definitions: 21 base definitions and four alternate definitions ...`, and add `messenger` to the "one each of" list.
   - Add a short paragraph naming `sdlc-messenger-l1` as a native subagent that polls `messages/new/codex` every 10 seconds through `messages.py`. On Codex it has its own lifetime and no Claude tools or hooks, and no Claude hook enforces anything on Codex. The Claude messenger lives only while its session runs, and its polling needs Monitor or a loop. One host working says nothing about the other.
   - Leave `docs/validation/*` untouched: those are dated evidence records (for example `plan-reviewer-live-run.md` "installed 24 project agents").
3. `plugins/sdlc-lite/AGENTS.md`, Contracts and routing: add a bullet saying `agents/` also holds two session agents that are not `run.sh` roles, the `conductor` and the `messenger`, and that `check.py` excludes both from the run.sh agreement check and checks the messenger's file and Codex mapping.
4. Repo `AGENTS.md`, Authoritative sources table: change the row `Shared role and output contracts` so its source cell reads `plugins/sdlc-lite/agents/*.md` (pipeline roles plus the `conductor` and `messenger` session agents).
5. No em dashes anywhere.

Focused checks: the criteria below, plus `generate --check`.
### Acceptance criteria
- `grep -qE "messenger.*not a .?run\.sh.? (pipeline )?role" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qE "^\| Messenger \| Terra 5\.6 low \|" docs/codex-role-execution.md`
- `f=docs/codex-role-execution.md; for w in "25 project agent definitions" "21 base definitions" "sdlc-messenger-l1" "no Claude tools or hooks"; do grep -qF -- "$w" "$f" || exit 1; done`
- `grep -qF messenger plugins/sdlc-lite/AGENTS.md`
- `grep -qF messenger AGENTS.md`
- `for a in planner-l1 planner-l2 planner-l3 plan-reviewer-l1 plan-reviewer-l1-alternate conductor-l1; do grep -qF messenger plugins/sdlc-lite/adapters/codex/agents/sdlc-$a.toml || exit 1; done`
- (guard) `! grep -q "—" AGENTS.md plugins/sdlc-lite/AGENTS.md docs/codex-role-execution.md plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- AGENTS.md plugins/sdlc-lite docs`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "AGENTS\.md|docs/codex-role-execution\.md|plugins/sdlc-lite/(AGENTS\.md|skills/level-rubric/SKILL\.md|agents/messenger\.md|adapters/codex/models\.json|adapters/codex/agents/sdlc-[a-z0-9-]+\.toml|scripts/codex_roles\.py|scripts/check\.py)" | { ! grep -q .; }`
