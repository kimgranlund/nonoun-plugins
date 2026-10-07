## Task goal
The Codex scout is back on `gpt-6-luna` at effort `high`, and the record says why.

## Step 2: Default model mapping table shows Luna for the scout
level: L1

### Do
In `docs/references/codex-role-execution.md`, under "## Default model mapping", change the Scout row from `Astra high` to `Luna high`, so the table matches `plugins/sdlc-lite/adapters/codex/models.json`. Change nothing else. Step 1 changed the mapping and the note; its verifier found this dependent row missed.

### Acceptance criteria
- `grep -qE '^\| Scout \| Luna high' docs/references/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
