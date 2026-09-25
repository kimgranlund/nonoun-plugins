<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- The grep output was reviewed, and each hit is a live-step-only reader, an intentionally inclusive reader, or a fixture. Changes are reported: pass. Evidence: I ran `grep -rn 'step-' plugins/sdlc-lite --include='*.sh' --include='*.py' --include='*.md'`, filtered out `bench/tasks` and `bench/results`, and classified every hit myself:
  - Live-step-only readers:
    - `board.py:55-56` (`live_step_dirs` uses `re.fullmatch(r'step-\d+')`).
    - `board.py:116-118` (`plan_steps` uses `live_step_dirs`).
    - `board.py:150` (`step_row` reads only `task / f'step-{n}'`).
    - `bench-summary.sh:13-16` (the `^step-[0-9]+$` filter).
    - `statusline.sh:46` (the `step-[0-9]*` match only extracts the step number from a running path).
  - Intentionally inclusive readers:
    - `board.py:61-62` (cost).
    - `board.py:196-198` (`has_step_work`).
    - `bench-summary.sh:26` (cost).
  - Fixtures and docs:
    - Selftest strings in `board.py` (418-577) and `tickets.py` (817-899).
    - `agents/filer.md:5`, where filer reading every `step-*` subfolder, superseded ones included, is appropriate.
    - `skills/chain/SKILL.md:25,30` and `skills/handoff-format/SKILL.md:17-29,87`.
  - I also ran a wider sweep: `grep -rnE "step[s]?[-_*/]|glob\(.step|'step|\"step"` over `bench.sh`, `skills`, `agents` and `hooks`. It found no step counter in `bench.sh` and nothing new in `skills/*`.
  - `plugins/sdlc-lite/CLAUDE.md` does not exist. In the repo-root `CLAUDE.md`, lines 23 and 28 do not describe step globbing. `grep -i step .claude/agents/sdlc-lite-author.md` has no hits, so it needs no edit.
  - The builder reported "Changes: None". That matches: every modified file belongs to steps 1 to 3.
- `plugins/sdlc-lite/scripts/check.sh` passes: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh > /tmp/v4check.out 2>&1; echo rc=$?` printed `rc=0`. The output showed ok for 18 role levels and 8 agents, then selftest, tickets selftest, board selftest and run selftest all PASS, then ok for shellcheck and plugin validate.
  - Negative control: I made a throwaway worktree at HEAD, applied the current `plugins` diff, and replaced the `live_step_dirs` fullmatch with `True`. `check.sh` then exited `rc=1` with `ValueError: invalid literal for int() with base 10: '2.superseded-1'`. The check does go red when the live-step filter is removed. I then removed the worktree, and `git status` was unchanged.

## Out of scope changes
None. The modified `board.py`, `bench-summary.sh`, `skills/chain/SKILL.md`, `skills/handoff-format/SKILL.md` and `.sdlc` files come from steps 1 to 3 of this task. Step 4 made no edits.

## For the next attempt
None
