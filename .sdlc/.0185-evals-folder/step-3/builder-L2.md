<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
plugins/sdlc-lite/scripts/check.py: added docstring item 14 (Evals lock) and the evals lock guard with its negative control, placed just before the final `FAIL` print loop.

## Checks
- AC1 (repo copy that includes .sdlc/evals and docs/reports): exit 0, `ok: 19 role levels, 9 agents checked`.
- AC2 (run.sh builder:L1 model changed to `evals-probe`): exit 1, and the output has `FAIL evals: .sdlc/evals/table-lock.json: model table changed: ...`. Passed.
- AC3 (bare plugin copy): exit 0, and the output has `skip: evals lock guard (no .../T/.sdlc)`. Passed.
- AC4 (empty .sdlc): exit 1, and the output has `FAIL evals: .sdlc/evals: missing`. Passed.
- AC5 `grep -qF '14. Evals lock' plugins/sdlc-lite/scripts/check.py`: exit 0.
- Guard `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0, ok.
- Guard: `git diff --quiet` on run.sh and models.json against `$SDLC_BASE_SHA`: exit 0.
- Guard: the changed-file allowlist check: exit 0.

## Notes
None
