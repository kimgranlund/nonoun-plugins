---
id: T-0404
title: "PLACEHOLDER_RE reads i<t ... >= as a placeholder and drops the criterion"
type: bug             # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A command span that holds `i<t` and a later `>=` or `=>` is not read as a `<placeholder>`, so `redck record` keeps its (red) control and `guard_skipped` does not drop the criterion.

## Intent
- Do: in scripts/steps.py `PLACEHOLDER_RE` (line 390) matches `<` through the next `>` inside a command span. Restrict it to what a template placeholder really is (an angle-bracketed word such as `<sha>` or `<step dir>` with no `=`, quote, or operator characters inside, and not inside a quoted `node -e` or `python -c` body), and check every caller of the regex (`guard_skipped`, lint, redck) still skips real placeholders.
- Non-goals: model or effort changes; changing the placeholder syntax the templates ship.
- Done when:
  - Selftest cases, each observed failing first: a criterion span `node -e "for(let i=0;i<t;i++){}; const f=(x)=>x"` is not skipped; `<sha>` and `<step dir>` are still skipped.
  - steps.py selftest, redck.py selftest, check.py and tickets.py check pass.

## Context
Fleet retro 2026-10-09 row 4 (ultimate-tokens, T-0044 steps 4 to 7: "redck: no (red) criteria"). Evidence in ultimate-tokens .sdlc/ui-standardization/step-{4,5,6,7}/builder-*.md.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and its output holds the cases `a node -e body with i<t and => is not skipped` and `<sha> and <step dir> are still skipped`.
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import steps; sys.exit(0 if not steps.guard_skipped('node -e \"for(let i=0;i<t;i++){}; const f=(x)=>x\"') and steps.guard_skipped('git cat-file -e <sha>') and steps.guard_skipped('test -d <step dir>/x') else 1)"`
- `python3 plugins/sdlc-lite/scripts/redck.py selftest`, `python3 plugins/sdlc-lite/scripts/check.py`, and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0.
