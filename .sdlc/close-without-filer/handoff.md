---
id: T-0037
title: "close a ticket finished by other work"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A ticket whose work was done by other tickets can be closed with a stated reason, without a filer file.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. `tickets.py close <slug> --force` refuses with "no filer-L*.md ... nothing written" (tickets.py:409). In that repo T-0015 was finished by T-0002 step 13, and T-0025 and T-0026 by a bench run. Suggested: `close <slug> --reason "<text>"` sets done and appends the reason, with no filer file needed and no follow-ups filed.

## Constraints
What must not change. "None" if none.
