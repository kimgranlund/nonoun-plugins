<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Finish T-0178 (the `messenger` session agent for Claude and Codex with `check.py` coverage, docs, and every gate green): keep step 1 as done, rewrite step 2 so its regenerated-TOML check names only the agents that preload level-rubric and the messenger body matches the built `messages.py`, and keep step 3.

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
- `test -f plugins/sdlc-lite/agents/messenger.md && ! grep -q $'\xe2\x80\x94' plugins/sdlc-lite/agents/messenger.md`
- `python3 -c "import json; d=json.load(open('plugins/sdlc-lite/adapters/codex/models.json')); assert d['messenger']['L1']==d['scout']['L1'], d.get('messenger')"`
- `f=plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml; grep -qx 'sandbox_mode = "workspace-write"' "$f" && grep -qF "messages.py read" "$f"`
- `tmp=$(mktemp -d); cp -R plugins/sdlc-lite "$tmp/p"; rm -f "$tmp/p/agents/messenger.md"; python3 "$tmp/p/scripts/check.py" "$tmp/p" >"$tmp/out" 2>&1; rc=$?; grep -q "^FAIL.*messenger" "$tmp/out" && test $rc -eq 1`
- `tmp=$(mktemp -d); cp -R plugins/sdlc-lite "$tmp/p"; m="$tmp/p/adapters/codex/models.json"; grep -v '"messenger"' "$m" >"$tmp/m" && cp "$tmp/m" "$m"; python3 "$tmp/p/scripts/check.py" "$tmp/p" >"$tmp/out" 2>&1; rc=$?; grep -q "^FAIL.*messenger" "$tmp/out" && test $rc -eq 1`
- `tmp=$(mktemp -d); cp -R plugins/sdlc-lite "$tmp/p"; rm -f "$tmp/p/adapters/codex/agents/sdlc-messenger-l1.toml"; python3 "$tmp/p/scripts/check.py" "$tmp/p" >"$tmp/out" 2>&1; rc=$?; grep -q "^FAIL.*messenger" "$tmp/out" && test $rc -eq 1`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/(agents/messenger\.md|adapters/codex/models\.json|adapters/codex/agents/sdlc-messenger-l1\.toml|scripts/codex_roles\.py|scripts/check\.py)" | { ! grep -q .; }`

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
2. `docs/codex-role-execution.md` (in the tree) holds:
   - the row `| Messenger | Terra 5.6 low | | | | |` after the Conductor row.
   - the count sentence `There are 25 project agent definitions: 21 base definitions and four alternate definitions ...`, with `conductor/messenger` ending the "one each of" list. The criterion derives 25 and 21 at run time from the generated TOMLs (every `*.toml`, and those not ending `-alternate.toml`), so it stays right when another lane adds an agent and updates the sentence.
   - the paragraph naming `sdlc-messenger-l1` as a native subagent that polls `messages/new/codex` every 10 seconds through `messages.py`. It states the Codex limits (own lifetime, no Claude tools or hooks, no Claude hook enforces anything on Codex) and the Claude limits (lives only while its session runs, polling needs Monitor or a loop) separately, and says one host working says nothing about the other.
   - Leave `docs/validation/*` untouched: those are dated evidence records (for example `plan-reviewer-live-run.md` "installed 24 project agents").
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
6. New: line 77 of `docs/ticket-stages/design.md`, the Message bus `Status:` line, says the `messenger` agent (T-0178) is pending, and that goes stale when this ticket lands. T-0177 updated the same line in its own step 4 (commit `5efe084`). Replace that line with exactly:
   ```text
   Status: the mailbox core is built in T-0177 (`scripts/messages.py` and the `run.sh` notice). The `messenger` agent is built in T-0178 (`plugins/sdlc-lite/agents/messenger.md` and the generated Codex agent `sdlc-messenger-l1`). The entry files with the live run (T-0179) are pending.
   ```
7. No em dashes and no trailing whitespace in any file written. `run.sh`, `agents/conductor.md`, and the hooks stay untouched.

Focused checks: the criteria below.
### Acceptance criteria
- `grep -qE "messenger.*not a .?run\.sh.? (pipeline )?role" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `for a in planner-l1 planner-l2 planner-l3 plan-reviewer-l1 plan-reviewer-l1-alternate; do grep -qF "The messenger is not a run.sh role" plugins/sdlc-lite/adapters/codex/agents/sdlc-$a.toml || exit 1; done`
- `grep -qE "^\| Messenger \| Terra 5\.6 low \|" docs/codex-role-execution.md`
- `d=plugins/sdlc-lite/adapters/codex/agents; n=$(ls "$d"/*.toml | wc -l | tr -d " "); b=$(ls "$d"/*.toml | grep -vc -- "-alternate\.toml$"); grep -qF "There are $n project agent definitions: $b base definitions" docs/codex-role-execution.md`
- `f=docs/codex-role-execution.md; for w in "sdlc-messenger-l1" "no Claude tools or hooks" "conductor/messenger"; do grep -qF -- "$w" "$f" || exit 1; done`
- `grep -qF messenger plugins/sdlc-lite/AGENTS.md`
- `grep -qF messenger AGENTS.md`
- `f=plugins/sdlc-lite/agents/messenger.md; grep -qF "messages.py read <id> --receiver <harness>" "$f" && ! grep -F "messages.py read" "$f" | grep -qvF -- "--receiver"`
- `grep -qF "read/<harness>/<id>.md" plugins/sdlc-lite/agents/messenger.md`
- `grep -qF "messages.py read <id> --receiver <harness>" plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`
- `grep -qF "agent is built in T-0178" docs/ticket-stages/design.md`
- `! grep -qF "(T-0178) and the entry files" docs/ticket-stages/design.md`
- (guard) `f=plugins/sdlc-lite/agents/messenger.md; for w in "messages.py count --receiver" "messages.py list" "messages.py read" ".sdlc/messages/AGENTS.md" "10 seconds" "follow_up_requested" "Monitor" "no Claude tools or hooks" "publish"; do grep -qF -- "$w" "$f" || exit 1; done`
- (guard) `! grep -q $'\xe2\x80\x94' AGENTS.md plugins/sdlc-lite/AGENTS.md docs/codex-role-execution.md docs/ticket-stages/design.md plugins/sdlc-lite/skills/level-rubric/SKILL.md plugins/sdlc-lite/agents/messenger.md`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- AGENTS.md plugins/sdlc-lite docs`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "AGENTS\.md|docs/codex-role-execution\.md|docs/ticket-stages/design\.md|plugins/sdlc-lite/(AGENTS\.md|skills/level-rubric/SKILL\.md|agents/messenger\.md|adapters/codex/models\.json|adapters/codex/agents/sdlc-[a-z0-9-]+\.toml|scripts/codex_roles\.py|scripts/check\.py)" | { ! grep -q .; }`

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
- Step 1 passed and is kept: verified by `step-1/verifier-L2.md` (Verdict pass) and commit `bd9dafa`. Its text matches `planner-L2.md` except for one criterion. That criterion now writes U+2014 as `$'\xe2\x80\x94'` instead of a literal em dash. The check and the bytes are the same, and the change keeps this file free of em dashes, as the user's global rule requires. Step 1 is not split again, so the change has no effect. Verified by diffing the two step 1 blocks: one line differs.
- Step 3 text is byte-identical to `planner-L2.md`: verified by diffing the two step 3 blocks.
- The blocked step 2 edits are committed at HEAD in `e7632cf`, not left uncommitted: verified by `git status --short` (only `.sdlc/0178-messenger-agent/planner-L3.attempt.json`) and `git diff --stat bd9dafa e7632cf` (AGENTS.md, docs/codex-role-execution.md, plugins/sdlc-lite/AGENTS.md, level-rubric SKILL.md, five TOMLs).
- Step 2's criteria for items 1 to 4 are green now, as the plan review requires, and were red at step 2's original base: verified by running each on the current tree (all rc 0) and through `git show bd9dafa:<file> | grep ...` (all rc 1; derived counts at bd9dafa were n=25, b=21 against a doc that said 24).
- Step 2's criteria for items 5 and 6 are red now for the right reason (the old `read <path>` line, no `read/<harness>/<id>.md`, a stale messenger TOML, the old design.md Status line): verified by running each (all rc 1).
- `sdlc-conductor-l1.toml` cannot carry the level-rubric note: verified at `codex_roles.py:56` (skills come only from the `  - name` front matter list) and in `agents/conductor.md` lines 1 to 4 (no `skills:` key). `grep -l messenger` over the TOMLs lists only messenger, the three planners, and the two plan-reviewers.
- The messages.py interface: `read <path-or-id> --receiver NAME` (`messages.py:7`), a missing `--receiver` exits 1 (`messages.py:17`), `list` rows are tab-separated with the id third (`messages.py:833`), and `read` prints no path (`messages.py:728` to `731`).
- Editing `agents/messenger.md` regenerates only `sdlc-messenger-l1.toml`: verified at `codex_roles.py:53` to `61` (`instructions(role)` reads `agents/<role>.md`) and because no agent lists `messenger` under `skills:`.
- The new step-2 dir starts with no `base-sha` after /chain 4.2 moves `step-2/` to `step-2.superseded-1/`, so run.sh sets `SDLC_BASE_SHA` to HEAD at the first builder run: verified at `run.sh:299` to `315` and in `skills/chain/SKILL.md` section 4 item 2. The scope criterion also holds with base `bd9dafa`, because every file `e7632cf` changed is on its allow-list.
- Step 2 guards are green now and can go red, verified as follows:
  - the literal-string loop is red with `f=/dev/null` (rc 1).
  - the em-dash grep is red on a temp file holding U+2014 (rc 1).
  - `git diff --check "$SDLC_BASE_SHA" -- f` is red in a temp repo with a trailing space (rc 2).
  - `generate --check` is red on a temp plugin copy with an extra level-rubric line (rc 2, "generated agent drift").
- Step 3's run.sh guard is red in a temp repo with a changed `run.sh` (rc 1).
- Every step 3 gate is green on the current tree, and the tree was unchanged afterwards:
  - `generate --check` (verified)
  - `check-packaging.py` (PASS)
  - `codex-selftest.py` (rc 0, installs 25 agents)
  - `check.py` (`ok: 19 role levels, 9 agents checked`)
  - `check.sh` (rc 0)
- `steps.py lint` passes on this plan: verified on a copy in `/tmp` with a stub `plugins/sdlc-lite/AGENTS.md` (`steps lint: ok`).
- Updating the design.md Status line belongs to this ticket: T-0177 updated the same line in its step 4 (`git show --stat 5efe084` lists `docs/ticket-stages/design.md`).

## Risks
- `hooks/block-role-spawn.sh` denies every `sdlc-lite:*` Agent spawn in a conductor session, `sdlc-lite:messenger` included. Until the hook allows it, a Claude conductor cannot spawn the messenger through the Agent tool. Hooks are a non-goal, so T-0179's live run must settle this.
- `.sdlc/messages/AGENTS.md` does not exist yet (checked in both the main checkout and this worktree). The messenger defers to it, so its full procedure is missing until T-0179 writes the entry files.
- Inside a linked worktree the mailbox resolves to the main checkout's `.sdlc/messages`. That path can sit outside a Codex `workspace-write` root, so `messages.py read` could be blocked by the sandbox on Codex. Only T-0179's live run can show this.
- The generated Codex description stays generic ("Read the handoff; follow the shared role contract"), but the messenger has no handoff.
- shellcheck is not installed on this host, so `check.sh` skips it. That part of the step 3 gate is unverified here. This ticket changes no `.sh` file.
- If the conductor runs `steps.py split --only 2` before moving `step-2/` aside, split refuses because `step-2/` still holds `builder-L2.md`. /chain 4.2 moves it first.
