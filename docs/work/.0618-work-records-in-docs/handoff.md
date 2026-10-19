---
id: T-0618
title: "Design: move tracked work records from .sdlc to docs/work, runtime stays in .sdlc"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A decompose manifest that fixes how tracked work records (tickets, closed tickets, roadmap, notes, evals, proposals, fleet.json) move from `.sdlc/` to `docs/work/` while `.sdlc/` keeps only machine state (config, runtime/, messages/, generated router), and splits the change into tickets each small enough for solo (L1 or L2).

## Context
User decision 2026-10-19: tickets to docs, runtime stays. Reference counts in `plugins/sdlc-lite/{scripts,agents,skills,hooks}`: 2,333 `.sdlc` mentions in 132 files; 587 literal `'.sdlc'` strings in scripts (dispatch.py 112, tickets.py 102, fanout.py 85, lanes.py 28, steps.py 21), many inside selftest fixtures. By subfolder: config 115, runtime 82, notes 79, tickets 62, messages 44, evals 25, roadmap 17, proposals 13. No central root resolver exists; `ticket_root:` in `.sdlc/config` is relative to `.sdlc/` today. Fleet repo layouts differ: sdlc-lite flat at `.sdlc/` top, ui-kit-maison `ticket_root: tickets` flat, agent-ui `layout: topics`, ultimate-tokens pre-ticket, gen-ui-kit none (`sdlc@adia`). Design homes: `docs/specs/ticket-stages/`, `docs/specs/repo-onboarding/`, `docs/layout.md`.

## Constraints
- Design only: no code edits; the manifest is the output.
- One resolver module is the single home of every root path; old layouts keep working unchanged by default (config opt-in), so repos migrate one at a time.
- Runtime records stay git-ignored and outside `docs/`; the collector, traces and retros keep reading them.
- The ticket split names, per ticket: files, level (L1 or L2), depends, and one red check. Order: resolver first, then readers, then the migrate command, then this repo's migration.
- Cover: closed-ticket dot rename and citation scan across the new root, the generated `.sdlc/AGENTS.md` router, `docs/` checks (`scripts/check.py` docs items, link checks) accepting ticket folders, hooks and agent texts that name `.sdlc/` paths, and Codex parity.

## Outcome

2026-10-19 · lane: full L2 · verdict: closed by reason (design done: architect manifest-v2 split into T-0621 to T-0636) · verifier: none · base: none
- Changed: see commits
- Commits: none
