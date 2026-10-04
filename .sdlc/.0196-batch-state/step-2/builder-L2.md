<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/board.py: added `import steps`. `step_row` now renders `🟢 pass · builder <L> · batch verifier <L>` when `steps.batch_verified` returns a path, checked right before the awaiting-verify return. Added a docstring sentence. Added two selftest cases (listed build passes; rebuilt after the batch shows awaiting verify), each printing `ok: batch:`.
- docs/maintenance/sdlc-internals.md: added a clause to the `scripts/board.py` entry naming the batched render.

## Checks
- AC1, the batch-verified board row: exit 0
- AC2 (guard), the rebuilt step renders awaiting verify: exit 0
- AC3, the selftest prints `ok: batch:`: exit 0
- AC4 (guard), the scope allow-list: exit 0
- AC5 (guard), `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (it logged "skip: shellcheck not installed")
- AC6 (guard), `python3 scripts/check-packaging.py`: exit 0
- AC7 (guard), `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0
- AC8 (guard), `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0
- AC9 (guard), `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0

## Notes
`SDLC_BASE_SHA` was set from step-2/base-sha (870ddd74e5ec06cddeaca0d99e0a14cfa4ab4ec7).
