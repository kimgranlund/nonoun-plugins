## Task goal
The Codex scout runs on a model this account accepts.

## Step 1: Scout L1 on Codex uses gpt-6-astra
level: L1

### Do
1. In `plugins/sdlc-lite/adapters/codex/models.json`, change the scout L1 entry from `["gpt-6-luna", "high"]` to `["gpt-6-astra", "high"]`.
2. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.
3. In `docs/codex-role-execution.md`, wherever the scout's `gpt-6-luna` default is described as pending a user decision, replace that with: on 2026-09-30 the user set scout L1 to `gpt-6-astra` at effort `high`, because `gpt-6-luna` is rejected on a ChatGPT account and `gpt-6-astra` was the only accepted model in the probes. Leave `docs/reports/release-0.19.0.md` unchanged; it is a dated record.

### Acceptance criteria
- `! grep -q "gpt-6-luna" plugins/sdlc-lite/adapters/codex/models.json`
- `grep -q "gpt-6-astra" plugins/sdlc-lite/adapters/codex/agents/sdlc-scout-l1.toml`
- `grep -q "2026-09-30" docs/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
