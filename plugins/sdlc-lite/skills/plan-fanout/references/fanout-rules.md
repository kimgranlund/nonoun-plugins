# Fanout rules

Labels: observed here (repo files or records) or from the code (`scripts/fanout.py`).

| Rule | Detail | Label |
|---|---|---|
| Spec | `<lane>=<id>[,<id>...]` or `<lane>@<branch>=<id>[,<id>...]` | from the code: `fanout.py --help` |
| Lane count | Default max 4; above that raise `--max-lanes`; above 16 needs `--yes-many` | from the code |
| Stagger | Default 20 seconds between lane starts | from the code |
| Overlap | Tickets citing the same file stop the run unless `--allow-overlap`; check before launch | from the code; observed in the 0.20.5 to 0.20.7 merges |
| Hot spots | `check.py` guard numbers, `check.sh`, root `AGENTS.md`, `README.md` collide most; merge one lane at a time with main merged in first | observed: the 0.20.x lane merges |
| Lane mode | `--lane auto` follows `steps.py lane`; solo for size S and M | from the code; `docs/reports/solo-vs-lean-benchmark-2026-10-04.md` |
| Gate | `--gate CMD` runs after each lane merge in the integration worktree and resets the merge when it fails | from the code: `fanout.py` gate loop |
| Budget | `budget.py` tiers S $5, M $30, L $60; `solo_run.py` and `run.sh` exit 4 at 80 percent unless acked; `budget.py` itself exits 3 on a warning | from the code |
| Dry run | `--dry-run` first; the real command is the dry run without that flag | from the code |

Example: `python3 plugins/sdlc-lite/scripts/fanout.py run a=T-0001 b=T-0002 --lane auto --max-lanes 2 --dry-run`
