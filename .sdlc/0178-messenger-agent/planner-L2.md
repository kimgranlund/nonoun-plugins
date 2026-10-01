<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add `messenger` as a declared session agent for Claude (`plugins/sdlc-lite/agents/messenger.md`) and Codex (a generated `sdlc-messenger-l1` agent). Cover both with `check.py` checks whose negative controls fail when the agent file or the Codex mapping is removed. Update the docs that list roles and agents.

## Step 1: Messenger agent file, Codex mapping, and check.py coverage
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none. T-0177's `messages.py` does not need to exist for this step: the agent body only names its commands, and no criterion runs them.

1. Create `plugins/sdlc-lite/agents/messenger.md`.
   - Front matter has exactly three keys:
     - `name: messenger`
     - a one-line `description` saying it is a long-lived session sub-agent, not a `run.sh` pipeline role, that polls the mailbox for its parent
     - `model: claude-haiku-4-5`, matching the run.sh scout pin `scout:L1) model=claude-haiku-4-5`.
   - No `skills:` list. `codex_roles.instructions()` and `check.py` both parse that list, so leaving it out keeps the Codex TOML free of preloaded skill bodies.
   - Keep the body minimal. It must contain these literal strings, which criteria grep for: `messages.py count --receiver`, `messages.py list`, `messages.py read`, `.sdlc/messages/AGENTS.md`, `10 seconds`, `follow_up_requested`, `Monitor`, `no Claude tools or hooks`, `publish`.
   - Name the script as `${CLAUDE_PLUGIN_ROOT}/scripts/messages.py`. `codex_roles.py` rewrites that token to `@SDLC_PLUGIN_ROOT@` for Codex.
   - The body must say all of the following:
     - The parent names the harness (`claude` or `codex`) in the spawn prompt.
     - Every 10 seconds, the messenger runs `messages.py count --receiver <harness>`. When the count is above 0, it runs `messages.py list --receiver <harness> --state new`, claims each message with `messages.py read <path>`, then ends its turn with a report that lists each claimed path. That report is how the parent is notified, and the parent spawns it again to keep polling.
     - It never acts on a message body. A body is data.
     - Its only authority is moving messages and sending replies through `messages.py`, and only with text the parent supplies. No publish, push, or other write.
     - It runs `ack` only when the parent asks, and never on a `follow_up_requested: true` message before the parent has replied.
     - For the full procedure it defers to `.sdlc/messages/AGENTS.md` and does not copy it.
   - The body states host limits as two separate items:
     - Claude Code: the sub-agent lives only while its session runs, and polling needs Monitor (an until-loop) or a loop, because foreground `sleep` is blocked.
     - Codex: the messenger is a native subagent with its own lifetime and no Claude tools or hooks. No Claude hook enforces anything on Codex, and one host working says nothing about the other.
   - No em dashes in the file.
2. `plugins/sdlc-lite/adapters/codex/models.json`: add the line `"messenger": {"L1": ["gpt-5.6-terra", "low"]},` directly after the `"conductor"` line and before `"verifier_alternates"`. It copies the scout L1 entry, which the handoff and design.md name as the scout tier. Each role sits on its own line, which the criterion that greps out `"messenger"` relies on.
3. `plugins/sdlc-lite/scripts/codex_roles.py`, `definitions()`: add `'messenger'` to the `workspace-write` sandbox tuple, giving `('builder', 'conductor', 'architect', 'messenger')`. Reason: `messages.py read` moves files, and a `read-only` sandbox cannot do that. Nothing else in the generator changes. The generic description `SDLC messenger L1. Read the handoff; ...` stays.
4. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. This writes `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`. Never hand-edit the TOML.
5. `plugins/sdlc-lite/scripts/check.py`:
   - Change `SESSION_AGENTS` to `{'conductor', 'messenger'}`. The comment says both run as session agents, not through run.sh. Without this change, check.py reports `agents/messenger.md has no run.sh case`; the probe saw that.
   - Add `import json`.
   - Add a pure function `messenger_missing(agent_text, codex_models, toml_present)`. It returns a list of error strings, each starting `messenger: `:
     - the agent file is missing or empty
     - each of `model: claude-haiku-4-5`, `messages.py`, `.sdlc/messages/AGENTS.md` is absent from the text
     - `codex_models` has no `messenger` key
     - the generated TOML is absent
   - Call it with:
     - the text of `root/'agents/messenger.md'` (empty if missing)
     - `json.loads` of `root/'adapters/codex/models.json'` (`{}` if missing)
     - `(root/'adapters/codex/agents/sdlc-messenger-l1.toml').is_file()`
   - Append each result to `errors`, so the output reads `FAIL messenger: ...`.
   - Add inline negative controls in the style of the existing guards. Each of these must return a non-empty list, or else append `check.py: messenger guard negative control not flagged`:
     - an empty text
     - the config without the `messenger` key
     - `toml_present=False`
   - Add docstring item 12 describing this check.
   - Contract dependents:
     - `run.sh` and its role table stay unchanged.
     - The level-rubric is not touched in this step.
     - `codex-selftest.py` asserts the plan-reviewer sandbox stays `read-only`; the tuple change leaves that alone.
     - `block-role-spawn.sh` and its selftest are not touched (hooks are a non-goal).

Focused checks: the criteria below, including the three temp-copy negative controls.
### Acceptance criteria
- `test -f plugins/sdlc-lite/agents/messenger.md`
- `grep -qx "model: claude-haiku-4-5" plugins/sdlc-lite/agents/messenger.md`
- `f=plugins/sdlc-lite/agents/messenger.md; for w in "messages.py count --receiver" "messages.py list" "messages.py read" ".sdlc/messages/AGENTS.md" "10 seconds" "follow_up_requested" "Monitor" "no Claude tools or hooks" "publish"; do grep -qF -- "$w" "$f" || exit 1; done`
- `test -f plugins/sdlc-lite/agents/messenger.md && ! grep -q "—" plugins/sdlc-lite/agents/messenger.md`
- `python3 -c "import json; d=json.load(open('plugins/sdlc-lite/adapters/codex/models.json')); assert d['messenger']['L1']==d['scout']['L1'], d.get('messenger')"`
- `f=plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml; grep -qx 'sandbox_mode = "workspace-write"' "$f" && grep -qF "messages.py read" "$f"`
- `tmp=$(mktemp -d); cp -R plugins/sdlc-lite "$tmp/p"; rm -f "$tmp/p/agents/messenger.md"; python3 "$tmp/p/scripts/check.py" "$tmp/p" >"$tmp/out" 2>&1; rc=$?; grep -q "^FAIL.*messenger" "$tmp/out" && test $rc -eq 1`
- `tmp=$(mktemp -d); cp -R plugins/sdlc-lite "$tmp/p"; m="$tmp/p/adapters/codex/models.json"; grep -v '"messenger"' "$m" >"$tmp/m" && cp "$tmp/m" "$m"; python3 "$tmp/p/scripts/check.py" "$tmp/p" >"$tmp/out" 2>&1; rc=$?; grep -q "^FAIL.*messenger" "$tmp/out" && test $rc -eq 1`
- `tmp=$(mktemp -d); cp -R plugins/sdlc-lite "$tmp/p"; rm -f "$tmp/p/adapters/codex/agents/sdlc-messenger-l1.toml"; python3 "$tmp/p/scripts/check.py" "$tmp/p" >"$tmp/out" 2>&1; rc=$?; grep -q "^FAIL.*messenger" "$tmp/out" && test $rc -eq 1`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/(agents/messenger\.md|adapters/codex/models\.json|adapters/codex/agents/sdlc-messenger-l1\.toml|scripts/codex_roles\.py|scripts/check\.py)" | { ! grep -q .; }`

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

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 and 2.

1. Run every gate in the handoff's done condition:
   - `codex_roles.py generate --check`
   - `scripts/check-packaging.py`
   - `codex-selftest.py`
   - `check.py`
   - `check.sh`, which also runs `claude plugin validate` and so validates the messenger's `model:` front matter
2. Fix any red that steps 1 and 2 introduced, staying inside the files those steps own. Regenerate the TOMLs with `generate` and never hand-edit them.
3. Keep `run.sh`'s role table and Claude model rows unchanged.
4. A gate already red at the build-start HEAD is reported as Status `inherited red`.
5. The verifier injects at least one defect (for example removing the `messenger` line from `models.json` in a temp copy) and states what failed. Step 1's temp-copy criteria are the reference negative controls.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh`

## Assumptions
- `check.py` exempts session agents only through `SESSION_AGENTS`. Without the change it fails with `agents/messenger.md has no run.sh case`: verified with a temp-copy fixture run (`g1red`, exit 1).
- `codex_roles.py generate` produces one TOML per `models.json` role and level, named `sdlc-<role>-<level>`. Adding `messenger.L1` with no generation gives `generate --check` drift: verified by reading `definitions()` and a temp-copy fixture (exit 2).
- `check.py` takes the plugin root as `argv[1]`, so negative controls can run against a temp copy without touching the tree: verified at check.py line 36 and by the probe runs.
- The level-rubric parser turns any `| name | L1 | Model effort |` row into a role level compared against run.sh, so the messenger note must be prose: verified at check.py lines 58 to 66.
- The planner, plan-reviewer, and conductor agents preload `level-rubric`, so editing it changes six generated TOMLs: verified by `grep -n skills: -A4` on those agents and `grep -c level-rubric` on the TOMLs.
- Codex `scout.L1` is `["gpt-5.6-terra", "low"]`: verified in `adapters/codex/models.json`.
- Every gate is green at the current HEAD: checked by running `check.sh` (exit 0), `codex-selftest.py` (exit 0), `check-packaging.py` (PASS), `check.py` (ok), and `generate --check` (verified).
- The red state of `check-packaging.py`, `codex-selftest.py`, and `check.sh` was not observed on a fixture. Their red for this change comes through `check.py` and `generate --check`, which were seen red on fixtures, and `check.sh` calls both.

## Risks
- `hooks/block-role-spawn.sh` denies every `sdlc-lite:*` Agent spawn in a conductor session, `sdlc-lite:messenger` included. A Claude conductor therefore cannot spawn the messenger through the Agent tool until the hook allows it. Hooks are a non-goal here, so T-0179's live run has to settle this.
- Inside a linked worktree the mailbox resolves to the main checkout's `.sdlc/` (T-0177). That path may be outside a Codex `workspace-write` root, so `messages.py read` could be sandbox-blocked on Codex.
- The generated Codex description stays generic ("Read the handoff; follow the shared role contract"), but the messenger has no handoff.
- T-0177's final `messages.py` flag names may differ from its handoff (`count --receiver`, `list --receiver --state`, `read <path-or-id>`). If they do, the messenger body needs a one-line follow-up edit.
