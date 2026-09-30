<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/conductor.md: added a route under `## Route every ask` that sends reviews of sdlc run traces to `/sdlc-lite:review-traces`.
- plugins/sdlc-lite/skills/sdlc-lite/SKILL.md: added the table row `| Review sdlc run traces for sdlc-lite waste and bugs | review-traces |`.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: added `.sdlc/runtime/` in three places: the Layout block, the ignore snippet, and the ignore explanation list.
- docs/maintenance/sdlc-internals.md: added a new `## \`scripts/traces.py\`` entry and named `/review-traces` in the Launcher skills paragraph.
- plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml: regenerated with `codex_roles.py generate`.

## Checks
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`: "generated", then `generate --check`: "verified" (exit 0).
- All five acceptance greps: exit 0.
- Scope guard with `SDLC_BASE_SHA` read from the step's `base-sha`: exit 0.
- `git diff --check`: exit 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0.

## Notes
- The new internals entry covers all six items the handoff asked for:
  - the four subcommands
  - the out dir and cursor
  - the detector families and a thresholds table
  - the two model-free stages
  - the selftest and its corpus case
  - `--rerun-criteria` and its worktree rule
- The table and the other details come from reading `traces/detectors/thresholds.py`, `store.py`, `rerun.py`, `selftest.py` and the `traces.py` docstring.
- `.gitignore`, `check.sh` and the traces files were already changed by earlier steps. This step did not touch them.
