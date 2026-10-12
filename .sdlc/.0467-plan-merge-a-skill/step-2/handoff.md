## Task goal
`/sdlc-lite:plan <kind> [args]` is one skill with kinds `steps` (default, today's `plan`), `doc`, `goal`, `campaign` and `fanout`, with the shared rules in one reference and a dry-run printed before every block.

## Step 2: Replay goal and fanout on old and new skills, record it, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: step 1. Create the report `docs/reports/2026-10-12-plan-merge-replay.md` [creates: docs/reports/2026-10-12-plan-merge-replay.md], following the shape of `docs/reports/2026-10-12-clarify-v3-replay.md` (title, a Date and a Ticket line naming T-0467, a Method section, a Result section). The handoff says "ticket notes"; a dated report is this repository's home for replay evidence (`docs/reports/AGENTS.md`; T-0461 step 2 did the same), and the ticket record cites it.

Replay, for the goal ask and the fanout ask of `plugins/sdlc-lite/skills/plan/evals/` (the other three kinds are optional and, when skipped, listed as not run):
1. Pick two tickets whose roadmap status is ready (`.sdlc/roadmap.md`, after `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`) and that share no files, and fill the ask placeholders with them. The design's ticket ids are closed or dropped. When fewer than two tickets are ready, or `fanout.py run --dry-run` refuses the pair, use two proposed tickets and record the refusal verbatim as the "lanes:" line of the dry-run block.
2. Run the replay in the lane. No throwaway worktree is needed, because ticket A leaves the old skills untouched, so the lane holds both the old and the new skill, `plan_check.py` reads the block from stdin, and fanout runs only as `fanout.py run --dry-run`. Write no plan artifact into the tree; keep the returned blocks in the report.
3. For each ask, follow the old skill (`plugins/sdlc-lite/skills/plan-goal/SKILL.md`, `plugins/sdlc-lite/skills/plan-fanout/SKILL.md`) as written with the environment variable SDLC_HEADLESS set to 1, then the new skill (`plugins/sdlc-lite/skills/plan/SKILL.md`, kind goal, kind fanout). Pipe each returned block to its lint (`plan_check.py goal`, `plan_check.py fanout`) on first return, before any fix.
4. Record one row per run in a table whose header cells are Ask, Skill, Questions, "plan_check.py refusals", and "First-return lint", with the Ask cell "goal" or "fanout" and the Skill cell "old" or "new": the questions the skill asked or would have asked (warn lines when unattended), the count of FAIL lines on first return, and the lint's last line verbatim. Add the dry-run block the new skill printed for each kind.
5. State in the report that this replay was run by the builder and is "unverified: not an independent run", and add a follow-up line for an independent replay (the T-0495 pattern). Give the outcome metric of the handoff (questions and refusals per plan artifact, old against new) from the table and nothing the table does not show.

Then run every gate below. Fix any red step 1 introduced; a gate already red at the build-start HEAD is reported as Status `inherited red`. `bash plugins/sdlc-lite/scripts/check.sh` passed at plan time in 1205 seconds on this tree, hence the 3600 second guard timeout. The whitespace guard reads tracked files only, so also check the new untracked files for trailing whitespace by eye or with grep.
### Acceptance criteria
- `R=docs/reports/2026-10-12-plan-merge-replay.md; test -f "$R" && grep -qF "T-0467" "$R" && grep -qF "| Ask | Skill | Questions | plan_check.py refusals | First-return lint |" "$R" && grep -qF "unverified: not an independent run" "$R" && grep -qF "Dry run (goal)" "$R" && grep -qF "Dry run (fanout)" "$R"`
- `R=docs/reports/2026-10-12-plan-merge-replay.md; for row in "goal | old" "goal | new" "fanout | old" "fanout | new"; do grep -qF "| $row |" "$R" || exit 1; done`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/plan_check.py selftest`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs scripts`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite/skills/plan" ":(exclude)plugins/sdlc-lite/skills/sdlc-lite/SKILL.md" ":(exclude)plugins/sdlc-lite/scripts/check.py" ":(exclude)docs/reports/2026-10-12-plan-merge-replay.md"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite/skills/plan" ":(exclude)docs/reports/2026-10-12-plan-merge-replay.md")"`
