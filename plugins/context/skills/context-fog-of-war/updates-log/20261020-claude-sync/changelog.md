---
date: 2026-10-20
slug: claude-sync
requested_by: user
harness: Codex desktop
authors:
  - role: solo
    agent: Codex
    model: not recorded
    did: Synced reviewed context guidance to Claude skill copies
project: User-level Claude skills
verification: Byte parity and both skill validators passed; 32 progressive-context tests and 49 context-fog-of-war tests passed
backup: /var/folders/rt/2p4p49z17k7fntz7tlyqr2xh0000gn/T/claude-context-skills-before-5y3byw47
---

## Added

- `references/learnings/cli-routing.md` and the original `20261020-cli-routing-lessons/changelog.md` provenance record from the reviewed Codex skill.

## Changed

- Synced `SKILL.md`, `references/engineering.md`, `references/learnings/README.md` and the change-log index from the reviewed source.
- Also synced seven guidance/template files in the sibling `progressive-context` skill.

## Fixed

- Claude copies now contain the same routing lessons and evaluation criteria as the reviewed Codex copies.

## Open

- No scripts, schemas, host metadata or detector behavior changed. Both skill validators and all 81 existing tests passed; no new live Claude invocation claimed.
