<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF '### Read first' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: the grep exited 0. `git diff` shows the string added in the planner template. It was absent at HEAD, so the check can go red.
- `grep -qE 'nearest .?AGENTS\.md' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: the grep exited 0. The new `## Entry files` section contains "nearest `AGENTS.md`", added in this diff.
- `grep -qF '### Read first' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: the grep exited 0. The diff shows the sentence added to the opening paragraph, and the numbered list is unchanged.
- `grep -qF '### Read first' plugins/sdlc-lite/agents/verifier.md`: pass. Evidence: the grep exited 0. The diff shows the sentence added to the opening paragraph.
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l1.toml`: pass. Evidence: the grep exited 0. `codex_roles.py generate --check` printed "Codex agent definitions generated ... verified".
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml`: pass. Evidence: the grep exited 0.
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-verifier-l1.toml`: pass. Evidence: the grep exited 0.

Other checks I ran against the Do section:
- `python3 plugins/sdlc-lite/scripts/check.py` printed "ok: 18 role levels, 8 agents checked". The diff has no hunk in the fenced merge-step block.
- `git diff --check` was clean.
- The planner template shows `### Read first` between `level:` and `### Do`, with an "only when needed" note.

## Out of scope changes
None from this step. `docs/maintenance/sdlc-internals.md` is modified, but this step's Do names no such file. The builder says the change predates the step and probably came from step 1. I did not diff it against the pre-build state, so I can't confirm where it came from. The other changed files are the three agent files and the regenerated Codex TOMLs, which the Do calls for.

## For the next attempt
None
