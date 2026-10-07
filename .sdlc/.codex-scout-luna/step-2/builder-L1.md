<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `docs/references/codex-role-execution.md`: Scout row in "Default model mapping" changed from `Astra high` to `Luna high` (line 37).

## Checks
- `grep -qE '^\| Scout \| Luna high' docs/references/codex-role-execution.md`: passed.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: passed, exit 0 ("Codex agent definitions verified").

## Notes
None
