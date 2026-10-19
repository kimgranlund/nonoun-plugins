---
id: T-0401
title: "messages.py has no version-free entry point, so a watcher breaks when the plugin cache updates"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A running watcher loop and the AGENTS.md hint call messages.py through a path that survives a plugin update, instead of a versioned cache folder that disappears.

## Intent
- Do: find every place the messenger, conductor or messages entry files and the T-0397 `watch` text name `.../sdlc-lite/<version>/scripts/messages.py`. Choose the smaller fix: a version-free resolver (a documented one-line resolve step such as picking the newest `sdlc-lite/*/scripts/messages.py` at call time, or a launcher the consumer repo gets from onboard) or a documented resolve-on-missing recovery step. Make the documented loop use it. Also check, and fix if wrong, that `messages.py beat` does not extend the `activate` window (maison saw a watcher expire while its Monitor was renewed): either `watch` re-activates each window or the docs say so, and a selftest case shows it.
- Non-goals: model or effort changes; running onboard in consumer repos.
- Done when:
  - A selftest or check.py guard, observed failing first: no shipped entry file or skill text hardcodes a versioned `sdlc-lite/<x.y.z>/` cache path, and the documented watch loop survives a simulated version-folder rename.
  - messages.py selftest, check.py and tickets.py check pass.

## Context
Maison and Codex, 2026-10-09: after 0.22.0 to 0.22.1 the 0.22.0 cache folder disappeared and a running watcher that hardcoded .../sdlc-lite/0.22.0/scripts/messages.py exited 2. Evidence: maison .sdlc/tickets/0283-messenger-listener-lifecycle/plugin-update-path-recovery-2026-10-09.md. Related: T-0396, T-0397.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest` exits 0 and includes the cases `entry files: no versioned plugin path, and the watch loop survives a plugin update` and `beat keeps the window; watch extends it`.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0; it fails when a skill, agent, command, hook or Codex adapter file names `sdlc-lite/<digits>.<digits>`.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
- The generated mailbox `AGENTS.md` runs every command through `<mailbox>/messages-run.py`, and the launcher falls back to the newest sibling `sdlc-lite/<version>/scripts/messages.py` when its recorded folder is gone.

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
