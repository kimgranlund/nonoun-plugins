<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/check.sh`: added the `footprint.py selftest` line after the `messages.py` selftest, and `footprint.py` to the header comment's selftest list.
- `docs/maintenance/sdlc-internals.md`: added a `## \`scripts/footprint.py\`` entry after the `order.py` entry. It names `--max-files`.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. shellcheck was skipped because it isn't installed.
- `python3 scripts/check-packaging.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0.
- `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: exit 0.
- Changed-file listing: only `check.sh` and `sdlc-internals.md` show as changed; `footprint.py` is not listed, so it was already committed before this step. All of these are on the allowed list.
- I did not run the three `grep -qF` criteria as commands. I made the matching edits, and the file-set criterion is covered by the changed-file listing above.

Footprint output for the four tickets (verbatim):

```
ticket: .0188-tighten-idle-note
files: 8
bytes: 8010
md_bytes: 4521
steps: 1
planner_bytes: 0
role_runs: 2
role_runs builder L1: 1
role_runs verifier L1: 1
---
ticket: .0164-fix-skill-lints-task-folder
files: 8
bytes: 10050
md_bytes: 6586
steps: 1
planner_bytes: 0
role_runs: 2
role_runs builder L2: 1
role_runs verifier L1: 1
---
ticket: .0181-messages-wait
files: 51
bytes: 214502
md_bytes: 185323
steps: 5
planner_bytes: 105542
role_runs: 15
role_runs builder L2: 1
role_runs builder L3: 4
role_runs plan-reviewer L1: 2
role_runs planner L2: 1
role_runs planner L3: 2
role_runs verifier L1: 1
role_runs verifier L2: 4
---
ticket: .0175-ticket-root-router
files: 69
bytes: 224330
md_bytes: 187209
steps: 8
planner_bytes: 68213
role_runs: 21
role_runs builder L2: 4
role_runs builder L3: 5
role_runs filer L1: 1
role_runs plan-reviewer L1: 1
role_runs planner L3: 1
role_runs verifier L1: 4
role_runs verifier L2: 5
---
```

All four match the design's Baseline table (`docs/lean-sdlc/design.md` "Baseline (measured 2026-10-03)") on steps, role runs, files, bytes and `.md` bytes. The per-role counts also agree with the table's parentheticals.

## Notes
None
