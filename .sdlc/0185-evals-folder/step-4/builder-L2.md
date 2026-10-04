<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/maintenance/sdlc-internals.md: added a ``## `scripts/evals.py` `` entry after the `scripts/results.py` entry. It covers the purpose, the CLI, the exit codes, the Python API (including `validate_eval`), the three keys of `table-lock.json`, check.py item 14 and when it skips, the selftest's three negative controls, and a link to `../../.sdlc/evals/AGENTS.md`.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: added the `.sdlc/evals/` line to the layout block, right after the `.sdlc/messages/` line.
- plugins/sdlc-lite/AGENTS.md: added the eval-plus-lock requirement to the Contracts bullet about the model tables, and added the evals check to the Verification list.
- docs/codex-role-execution.md: added the sentence about a new eval plus `evals.py lock` after "Regenerate the agent files after changes."

## Checks
- The five grep criteria (sdlc-internals heading and table-lock.json, handoff-format, plugin AGENTS.md, codex-role-execution): all matched.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: "Codex agent definitions verified", exit 0.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: "ok: 19 role levels, 9 agents checked".
- `git diff --quiet "$SDLC_BASE_SHA" -- run.sh models.json`: exit 0.
- Scope guard (changed files outside `.sdlc` limited to the allowed list): exit 0.
- `git diff --check`: exit 0.
- Em dash count in the three edited docs: 0.

## Notes
- I ran check.py piped through `tail`, so the exit code I recorded belongs to `tail`. The output was the ok line, not a FAIL line.
- The edited text only links to `.sdlc/evals/AGENTS.md`, which already exists. The record format and canonical text are not copied into these docs.
