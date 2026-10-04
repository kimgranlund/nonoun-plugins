<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/sdlc-lite/SKILL.md: the lane mapping now reads `solo` (solo session agent at the tier for the ticket size, Codex agents `sdlc-solo-l1`/`-l2`/`-l3`), `lean`, `full`
- plugins/sdlc-lite/skills/chain/SKILL.md: `lane` now prints `solo`, `lean`, or `full`
- plugins/sdlc-lite/skills/level-rubric/SKILL.md: line 93 lists `solo` among the session agents
- docs/lean-sdlc/design.md: lines 68 and 283 say `solo` instead of `fix`
- plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l1/l2/l3.toml, sdlc-plan-reviewer-l1.toml, sdlc-plan-reviewer-l1-alternate.toml: regenerated with `codex_roles.py generate` because they embed the level-rubric skill text

## Checks
- All five grep criteria: exit 0
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 2 (drift) right after the skill edit. At base `$SDLC_BASE_SHA` in a throwaway worktree it was exit 0, so my edit caused the drift. After `generate`: exit 0, "Codex agent definitions verified"
- `python3 scripts/check-packaging.py`: exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (the one exit 1 run was before regeneration)
- `git diff --check main -- plugins docs`: exit 0

## Notes
The level-rubric edit changed the generated Codex TOMLs, which embed that skill. I regenerated them with the sanctioned generator rather than editing them by hand. They are outside the handoff's file list, but the `generate --check` criterion needs them. Nothing is committed. The throwaway base worktree was removed.
