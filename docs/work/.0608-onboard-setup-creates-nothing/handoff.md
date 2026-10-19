---
id: T-0608
title: "onboard.py setup creates entry stubs and layout.md in a repo that never asked"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`onboard.py setup` changes nothing a repo did not ask for. It refreshes an existing managed block in place. It appends a root block, creates `docs/` entry stubs, or writes `docs/layout.md` only with an explicit `--init` (or the equivalent flag the skill documents).

## Context
Reported by the gen-ui-kit conductor 2026-10-15 after `onboard.py setup` on 0.24.0 (reverted). gen-ui-kit is a bare clone with lanes at `<bare parent>/lanes/`, tickets in `docs/tickets` (`ticket_root:`), its own doc routing and AGENTS.md size gates, and an owner ruling that `.gitignore` stays as is. Check mode reported the root `AGENTS.md` as "unmanaged". Setup then appended a new block and created 24 `AGENTS.md` and `CLAUDE.md` files under `docs/` with a "Describe what this topic covers" placeholder and full file listings (`docs/tickets/AGENTS.md` listed every ticket), plus a new `docs/layout.md`. The 0.24.0 release note told every repo to rerun setup, which caused this.

## Intent
- Do: default setup refreshes existing managed blocks only and prints what `--init` would add. `--init` keeps today's behavior. Update `skills/onboard/SKILL.md` and the 0.24.0 upgrade notes (in the next release report) to say "refresh only".
- Non-goals: block content (the sibling ticket).
- Done when: the criteria pass.

## Constraints
A repo already set up keeps refreshing exactly as today.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0. Its new cases cover:
   - a repo with no managed block and a `docs/` tree, where setup without `--init` changes no file and lists what `--init` would add;
   - the same repo with `--init`, which behaves as before.

   The cases failed before the change.
2. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: fix-now: `plugins/sdlc-lite/scripts/reorg.py:35` and `:103` tell the user "run onboard.py setup first" when `docs/layout.md` is missing. Setup without `--init` no longer creates `layout.md`, so the hint should say `onboard.py setup --init`. This is a stale message, and no criterion covers it. | note: `plugins/sdlc-lite/scripts/tickets.py:191` and `plugins/sdlc-lite/skills/ticket/SKILL.md:53` say to run `onboard.py setup` to refresh the root block. That still works when a managed block exists, so I left it. | note: the release-report "refresh only" wording is the conductor's job at release time, as instructed. | note: cleanup of my scratch probe was denied by the permission system, so `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0608-verifier-L2/probe` is still there. It is outside the repo and I created no throwaway worktree.) · verifier: verifier-L2 (sonnet) · base: 1266e8db128c
- Changed: see commits
- Commits: beb20cb T-0608: onboard.py setup creates entry stubs and layout.md in a repo that never asked; 28c8c14 T-0608: record lane T-0608-t0608
- Check: 1 `onboard.py selftest` exits 0, with new cases for no-`--init` and `--init`: pass
- Check: 2 `git diff --check` exits 0: pass
