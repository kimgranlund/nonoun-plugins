---
id: T-0041
title: "close confirms follow-ups before filing them"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Follow-up tickets are proposed to the user, or checked against the task's artifacts, before close files them, so already-answered and duplicate follow-ups never land.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Reported by the setup-sdlc-lite-generative-ui session from gen-ui-system-svelte-lite (seen on 0.3.0); confirmed still present in 0.4.3. On 0.3.0, `close` on four small tickets filed 15 follow-ups, some already answered in the same session. Partly covered since 0.4.2: the filer now lists only follow-ups that change behavior or close a real risk (3 became 1 in a live rerun). Still missing: a confirm step (for example `close --dry-run` listing the proposed follow-ups, which /file then shows through AskUserQuestion) and a duplicate check against existing tickets.

## Constraints
What must not change. "None" if none.
