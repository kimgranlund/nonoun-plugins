<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/chain/SKILL.md: section 4 now opens by running `steps.py next .sdlc/<task>/step-<n>` after each builder and verifier run and maps each action (build, rebuild, bump, verify, replan, done, stop, nonzero exit) to what to do next. The existing rules stay as the spec.
- plugins/sdlc-lite/agents/conductor.md: the escalation line now says the next action comes from `steps.py next <step dir>` after every builder and verifier run.
- CLAUDE.md: three edits.
  - The `scripts/steps.py` layout line now covers `next <step dir>`: read-only, the action keywords, `order.py` ordering, exit 1 with `steps next:` on stderr, and that /chain step 4 runs it.
  - The Roadmap "Escalation is enforced" sentence now names `steps.py next` as computing the step 4 action in code.
  - The Decisions plan-defect bullet now says `steps.py next` routes a `plan defect:` tag or a blocked build to `replan`.
- .claude/agents/sdlc-lite-author.md: `steps.py next` is added to the plan-defect sync list on line 18.

## Checks
- All 5 grep acceptance criteria and the no-em-dash guard, run as one chained command: passed (printed ALLOK).
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Every selftest, shellcheck and plugin validate passed.

## Notes
None
