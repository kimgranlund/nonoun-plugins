<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Set `SDLC_ROLE=conductor` in the fanout lane driver env so `hooks/block-publish.sh` guards lane drivers, prove it in the selftest, and fix the docs that say only `run.sh` sets it.

## Step 1: Set SDLC_ROLE in the lane env, selftest it, repair docs
level: L2
### Do
- In `plugins/sdlc-lite/scripts/fanout.py` `run_ticket`, add `SDLC_ROLE='conductor'` to the lane `env` dict, next to `SDLC_HEADLESS='1'`. Do not touch `hooks/block-publish.sh`.
- Update the module docstring's driver env list (~line 36) to name `SDLC_ROLE=conductor` and say it makes `hooks/block-publish.sh` block push, `gh` writes, and publishing in a lane. Update the `--driver` help text too if it lists env.
- In the selftest `STUB` (~line 504), add a line next to the `SDLC_HEADLESS` check that exits 1 with a message unless `${SDLC_ROLE:-}` equals `conductor`.
- Repair stale records:
  - `plugins/sdlc-lite/agents/conductor.md` line 24: `SDLC_ROLE` is set by `scripts/run.sh` and by fanout lane drivers. Your own interactive session is still not guarded.
  - Repo-root `CLAUDE.md`: the `block-publish.sh` bullet (line 23) and the `block-background.sh` bullet (line 24) say `SDLC_ROLE` is set by run.sh or fanout. Add `SDLC_ROLE=conductor` to the fanout bullet's driver env.
  - `.claude/agents/sdlc-lite-author.md`: fix any line that repeats "only run.sh sets it" (line 30 mentions `SDLC_ROLE`).
  - `plugins/sdlc-lite/skills/fanout/SKILL.md`: line 18 says fanout sets `SDLC_HEADLESS=1`. Add that it also sets `SDLC_ROLE=conductor`.
- Leave `skills/file/SKILL.md` alone. No em dashes.
### Acceptance criteria
- `grep -q "SDLC_ROLE='conductor'" plugins/sdlc-lite/scripts/fanout.py` (red now: fanout.py has no `SDLC_ROLE`)
- `grep -q 'SDLC_ROLE' plugins/sdlc-lite/scripts/fanout.py && python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and its stub driver fails if `SDLC_ROLE` is not `conductor`. The selftest STUB text contains a `SDLC_ROLE` check: `grep -c 'SDLC_ROLE:-' plugins/sdlc-lite/scripts/fanout.py` prints at least 1 (red now: 0).
- `! grep -n 'only `scripts/run.sh` sets it' plugins/sdlc-lite/agents/conductor.md` (red now: line 24 matches)
- `grep -q 'fanout' plugins/sdlc-lite/agents/conductor.md` on line 24's `SDLC_ROLE` sentence, and `grep -n 'SDLC_ROLE' CLAUDE.md` shows the block-publish bullet naming fanout as a setter.
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/block-publish.sh plugins/sdlc-lite/skills/file/SKILL.md`
- (guard) `git diff HEAD -- CLAUDE.md plugins/sdlc-lite .claude | grep '^+' | grep -v '^+++' | grep -c '—'` prints 0.
- (guard) `plugins/sdlc-lite/scripts/check.sh` passes with no new findings versus the base commit. The expected validate warning about CLAUDE.md is not a new finding.

## Risks
`SDLC_ROLE` also switches on `block-background.sh`, but `SDLC_HEADLESS=1` already did that, so nothing changes there. A custom `--driver` that pushes on purpose will now be blocked; that is the intent. The selftest criterion depends on the stub failing loudly, so a lane driver failure is how a missing `SDLC_ROLE` shows up.
