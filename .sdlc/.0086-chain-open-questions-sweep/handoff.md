---
id: T-0086
title: "Close-out sweep at the end of /chain: batch unresolved items into one AskUserQuestion round"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A /chain run ends with one batched AskUserQuestion round for everything left unresolved.

## Intent
Literal ask: A /chain run ends with one batched AskUserQuestion round for everything left unresolved; port harness find-open-questions so sdlc-lite carries it itself.
Deltas:
- Where the sweep lives: defaulted: a new sdlc-lite skill `skills/open-questions/SKILL.md` (user-invocable as `/sdlc-lite:open-questions`), ported and trimmed from the harness source, plus a final close-out step in `skills/chain/SKILL.md` that runs its flow after step 5 (File). The conductor names it as the route for "anything still open" asks.
- Item sources in sdlc-lite terms: defaulted: `(gap: ...; default: ...)` lines the /clarify flow wrote into the task handoff's Intent, `## Plan review` entries still unanswered, verifier or builder notes and filer output that ask for a user decision, and questions raised earlier in the session. Items already asked in /file's own publishing round, or settled since, are stale and dropped.
- Unattended (headless, no person present): defaulted: never call AskUserQuestion; list the open items as plain lines in the final report instead (the ticket's Context says so), or say nothing is open.
- No harness dependency: defaulted: the skill must not reference harness skills (write-handoff, find-intent, file-leftovers, close-session); it may point at sdlc-lite siblings (/clarify, /ticket).
Do: add `skills/open-questions/SKILL.md` (procedure: scan sources, nothing open -> one line, else one AskUserQuestion call with 1 to 4 questions of 2 to 4 options, recommendation first only where a default was actually stated, more than 4 -> top 4 plus a count of the rest, stale items dropped, a decline is not re-asked; unattended -> list in the report), add the close-out step to /chain after File and before/inside Report, add the route line to `agents/conductor.md`, and update the repo CLAUDE.md skill list (and `.claude/agents/sdlc-lite-author.md` if it lists skills) so records stay in sync.
Non-goals: no script or code gate; no change to /file's own publishing questions; no change to /clarify or /grill; no ticket filing of leftovers.
Done when: `scripts/check.sh` passes; `skills/open-questions/SKILL.md` exists with valid frontmatter and no reference to harness skills; `skills/chain/SKILL.md` has a close-out step naming open-questions with both the interactive (one AskUserQuestion round) and unattended (list in the report) behavior; conductor.md routes to it; CLAUDE.md lists it.

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/find-open-questions/SKILL.md (76 lines). The conductor asks per decision but has no close-out sweep. Unattended runs list the items in the report instead.

## Constraints
What must not change. "None" if none.
