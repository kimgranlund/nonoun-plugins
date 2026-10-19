---
id: T-0617
title: "steps.py lint accepts criteria that use git commands the verifier may not run"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` refuses an acceptance criterion whose command runs a git command the verifier may not run (`git stash`, `git checkout`, `git reset`, `git restore`, `git commit`), proven by a selftest case that failed before the fix.

## Repro
1. Write a step handoff whose criterion is `` `s=$(git stash create); test -n "$s"` ``.
2. `python3 plugins/sdlc-lite/scripts/steps.py lint <handoff>` prints `steps lint: ok`.

## Expected
Lint refuses it as a plan defect, naming the command and `agents/verifier.md` rule 3, the way it refuses a `||` fallback today (`steps.py:2036`).

## Actual
On ui-kit-maison T-0599 the planner wrote `s=$(git stash create)` into two criteria; lint passed them, and plan review 2 (`/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0599-tags-input-validate-default-bounds/plan-reviewer-L1-2.md:6`) caught it, costing a second planner run and review ($16.28 in `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0599-tags-input-validate-default-bounds/runs.jsonl`) and a user override.

## Context
Fleet retro 2026-10-18 (`docs/reports/2026-10-18-fleet-retro.md`, Late reply), graded actionable 7/10 by `.sdlc/runtime/tasks/fleet-retro-2026-10-18/verify3/verifier-L1-2.md`. The verifier's forbidden list is `plugins/sdlc-lite/agents/verifier.md:20`; `plugins/sdlc-lite/agents/planner.md` and `plugins/sdlc-lite/scripts/steps.py` never mention it. Lint rules live in `lint_steps` (`steps.py:1988`).
outcome metric: the new `steps.py selftest` case, before: lint accepts `git stash create` in a criterion

## Constraints
The failing test lands before or with the fix, never after. Match the command as a git subcommand in the criterion's command text only (not in prose, not `git stash list` inside a quoted string the verifier reads). Keep `git worktree add --detach` and read-only git (`log`, `diff`, `show`, `rev-parse`, `status`) allowed.

## Do
1. Add a `steps.py selftest` case first: a handoff with a `git stash create` criterion must be refused with a message naming `git stash`; a control handoff with `git diff --check` must pass. See it fail.
2. Add the rule in `lint_steps`, reporting `plan defect` like the `||` rule.
3. Add one line to `agents/planner.md` naming the forbidden git commands, then run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.

## Acceptance criteria
- (red) `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | grep -F 'ok:' | grep -qF 'git stash'` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
- (red) `grep -qF 'git stash' plugins/sdlc-lite/agents/planner.md` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
