<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
None. The base commit `f101786` (via `bd9dafa`, the superseded step-1 build) already holds everything this step asks for:
- `plugins/sdlc-lite/agents/messenger.md`
- the `messenger` entry in `adapters/codex/models.json`
- `'messenger'` in the `workspace-write` tuple in `scripts/codex_roles.py`
- the generated `adapters/codex/agents/sdlc-messenger-l1.toml`
- in `scripts/check.py`: `SESSION_AGENTS`, `import json`, `messenger_missing`, the negative controls and docstring item 12

## Checks
- `test -f plugins/sdlc-lite/agents/messenger.md`: rc=0
- `grep -qx "model: claude-haiku-4-5" .../messenger.md`: rc=0
- Required-strings loop (9 literals): rc=0
- No em dash (`$'\xe2\x80\x94'` grep): rc=0
- models.json `messenger.L1 == scout.L1` assertion: rc=0
- TOML `sandbox_mode = "workspace-write"` and contains `messages.py read`: rc=0
- Negative control, agent file removed in temp copy: prints `FAIL messenger: agents/messenger.md missing or empty`, rc 1. Criterion passes (rc=0).
- Negative control, `"messenger"` line removed from models.json in temp copy: prints `FAIL messenger: adapters/codex/models.json has no messenger entry`, rc 1. Criterion passes.
- Negative control, TOML removed in temp copy: prints `FAIL messenger: adapters/codex/agents/sdlc-messenger-l1.toml missing`, rc 1. Criterion passes.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: `ok: 19 role levels, 9 agents checked`, rc=0
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: `Codex agent definitions verified`, rc=0
- Scope check (diff against `$SDLC_BASE_SHA` plus untracked files, excluding `.sdlc`): rc=0. The diff is empty.

## Notes
The only change between the superseded step-1 handoff and this one is the em-dash criterion, which now uses `$'\xe2\x80\x94'` instead of a literal character. The work committed in `bd9dafa` already meets every criterion, so this run edited nothing. The diff against base is empty, and the verifier should check the artifacts as they stand at base `f101786`. The em-dash criterion only works under bash, because zsh `-c` handles `$'...'` differently; I ran every criterion through `bash -c`.
