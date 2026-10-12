---
id: T-0515
title: "Merge ops names the two PR merge invariants; fanout skill and run-operations (T-0501 B6)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`## Merge ops` in `agents/conductor.md`, the fanout skill and `run-operations.md` state the two invariants a project PR merge script must keep, so a stale-base squash cannot revert merged work.

## Intent
- Do: two lines: (a) the branch head contains the base tip before the merge (`git merge-base --is-ancestor origin/main HEAD`, by rebase or merge commit; never a squash of a branch cut before the last merge); (b) the gates ran at that head sha and none is pending (`gh pr checks <n> --watch --fail-fast` is the GitHub form; read-only). State that the plugin ships no PR merge script and `settle --forward` keeps both for the local path. Regenerate both hosts.
- Non-goals: a plugin script that polls `gh`.
- Done when: a `check.py` agreement item (conductor, fanout skill, `run-operations.md` carry both invariants) observed red first; `prompt_lint.py` not raised for `conductor.md`; `generate --check` and `check.py` exit 0.

## Context
Design: `docs/planning/inner-loop-profile.md`. Opt-in by `profile: inner-loop` in `.sdlc/config`; a repo that does not declare it sees no change. Evidence: agent-ui PR 1888 squashed a tree cut before 1886 and 1887 and reverted both; its first CI wait returned early and left PRs open. Add the agent-ui evidence line to T-0498 (done): `ui-board-grid/step-1.superseded-1/builder-L3.md` criterion C6, 45 minutes.

## Constraints
One writer on `conductor.md` (after T-0492, merged).
