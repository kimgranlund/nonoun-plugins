<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add a deterministic `plan_check.py clarify` lint with eval cases, then rewrite the clarify skill so its output is a plan-ready intent block that the lint accepts, with a reported replay and all gates green.

## Step 1: The `plan_check.py clarify` lint and the eval cases
level: L3
### Do
Depends on: none.

Implementation targets:
- `plugins/sdlc-lite/scripts/plan_check.py`. It gets a new kind `clarify` and a `check_clarify(text)` function. The new kind is added to the argparse `kind` choices and to `run_check`. It also gets its selftest cases and updated module docstring usage and kind lines.
- The new folder `plugins/sdlc-lite/skills/clarify/evals/`.

Settled interface. The evidence is that plan_check.py already lints planned blocks by kind and prints `FAIL <rule>: <why>` and `ok: <kind> plan passes` through `report()` (lines 1-10 and 835-847).
- Usage is `plan_check.py clarify [--text T | --file F]`. The text is not unwrapped, because a clarify block holds backticks. Findings print `FAIL <rule>: <why>` lines and exit 1. Otherwise it prints `ok: clarify plan passes` and exits 0.
- Pass-through: a text with exactly one non-empty line that starts with `already scoped: ` or `follow-up: ` passes with exit 0. Every other text runs the rules below. A single non-empty line that is not a pass-through also runs them, so `--text x` fails `clarify-goal`.
- The block it reads is the clarify output, which is a task handoff:
  - a `## Goal` heading with a non-empty body;
  - a `## Intent` heading whose body holds the lines `Level: L<1-4> ...` and `Non-goals: <text>`;
  - a `Done when:` line in `## Intent`, followed by inline text or by `- ` list items. Inline text counts as one item.
- The literal labels `Done when:` and `(gap: <what>; default: <x>)` stay unchanged. `plugins/sdlc-lite/scripts/specgate.py` (lines 32 and 364) reads `(red)` lines under `Done when`. `plugins/sdlc-lite/skills/open-questions/SKILL.md` line 16 reads the `(gap: ...; default: ...)` lines. Both are dependents left untouched on purpose.
- The rules are exactly these six ids:
  1. `clarify-goal`: `## Goal` is missing or empty.
  2. `clarify-non-goals`: `## Intent` has no `Non-goals:` line with text.
  3. `clarify-level`: `## Intent` has no `Level: L1` to `L4` line.
  4. `clarify-done`: `Done when:` is missing, or an item has neither a backticked command span nor the literal `unverifiable: ` followed by a reason. An item that starts with `[owner: maintainer]` is exempt.
  5. `clarify-done-defect`: an item that does not start with `[owner: maintainer]` and does one of these:
     - reads its own step's verifier result (it matches `verifier-L[0-9]`, `verifier-*`, or `verifier result`);
     - names a fixed sha, meaning a lowercase hex token of 7 to 40 characters with at least one digit and at least one letter a-f (so `$SDLC_BASE_SHA` and ordinary words pass);
     - needs a live run that a verifier cannot do (case-insensitive `live run`, `rehearsal`, or `throwaway project`).

     The evidence is the T-0438 Done when "one more rehearsal plan runs to `plan done` with no hand step" (`.sdlc/.0438-executor-live-run-fixes/handoff.md` line 20). It had to be moved to T-0439. See also `docs/reports/2026-10-11-plan-doc-live-run.md`.
  6. `clarify-pass-through`: the first non-empty line starts with `already scoped: ` or `follow-up: `, but the text has more lines. A pass-through must be one line.
- Selftest cases:
  - a `GOOD_CLARIFY` block that passes;
  - two one-line pass-throughs that pass;
  - one mutant per rule, flagged as exactly that rule and no other. A rule that flags `GOOD_CLARIFY` is a bug, as in `plan_selftest`.
  - one positive and one negative case for the `[owner: maintainer]` exemption.

  Each case label starts with `clarify: <rule-id> `. `expect()` prints `ok: clarify: ...` or `FAIL: clarify: ...` for those labels, the same way it already prints labels that start with `plan: ` (lines 1107-1111). These mutants are the observed-red negative control per rule that the ticket asks for.

Eval cases:
- Eight pairs of files:
  - `evals/<case>.ask.md` holds the ask near-verbatim, taken from this repo's history, plus one line naming its source.
  - `evals/<case>.expected.md` holds the reference clarify output.
- The cases:
  - `01-bare-goal`.
  - `02-wrong-unit`: "build an agent" for what is a deterministic check.
  - `03-conflicting-ask`.
  - `04-unattended-gap`: has a `(gap: ...; default: ...)` delta.
  - `05-multi-step`: the expected output also carries the plan-doc Outcome block lines `Outcome:`, `Measured by:`, `Rubric:` and `Negative control:`.
  - `06-bad-done-when`: the ask's done-condition is a live rehearsal, and the expected output moves it to `[owner: maintainer]`.
  - `07-already-scoped` and `08-follow-up`: the expected output is one line starting `already scoped: ` or `follow-up: `.
- Add `evals/README.md` saying how to replay: run clarify on each `.ask.md`, then run `plan_check.py clarify --file <output>`.
- The eval files sit under `skills/**`, so check.py items 42 and 43 apply to them:
  - item 42: no link that leaves the skill folder and no `plugins/` prose path;
  - item 43: no retired size letters, such as a size word followed by S, M or L.

  Write levels as L1 to L4, and name scripts as `${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py`.

Validation scope: the criteria below and `python3 plugins/sdlc-lite/scripts/plan_check.py selftest`. Contract dependents of plan_check.py, found by `git grep -n plan_check -- plugins scripts docs/specs docs/references`:
- `scripts/check.py` item 49 (`PLAN_DOC_NEEDS`, lines 1003-1010) greps plan_check.py for the plan-doc rule ids. This step keeps them.
- `plan_done.py` imports plan_check for kind `plan`, which stays unchanged.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/plan_check.py selftest 2>&1) && for r in clarify-goal clarify-non-goals clarify-done clarify-done-defect clarify-level clarify-pass-through; do printf "%s\n" "$out" | grep -qF "ok: clarify: $r " || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/plan_check.py clarify --text x); test $? -eq 1 && printf "%s\n" "$out" | grep -qF "FAIL clarify-goal"`
- (red) `for n in 01-bare-goal 02-wrong-unit 03-conflicting-ask 04-unattended-gap 05-multi-step 06-bad-done-when 07-already-scoped 08-follow-up; do test -s plugins/sdlc-lite/skills/clarify/evals/$n.ask.md || exit 1; python3 plugins/sdlc-lite/scripts/plan_check.py clarify --file plugins/sdlc-lite/skills/clarify/evals/$n.expected.md >/dev/null || exit 1; done`
- (red) `E=plugins/sdlc-lite/skills/clarify/evals; test "$(grep -c . $E/07-already-scoped.expected.md)" -eq 1 && grep -q "^already scoped: " $E/07-already-scoped.expected.md && test "$(grep -c . $E/08-follow-up.expected.md)" -eq 1 && grep -q "^follow-up: " $E/08-follow-up.expected.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/(scripts/plan_check\.py|skills/clarify/|skills/handoff-format/SKILL\.md|adapters/codex/agents/)|docs/reports/[0-9-]+-clarify-v2-replay\.md$)" | { ! grep .; }`

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

## Assumptions
- `plan_check.py` is the right home for the lint, not `steps.py lint`: verified by the plan_check.py docstring (lines 1-10), which says it lints planned blocks by kind before handoff, and by `steps.py lint` linting step plans, not intent blocks.
- T-0447's agent-task schema has not landed: verified by `find . -name work-items.md` returning nothing outside `.worktrees`. The handoff allows defining the block in the skill.
- `Done when:` and `(gap: ...; default: ...)` must keep their literal shape: verified by `plugins/sdlc-lite/scripts/specgate.py:32,364` and `plugins/sdlc-lite/skills/open-questions/SKILL.md:16`.
- check.sh needs about 900 s under load: verified by earlier verifier records (14m35s and 15m21s, `plan_check selftest: PASS (182 checks)`).
- Every criterion was run once at HEAD. The red ones are red for the right reason: the selftest prints no `ok: clarify:` lines, `clarify` is an invalid argparse choice, the evals folder is absent, the skill lacks `plan_check.py clarify`, handoff-format lacks `level, verify`, and no replay report exists. The scope guard, check.py, check-packaging.py, generate --check and git diff --check exit 0 at HEAD. The scope guard exits 1 on a planted `README.md` path.

## Risks
- The replay is run by the builder, not by an independent fresh model per ask, so the 5 of 6 figure is self-reported. The report must say so. The verifier can re-lint the outputs only if the builder keeps them in the report.
- The `clarify-done-defect` detectors are heuristics (a hex token, `rehearsal`, `live run`). A valid Done when that names a hex-like word or a "rehearsal" fixture would be flagged, and must be moved to `[owner: maintainer]` or reworded.
- The guards for check.py, check-packaging.py, generate --check and git diff --check were not seen red at plan time. They carry their own negative controls inside the scripts.
- The upstream find-intent repo may be unreachable from the builder host. It is prior art only, so the build does not depend on it.
- check.sh may run longer than 2700 s under heavier fanout load.
- Plan-time probe scratch was written to `/tmp/0448probe.sh` and `.worktrees/tmp/0448-planner-L2/plan.md`. No worktree was created and nothing in the repository tree was changed.
