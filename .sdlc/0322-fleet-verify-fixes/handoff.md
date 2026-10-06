---
id: T-0322
title: "Fix the three findings from the T-0307 and T-0310 verifier and the flaky fleet_status selftest"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The failed criteria of the T-0319 verifier (A4 for T-0307, B3 for T-0310) are fixed, and the flaky fleet_status selftest is deterministic.

## Intent
- Do: (1) T-0307 A4: do the read-through the ticket asked for against all three 2026-10-06 root-cause reports (maison: /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/root-cause-2026-10-06.md; agent-ui: /Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/root-cause-2026-10-06.md; gen-ui-kit: /Users/kimgranlund/Projects/adia/ui-kit/main/.git-worktrees/rootcause/docs/ops/root-cause-2026-10-06.md, a local worktree), and record in the T-0307 ticket notes (and a short list in plugins/sdlc-lite/skills/fleet-retro/interview.md if it needs a rule) the findings that fit a row only with an unstated rule: agent-ui lines 7, 9, 30, 31 carry a [V] and a [U] inside one finding while the row format has one mark cell; maison line 35 lists positives with no Symptom or Prevention; maison line 3 marks unverified items with a symbol and no [V]. State the translation rule in interview.md in one or two lines. (2) T-0310 B3: fleet_config.py `_line_of` falls back to line 1 for an entry with no `name` and for a non-object entry; report the real line of the malformed entry (scan the raw text for the entry's start) and make the selftest reject `:1:` for those cases (red before, green after). (3) fleet_status.py selftest: the negative control 'a third run with nothing changed lists no close and no state change' flaked once under load; find the time dependence and make it deterministic (injected clock or snapshot compare), red-then-green where possible.
- Non-goals: new features; any model or effort change.
- Done when:
  - The T-0307 notes hold the read-through result (including the gen-ui-kit report) and interview.md states the translation rule; its negative control: a one-row-per-finding example with two marks is accepted by the stated rule.
  - A nameless entry at line 4 and a non-object entry at line 4 report `:4:` (selftest, observed red then green).
  - fleet_status selftest passes 20 times in a loop under `nice` with a parallel CPU burner (observed).
  - `check.py` and `tickets.py check` pass.

## Context
From .sdlc/verify-fleet-0307-0310/verifier-L3.md (T-0319, fail on A4 and B3, low severity; exit 1 and no silent drop hold) and the 0.20.12 merge agent's flake report. Files: plugins/sdlc-lite/skills/fleet-retro/interview.md, scripts/fleet_config.py, scripts/fleet_status.py.

## Constraints
No em dashes. No push, tag or publish.
