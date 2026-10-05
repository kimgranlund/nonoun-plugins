---
id: T-0270
title: "steps.py lint gives a generic error for nested backticks"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
steps.py lint names nested backticks and the concatenation workaround; widen names the accepted scope forms.

## Context
Source: maison `.0130` report, draft 2. Today lint says only `acceptance criterion command does not parse: node -e "console.log("`. In `lint_steps`, when a span fails `bash -n` and the criterion line holds more than two backticks, append a hint line naming nested backticks and string concatenation; keep the first line (selftest needles "does not parse"). At the widen refusal (`steps.py` near 2048) append the accepted forms (`grep -vxF -e <word>...`, `grep -vxE "<pattern>"`, `grep -vE "^(...)$"`). One selftest case per message; `agents/planner.md` unchanged.

## Constraints
No push, tag, version bump, or publish. No em dashes.
