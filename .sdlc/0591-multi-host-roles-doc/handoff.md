---
id: T-0591
title: "Conductor, worker and verifier rules for Claude, Codex and Pi in one repo"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0590]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One short authoritative statement of how Claude Code, Codex and Pi share a repo: who is conductor, what a worker may write, how it signals ready, and that the verifier is a different model family. It lives in `plugins/sdlc-lite/AGENTS.md` (the Lanes section) and the consumer `conductor` agent, and the onboarding `AGENTS.md` block names it in one line.

## Context
Maintainer decision 2026-10-15: Claude Code, Codex and Pi work tickets in one repo at once. The design is in the conversation summary: claims and ids are atomic through git refs, which every worktree and host shares; lanes are locked with their owner; workers signal ready with a pinned sha; one conductor per repo writes main. Workers commit nothing (Codex workspace-write cannot write .git); the conductor commits. Built pieces: T-0588 (claims), T-0589 (lane lock), T-0590 (ready).

## Intent
- Do: write the rules (the conductor writes main; a worker writes only its locked lane and commits nothing; `lanes.py ready` when done; the verifier is a different family from the worker; Pi works as a mailbox-driven worker until it has a backend). Regenerate agents.
- Non-goals: new mechanisms.
- Done when: the criteria pass.

## Constraints
One authoritative location; others link to it.

## Acceptance criteria
1. `grep -n 'lanes.py ready' plugins/sdlc-lite/AGENTS.md plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/scripts/onboard.py` prints at least one line from each.
2. `python3 plugins/sdlc-lite/scripts/check.py`, `claude_roles.py generate --check`, `codex_roles.py generate --check` and `git diff --check` exit 0.
