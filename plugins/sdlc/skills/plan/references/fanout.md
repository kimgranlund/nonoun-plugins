# Fanout rules

Labels: observed here (repo files or records) or from the code (`scripts/fanout.py`).

| Rule | Detail | Label |
|---|---|---|
| Spec | `<lane>=<id>[,<id>...]` or `<lane>@<branch>=<id>[,<id>...]` | from the code: the `fanout.py` usage text |
| Lane count | Default max 4; above that raise `--max-lanes`; above 16 needs `--yes-many` | from the code |
| Stagger | Default 20 seconds between lane starts | from the code |
| Overlap | Tickets citing the same file stop the run unless `--allow-overlap`; check before launch | from the code; observed in the 0.20.5 to 0.20.7 merges |
| Hot spots | `check.py` guard numbers, `check.sh`, root `AGENTS.md`, `README.md` collide most; merge one lane at a time with main merged in first | observed: the 0.20.x lane merges |
| Lane mode | `--lane auto` follows `steps.py lane`; solo for ticket levels L1 and L2 | from the code; `docs/reports/solo-vs-lean-benchmark-2026-10-04.md` |
| Gate | `--gate CMD` runs after each lane merge in the integration worktree and resets the merge when it fails | from the code: `fanout.py` gate loop |
| Budget | `budget.py` levels L1 $5, L2 $30, L3 $60; `solo_run.py` and `run.sh` exit 4 at 80 percent unless acked; `budget.py` itself exits 3 on a warning | from the code |
| Dry run | `--dry-run` first; the real command is the dry run without that flag | from the code |

Example: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py run a=T-0001 b=T-0002 --lane auto --max-lanes 2 --dry-run`

## Gather

Run `tickets.py --root .sdlc check`, list the ready tickets, and run `steps.py lane <task dir>` for each (it records the lane in that task's `skips.md`; that is its only write). Read each ticket's handoff for the paths it will touch. Ask only for what is missing (which tickets, the spend cap).

## Group the lanes

One lane per ticket by default. Two tickets share a lane only when they touch the same files, so they run in order. Tickets that touch a hot-spot file (`check.py`, `check.sh`, `AGENTS.md`, `README.md`) go to separate merge turns or one lane. Keep lanes at or below 4; above 4 raise `--max-lanes`, and above 16 add `--yes-many` only with the person's say-so. Solo tickets use `--lane auto` so the lane script decides. Set `--gate` to the check that must pass after each lane merge, and `--stagger` at the default 20 seconds unless the person knows better.

## Check and return

Build the command, pipe it to the fanout lint, then run it as `fanout.py run --dry-run <specs and flags>` (the flag right after `run`) and fix whatever it prints; its output is the `lanes:` line of the dry run. The returned block holds two lines: the dry-run command first, then the same command without `--dry-run`; `plan_check.py` rejects any other shape. `Why this plan` covers the lane grouping, the cap and the gate; `You must authorize` names the spend and says that fanout merges nothing to a remote and publishes nothing.
