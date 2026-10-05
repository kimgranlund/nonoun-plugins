## Task goal
Independent verification of T-0223, the `/sdlc-lite:agent {agent-name} {instructions}` command, on branch agent-cmd against its base (the merge-base with main). You did not build it.

## Step 1: Verify the /agent command
level: L3

### Do
Read-only. Read `.sdlc/.0223-agent-command/handoff.md` (the ticket), `plugins/sdlc-lite/skills/agent/SKILL.md`, the check.py item 25 guard (`agent_cmd_bad` and its controls) and `docs/reports/agent-command-live-run.md` with its evidence under `docs/reports/agent-command-live-run/`. Run every criterion below. Check that the skill's start paths agree with `agents/solo.md` (`## Start`, tiers table) and with the role skills (`skills/scout`, `research`, `architect`, `dig`), that it never tells a conductor to use the Agent tool for an sdlc-lite agent, that the live run record's numbers match the committed evidence (models in `session-models.txt`, costs in the arm files, the 13 of 13 hidden check), and that its limits are honest. Try to break the guard: inject a defect (remove a stem from the skill, add a table row for a name with no agent file, drop a Codex entry) in a throwaway copy and confirm `check.py` reports it.

### Acceptance criteria
- `test -f plugins/sdlc-lite/skills/agent/SKILL.md`
- `grep -q "block-role-spawn.sh" plugins/sdlc-lite/skills/agent/SKILL.md`
- `for n in solo scout researcher architect archaeologist planner builder verifier plan-reviewer filer messenger conductor; do grep -q "\`$n\`" plugins/sdlc-lite/skills/agent/SKILL.md || exit 1; done`
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `grep -q "13/13 passed" docs/reports/agent-command-live-run/arms/solo-hidden-check.txt`
- `test -f docs/reports/agent-command-live-run/session-models.txt && grep -q "sdlc-lite:solo" docs/reports/agent-command-live-run/session-models.txt`
- `bash plugins/sdlc-lite/scripts/check.sh`
