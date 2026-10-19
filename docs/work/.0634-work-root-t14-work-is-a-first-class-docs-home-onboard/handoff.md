---
id: T-0634
title: "work_root t14: work/ is a first-class docs home: onboard templates for the docs/AGENTS.md block row and t"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0621]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
work/ is a first-class docs home: onboard templates for the docs/AGENTS.md block row and the docs/layout.md Kinds row; docs_check accepts ticket folders under work/.

## Context
Part 14 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t14` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `plugins/sdlc-lite/scripts/onboard.py (DOC_KINDS, docs layout template, docs AGENTS.md managed block, Which-home order)`, `plugins/sdlc-lite/scripts/docs_check.py (DEFAULT_HOMES, work kind)`, `docs/layout.md (regenerated row)`, `docs/AGENTS.md (regenerated block)`, `docs/specs/repo-onboarding/design.md`

Actions this ticket hosts:
-  accept ticket folders under docs/ in docs checks: no topic rules, no retry-name error, record rules apply
-  record the layout and config key in the design homes (ticket-stages, repo-onboarding, docs/layout.md)
-  make work/ a first-class docs home: its Kinds row and docs/AGENTS.md row (Home, Holds, Never holds, Which-home position) written by the onboard templates

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0 with the case: the generated docs/AGENTS.md block has a `work/` row (Home, Holds, Never holds) first in the Which-home order, and the generated docs/layout.md Kinds table has a `work/` row with form `NNNN-slug/handoff.md`, life `close dot-renames in place`, owner `tickets.py` (red before: no row); `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` exits 0 with the case: docs/work/0001-a/handoff.md, docs/work/.0002-b/builder-L1-2.md, docs/work/ROADMAP.md and docs/work/NOTES.md raise no finding and docs/work/stray.md is flagged (red before: topic rules and B-1a); `docs_check.py --root .` exits 0 on this repository

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: `git grep "eleven default"` over plugins, scripts and docs found no stale count outside the touched docs_check.py strings (updated to "twelve"). | note: `onboard.py check` still reports size/stale/missing lines for docs entries (e.g. docs/AGENTS.md 70 lines over the 60-line target). docs/AGENTS.md and docs/layout.md report `current` and `present`. I did not diff those lines against base. | note: Scratch cleanup was partial. The throwaway base worktree was removed with `git worktree remove`. rm of the scratch fixture dirs (/Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/tmp/0634-verifier-L2 and /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0634-verifier-L2) was denied by the permission system, so a small fixture dir remains in each.) · verifier: verifier-L2 (sonnet) · base: 07f5a2f160a6
- Changed: see commits
- Commits: 0da23c2 T-0634: work_root t14: work/ is a first-class docs home: onboard templates for the docs/AGENTS.md block row and t
- Check: 1 onboard.py selftest exits 0 with the work/ row cases (AGENTS.md block row first in Which-home; la...: pass
- Check: 2 docs_check.py selftest exits 0 with docs/work/0001-a/handoff.md, docs/work/.0002-b/builder-L1-2.m...: pass
- Check: 3 `docs_check.py --root .` exits 0 on this repository: pass
