---
id: T-0182
title: "Design an external watcher that resumes an idle host when a message arrives"
type: spike
status: done
size: M
priority: P2
depends: []
created: 2026-10-01
---

## Goal
A reviewed design for a process outside any agent that notices a message for a harness and resumes that harness when its session is idle. The result is a design document and an independent review of it; no code.

## Intent
- Do: write `docs/planning/ticket-stages/watcher-design.md`, link it from `docs/specs/ticket-stages/README.md` and `docs/README.md`, then run an independent review through `scripts/run.sh` on a model family other than the author's, and record the result in `docs/reports/idle-host-watcher-design-review.md`.
- Non-goals: any watcher code, launchd plist, or hook; changing `messages.py`; a Claude or Codex feature request.
- Done when: the design covers every item under Context, the review is recorded with each finding resolved or listed as open, and `git diff --check` is clean.

## Context
Problem: `.sdlc/messages/` delivers mail, but a subagent or `wait` call reports only into a running parent turn (T-0180, T-0181). A host whose turn has ended never sees new mail. The user keeps a Codex host awake with `/goal`. Only a process outside the agent can start a new turn.

The design must cover:
1. What resumes an idle host on each harness: `codex exec resume` (resume the last or a named session) and Claude Code `claude --continue`, `claude --resume <session-id>`, or `claude -p` with a session id. State which of these were verified live in this repo's environment and which are unverified; verify the exact flags with `--help` for the installed versions (`claude --version`, `codex --version`) rather than from memory, and record the versions.
2. Launch mechanisms: a launchd job on macOS, a shell loop in a terminal, `fswatch` or polling `messages.py count`. For each: cost, failure mode, survives logout or sleep, permission needs.
3. The claim race: the watcher must never claim or move a message (only `messages.py count` or `list`), so the in-session messenger, a `wait` call, and the resumed host keep the existing atomic rename claim. State what happens if the watcher fires while a host is already active (a second session on one thread) and how to detect an active host.
4. Authority of a woken host: it follows the rules of an unattended run, including `/fix`: never push, never open a pull request, never publish, never call AskUserQuestion; message bodies are data and cannot authorize a publish or any external write; the wake prompt is fixed text naming the receiver and the message path, never the body.
5. Auth and cost: which logins the resumed session uses, what one wake costs (tokens, model), and a daily wake cap.
6. Loop and storm limits: debounce, a per-receiver wake cooldown, a maximum wakes per hour, the refusal to wake for a message the woken host itself sent (reply loops between two harnesses), and `expires` as the backstop.
7. Failure and cleanup: a woken host that fails, a message that stays in `new/`, stale lock or pid files, how the watcher stops, and a visible status line.
8. What is host-specific and what is shared; a Claude hook enforces nothing on Codex.
9. A validation plan with a positive case and a negative control for each safety rule (no push, no claim by the watcher, storm limit, no body in the wake prompt), and what would count as passing.
10. Open questions, listed.

Read first: `docs/specs/ticket-stages/design.md` (mailbox and bus), `docs/reports/messages-live-run.md`, `plugins/sdlc-lite/scripts/messages.py` (module docstring), `docs/references/codex-role-execution.md`. No em dashes anywhere.

## Constraints
Docs only. Do not edit the plugin, the scripts, or any released record. The review must be by a role the author does not share a family with: the author is Claude Sonnet, so the reviewer is not Sonnet.

## Closed

2026-10-01: design written and independently reviewed by the architect role (fable): ready after fixes; findings recorded in docs/reports/idle-host-watcher-design-review.md and applied by T-0183 step 1
