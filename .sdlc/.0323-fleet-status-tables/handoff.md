---
id: T-0323
title: "fleet_status render: colored emoji marks and tables, collapse done-but-open rows"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fleet_status.py render` prints colorful emoji state marks and markdown tables, and collapses done-but-open board rows into one line, so the output reads well in a terminal.

## Intent
- Do: In plugins/sdlc-lite/scripts/fleet_status.py `render(data, ping)`: (1) use colored emoji marks for state (🟢 live, 🟡 idle, 🔴 dead, ⚠️ stale, ⚪ nothing moving) in place of the current glyphs; (2) render Needs you, Moving, Stale or stuck, and Release state as markdown tables (columns such as Repo, Row, State, Detail, Source) while the Machine line stays one line; (3) collapse every stale row flagged `ticket-done-board-open` into one line per repo ("N closed tickets still shown on the board") and keep genuinely stale rows listed; (4) shorten the bracketed source so a row stays on one line at 120 columns where it can. Update the skill text and docs/references/sdlc-internals.md paragraph for fleet_status render to match, and update the T-0312 selftest controls that pin the old glyphs and layout; keep the RenderError no-source control and the 60-line cap (a wrapped table counts the same).
- Non-goals: any change to `collect` data, the stop line, or the skill's AskUserQuestion step.
- Done when:
  - `fleet_status.py selftest` passes, with a control that a done-but-open row is collapsed and a control that a row with no source still raises RenderError (observed failing before the fix).
  - `fleet_status.py render --no-write --no-gh` from this repo prints tables, colored marks, and no em dash.
  - `python3 plugins/sdlc-lite/scripts/check.py` and `tickets.py check` pass.

## Context
The user saw the 0.20.12 output wrap and be dominated by 60 closed maison tickets under Stale or stuck, and asked for colorful emojis and tables. Marks live in the MARKS dict near the top of render. The skill prints stdout verbatim, so tables must be plain markdown the terminal shows readably.

## Constraints
No em or en dashes in output. No push or publish. Model and effort defaults unchanged.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest`
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_status.py render --no-write --no-gh) && printf '%s\n' "$out" | grep -qxF '| Repo | Row | State | Detail | Source |' && ! printf '%s\n' "$out" | grep -q "$(printf '\xe2\x80\x94')"`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `test -z "$(git diff --name-only HEAD | grep -vxF -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/scripts/fleet_status.py -e plugins/sdlc-lite/skills/fleet-status/SKILL.md -e .sdlc/0323-fleet-status-tables/handoff.md)"`
- `diff <(git show HEAD:plugins/sdlc-lite/scripts/fleet_status.py | sed -n '/^import datetime/,/^# --- render/p') <(sed -n '/^import datetime/,/^# --- render/p' plugins/sdlc-lite/scripts/fleet_status.py)` (collect data code is unchanged)
- The selftest holds a control that done-but-open rows fold into one `N closed tickets still shown on the board` row per repo while a genuinely stale row stays listed, and a control that a row with no source still raises RenderError. Each fails when its behavior is removed: in a scratch copy of `plugins/sdlc-lite/scripts/`, make the `if 'ticket-done-board-open' in r['flags']:` test in `stale_items` read `if False:` (the collapse controls print FAIL), and delete the `if not clean(source): raise RenderError(...)` lines in `trow` (the source controls print FAIL).
- `python3 plugins/sdlc-lite/scripts/fleet_status.py render --no-write --no-gh` prints Needs you, Moving, Stale or stuck and Release state as markdown tables with the marks 🟢 live, 🟡 idle, 🔴 dead, ⚠️ stale, ⚪ nothing moving, keeps Machine as one line, and the `skills/fleet-status/SKILL.md` text and the `docs/references/sdlc-internals.md` fleet_status paragraph describe the same layout and marks; the skill's AskUserQuestion step is unchanged apart from naming the State, Detail and Source columns.

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
