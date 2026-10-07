## Task goal
`messenger` is a required declared agent for Claude and Codex that polls `messages/new/<harness>` every 10 seconds through `messages.py` and notifies its parent, with `check.py` coverage that fails when the agent file or its Codex mapping is missing.

## Step 2: Level-rubric note, Codex execution doc, AGENTS guidance, and messenger CLI alignment
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.

Tree state. The blocked L2 attempt's edits for items 1 to 4 are already committed at HEAD, in the conductor's commit `e7632cf` ("T-0178: record plan defect and replan request"). The handoff's `## Plan review` calls them uncommitted, but `git status --short` lists only `.sdlc/` files, and `git diff --stat bd9dafa e7632cf` lists the four prose files and five regenerated TOMLs. For items 1 to 4, run the criteria and change a file only where a criterion is red. Items 5 and 6 are new work, and their criteria are red now. Because those edits are committed, `git diff "$SDLC_BASE_SHA"` (HEAD at this step dir's first builder run) no longer shows them. The content criteria read the files directly, so they hold whatever the base is.

1. `plugins/sdlc-lite/skills/level-rubric/SKILL.md` (in the tree): the prose section `## Session agents (not run.sh roles)` after the `## Single-level roles` table. It says the `conductor` and the `messenger` are session agents, the messenger is not a run.sh role, its Claude model `claude-haiku-4-5` is pinned in its own front matter, its Codex agent `sdlc-messenger-l1` comes from `adapters/codex/models.json`, and `run.sh` has no messenger case. It stays prose, never a table row: `check.py`'s rubric parser (check.py:64 to 75) reads any `| <name> | L1 | <model effort> |` row as a role level and would flag `messenger:L1` as missing from run.sh.
   - Contract dependents: the planner and plan-reviewer agents preload this skill (`  - level-rubric` at `agents/planner.md:5` and `agents/plan-reviewer.md:5`), so `codex_roles.py generate` rewrites `sdlc-planner-l1`, `sdlc-planner-l2`, `sdlc-planner-l3`, `sdlc-plan-reviewer-l1`, and `sdlc-plan-reviewer-l1-alternate` (already regenerated in the tree).
   - Left untouched on purpose: `sdlc-conductor-l1.toml` and `agents/conductor.md`. The conductor names the level-rubric in its body but has no `skills:` list, and `codex_roles.instructions()` inlines only the skills listed there (`codex_roles.py:56`, `re.findall(r'^  - ([a-z-]+)$', header, re.M)`), so regenerating never adds the note to the conductor TOML. This was the plan defect in the blocked attempt. Do not edit `agents/conductor.md`.
2. `docs/references/codex-role-execution.md` (in the tree) holds:
   - the row `| Messenger | Terra 5.6 low | | | | |` after the Conductor row.
   - the count sentence `There are 25 project agent definitions: 21 base definitions and four alternate definitions ...`, with `conductor/messenger` ending the "one each of" list. The criterion derives 25 and 21 at run time from the generated TOMLs (every `*.toml`, and those not ending `-alternate.toml`), so it stays right when another lane adds an agent and updates the sentence.
   - the paragraph naming `sdlc-messenger-l1` as a native subagent that polls `messages/new/codex` every 10 seconds through `messages.py`. It states the Codex limits (own lifetime, no Claude tools or hooks, no Claude hook enforces anything on Codex) and the Claude limits (lives only while its session runs, polling needs Monitor or a loop) separately, and says one host working says nothing about the other.
   - Leave `docs/reports/*` untouched: those are dated evidence records (for example `plan-reviewer-live-run.md` "installed 24 project agents").
3. `plugins/sdlc-lite/AGENTS.md` (in the tree), Contracts and routing: the bullet saying `agents/` also holds two session agents that are not `run.sh` roles, the `conductor` and the `messenger`, and that `scripts/check.py` excludes both from the run.sh agreement check and checks the messenger's file and Codex mapping.
4. Repo `AGENTS.md` (in the tree), Authoritative sources table: the `Shared role and output contracts` source cell reads `plugins/sdlc-lite/agents/*.md` (pipeline roles plus the `conductor` and `messenger` session agents).
5. New: `plugins/sdlc-lite/agents/messenger.md`, `## Loop` items 3 and 4 (lines 14 and 15). Step 1 wrote them against T-0177's handoff. The built `messages.py` differs in two ways, so a messenger following the body as written gets exit 1 on every claim:
   - `read` requires `--receiver`: `messages.py:7` is `read <path-or-id> --receiver NAME`, and `messages.py:17` says a missing `--receiver` exits 1.
   - `list` prints `<state>`, `<receiver>`, `<id>`, `<sender>`, `<topic>` separated by tabs, never a path (`messages.py:833`). `read` prints the front matter, the trust line, and the body, never a path (`messages.py:728` to `731`).
   Replace lines 14 and 15 with exactly these two lines:
   ```text
   3. Claim each listed message with `messages.py read <id> --receiver <harness>`, where `<id>` is the third tab-separated field of its `list` line.
   4. End your turn with a report that lists, for each claimed message, its id and its path `read/<harness>/<id>.md` in the mailbox (`.sdlc/messages/` in the main checkout). That report is how your parent is notified. Your parent spawns you again to keep polling.
   ```
   - Keep every other line. The step 1 literal strings and `check.py`'s `MESSENGER_WORDS` (`check.py:368`: `model: claude-haiku-4-5`, `messages.py`, `.sdlc/messages/AGENTS.md`) must all still be present. The new item 3 still holds `messages.py read`.
   - This replaces step 1's Do wording "claims each message with `messages.py read <path>`". Step 1 stays done and is not rebuilt.
   - Contract dependent: the generated Codex agent inlines this body. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. It rewrites only `adapters/codex/agents/sdlc-messenger-l1.toml`, because `instructions(role)` reads only `agents/<role>.md` and no agent preloads the messenger. Never hand-edit the TOML.
6. New: line 77 of `docs/specs/ticket-stages/design.md`, the Message bus `Status:` line, says the `messenger` agent (T-0178) is pending, and that goes stale when this ticket lands. T-0177 updated the same line in its own step 4 (commit `5efe084`). Replace that line with exactly:
   ```text
   Status: the mailbox core is built in T-0177 (`scripts/messages.py` and the `run.sh` notice). The `messenger` agent is built in T-0178 (`plugins/sdlc-lite/agents/messenger.md` and the generated Codex agent `sdlc-messenger-l1`). The entry files with the live run (T-0179) are pending.
   ```
7. No em dashes and no trailing whitespace in any file written. `run.sh`, `agents/conductor.md`, and the hooks stay untouched.

Focused checks: the criteria below.
### Acceptance criteria
- `grep -qE "messenger.*not a .?run\.sh.? (pipeline )?role" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `for a in planner-l1 planner-l2 planner-l3 plan-reviewer-l1 plan-reviewer-l1-alternate; do grep -qF "The messenger is not a run.sh role" plugins/sdlc-lite/adapters/codex/agents/sdlc-$a.toml || exit 1; done`
- `grep -qE "^\| Messenger \| Terra 5\.6 low \|" docs/references/codex-role-execution.md`
- `d=plugins/sdlc-lite/adapters/codex/agents; n=$(ls "$d"/*.toml | wc -l | tr -d " "); b=$(ls "$d"/*.toml | grep -vc -- "-alternate\.toml$"); grep -qF "There are $n project agent definitions: $b base definitions" docs/references/codex-role-execution.md`
- `f=docs/references/codex-role-execution.md; for w in "sdlc-messenger-l1" "no Claude tools or hooks" "conductor/messenger"; do grep -qF -- "$w" "$f" || exit 1; done`
- `grep -qF messenger plugins/sdlc-lite/AGENTS.md`
- `grep -qF messenger AGENTS.md`
- `f=plugins/sdlc-lite/agents/messenger.md; grep -qF "messages.py read <id> --receiver <harness>" "$f" && ! grep -F "messages.py read" "$f" | grep -qvF -- "--receiver"`
- `grep -qF "read/<harness>/<id>.md" plugins/sdlc-lite/agents/messenger.md`
- `grep -qF "messages.py read <id> --receiver <harness>" plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`
- `grep -qF "agent is built in T-0178" docs/specs/ticket-stages/design.md`
- `! grep -qF "(T-0178) and the entry files" docs/specs/ticket-stages/design.md`
- (guard) `f=plugins/sdlc-lite/agents/messenger.md; for w in "messages.py count --receiver" "messages.py list" "messages.py read" ".sdlc/messages/AGENTS.md" "10 seconds" "follow_up_requested" "Monitor" "no Claude tools or hooks" "publish"; do grep -qF -- "$w" "$f" || exit 1; done`
- (guard) `! grep -q $'\xe2\x80\x94' AGENTS.md plugins/sdlc-lite/AGENTS.md docs/references/codex-role-execution.md docs/specs/ticket-stages/design.md plugins/sdlc-lite/skills/level-rubric/SKILL.md plugins/sdlc-lite/agents/messenger.md`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- AGENTS.md plugins/sdlc-lite docs`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "AGENTS\.md|docs/codex-role-execution\.md|docs/specs/ticket-stages/design\.md|plugins/sdlc-lite/(AGENTS\.md|skills/level-rubric/SKILL\.md|agents/messenger\.md|adapters/codex/models\.json|adapters/codex/agents/sdlc-[a-z0-9-]+\.toml|scripts/codex_roles\.py|scripts/check\.py)" | { ! grep -q .; }`
