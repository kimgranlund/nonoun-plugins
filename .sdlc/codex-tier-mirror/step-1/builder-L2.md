<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/adapters/codex/models.json: switched to the mirrored tier mapping and added the luna→sol verifier alternate.
- plugins/sdlc-lite/adapters/codex/agents/*.toml: regenerated with `codex_roles.py generate`. 18 files changed.
- plugins/sdlc-lite/scripts/codex-selftest.py: the three verifier alternate tests now use `gpt-6-luna` where they used `gpt-6-astra`. Covers lines 256 to 281, including the empty and configured alternate maps and the negative controls.
- docs/codex-role-execution.md: replaced the default-model table and appended the dated sentence to the 2026-09-29 note.

## Checks
- AC1 `c.models()==want` assert: passed.
- AC2 `verifier_alternates()` assert: passed.
- AC3 `grep -qF "Terra 5.6 low"`: passed.
- AC4 `grep -qF "the user mirrored the Claude tiers"`: passed.
- (guard) `codex_roles.py generate --check`: exit 0, printed "Codex agent definitions verified".
- (guard) `codex-selftest.py`: exit 0.
- (guard) `check.py`: exit 0, printed "ok: 18 role levels, 8 agents checked".
- `git diff --check`: clean.

## Notes
- The doc table used to have one row for "Archaeologist, filer, conductor". Conductor now runs on a different model (Astra medium) from the other two (Luna medium), so I split it into "Archaeologist, filer" and "Conductor".
- The paragraph right after the table still says "The current alternate pairs `gpt-6-astra` builders with `gpt-6.1-sol` verifiers". That is still true, but it doesn't mention the new luna→sol alternate. The handoff scoped doc edits to the table and the dated note, so I left that paragraph unchanged.
- The `sdlc-verifier-l1-alternate.toml` and `sdlc-verifier-l2-alternate.toml` files already existed, and regeneration didn't create any new files.
