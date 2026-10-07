---
id: T-0323
title: "fleet_status render: colored emoji marks and tables, collapse done-but-open rows"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fleet_status.py render` prints colorful emoji state marks and markdown tables, and collapses done-but-open board rows into one line, so the output reads well in a terminal.

## Intent
- Do: In plugins/sdlc-lite/scripts/fleet_status.py `render(data, ping)`: (1) use colored emoji marks for state (🟢 live, 🟡 idle, 🔴 dead, ⚠️ stale, ⚪ nothing moving) in place of the current glyphs; (2) render Needs you, Moving, Stale or stuck, and Release state as markdown tables (columns such as Repo, Row, State, Detail, Source) while the Machine line stays one line; (3) collapse every stale row flagged `ticket-done-board-open` into one line per repo ("N closed tickets still shown on the board") and keep genuinely stale rows listed; (4) shorten the bracketed source so a row stays on one line at 120 columns where it can. Update the skill text and docs/maintenance/sdlc-internals.md paragraph for fleet_status render to match, and update the T-0312 selftest controls that pin the old glyphs and layout; keep the RenderError no-source control and the 60-line cap (a wrapped table counts the same).
- Non-goals: any change to `collect` data, the stop line, or the skill's AskUserQuestion step.
- Done when:
  - `fleet_status.py selftest` passes, with a control that a done-but-open row is collapsed and a control that a row with no source still raises RenderError (observed failing before the fix).
  - `fleet_status.py render --no-write --no-gh` from this repo prints tables, colored marks, and no em dash.
  - `python3 plugins/sdlc-lite/scripts/check.py` and `tickets.py check` pass.

## Context
The user saw the 0.20.12 output wrap and be dominated by 60 closed maison tickets under Stale or stuck, and asked for colorful emojis and tables. Marks live in the MARKS dict near the top of render. The skill prints stdout verbatim, so tables must be plain markdown the terminal shows readably.

## Constraints
No em or en dashes in output. No push or publish. Model and effort defaults unchanged.
