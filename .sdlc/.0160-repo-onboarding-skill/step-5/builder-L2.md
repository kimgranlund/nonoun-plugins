<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. Every gate was already green, so there was nothing to fix.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: pass, exit 0. All selftests passed, the onboard gates passed their positive and negative controls, and plugin validate is ok. shellcheck is not installed, so the script skipped it.
- `python3 scripts/check-packaging.py`: PASS, exit 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: "Codex agent definitions verified", exit 0.
- `git diff --check bd0ed95dc0a08cbfac9056a87608bfc065626a26 -- . ":(exclude).sdlc"`: no output, exit 0.
- Skill validator: the repo has none installed, and `skills-ref` and `agentskills` are not on PATH. I ran the user-scoped harness linter `~/.claude/plugins/marketplaces/nonoun-plugins/harness/scripts/skill_lint.py` on `plugins/sdlc-lite/skills/onboard/SKILL.md` and `plugins/progressive-context/skills/progressive-context/SKILL.md`. Both got the same result: 2 fails for F2, a house rule that `disable-model-invocation` and `user-invocable` must be declared explicitly, and 1 warn for W2, no "Use when" trigger phrasing. Exit was 0.

## Notes
- Skill validation against a repo or host validator is unverified, because none is installed.
- The harness lint findings come from the user's personal house rules, not a gate in this repo, and both skills hit the same ones. I left the frontmatter unchanged because that would widen the step's scope. The planner can decide whether to adopt those rules.
