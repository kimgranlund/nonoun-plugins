---
id: T-0709
title: "Role definitions name the brief's literal throwaway prefix, not SDLC_TMP_WORKTREES"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
No source role definition teaches a `$SDLC_TMP_WORKTREES/...` command form; each tells the role to use the literal throwaway prefix its brief names.

## Intent
- Do: in the source definitions `plugins/sdlc-lite/agents/builder.md`, `verifier.md`, `planner.md`, `plan-reviewer.md` (and any other source agent or skill reference `git grep -n SDLC_TMP_WORKTREES plugins/sdlc-lite/agents plugins/sdlc-lite/skills` finds that shows a command using it), replace the variable in example commands and rules with "the throwaway prefix your brief names" written as a literal path placeholder such as `"<throwaway prefix>/base"`. Keep a short note that run.sh-launched roles may also have `SDLC_TMP_WORKTREES` set. Regenerate with `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Update any selftest or check that pins the old wording.
- Non-goals: hook or brief changes (T-0707, T-0708).
- Done when: the criteria pass.

## Context
T-0708 (landed) makes the hooks refuse `$SDLC_TMP_WORKTREES/...` when the variable is unset, which it is for every `dispatch.py prepare` sub-agent. T-0708 verifier-L2: "decide: the verifier agent instructions (rule 3, `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`) still teach the variable form, which a dispatch.py prepare sub-agent now has refused." So every role that follows its definition now hits a refusal and retries.

## Acceptance criteria
1. `git grep -nE '\$\{?SDLC_TMP_WORKTREES' plugins/sdlc-lite/agents` prints only lines that describe run.sh behavior, none that shows a command to run.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 (generated-definition parity) and `python3 scripts/check-packaging.py` passes.
3. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0.
4. `git diff --check <base sha>` exits 0.

## Outcome
Source definitions `builder.md`, `verifier.md`, `planner.md`, `plan-reviewer.md` now show `"<throwaway prefix>/base"` in every example command and tell the role to use the throwaway prefix its brief names, with a note that a `run.sh`-launched role may also have `SDLC_TMP_WORKTREES` set. The 12 level variants and 16 Codex TOMLs were regenerated, not hand-edited. `git grep -nE '\$\{?SDLC_TMP_WORKTREES' plugins/sdlc-lite/agents` prints nothing. `check.py`, `check-packaging.py`, `dispatch.py selftest`, `hook-selftest.sh` and `git diff --check` all exit 0.
