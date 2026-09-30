<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `! grep -qF "verifier alternate profiles that enforce a different model" plugins/sdlc-lite/adapters/codex/instructions.md`: pass. Evidence: exits 0 on the built tree (`c1=0`). At `$SDLC_BASE_SHA` 5ddad89 in a throwaway worktree it exits 1 (`base_c1=1`), so the check can fail. The diff shows line 22 now reads "including a verifier alternate profile when `models.json` configures one." That wording matches the config: `plugins/sdlc-lite/adapters/codex/models.json:11` has `"verifier_alternates": {}`.
- `grep -qF "That alternate profile is generated only when" docs/codex-role-execution.md`: pass. Evidence: exits 0 on the built tree (`c2=0`) and 1 at base (`base_c2=1`). The diff shows the sentence was appended to the end of the "live native builder/verifier sequence" paragraph, and the rest of that paragraph is unchanged.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: the built tree printed "Codex agent definitions verified" with exit 0. For a negative control, I copied the new instructions.md into the base worktree without regenerating. There it printed "generated agent drift: .../sdlc-builder-l1.toml", so the guard does fail on stale generated agents.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: the built tree printed "ok: 18 role levels, 8 agents checked" with exit 0 (`c4=0`). Base gave the same result (`base_c4=0`).

## Out of scope changes
None from this step. I checked each part of the tree:
- **Generated agents:** all 19 `adapters/codex/agents/*.toml` diffs are a single -/+ pair each. A `git diff -U0` count shows 18 lines with the old phrase replaced by 18 lines with the new phrase. The conductor toml's pair is the same line change; my count only reported it differently. This is the regeneration the Do asked for.
- **Other dirty files:** these were already modified before the builder ran. The builder ran 18:07:00–18:07:17 local (attempt.json, 01:07 UTC). By mtime:
  - The plugin.json version bumps date from 17:48.
  - `docs/README.md` and the untracked `docs/validation/release-0.19.0.md` date from 17:49.
  - `.sdlc/notes.md` dates from 18:06.
  - The deleted `.sdlc/0162-*` files and the `.sdlc` bookkeeping are also not from this build.
- **This step's files:** `instructions.md` and `codex-role-execution.md` are the only project files with mtime 18:07:10, which falls inside the build window.

## For the next attempt
None
