---
id: T-0635
title: "work_root t12: tickets.py migrate-work-root: flat, nested and topics sources into one docs/work shape"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0622, T-0625, T-0626, T-0627, T-0628, T-0629, T-0630, T-0631, T-0632, T-0633, T-0634]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
tickets.py migrate-work-root: flat, nested and topics sources into one docs/work shape.

## Context
Part 15 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t12` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/tickets.py (cmd_migrate_work_root, usage)`, `docs/specs/ticket-stages/design.md`

Actions this ticket hosts:
-  migrate one repo: move tracked records, rewrite citations, set config, regenerate, refuse on dirt or running roles
-  record the layout and config key in the design homes (ticket-stages, repo-onboarding, docs/layout.md)
-  name the work-root singletons as UPPERCASE masters ROADMAP.md and NOTES.md, with ticket folders as the children
-  bring a nested (ticket_root: tickets) or topics repo into the same flat docs/work shape when it migrates

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with cases: `migrate-work-root --to docs/work` on a flat fixture moves .0001-a, 0002-b, a plain task, evals/, proposals/ and fleet.json under docs/work/, roadmap.md to docs/work/ROADMAP.md and notes.md to docs/work/NOTES.md (exact case in os.listdir), leaves config, _templates, runtime/, messages/, AGENTS.md and CLAUDE.md in .sdlc, writes `work_root: docs/work`, and `check` then passes; a topics fixture (tickets/, tickets/roadmap.md, notes/notes.md, work/) lands in the same flat shape with its ticket_root and layout lines dropped; it refuses, writing nothing, on a *.running marker, an uncommitted change, or an existing target (red before: unknown command)

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/T-0635-t0635/plugins/sdlc-lite/skills/ticket/SKILL.md: edited though absent from the ticket's Files list; confirm the doc update is wanted in this ticket. | note: Verifier scratch dir /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0635-verifier-L2 could not be removed (rm was denied); it holds only a throwaway test repo and a script copy. The two throwaway git worktrees were removed.) · verifier: verifier-L2 (sonnet) · base: f70b1dad8486
- Changed: see commits
- Commits: e718a1c T-0635: work_root t12: tickets.py migrate-work-root: flat, nested and topics sources into one docs/work shape
- Check: 1 `tickets.py selftest` exits 0 with the migrate-work-root cases: pass
