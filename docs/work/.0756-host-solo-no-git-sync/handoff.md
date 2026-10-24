---
id: T-0756
title: "A host-worktree solo brief asks for no git sync"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The solo brief `fanout.py prep` writes for a host worktree asks for no git command at all (the host sandbox refuses every git command and compound or quoted shell lines in that worktree), and the ticket stays reachable: either prep refuses when the base sha is not on the remote default branch the host cuts worktrees from, or land merges the base itself, so a solo never needs `git merge --ff-only <base>`.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: the brief line `before anything else run git merge --ff-only <base sha> in your worktree so the ticket folder is visible` (fanout.py SOLO_SYNC); all three solos reported it refused ("The host worktree guard refused every git command and any compound shell line", "refused any command containing a quoted string"). The host cut every worktree from origin/main 1e7dd6d while prep's base was the unpushed local main 304126d, then 26b7276.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case: prep for a host lane whose base is not reachable from the remote default branch refuses (exit 2) naming the push to make, or the brief carries no git command and land merges the base; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Picked option A: `fanout.py prep` refuses (exit 2) when any ticket runs solo and the base sha (HEAD, the sha the dispatch writes) is not reachable from the remote default branch the host cuts worktrees from (`origin/HEAD`, else `origin/main` or `origin/master`; a repo with no origin skips the check). The message names the push to make (`... HEAD:<branch>`). Why A over land merging the base: under B the host worktree still starts at the origin tip, so a ticket folder that exists only on the unpushed base is invisible to the solo before any land runs; a land-time merge of the base also risks a conflict in `handoff.md`, which the claim commit and an L2 solo both edit. Under A the host worktree starts at (a descendant of) prep's base, which is what T-0757 can rely on: the verifier's Base sha equals prep's base.

Change: `SOLO_SYNC` keeps `Base sha:` and the `export SDLC_BASE_SHA=... &&` sentence, drops `git merge --ff-only`, and says to run no git command; new `remote_default` and `host_base_refusal` in `plugins/sdlc-lite/scripts/fanout.py`, called inside `cmd_prep`'s refusal block (before `sweep_lanes` and any record write); module docstring and `docs/references/sdlc-internals.md` updated.

Checks:
- New selftest case 22 (T-0756): a repo with a bare origin, main pushed, one more local commit: prep exits 2 naming `origin/main` and the push, writes no dispatch; after the push prep exits 0 and the brief has no backticked git command. The old T-0438 assertion now checks the brief has `Base sha:` and no git command.
- Negative control: the case was written before the fix and run against the unfixed fanout.py; FAIL lines: `case 22 prep: the brief carries \`Base sha: <base>\` and no git command, got ...`, `case 22 prep (T-0756): a base not on origin/main exits 2 naming the push and writes no dispatch, got rc=0 err=''`, `case 22 prep (T-0756) control: once pushed, prep exits 0 and the brief asks for no git, got rc=0 err=''`.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0 (PASS)
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0
- `python3 scripts/check-packaging.py` exit 0
- `git diff --check 12f046a9` exit 0

## Outcome

2026-10-24 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 12f046a92ed1
- Changed: see commits
- Commits: 00b7c6a T-0756: A host-worktree solo brief asks for no git sync
- Check: 1 fanout.py selftest case: prep for a host lane whose base is not on the remote default branch refu...: pass
- Check: 2 gate_lock selftest exit 0, `check.py` exit 0, `check-packaging.py` passes, `git diff --check 12f0...: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:2211: decide: the refusal... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:2211: note: for a base on a... -> notes.md
