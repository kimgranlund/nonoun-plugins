<!-- role=builder level=L1 model=sonnet effort=low -->
No rendering break. No code change needed, matching the handoff's expectation. All acceptance criteria verified.

## Status
done

## Changes
None (no code change needed; board.py already tolerates YAML front matter)

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc` — ran without error, listed `ticket-front-matter` task rows correctly (all current `.sdlc/*/handoff.md` files carry front matter after step 1, confirming board.py renders with front matter present).
- `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc-tmp-check` against a scratch task dir with a front-matter-free `handoff.md` — ran without error, rendered the task row correctly (confirms pre-existing no-front-matter behavior unchanged); scratch dir removed after.
- `plugins/sdlc-lite/scripts/check.sh` — exited 0 (`ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`).

## Notes
Every task under `.sdlc/` now has front matter (added in step 1), so there was no longer a real task dir without it to test against; I used a throwaway scratch dir (`.sdlc-tmp-check`, created and deleted within this run) to prove the no-front-matter path still works, rather than stripping front matter from a real task's handoff.
