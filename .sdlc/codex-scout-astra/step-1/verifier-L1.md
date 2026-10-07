<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `! grep -q "gpt-6-luna" plugins/sdlc-lite/adapters/codex/models.json`: pass. Evidence: on the built tree c1=0. At the base worktree (`$SDLC_BASE_SHA` f0bf06a) c1=1, so the check can fail. The file exists, so this is not a vacuous `!`. The diff at models.json:7 shows `"scout": {"L1": ["gpt-6-astra", "high"]}`.
- `grep -q "gpt-6-astra" plugins/sdlc-lite/adapters/codex/agents/sdlc-scout-l1.toml`: pass. Evidence: built c2=0 and base c2=1. The diff shows `model = "gpt-6-astra"` and effort `high` is unchanged.
- `grep -q "2026-09-30" docs/references/codex-role-execution.md`: pass. Evidence: built c3=0 and base c3=1. At docs/codex-role-execution.md:43, "Luna for scout is kept pending a user decision." is replaced with the exact decision text from the Do. `git diff --stat -- docs/reports` is empty, so release-0.19.0.md is unchanged.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: built rc=0 with "Codex agent definitions verified". It can go red: in the base worktree I changed only models.json, and the check printed `generated agent drift: .../sdlc-scout-l1.toml` with rc=2.
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: pass. Evidence: built tree selftest_rc=0. It also passes at base.

## Out of scope changes
None. `git status` shows only the three files the Do names, plus the untracked task folder `.sdlc/codex-scout-astra/`. Contract dependents: `git grep -n gpt-6-luna` outside `.sdlc/` and `docs/reports` now finds only the new doc sentence. No script or test pins the scout model, and both guards are green.

## For the next attempt
None.
