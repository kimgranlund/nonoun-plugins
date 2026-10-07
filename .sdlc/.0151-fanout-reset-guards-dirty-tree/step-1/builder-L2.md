<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: `run_ticket` now checks the integration worktree with `git status --porcelain --untracked-files=no` inside the merge lock and before `before = ...`. If the tree is dirty, it returns `integration dirty: <first path>` with `lane_sha[:7]`. No merge, reset, or gate runs. If the status command itself fails, it returns `integration status failed: ...`. Also updated the step-5 docstring and added selftest case 5d.
- `docs/references/sdlc-internals.md`: the fanout paragraph now says a dirty integration tree is refused with `integration dirty`.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: added one sentence on the `integration dirty` refusal.

## Checks
- Negative control: I wrote case 5d before the guard existed. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` then printed FAIL with two misses. The outcome was `red: test -z ... rc=1` and the integration `git diff` was empty, meaning the edit had been wiped by `reset --hard`.
- After the guard: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` printed `fanout selftest: PASS`, exit 0.
- `grep -qF 'integration dirty'` passes on fanout.py, sdlc-internals.md and SKILL.md.
- Scope guard (`git diff --name-only "$SDLC_BASE_SHA"` filtered to the three allowed files): passed.
- `git diff --check`: clean.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0 at HEAD with the changes. It also exits 0 in a detached worktree of HEAD under `$SDLC_TMP_WORKTREES/base`, and the two outputs are identical (`ok: 18 role levels, 8 agents checked`). I removed the worktree afterwards.

## Notes
- The path is taken from raw `git status` stdout, not `git_out`, because `git_out` calls `.strip()`, which would remove the leading status space and cut the path (`[3:]`).
- The new `integration status failed: ...` outcome goes beyond the handoff. I added it so a failing status command stops the ticket instead of raising through `git_out`.
