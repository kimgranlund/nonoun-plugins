---
id: T-0874
title: "The lead can claim paths for one lane, and every lane sees who owns a path before it creates or changes it"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0873]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-20
branch: lane/T-0874-t0874
worktree: ../sdlc-lite.worktrees/T-0874-t0874
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The lead can claim paths for one lane, and every lane sees who owns a path before it creates or changes it.

## Intent
- Do: add `lanes.py claim`, `lanes.py owners`, claim reporting in `list --overlap` and `status`, and an "append" mark for shared append-only paths.
- Non-goals: refusing commits (lane-claims-commit-guard); git hook installation.
- Done when: the criteria below hold.

## Context
- #102: two lanes each planned to create `src/lib/app-scopes.ts`; caught only because one lane announced it. Proposal: `lanes.py claim <lane> <path-glob>...`, `lanes.py owners`, `list --overlap` reports claims, and a path marked "append, expect conflicts" warns instead of refusing.
- `plugins/sdlc/scripts/lanes.py`: the lanes root holds `lanes.lock` (used for port picks under a flock) and `host/` records; `overlap` (around line 2290) matches paths and directories; `close_lane` (line 1128) is where a lane's claims should be dropped.
- Design: claims live in `<lanes root>/claims.json` (shared by every worktree), written under the `lanes.lock` flock: `{glob: {lane, mode: own|append, at}}`. `claim <lane> <glob>... [--append]` refuses a glob another open lane owns (naming it) unless both are `append`; `claim --release <lane> [<glob>...]`; `owners [--json]` lists claims and drops ones whose lane is gone. `list --overlap <path>` adds `claimed <lane> <glob>` lines; `status` adds an owner note. Closing a lane releases its claims.
- Match globs with git pathspec rules (`:(glob)`), as `hash_bound:` does.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Add the claims store, `claim`, `claim --release` and `owners`.
2. Report claims in `list --overlap` and `status`; release on close.
3. Add selftest cases (two lanes: a second own-claim refused naming the owner, two append claims allowed, close releases, `--overlap` prints the claim) and document in the docstring and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- The lanes selftest shard holding the new cases exits 0; with the owner check removed from `claim`, the refusal case fails (state the observed red).
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- No claim is ever enforced at commit in this ticket.

## Outcome

2026-11-20 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: a99becd3c8a4
- Changed: see commits
- Commits: 6e5843e T-0874: a lane can claim paths so two lanes never create the same file (#102)
- Check: 1 The lanes selftest shard holding the new cases exits 0; with the owner check removed, the refusal...: pass
- Check: 2 `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean: pass
- Follow-up: note: plugins/sdlc/scripts/lanes.py store shape is {glob: {lane, path... -> notes.md
- Follow-up: note: the diff adds no commit-time enforcement CHANGELOG states claims... -> notes.md
