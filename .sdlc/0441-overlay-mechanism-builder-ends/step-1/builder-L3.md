<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/overlays/builder.md: new file with exactly two sections. `## L1` has the ordered procedure (Read first and the handoff, then rules 11, 1, 6, 2, 8, 10), the five gap defaults, and the closing line. `## L5` has the goal, the KPI, the budget and the four judgment rules. It uses H3 inside sections and contains no model or effort name.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/scripts/claude_roles.py: changes below.
  - New `overlay(plugin, role)` with every refusal raising `TableError`.
  - New `insert_overlay(body, level, text)`.
  - `definitions()` now refuses an `overlays/*.md` stem that has no `levels.json` role, and inserts the block for any row that has a section.
  - Module docstring updated.
  - Selftest: copies `overlays/`, the verbatim case now expects the overlay when a row has one, `builder-L1` was added to that loop, and 16 new `ok: overlay:` cases were added.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/scripts/codex_roles.py: `instructions(role, level)` imports `claude_roles` lazily and applies the overlay. `raw_definitions()` passes the row's level. `main()` is now a wrapper that catches `claude_roles.TableError` and exits 2 with the message on stderr; the former body is `command()`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/scripts/check.py: new docstring item 52 with code `overlay_placement_bad` and three controls (ghost stem, `agents/overlays/x.md`, and an allowed case). The item 39 temp plugin now copies `overlays/` when it exists.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/agents/builder-L1.md: regenerated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/agents/builder-L5.md: regenerated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml: regenerated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l5.toml: regenerated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/plugins/sdlc-lite/AGENTS.md: the generated-agents bullet (line 18) now names `overlays/<role>.md`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/a/docs/references/sdlc-internals.md: one sentence in the `scripts/claude_roles.py` entry on `overlays/<role>.md` and the `## At this level` block.

## Checks
- `redck.py record <handoff>` before the first edit: exit 0, 7 pre-edit controls recorded red.
- `python3 plugins/sdlc-lite/scripts/claude_roles.py selftest`: exit 0, PASS, 16 `ok: overlay:` lines, 0 FAIL.
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`: exit 0 (22 files verified).
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0.
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0, no FAIL lines ("ok: 19 role levels, 9 agents, 22 generated definitions checked").
- I ran `codex-selftest.py` and `check.py` twice. In the first run, zsh did not set `PIPESTATUS`, so the exit code was not captured. The second run was only to record the exit code.
- Manual check of the Codex refusal path: I added `## L9` to `overlays/builder.md`, ran `codex_roles.py generate --check` and got exit 2 with "section ## L9 has no levels.json row for builder" on stderr. After restoring the file, `--check` returned 0.
- All 12 acceptance criteria were run with `SDLC_BASE_SHA=222f817e…` exported, and each exited 0. That covers the 7 red criteria, the 4 guards (builder-L3 unchanged, both `generate --check` commands, the scope guard) and the generated-files set check (exactly the four builder L1/L5 files).
- `git diff --check -- plugins docs`: exit 0.
- `grep -niwE 'sonnet|opus|fable|haiku|low|medium|high|xhigh|max'` on the overlay: no match.

## Notes
- The check.py item number chosen at build time is 52.
- `claude_roles.py` imports `results` at module level, using the same scripts-dir pattern as its other importers (check.py, dispatch.py, codex_roles.py).
- The `.sdlc/0441-overlay-mechanism-builder-ends/skips.md` modification was already in `git status` before this build and is not mine.
- `plugins/sdlc-lite/AGENTS.md` line 17 (the Codex regenerate bullet) does not name `overlays/<role>.md`. The handoff limited the edit to line 18, so I left it for the planner.
- `skills/level-rubric/SKILL.md` was left untouched, as the handoff instructs.
