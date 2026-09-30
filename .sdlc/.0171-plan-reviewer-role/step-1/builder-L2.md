<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/planner.md`: made three edits to the planner file.
  - Added a `## Assumptions` section to the final-message format, placed between the step blocks and `## Risks`.
  - Expanded the `### Do` line to require targets, settled interface decisions with evidence, `Depends on:`, and focused checks, plus the rule that no design decision is left to the builder.
  - Added the `plan review:` handling to rule 9.

## Checks
- `grep -qx '## Assumptions' plugins/sdlc-lite/agents/planner.md`: exit 0
- `grep -qF 'unresolved:' plugins/sdlc-lite/agents/planner.md`: exit 0
- `grep -qF 'plan review:' plugins/sdlc-lite/agents/planner.md`: exit 0
- `grep -qF 'Depends on:' plugins/sdlc-lite/agents/planner.md`: exit 0
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0 ("ok: 18 role levels, 8 agents checked")
- (guard) scope check (only planner.md changed outside `.sdlc`): exit 0
- `git diff --check`: exit 0

## Notes
- `codex_roles.py generate` was not run. Generated Codex agents may now be out of step with the new planner body. The step limits its scope to planner.md, so a later step or the gates step has to regenerate them.
- One check-output line went to `/tmp/null` because of a redirect typo in my probe command. That check only reads files, and it did not affect the result.
