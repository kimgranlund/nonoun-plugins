---
id: T-0009
title: "Optional id and status columns in scripts/board.py"
type: idea            # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0001
---

## Goal
`/board` shows each task's ticket id and ticket status, so a reader can tie a board row to its roadmap ticket, without changing the board for task dirs that have no ticket front matter.

## Context
Follow-up from T-0001 (ticket-front-matter/filer-L1.md):

Optional id and status columns in `scripts/board.py`. T-0001 listed this as optional, and the plan left it out of scope.

## Intent
Literal ask: Optional id and status columns in `scripts/board.py` (T-0001 listed it as optional; its plan left it out of scope).
Deltas:
- "Optional" is ambiguous (optional to build, or opt-in at render time): defaulted: the columns appear automatically only when at least one rendered task has ticket front matter; no new flag.
- "Status" clashes with the existing step Status column: defaulted: new columns are `ID` (first) and `Ticket` (after Task), giving `| ID | Task | Ticket | Step | Status | % |`. A task with no front matter shows an empty cell in both.
- Second front matter parser: defaulted: board.py reuses `tickets.py`'s `parse()` (import from the same scripts dir) so tickets.py stays the only parser; board.py must still run when tickets.py raises on a bad file (treat as no front matter).
- Record the change: `skills/handoff-format/SKILL.md` line 45 says board.py does not parse front matter; `skills/board/SKILL.md` describes the table as (Task, Step, Status, %). Both must be updated in the same change.
Do: in `plugins/sdlc-lite/scripts/board.py`, read each task's `id` and `status` via tickets.py's parser, add the `ID` and `Ticket` columns when any rendered task has front matter, keep the table byte-identical otherwise; update the docstring, `skills/board/SKILL.md`, and `skills/handoff-format/SKILL.md`; add a regression check that bites (render with and without front matter).
Non-goals: `--summary` output (statusline) stays unchanged; no filtering or sorting by ticket status; no change to tickets.py behavior; `.board-state.json` keys stay `task/step` so the `· changed` marker keeps working.
Done when: `python3 plugins/sdlc-lite/scripts/board.py` in this repo shows `ID` and `Ticket` columns with e.g. `T-0009` and `proposed`; `board.py --root plugins/sdlc-lite/bench/results` (no front matter) prints the same table as before the change; `--summary` output is unchanged; `plugins/sdlc-lite/scripts/check.sh` passes.

## Constraints
- `--summary` output and the statusline stay unchanged.
- Task dirs without front matter (bench results) render exactly as today.
- tickets.py remains the only front matter parser.

## Baselines
Captured before the change: `baseline-bench-board.txt` (`board.py --root plugins/sdlc-lite/bench/results`) and `baseline-summary.txt` (`board.py --summary` in this repo; may drift as task dirs change mtime). Compare after the change.
