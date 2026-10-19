---
id: T-0079
title: "close --dry-run lists open tickets from the local --root only, so..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0066
---

## Goal
`tickets.py close <slug> --dry-run` also lists proposed, ready, and blocked tickets that exist only in another git worktree's same-relative ticket root, so `/file` can spot a follow-up that duplicates open work in a parallel worktree.

## Context
Follow-up from T-0066 (file-semantic-duplicates/filer-L1.md):

`close --dry-run` lists open tickets from the local `--root` only, so `/file` cannot catch a follow-up that duplicates an open ticket in another worktree or on an unmerged branch (T-0066 plan risk).

## Scope (clarified unattended)
- Source of other roots: the existing `worktree_roots(root)` helper (same source `new`/`close` use for ids). Branches not checked out in any worktree are out of scope (the same accepted limit as ids; `check` catches clashes after merge).
- Worktrees branched from one base share copies of the same tickets. Dedupe by ticket id: a ticket whose id exists in the local root is decided by the local copy only (a ticket done locally but still open in a stale worktree copy is not listed); across other worktrees, list each id once.
- Other-worktree lines keep the `open T-NNNN <title> [<slug>]` shape and add the worktree so the reader knows where it lives, e.g. `open T-NNNN <title> [<slug>] (worktree <basename>)`. Local lines stay byte-identical.
- Done when: selftest cases in a throwaway repo with two worktrees prove (a) an open ticket only in the other worktree is listed with its worktree, (b) a ticket present locally is not listed twice or from the other copy, (c) outside git the output is unchanged; `scripts/check.sh` passes; docs that describe the dry-run open lines (tickets.py docstring/usage, `skills/file/SKILL.md`, `skills/ticket` if it mentions it, CLAUDE.md and `.claude/agents/sdlc-lite-author.md` Layout text) say it covers other worktrees.

## Constraints
- The `expect <digest>` line covers the ordered follow-ups only; its value must not change because of other-worktree open lines.
- Nothing is written in other worktrees; the dry run still writes nothing anywhere.
- Exact-duplicate skipping of follow-ups at close stays local-root only (not in scope).
