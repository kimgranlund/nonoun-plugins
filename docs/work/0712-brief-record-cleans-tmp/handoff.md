---
id: T-0712
title: "Briefs say record removes the throwaway prefix and scratch dir"
type: chore           # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A prepared brief no longer tells the role to remove its throwaway prefix or scratch dir, since `dispatch.py record` removes both; roles stop spending turns on `rm -rf` the host may deny.

## Intent
- Do: in the brief `plugins/sdlc-lite/scripts/dispatch.py` prepare builds (the `Throwaway worktrees only under` and `Scratch files ... only under` lines, about lines 1310 to 1313), replace "remove them, and any scratch output you wrote under that prefix (rm is allowed there and refused elsewhere), when done" and "(rm is allowed there too)" with one clause: `dispatch.py record` removes this prefix and the scratch dir after the run, so do not remove them yourself (a `git worktree remove` of a worktree you made is fine). Keep T-0707's literal-path sentence. Update the selftests that pin the old text.
- Non-goals: cleanup code, hooks, user permission settings.
- Done when: the criteria pass.

## Context
`dispatch.py` `remove_tmp` (about line 1426) and the scratch `shutil.rmtree` (about line 1418) already clean both after record (T-0426). Tonight the T-0706, T-0708 and T-0709 verifiers each spent several calls on `rm -rf <prefix>` / `rm -rf <scratch>` that the user's `Bash(rm -rf /*)` deny rule refused ("Permission to use Bash with command rm -rf ... has been denied."), and the directories were removed by record anyway.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and a case asserts the prepared brief says record removes the prefix and has no "rm is allowed there".
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `plugins/sdlc-lite/scripts/dispatch.py`: the prepared brief now says `dispatch.py record` removes the throwaway prefix and the scratch dir after the run, so the role does not remove them (`git worktree remove` of its own worktree is fine); "rm is allowed there" text dropped, T-0707 literal-path sentence kept. Selftest case rewritten to assert the new clause appears once and the old text is absent.
- `plugins/sdlc-lite/agents/builder.md` (and generated builder-L1..L5, Codex sdlc-builder-l1..l5): "Remove it when done" aligned to the same rule. `hooks/block-role-rm.sh`: header comment only.
- Checks: dispatch selftest exit 0 (via gate_lock), `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check c07d6a20` exit 0.
