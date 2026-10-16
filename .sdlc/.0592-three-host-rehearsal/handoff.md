---
id: T-0592
title: "Live rehearsal: Claude, Codex and Pi working tickets in one repo"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0591, T-0570]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Evidence that Claude Code, Codex and Pi can work tickets in one repo at the same time without double claims, lost work or a stuck conductor.

## Context
Maintainer decision 2026-10-15: Claude Code, Codex and Pi work tickets in one repo at once. The design is in the conversation summary: claims and ids are atomic through git refs, which every worktree and host shares; lanes are locked with their owner; workers signal ready with a pinned sha; one conductor per repo writes main. Workers commit nothing (Codex workspace-write cannot write .git); the conductor commits. Pi has no `run.sh` backend; drive it as a mailbox worker in its own session. codex-cli 0.162.1 is installed here; Pi's install state is [U].

## Intent
- Do: in a throwaway repo, file three L1 tickets. Have all three hosts try to claim the same ticket at the same moment, then each take one ticket in its own lane, `lanes.py ready`, and the conductor verify (a different family each time), land and close. Write `docs/reports/<date>-three-host-rehearsal.md` with commands, exit codes and every failure. File each failure as its own ticket.
- Non-goals: fixing failures here.
- Done when: the criteria pass.

## Constraints
Throwaway repo only. No push.

## Acceptance criteria
1. The report exists. It shows exactly one host winning the shared claim, and all three tickets ending `status: done` in main, or names the ticket filed for each failure.
2. `git diff --check` exits 0.

## Plan review
- amend: Pi is not installed on this machine (`pi` not found), so the rehearsal runs two hosts, Claude Code and Codex (codex-cli 0.162.1). Criterion 1 reads "two hosts" for "three"; the report records Pi as not run, and a Pi follow-up ticket is filed. Decided: the user, 2026-10-15 ("Claude + Codex now").

## Outcome

2026-10-15 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: docs/reports/2026-10-15-two-host-rehearsal.md: the Intent names `<date>-three-host-rehearsal.md`; the file is `two-host-rehearsal` to match the amend. Criterion 1 only says "the report exists", so not a fail. | note: docs/reports/2026-10-15-two-host-rehearsal.md: Claude's refused claim (exit 1, "nothing written") and the Codex verifier runs are reported from the solo's own run; I checked only the surviving repo state and Codex logs, per the brief not to rerun Codex.) · verifier: verifier-L2 (sonnet) · base: 20204aed252d
- Changed: see commits
- Commits: 7760b8f T-0592: Live rehearsal: Claude, Codex and Pi working tickets in one repo
- Check: 1 Report exists; exactly one host wins the shared claim; all tickets end `status: done` in main or ...: pass
- Check: 2 `git diff --check` exits 0: pass
