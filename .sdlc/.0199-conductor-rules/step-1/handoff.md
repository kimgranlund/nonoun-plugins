## Task goal
Write the conductor rules: lane first, solo default, thin conductor, and a session footprint. Read `.sdlc/0199-conductor-rules/handoff.md` (Goal, Intent items a to f, Constraints) first: it is the ticket and holds the user's decisions.

## Step 1: Conductor rules, footprint --session, and the check.py guard
level: L3

### Read first
- plugins/sdlc-lite/agents/conductor.md
- plugins/sdlc-lite/skills/chain/SKILL.md
- plugins/sdlc-lite/scripts/footprint.py
- plugins/sdlc-lite/scripts/check.py

### Do
Make the smallest change that meets the criteria. No refactors, no extra tests or doc edits outside this step. Report blocked instead of looping. Do not edit the repository or plugin AGENTS.md. Keep conductor.md short: it is read every turn.
1. conductor.md opens with the philosophy quoted exactly, "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction.", then one objective line: the job is the cheapest path that still passes independent verification, and the lane is chosen before any role runs.
2. "Route every ask" puts the lane decision first, reconciled with what is already on main (T-0215 made `solo` the default): run `steps.py lane` and follow it; size S and M go to `solo`; `lean` only after planning when the lane script says so; the full chain only with a stated reason (an L4 or L5 step, a merge step, cross-cutting scope, a security-sensitive change). Escalating to a heavier lane is what needs justification. Keep the existing solo pointer line, do not duplicate it.
3. Before dispatch the conductor writes one line, `Lane: <lane> because <reason>`, and records the same line in the ticket or task folder (the lane script already appends to skips.md; say so).
4. Rules from the design: record every skip in skips.md; a skip the lane script does not permit needs the user's approval through AskUserQuestion; never skipped: the independent verifier on L4 or L5 and merge steps, the required plan review, a focused live run for a role behavior change, the filer when follow-ups or warnings were reported, user approval for any publish; batch plan reviews across a fanout run on one model family; one /open-questions round per ticket set; parallelize independent tickets in fanout lanes.
5. Stop rules: a second replan verdict, or a ticket past its budget when the budget ticket lands, is a hard stop that comes to the user.
6. Thin conductor: delegate context-heavy reads and long checks to a role or read-only agent and take back conclusions, not file contents or logs; do not narrate every background wake-up; keep the conductor's own context small.
7. `footprint.py`: add an optional `--session <transcript.jsonl>` that reports the conductor session's token usage (input, cache read, output) next to the task's role costs. A transcript with no usage lines reports `none`, not zero. Add a selftest positive case and that negative control.
8. check.py: add the next numbered item with a guard for each of (1) the philosophy line and objective line, (2) the lane-first routing and `Lane: <lane> because <reason>`, (3) the stop rules, (4) the thin-conductor rule, each with a negative control (phrase removed must be flagged), in the style of the existing items. Do not guard phrases that other items already pin.
9. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` (conductor.md is a shared role body) and keep `--check` green.

### Acceptance criteria
- `grep -q "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction." plugins/sdlc-lite/agents/conductor.md`
- `grep -q "Lane:" plugins/sdlc-lite/agents/conductor.md`
- `grep -q "steps.py" plugins/sdlc-lite/agents/conductor.md`
- `python3 plugins/sdlc-lite/scripts/footprint.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `git diff --check main -- plugins docs`
