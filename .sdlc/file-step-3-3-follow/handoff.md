---
id: T-0080
title: "/file step 3.3 follow-ups multiSelect can exceed AskUserQuestion's..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0067
---

## Goal
`/file` step 3.3's follow-up question never asks AskUserQuestion for more than 4 options in one question (the tool's per-question limit), however many follow-ups the filer lists, and `scripts/check.py` fails if that rule is removed from `plugins/sdlc-lite/skills/file/SKILL.md`.

## Context
Follow-up from T-0067 (file-publish-question-options/filer-L1.md):

`/file` step 3.3 follow-ups multiSelect can exceed AskUserQuestion's 4-option limit when a filer file lists more than 4 follow-ups; cap or batch it and add a check.py guard.

## Constraints
- Keep step 3's other behavior (dry run, `--skip`/`--expect` digest, unattended path in 3.5, recommended set first) unchanged.
- Keep the existing check.py guards for step 4 (`at most 4 options`, no issues among publish options) passing.
- Paths: plugin source is `plugins/sdlc-lite/`; run `plugins/sdlc-lite/scripts/check.sh` as the final gate.
- No em dashes.

## Scope (clarify, unattended)
Do: edit step 3.3 of `plugins/sdlc-lite/skills/file/SKILL.md` to batch follow-ups into questions of at most 4 options (AskUserQuestion also accepts up to 4 questions per call, and a question needs at least 2 options, so a lone leftover follow-up must still be a valid question), and add a check.py guard with a negative control proving it fires. Done when check.sh is green and the guard fails on the pre-change SKILL.md text.
