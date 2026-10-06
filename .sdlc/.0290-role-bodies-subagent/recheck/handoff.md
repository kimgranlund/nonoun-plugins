## Goal
Re-verify only the one criterion that failed in the first verifier pass of T-0290 (`../verifier-L3.md`). Check only this criterion; the others passed.

## Acceptance criteria
- `for r in scout researcher architect archaeologist planner plan-reviewer builder verifier filer solo; do grep -q "results.py" plugins/sdlc-lite/agents/$r.md || exit 1; done`
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0
