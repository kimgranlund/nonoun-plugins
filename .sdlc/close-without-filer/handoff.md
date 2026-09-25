---
id: T-0037
title: "close a ticket finished by other work"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A ticket whose work was done by other tickets can be closed with a stated reason, without a filer file.

## Intent
- Root goal: a ticket already finished by other work can be marked done honestly, with a recorded reason, without faking a filer file.
- Do: add `--reason "<text>"` to `tickets.py close`. With it, close skips the filer lookup entirely (no filer-L*.md needed, an existing one is ignored, no follow-ups filed, no warnings check), sets `status: done`, appends a `## Closed` section to the handoff body with the date and the reason, and regenerates the roadmap. Keep every existing refusal that still applies (bad slug, not a ticket, other ticket problems, already done, no status line), each writing nothing. Refuse an empty or whitespace-only reason, writing nothing. `--reason` combines with `--numbered` as before; `--force` with `--reason` is accepted and has no effect. Update the success message to say it was closed by reason. Add selftest cases proving: closes with no filer file; the reason lands in the handoff; an existing filer with open warnings and follow-ups is ignored (no follow-up tickets written); empty reason refuses and writes nothing; already-done still refuses. Update the usage docstring, the argparse help, `skills/ticket/SKILL.md` (argument-hint and the close line), the `/file` skill only if it needs a pointer, the `tickets.py` bullet in the repo-root `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md` if it describes close.
- Non-goals: changing the normal filer-based close path; changing `/file`'s flow; a separate `dropped` path.
- Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes with the new cases, the new cases fail against the old code (negative control), and `plugins/sdlc-lite/scripts/check.sh` passes.

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. `tickets.py close <slug> --force` refuses with "no filer-L*.md ... nothing written" (tickets.py:409). In that repo T-0015 was finished by T-0002 step 13, and T-0025 and T-0026 by a bench run. Suggested: `close <slug> --reason "<text>"` sets done and appends the reason, with no filer file needed and no follow-ups filed.

## Constraints
What must not change. "None" if none.
