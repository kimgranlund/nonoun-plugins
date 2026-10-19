---
id: T-0621
title: "work_root t01: roots.py resolver; tickets.py ticket_dir/layout_paths/layout_lines delegate to it"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
roots.py resolver; tickets.py ticket_dir/layout_paths/layout_lines delegate to it.

## Context
Part 1 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t01` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/roots.py (new)`, `plugins/sdlc-lite/scripts/tickets.py (parse functions only)`, `plugins/sdlc-lite/scripts/check.sh`, `docs/references/sdlc-internals.md`, `docs/specs/ticket-stages/design.md`

Actions this ticket hosts:
-  declare a repo's work root by an opt-in config line; no line keeps today's paths
-  answer every root path (state, config, runtime, messages, router, templates, work, tickets, roadmap, notes, tasks, archive, evals, proposals, fleet registry) from one module
-  refuse an unsafe work root (inside .sdlc, outside the repo, absolute) before writing anything
-  resolve another worktree's or git branch's work root from its own config so ticket ids stay unique
-  keep flat, ticket_root: tickets, layout: topics and no-ticket repos working unchanged, composing with the work root
-  record the layout and config key in the design homes (ticket-stages, repo-onboarding, docs/layout.md)
-  name the work-root singletons as UPPERCASE masters ROADMAP.md and NOTES.md, with ticket folders as the children
-  bring a nested (ticket_root: tickets) or topics repo into the same flat docs/work shape when it migrates

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/roots.py selftest` exits 0 (red before: no such file) with cases: `work_root: docs/work` resolves tickets to <top>/docs/work, roadmap to <top>/docs/work/ROADMAP.md, notes to <top>/docs/work/NOTES.md and runtime to <top>/.sdlc/runtime; no work_root line resolves every path exactly as tickets.layout_paths did; `work_root: .sdlc/x`, `../x`, an absolute path, and work_root beside `ticket_root: tickets` or `layout: topics` each raise Fail; and `python3 plugins/sdlc-lite/scripts/tickets.py selftest` still exits 0
