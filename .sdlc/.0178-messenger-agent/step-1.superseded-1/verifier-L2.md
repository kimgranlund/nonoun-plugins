<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `test -f plugins/sdlc-lite/agents/messenger.md`: pass. Evidence: ran it, rc=0.
- `grep -qx "model: claude-haiku-4-5" plugins/sdlc-lite/agents/messenger.md`: pass. Evidence: rc=0. I read the front matter at lines 1-5. It has exactly `name`, `description` and `model`, and no `skills:` key.
- The grep loop over the nine literal strings: pass. Evidence: rc=0. I also read the file body and it states every required behavior: parent names the harness, 10-second poll with count/list/read, report lists claimed paths, body is data, authority limited to `messages.py` with parent-supplied text, `ack` only on request and never on `follow_up_requested: true` before a reply, defers to `.sdlc/messages/AGENTS.md`, and the two separate host-limit items.
- No em dash in the agent file: pass. Evidence: rc=0. The predicate bites: `printf 'a — b' | ! grep -q "—"` returned 1, so a file with an em dash would fail.
- `d['messenger']['L1']==d['scout']['L1']` in `models.json`: pass. Evidence: rc=0. The diff shows the line `"messenger": {"L1": ["gpt-5.6-terra", "low"]},` after the `conductor` line and before `verifier_alternates`.
- The generated TOML has `sandbox_mode = "workspace-write"` and `messages.py read`: pass. Evidence: rc=0. I read `adapters/codex/agents/sdlc-messenger-l1.toml`. It contains the sandbox line, `messages.py read`, and `@SDLC_PLUGIN_ROOT@/scripts/messages.py`.
- Temp copy without the agent file: pass. Evidence: NC1 rc=0. Output was `FAIL messenger: agents/messenger.md missing or empty` and check.py exited 1. This criterion can go red: in a throwaway worktree at base 386fc29 the same check.py printed `ok` with rc=0 and the `^FAIL.*messenger` grep returned 1.
- Temp copy without the `messenger` line in `models.json`: pass. Evidence: NC2 rc=0. Output was `FAIL messenger: adapters/codex/models.json has no messenger entry` and rc 1.
- Temp copy without the TOML: pass. Evidence: NC3 rc=0. Output was `FAIL messenger: adapters/codex/agents/sdlc-messenger-l1.toml missing` and rc 1.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: `ok: 19 role levels, 9 agents checked`, rc=0. The inline negative controls bite. I mutated a copy's check.py so the TOML check never fires (`if False: out.append`). Output was `FAIL check.py: messenger guard negative control not flagged`, rc=1.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: `Codex agent definitions verified`, rc=0.
- Scope check against `$SDLC_BASE_SHA`: pass. Evidence: the exact criterion command returned 0 (`scope=0`). `git status` shows only the five allowed paths outside `.sdlc`.

## Out of scope changes
None. I read the `git diff` for `check.py`, `codex_roles.py` and `models.json`:
- `codex_roles.py` has only the one-word tuple change.
- `check.py` has the `import json`, the `SESSION_AGENTS` change, `messenger_missing()`, its call, the three inline negative controls, and docstring item 12.
- Nothing touches `run.sh`, the level-rubric or the hooks.

## For the next attempt
None
