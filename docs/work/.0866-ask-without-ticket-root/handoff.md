---
id: T-0866
title: "`/sdlc:ask` in a repo with no ticket root notes 'no tickets' and goes on with the rest of the sweep"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
branch: lane/T-0866-t0866
worktree: ../sdlc-lite.worktrees/T-0866-t0866
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc:ask` in a repo with no ticket root notes "no tickets" and goes on with the rest of the sweep.

## Intent
- Do: change the ticket step of the ask skill so a `not a ticket root` refusal is a "no tickets" fact, not an error.
- Non-goals: weakening the `tickets.py` root guard, which is deliberate and pinned by its selftest.
- Done when: the criteria below hold.

## Context
- #95: "`tickets.py --root .sdlc blockers` errored with `.sdlc: holds no config, roadmap.md or ticket folder, so it is not a ticket root`, so `/sdlc:ask` started with an error in a repo that uses live mode without tickets." Expected: "the sweep notes `no tickets` and goes on".
- `plugins/sdlc/skills/ask/SKILL.md:30` runs `tickets.py --root .sdlc blockers` and says "an error naming a missing directory is a finding to report, not `Nothing open.`". The root-guard error is a different case.
- `plugins/sdlc/scripts/tickets.py:641-650` `root_guard` raises that message for every command but `new`; `tickets.py:8816-8820` pins it for `blockers`. Keep it.
- Change the bullet: when the command fails with `not a ticket root` (or `.sdlc` does not exist), record `no tickets` and continue with the other searches; a missing ticket dir under a real root stays a finding.

## Do
1. Edit the ticket bullet in `skills/ask/SKILL.md` as above.
2. Add a CHANGELOG `[Unreleased]` line.

## Acceptance criteria
- `grep -n "not a ticket root" plugins/sdlc/skills/ask/SKILL.md` prints the new rule (it exits 1 at HEAD: the red-first check for a skill-text fix, which has no selftest).
- In a throwaway git repo with an empty `.sdlc/`, `python3 plugins/sdlc/scripts/tickets.py --root .sdlc blockers` still exits 1 with `not a ticket root` (the guard is unchanged).
- `python3 plugins/sdlc/scripts/check.py` exits 0, `python3 plugins/sdlc/scripts/prompt_lint.py` exits 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- `tickets.py` is not edited.

## Outcome

2026-11-19 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: 838b6ed4eeba
- Changed: see commits
- Commits: 280b92a T-0866: /sdlc:ask goes on when the repo has no ticket root (#95)
- Check: 1 grep prints the new rule, exits 1 at HEAD: pass
- Check: 2 guard unchanged in a throwaway repo with empty `.sdlc/`: pass
- Check: 3 check.py, prompt_lint.py, check-packaging.py exit 0 and git diff --check clean: pass
