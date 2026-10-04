<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/sdlc-lite/SKILL.md: added a new `## Lane per ticket` section between `## Host translations` and `## Native execution`, using the exact paragraph from the handoff.
- plugins/sdlc-lite/skills/chain/SKILL.md: replaced line 27 ("no script computes the lane yet") with the exact `steps.py lane` sentence from the handoff.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: added the `skips.md` layout line between `runs.jsonl` and `step-1/` in the Layout block.

## Checks
I ran every check with `SDLC_BASE_SHA=5b3d1eebbcfc63330dd25765e94550cf529bd9aa`. All passed:
- The five acceptance greps (sdlc-lite steps.py lane, sdlc-lite skips.md, chain line removed, chain steps.py lane, handoff-format skips.md line).
- Guard: no em dash in the five named files.
- Guard: only allowed files differ from base.
- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, which reported no drift, so I did not regenerate.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `git diff --check "$SDLC_BASE_SHA" -- plugins docs`

## Notes
None
