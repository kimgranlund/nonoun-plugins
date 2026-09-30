## Task goal
It is known whether SDLC Lite's Codex defaults work on a ChatGPT account, and a role launched at a default level either runs or fails with a message that names the cause.

## Step 3: Loose ends
level: L1

### Do
1. In `plugins/sdlc-lite/adapters/codex/instructions.md` line 22, replace "including verifier alternate profiles that enforce a different model from the builder." with "including a verifier alternate profile when `models.json` configures one." Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`, because this text is embedded in every generated agent.
2. In `docs/codex-role-execution.md`, at the end of the paragraph that begins "The live native builder/verifier sequence also passed using `sdlc-builder-l1` and `sdlc-verifier-l1-alternate`.", add one sentence: "That alternate profile is generated only when `verifier_alternates` in `models.json` configures one; the defaults configure none." Leave the rest of that historical record unchanged.

### Acceptance criteria
- `! grep -qF "verifier alternate profiles that enforce a different model" plugins/sdlc-lite/adapters/codex/instructions.md`
- `grep -qF "That alternate profile is generated only when" docs/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
