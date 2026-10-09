---
id: T-0403
title: "steps.py widen rewrites a deny-path guard"
type: bug             # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py widen` rewrites a deny-path scope guard (`git diff --name-only -- <pathspec>` form) as well as the allow-list form, so a one-line scope growth does not force a replan.

## Intent
- Do: read `is_scope_span`, `widen` and `widen_recorded` in scripts/steps.py (the refusal near line 2925) and the T-0365 change that shipped the allow-list form. Reproduce the ultimate-tokens case: a step whose scope criterion is a deny-path guard such as `git diff --name-only <base> -- . ':(exclude)<path>' | { ! grep -q .; }`; `steps.py widen <step dir> <path>` exits 1 today. Teach widen to append an `:(exclude)<path>` pathspec to that form (or the smallest equivalent), keep the refusal for forms it cannot rewrite, and keep the `--reason` fallback.
- Non-goals: model or effort changes; changing the allow-list form.
- Done when:
  - Selftest cases, each observed failing first: widen rewrites a deny-path guard and the new span is green; an unrecognised form is still refused with the existing message.
  - steps.py selftest, check.py and tickets.py check pass.

## Context
Fleet retro 2026-10-09 row 3 (ultimate-tokens, T-0044 step 8): "no criterion line has a command span with git diff --name-only and a grep -v allow-list". Evidence in ultimate-tokens .sdlc/fleet-retro-2026-10-09.md.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- Selftest cases `widen: (d)` cover a deny-path guard rewrite (red before, green after, lookalike still red), the rerun `widen: already applied`, a span with no allow-list and no exclude still refused with the existing "no criterion line" message, and a span with two exclude runs refused.
- The allow-list forms F, E and A are unchanged (their `widen: (a)` and `(b)` cases still pass).
