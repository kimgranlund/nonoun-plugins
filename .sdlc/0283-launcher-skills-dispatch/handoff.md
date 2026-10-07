---
id: T-0283
title: "Launcher skills dispatch through sub-agents"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0282]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The launcher skills and /agent route a role through dispatch instead of run.sh.

## Intent
- Do: Launcher skills dispatch through sub-agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `skills/build`, `plan`, `verify`, `research`, `scout`, `architect`, `dig`, `file`, `agent`, `ticket`, `bench`, `review-traces`, and `sdlc-lite` name the dispatch path for the Claude backend; `git grep -n "scripts/run.sh" plugins/sdlc-lite/skills` finds only Codex-transport or legacy-note lines (list them in the ticket).
  - `check.py` item 25 (agent command names) passes, and a skill that names a role absent from `agents/` fails it (negative control).
  - `python3 scripts/check-packaging.py` and `python3 plugins/sdlc-lite/scripts/check.py` pass.

## Context
Design section 1. Text only; mechanics are in dispatch.py.

## Constraints
No script changes. No em dashes. No push, tag, or publish.

## Remaining `scripts/run.sh` lines in skills

`git grep -n "scripts/run.sh" plugins/sdlc-lite/skills` finds only Codex-transport or legacy-note lines. Each of these is the Codex run line next to a dispatch line (every one names Codex on the same line):

- `agent/SKILL.md` 17, 18, 19, 20 (start table, `Codex:` form) and 28 (step 4, `On Codex run ...`)
- `architect/SKILL.md` 16, `build/SKILL.md` 15, `dig/SKILL.md` 16, `plan/SKILL.md` 16 and 18, `research/SKILL.md` 16, `scout/SKILL.md` 16, `verify/SKILL.md` 16, `file/SKILL.md` 14: the dispatch step, ending `On Codex run SDLC_BACKEND=codex ...run.sh`
- `file/SKILL.md` 23: `hooks/block-publish.sh` note, Codex `scripts/run.sh` sets `SDLC_ROLE` per role run
- `bench/SKILL.md` 16, `fleet-retro/SKILL.md` 56, `review-traces/SKILL.md` 12: the dispatch paragraph's Codex clause
- `sdlc-lite/SKILL.md` 57: the Codex adapter's own `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=subagent` runner example
- `handoff-format/SKILL.md` 48: names `run.sh` as the Codex writer of `<role>-<level>.md` (T-0282 text, unchanged)

## Acceptance criteria
- `git grep -n "scripts/run.sh" plugins/sdlc-lite/skills | grep -vi codex` prints nothing: no Claude-scoped `run.sh` line is left in a skill.
- `skills/build`, `plan`, `verify`, `research`, `scout`, `architect`, `dig`, `file`, `agent`, `review-traces`, and `bench` each name `dispatch.py prepare`, `dispatch.py record`, and an `Agent` call; `skills/ticket` and `skills/sdlc-lite` name `dispatch.py` for the Claude backend; `skills/fleet-retro` (its verifier run) does too. Their `allowed-tools` no longer grant `run.sh` and grant `dispatch.py` and `Agent` where a role is launched.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0, including item 25; appending a table row for a role with no `agents/` file to `skills/agent/SKILL.md` makes it exit 1 with `table row ... has no agents/...md` (observed, then restored).
- `python3 scripts/check-packaging.py` passes; `git diff --check` is clean; the diff adds no em dash and changes no script.
