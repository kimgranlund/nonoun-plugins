---
id: T-0783
title: "The fanout skill says when a sub-agent round needs main pushed"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor running sub-agent lanes knows that a second `prep` after a `settle` that moved main needs main on the remote, and asks the user for that push instead of stalling or pushing on its own.

## Intent
- Do: in `plugins/sdlc-lite/skills/fanout/SKILL.md` (sub-agent section) or its `references/main.md`, add: `prep` refuses a base the remote default branch lacks (T-0756), so after a `settle` that moved main and printed `next: git push origin <main>` (T-0778), the next sub-agent round needs that push; it is the user's call: ask with AskUserQuestion (push now, or stop here), never push unasked. Keep "fanout.py never pushes" true. Mirror one line in `agents/conductor.md` only if it describes the sub-agent round loop; regenerate agents if it changes.
- Non-goals: changing any script.
- Done when: the criteria pass.

## Context
Third 0.36 rehearsal (2026-10-25, /Users/kimgranlund/Projects/nonoun/live036c-run/report.md, read-only): round 1 settle moved local main and printed `next: git push origin main`; the skill says the script "never pushes"; round 2 prep then refused (`base 5811326... is not on origin/main ... push it first`), and the headless conductor, told not to push, stopped.

## Acceptance criteria
1. The skill text (SKILL.md or a linked reference) states the push-between-rounds rule and that the push is asked of the user; `grep -n "push" plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/skills/fanout/references/*.md` shows it.
2. `python3 scripts/check-packaging.py` passes (SKILL.md under 18,000 characters), `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and `git diff --check <base sha>` exits 0.
