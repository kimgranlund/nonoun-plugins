## Task goal
`/sdlc-lite:plan compaction [--write-handoff|--clear] [<prose>]` authors one high signal prompt, in a fixed shape and controlled language, that the person pastes into a manual `/compact <prompt>`, linted by `plan_check.py compaction`; it never runs the compaction.

## Step 2: Record the replay and the live check, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: step 1. Create the report `docs/reports/2026-10-12-compaction-prompt-replay.md` [creates: docs/reports/2026-10-12-compaction-prompt-replay.md] in the shape of `docs/reports/2026-10-12-plan-merge-replay.md` (title, a Date line, a Ticket line naming T-0465, Method, Result), with its fixtures in the sibling folder `docs/reports/2026-10-12-compaction-prompt-replay/` [creates: docs/reports/2026-10-12-compaction-prompt-replay/plan-doc-run.md]. The handoff says "ticket notes"; a dated report is this repository's home for replay evidence (`docs/reports/AGENTS.md`, and T-0467 step 2 did the same), and the ticket record cites it.

1. Fixtures (spec section 9): write three short fixture transcripts in the sibling folder, `plan-doc-run.md`, `lane-wave.md` and `design-thread.md`, each a turn-numbered session of 15 to 30 turns that holds one goal, two or more standing rules, two or more decisions with who and date, and open items, and that ends with a "## Probe questions" list of five next-turn questions with the answer each expects from the transcript.
2. For each fixture, produce two arms. Arm "prompt": author the prompt as `plugins/sdlc-lite/skills/plan/references/compaction.md` says (state facts come from the fixture text here, since the command list cannot run on a fixture; say so in Method), pipe the first return to `plan_check.py compaction` before any fix, then write the summary a summarizer would keep under that prompt. Arm "free": write the summary of a bare `/compact`. Keep both summaries in the report or the sibling folder.
3. Score each arm against the fixture's five probe questions: "Re-asked" counts questions the summary cannot answer, "Rule violated" counts standing rules absent from it, "Decision lost" counts decisions absent from it, and "Words carried" is the `wc -w` of the summary. Record one row per fixture and arm in a table whose header cells are Fixture, Arm, Lines, "First-return lint", "Re-asked", "Rule violated", "Decision lost" and "Words carried"; the free arm writes "n/a" for Lines and the lint.
4. Section "## Run on this repository": follow the new skill once on this repository with a real focus phrase (`SDLC_HEADLESS=1`, no `--write-handoff`), with the command list run for real, and paste the returned fence, its `lines:` line and the last line of the `plan_check.py compaction` output.
5. Section "## Live check": one line that starts "verified" or "unverified" on whether Claude Code loads `CLAUDE.local.md` after `/compact`. A headless builder cannot run `/compact`, so unless a live run is on record the line reads "unverified [U]" with the reason, and `--write-handoff` stays off by default.
6. State that the replay was run by the builder and is "unverified: not an independent run", give the outcome metric of the handoff from the table and nothing the table does not show (the before value stays unmeasured until a live run), and add a follow-up line for an independent live replay in real sessions.

Then run every gate below. Fix any red step 1 introduced; a gate already red at the build-start HEAD is reported as Status `inherited red`. `bash plugins/sdlc-lite/scripts/check.sh` passed in 1205 seconds on record (`.sdlc/.0467-plan-merge-a-skill/planner-L2.md`), hence the 3600 second guard timeout. The whitespace guard reads tracked files only, so also check the new untracked files for trailing whitespace with grep.
### Acceptance criteria
- `R=docs/reports/2026-10-12-compaction-prompt-replay.md; test -f "$R" && grep -qF "T-0465" "$R" && grep -qF "| Fixture | Arm | Lines | First-return lint | Re-asked | Rule violated | Decision lost | Words carried |" "$R" && grep -qF "unverified: not an independent run" "$R"`
- `R=docs/reports/2026-10-12-compaction-prompt-replay.md; for f in plan-doc-run lane-wave design-thread; do test -f "docs/reports/2026-10-12-compaction-prompt-replay/$f.md" || exit 1; grep -qF "## Probe questions" "docs/reports/2026-10-12-compaction-prompt-replay/$f.md" || exit 1; for a in prompt free; do grep -qF "| $f | $a |" "$R" || exit 1; done; done`
- `R=docs/reports/2026-10-12-compaction-prompt-replay.md; grep -qxF "## Run on this repository" "$R" && grep -qF "ok: compaction plan passes" "$R" && grep -qE "^lines: [0-9]+ of 60" "$R" && grep -qF "Run: /compact" "$R"`
- `R=docs/reports/2026-10-12-compaction-prompt-replay.md; grep -qxF "## Live check" "$R" && grep -qE "^(verified|unverified)" "$R"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/plan_check.py selftest`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs scripts .gitignore`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite/skills/plan" ":(exclude)plugins/sdlc-lite/skills/sdlc-lite/SKILL.md" ":(exclude)plugins/sdlc-lite/scripts/plan_check.py" ":(exclude)plugins/sdlc-lite/scripts/check.py" ":(exclude)plugins/sdlc-lite/scripts/check.sh" ":(exclude).gitignore" ":(exclude)docs/reports/2026-10-12-compaction-prompt-replay.md" ":(exclude)docs/reports/2026-10-12-compaction-prompt-replay"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite/skills/plan" ":(exclude)docs/reports/2026-10-12-compaction-prompt-replay.md" ":(exclude)docs/reports/2026-10-12-compaction-prompt-replay")"`
