<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/onboard.py`: added the `Model.roadmap` field with default `.sdlc/roadmap.md`. Added `_roadmap_path`, which imports `tickets` locally and re-raises `tickets.Fail` as `SetupError`. `build_model` now sets `roadmap`, and `render_templates` substitutes it into the root block. Added the `layout-variant` gate with its two negative render variants, and updated the docstring.

## Checks
- AC1, topics setup: the block names `.sdlc/tickets/roadmap.md` only and check reports `current AGENTS.md`. rc 0
- AC2, `layout: nested`: setup fails, stderr contains `layout: nested`, and no AGENTS.md is written. rc 0
- AC3, `onboard.py selftest | grep -qx 'gate layout-variant: positive ok, negative ok'`: rc 0
- Guard: blocks written by the base onboard.py, with no config and with a nested config, are still `current` under the new code. rc 0
- Guard: `grep -qx 'TEMPLATE_VERSION = 1'`: rc 0
- Guard: `onboard.py selftest`: all 14 gates pass.
- Guard: files changed are only within the allowed set. rc 0
- Guard: `git diff --check $SDLC_BASE_SHA -- plugins/sdlc-lite/scripts`: rc 0
- Guard: `bash plugins/sdlc-lite/scripts/check.sh`: rc 0
- Guard: `python3 scripts/check-packaging.py`: rc 0
- Guard: `codex_roles.py generate --check`: rc 0
- Guard: `tickets.py --root .sdlc check`: rc 0

## Notes
`SDLC_BASE_SHA` was taken from `step-2/base-sha` (264be0cb). The `tickets.py` changes from step 1 were already in the tree, and I left them as they were.
