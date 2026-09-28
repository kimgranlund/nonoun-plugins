<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/check.sh`: runs `steps.py selftest` right after the board selftest, and the header comment now lists it.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: added `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*)` to allowed-tools. Step 3 now runs `steps.py split .sdlc/<task>` and says never to parse the plan by hand. Step 4.2 keeps the superseded rename, then runs `steps.py split` (optionally `--only N`) and notes that the script refuses a step dir holding builder or verifier output.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added one line under "Step handoff" saying `scripts/steps.py split` writes these files and no one writes them by hand.
- `CLAUDE.md`: new Layout bullet for `scripts/steps.py`, and "steps" added to the check.sh selftest list.
- `.claude/agents/sdlc-lite-author.md`: added "steps.py selftest" to the check.sh list on line 19.

## Checks
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. Output includes the steps.py `ok:` lines and "steps selftest: PASS".
- Negative control: prefixed the assertion for check (a) in `steps.py` with `False and`. `check.sh` then exited 1 with "steps selftest: FAIL". Restored the file from a backup, confirmed it matches with `cmp`, and reran `check.sh`: exit 0.
- `grep -n 'steps.py'` on chain/SKILL.md: hits on lines 5 (allowed-tools), 25 (step 3) and 30 (step 4.2).
- The grep for the old "write `step-<n>/handoff.md` per the step template" phrase: no match (exit 1).
- `grep 'steps.py'` on handoff-format/SKILL.md, CLAUDE.md and sdlc-lite-author.md: 1 hit each.
- `grep -rn '## Step'` over agents and skills: hits in planner.md, handoff-format (the section heading and the template) and `decompose/SKILL.md:23 ## Steps`.
- chain/SKILL.md line 30 still says the conductor moves step dirs to `step-<n>.superseded-<k>/`.
- `git diff --stat`: nothing under run.sh, board.py or planner.md.

## Notes
- The `## Step` grep also matches the `## Steps` heading in `decompose/SKILL.md`. That is the skill's own section heading, not an instruction to parse plans or write step handoffs, so I left it alone. It still misses the criterion's literal "only planner.md and the handoff-format template".
- The audit found nothing else to point at the script.
- `git diff` also shows changes to `.sdlc/0040-split-plan-into-steps/handoff.md`. Those were already there; I did not make them.
- The handoff said to add "steps selftest" to the author agent's list, but another criterion needs a `steps.py` hit in that file, so I wrote "steps.py selftest".
