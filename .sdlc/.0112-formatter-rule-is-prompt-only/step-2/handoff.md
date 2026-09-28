## Task goal
Inside a builder run, a repo-wide formatter, `--fix` linter, or format script (including one reached through a project script such as `npm run format`) is stopped by code before it runs, so builder rule 6 no longer rests on the prompt alone.

## Step 2: Records in sync and gates green
level: L2
### Do
Bring every record in line with the new hook, then run the full gate and fix any red that step 1 introduced (for example shellcheck, `claude plugin validate`, or a check.py phrase guard).

1. `plugins/sdlc-lite/agents/builder.md` rule 6: add one sentence saying that `hooks/block-repo-format.sh` blocks repo-wide formatters, `--fix` linters, and format scripts in builder runs. Keep the existing phrase "files this step changed", because check.py guards it.
2. `plugins/sdlc-lite/scripts/check.sh`: add `block-repo-format.sh` to the header comment's hook-selftest list.
3. Root `CLAUDE.md`:
   - add `block-repo-format.sh` to the `check.sh` line's `hook-selftest.sh` list;
   - add a Layout bullet ``- `hooks/block-repo-format.sh`: PreToolUse(Bash) hook.`` that states the builder-only scope, the blocked forms, that explicit paths pass, and the fail-closed rules;
   - add the hook to the `block-background.sh` bullet's sentence about where the fixtures live, if it names the other hooks.
4. `.claude/agents/sdlc-lite-author.md`:
   - add `block-repo-format.sh` to After-every-change item 1's hook-selftest list;
   - add one Hazards line about repo-wide formatters and the hook.

No em dashes.

### Acceptance criteria
- `grep -qF block-repo-format.sh plugins/sdlc-lite/agents/builder.md`
- `grep -qF 'files this step changed' plugins/sdlc-lite/agents/builder.md`
- `grep -qF block-repo-format.sh plugins/sdlc-lite/scripts/check.sh`
- ``grep -qF '`hooks/block-repo-format.sh`: PreToolUse(Bash)' CLAUDE.md``
- `grep -F 'Check everything' CLAUDE.md | grep -qF block-repo-format.sh`
- `grep -F 'must exit 0' .claude/agents/sdlc-lite-author.md | grep -qF block-repo-format.sh`
- `grep -F 'Hazards' -A 40 .claude/agents/sdlc-lite-author.md | grep -qF block-repo-format.sh`
- `! grep -qF '—' plugins/sdlc-lite/hooks/block-repo-format.sh`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
