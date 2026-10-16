---
id: T-0605
title: "builder.md says a second redck record is only a base control, stale since T-0473"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`agents/builder.md` rule 11 describes `redck.py record` as T-0473 changed it, and the generated builder files match.

## Context
`plugins/sdlc-lite/agents/builder.md:28` still says a second `record` "is only a base control and is stored as retrospective". T-0473 changed `redck.py` to bind records to the working tree and an ancestor base, so that sentence is partly stale. T-0473 forbade prompt wording changes, so it was left. Source note: `.sdlc/notes.md` T-0473.

## Constraints
Read `plugins/sdlc-lite/scripts/redck.py` first and word the sentence from its current behavior. Edit `builder.md` only, then run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Model and effort defaults stay unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.
2. `grep -c 'only a base control' plugins/sdlc-lite/agents/builder.md` prints 0.
