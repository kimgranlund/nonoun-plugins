## Task goal
`/sdlc-lite:clarify` turns a fuzzy ask into a plan-ready intent in one pass: a handoff or plan-doc front block that `steps.py lint` and `plan_check.py` accept without a rewrite, with questions asked only when the answer changes the lane, level, cost or an irreversible step.

## Step 2: Rewrite the clarify skill, report the replay, gates green
level: L3
guard timeout: 2700
### Do
Depends on: step 1 (the lint and the eval cases).

Rewrite `plugins/sdlc-lite/skills/clarify/SKILL.md`.
- Keep the frontmatter `name`, the Codex host line, and `allowed-tools`. Add `Bash` to `allowed-tools` only if the skill tells the agent to run `plan_check.py` or `steps.py`.
- The upstream `find-intent` (github.com/kimgranlund/claude-plugins at 5f9819b86b4dc77934fd36226025cec2e2a88d81, `harness/skills/find-intent`) is prior art only. Read it if it is reachable, and vendor nothing.
- T-0447's `work-items.md` card has not landed (no such file is in the tree). The skill therefore defines the block itself, which the handoff allows.

Changes, each small:
1. Output. Map the agent-task schema onto the task handoff (`${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`):
   - goal goes in `## Goal`;
   - context pointers go in `## Context`;
   - constraints go in `## Constraints`;
   - `## Intent` holds, in order: `Literal ask:`, `Level: L<n> (lane: <solo|lean|full>; cost: <one line>; reversible: <yes|no, why>)`, `Deltas:`, `Do:`, `Non-goals:` (out of scope), `Done when:` (definition of done, a `- ` list), and `Verify: <one backticked command>`.

   For multi-step work, the skill also adds the Outcome block (`Outcome:`, `Measured by:`, `Rubric:`, `Negative control:`) as defined in `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/references/outcome-block.md`. It names `${CLAUDE_PLUGIN_ROOT}/skills/plan-doc/references/plan-doc-format.md` for a plan doc. Keep the `Done when:` label and the `(gap: <what>; default: <x>)` shape, because specgate.py and open-questions read them.
2. Done when. Every item is a backticked runnable command or the literal `unverifiable: <why>`. Move an item to `[owner: maintainer]` when it reads its own step's verifier result, pins a fixed sha, or needs a live run that a verifier cannot do. The skill ends by running `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py clarify --file <handoff>` and fixing any FAIL.
3. Size and lane. Estimate `Level:` (L1 to L4) from the level table in `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`. Once the handoff with ticket front matter exists, `steps.py lane <task dir>` (`${CLAUDE_PLUGIN_ROOT}/scripts/steps.py`) confirms the lane. It reads the ticket `size:` (`lane_action`, steps.py line 2829). Ask only about forks that change the lane, the level, the cost, or an irreversible action. Default everything else and state the default.
4. Tracker. Before any lane, claim the existing ticket or create one in the repo's tracker: local `.sdlc` with `claimed_by: <who> <date>`, GitHub, or Linear. Never create a second tracker. State the lane-lifecycle section 8.1 rule in the skill's own words, with no link outside the skill folder.
5. Pass-through:
   - an ask that is already scoped gets the one-line reply `already scoped: <ask>, done = <condition>`;
   - a follow-up that points at session state ("any updates", "do that") gets the one-line reply `follow-up: <what it points at>` and runs no extraction.
6. Add a `## Low tier` section with three steps (extract, default, write) for Sonnet low and Haiku. It matches the per-tier overlay design: a directed procedure plus a default for each gap. The design is `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md`; read it only, do not link it.
7. Unchanged:
   - the unattended gap and default format;
   - at most one AskUserQuestion round, with the recommendation first and no drip questions.

   A changed ask means a re-run of clarify, not a patch of the old block.

Also in the skill: name `evals/README.md`. Keep the skill self-contained (check.py item 42) and free of retired size letters (item 43).

Update the one dependent line in `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, line 122, to read: `Written by /clarify: literal ask, level, verify, deltas, do, non-goals, done when. Optional.`

These other dependents route to clarify by name only, so they stay unchanged on purpose (found by `git grep -ln clarify -- plugins/sdlc-lite docs/specs`):
- `agents/conductor.md` line 16;
- `skills/chain/SKILL.md` line 33;
- `skills/sdlc-lite/SKILL.md` line 20;
- `skills/open-questions/SKILL.md` line 16.

If the builder does change `agents/conductor.md`, it runs `codex_roles.py generate`. That is why `adapters/codex/agents/` is in the scope allow-list.

Replay:
1. Run the new skill in unattended mode on each of the eight `evals/*.ask.md`. Apply the skill to each ask in fresh context where you can.
2. Write each output under `$SDLC_TMP_WORKTREES`.
3. Lint each output with `plan_check.py clarify --file`.
4. Write `docs/reports/<YYYY-MM-DD>-clarify-v2-replay.md`, dated the day of the build. The name must match docs_check.py's report-name rule. The report holds:
   - one line per case, ending `pass`, `fail`, or `unverified`;
   - exactly one summary line: `Result: <n> of 6 non-pass-through accepted, <m> of 2 pass-through one-line`, or `Result: unverified: <why>` if no replay could run;
   - a statement that a builder replay is not an independent model run.

The ticket's target is 5 of 6 and 2 of 2. A lower count is reported as it is, not hidden.

Then run every gate below and fix any red that step 1 or this step introduced, inside the scope list.
- `check.sh` exited 0 after 14m35s and 15m21s in earlier verifier records under fanout load, so give its Bash call a timeout of at least 2700000 ms.
- A gate that was already red at the build-start HEAD is `inherited red`.
### Acceptance criteria
- (red) `for p in "plan_check.py clarify" "unverifiable: " "[owner: maintainer]" "steps.py lane" "Level: L" "Verify: " "Outcome:" "already scoped: " "follow-up: " "claimed_by:" "## Low tier" "(gap: " "one AskUserQuestion round" "re-run"; do grep -qF -- "$p" plugins/sdlc-lite/skills/clarify/SKILL.md || exit 1; done`
- (red) `sed -n "/^## Intent/,/^## Context/p" plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qF "level, verify"`
- (red) `for f in docs/reports/*-clarify-v2-replay.md; do grep -qE "^Result: ([0-6] of 6 non-pass-through accepted, [0-2] of 2 pass-through one-line|unverified: .+)$" "$f" || exit 1; done`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/(scripts/plan_check\.py|skills/clarify/|skills/handoff-format/SKILL\.md|adapters/codex/agents/)|docs/reports/[0-9-]+-clarify-v2-replay\.md$)" | { ! grep .; }`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite docs/reports`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
