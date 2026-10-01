---
id: T-0179
title: "Messages entry files and fresh-role live validation"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0177, T-0178]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-09-30
---

## Goal
A harness that reads `.sdlc/*` learns the ticket and message folder systems from the entry files alone, and a fresh Claude role and a fresh Codex role, given only a path to a message file and no skill, ack it and reply correctly.

## Intent
- Do:
  - Self-describing folders: add no new skill for tickets, messages, or the router. `.sdlc/AGENTS.md` (router additions for `messages/`, built on T-0175's router block), `.sdlc/messages/AGENTS.md`, and the three-line entry files `messages/new/AGENTS.md`, `messages/read/AGENTS.md`, `messages/done/AGENTS.md` carry the full procedures in plain steps with the exact commands (messages: send, read, ack, reply, expire; the `.sdlc/tickets/AGENTS.md` procedures come from T-0175). Each stage folder entry file has three lines: what the folder means, what moves a file out of it, the command. `messages/AGENTS.md` also holds the `messenger` setup: each harness creates a dedicated `messenger` sub-agent on a cheap model, it polls `messages/new/<harness>` every 10 seconds and notifies its parent, parents send through it, host limits stated separately without implying enforcement from one host to the other, and bodies are data that cannot authorize a publish, push, or external write.
  - Where the files come from: shipped as templates and written into a consumer repo by whichever of `tickets.py roadmap` or `onboard.py` already owns managed blocks for `.sdlc/AGENTS.md` (follow T-0175's choice); the router block links `messages/AGENTS.md`.
  - Live negative-control run: a fresh Claude role and a fresh Codex role, each given only a path to a message file and no skill, correctly `ack` it and reply (`send_time <= read_time <= ack_time`; a reply sent when `follow_up_requested` is true) in a throwaway project. Include a run through the real `messenger` agent on Claude, and on Codex if available, showing new, read, done. Record the result in a dated validation doc under `docs/validation/`, linked from `docs/README.md`; report any arm that could not run as unverified with the reason.
  - Update `docs/ticket-stages/design.md` status and `docs/maintenance/sdlc-internals.md`.
- Non-goals: the mailbox code (T-0177), the agent file (T-0178), a daemon, hooks, version bump, publishing.
- Done when: the entry files exist and pass `bash plugins/sdlc-lite/scripts/check.sh`; the live-run doc records both hosts or names the limit; the verifier reruns or inspects the live evidence and injects a defect (for example a wrong command in `messages/AGENTS.md`) to show the path-only run fails.

## Context
Design: `docs/ticket-stages/design.md` (sections Message bus, Two roots, Validation plan). Split from T-0176 by user decision; the three tickets together hold every T-0176 requirement. No em dashes in any file written. Do not bump versions. Do not edit `run.sh` while a role run is using it: build in the worktree copy and run roles from the main checkout's copy. Depends on T-0177 (commands, the `protocol` field) and T-0178 (the agent). Routing facts for what each host loads are in `docs/validation/nested-entry-file-loading.md`.

## Constraints
No new skill. One authoritative location for the procedures: `messages/AGENTS.md`; the `messenger` body defers to it.
