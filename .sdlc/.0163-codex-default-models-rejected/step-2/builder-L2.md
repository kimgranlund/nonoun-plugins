<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: line 9 now describes the `verifier_alternates` switch and the `shared_with_builder` fallback. The Claude tables are unchanged.
- `docs/codex-role-execution.md`: the agent count is now 19 while no alternate is configured. The mapping table moves Sol to Astra with efforts unchanged, and Scout stays Luna high. The verifier paragraph is rewritten, and I added the dated ChatGPT-account note (2026-09-29, Codex CLI 0.154.0). The historical evidence paragraphs are unchanged.
- `plugins/sdlc-lite/HARNESS-NOTES.md`: fixed the agent count and alternate-profile wording on the install line, and replaced "between Sol and Astra" with the configured-alternate / shared rule.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l1.toml`, `sdlc-planner-l2.toml`, `sdlc-planner-l3.toml`: regenerated with `codex_roles.py generate`, because the planner agents embed the level-rubric skill body.

## Checks
- All 8 grep acceptance criteria: pass.
- `bash plugins/sdlc-lite/scripts/check.sh`, first run: exit 1. The codex-selftest failures came from stale generated agents after the SKILL.md edit.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`: regenerated the 3 planner TOMLs.
- `bash plugins/sdlc-lite/scripts/check.sh`, rerun: exit 0 (shellcheck is not installed, so the suite skipped it).
- `python3 scripts/check-packaging.py`: exit 0, PASS.
- `git diff --check`: exit 0.

## Notes
- The 3 regenerated planner TOMLs are outside the handoff's file list. They are required: `plugins/sdlc-lite/AGENTS.md` requires regeneration after a preloaded skill body changes, and `check.sh` fails without it.
- The adapter currently ships 19 agent files in `adapters/codex/agents/`, which matches the new count.
