## Task goal
`/sdlc-lite:plan compaction [--write-handoff|--clear] [<prose>]` authors one high signal prompt, in a fixed shape and controlled language, that the person pastes into a manual `/compact <prompt>`, linted by `plan_check.py compaction`; it never runs the compaction.

## Step 3: Loose ends
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: steps 1 and 2 (built and verified in this tree, uncommitted). Change only `docs/reports/2026-10-12-compaction-prompt-replay.md` and add files only under `docs/reports/2026-10-12-compaction-prompt-replay/`. Do not edit any skill, script, `AGENTS.md` or `CLAUDE.md`. Commit nothing.

1. Run the skill itself once, live, on this repository. The recorded "Run on this repository" was a builder following the reference by hand; the ticket's Done when asks for the skill invocation. From the tree root run a headless Claude Code session that loads this lane's plugin, in the form `scripts/bench.sh` uses: `SDLC_HEADLESS=1 claude -p --plugin-dir plugins/sdlc-lite --model sonnet --dangerously-skip-permissions '/sdlc-lite:plan compaction "finish the loose ends of T-0465"'`, with no `--write-handoff`. Unset `SDLC_ROLE` for that child process if the hooks refuse it, and say so. Save the child's full stdout as `docs/reports/2026-10-12-compaction-prompt-replay/live-skill-run.out.txt` [creates: docs/reports/2026-10-12-compaction-prompt-replay/live-skill-run.out.txt] and the returned fence body, byte for byte and with no fix of yours, as `docs/reports/2026-10-12-compaction-prompt-replay/live-skill-run.prompt.txt` [creates: docs/reports/2026-10-12-compaction-prompt-replay/live-skill-run.prompt.txt]. Run `python3 plugins/sdlc-lite/scripts/plan_check.py compaction --file` on the saved prompt. Append a section `## Live skill run` to the report, placed before `## Live check`, that gives the exact command, the model, the `lines:` line the skill returned, whether the output held one fence and the `Run: /compact` line, and the last line of the lint output. If the lint is red on the skill's own return, do not edit the prompt: report Status blocked with the FAIL lines. If the child session cannot start (no credentials, hook refusal that unsetting `SDLC_ROLE` does not lift), report Status blocked with the stderr.
### Acceptance criteria
- `R=docs/reports/2026-10-12-compaction-prompt-replay.md; D=docs/reports/2026-10-12-compaction-prompt-replay; grep -qxF "## Live skill run" "$R" && test -s "$D/live-skill-run.out.txt" && grep -qF "Run: /compact" "$D/live-skill-run.out.txt" && grep -qE "lines: [0-9]+ of 60" "$D/live-skill-run.out.txt" && python3 plugins/sdlc-lite/scripts/plan_check.py compaction --file "$D/live-skill-run.prompt.txt" | grep -qxF "ok: compaction plan passes"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs scripts .gitignore`
- (guard) `test -z "$(git status --porcelain -- CLAUDE.local.md AGENTS.md CLAUDE.md)"`
