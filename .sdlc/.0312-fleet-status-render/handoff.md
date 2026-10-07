---
id: T-0312
title: "fleet_status.py render and the /sdlc-lite:fleet-status skill"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0310, T-0311]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:fleet-status`: one command that prints the full status in the fixed order and asks the user only for what needs them.

## Intent
- Do: Add `fleet_status.py render [--repos A,B] [--since last|DATE]` printing sections in this order, one screen: Machine (one line: load, trend, cores, top consumers, verdict), Needs you (decision, credential or merge, owner, age), Moving per repo with the liveness mark, Stale or stuck, Done since last report, Release state. Add plugins/sdlc-lite/skills/fleet-status/SKILL.md: run the script, print its output verbatim, then at most one AskUserQuestion round for the Needs-you items with a recommendation first; never composes a table itself; optional `--ping` lists which conductor sessions to message for health reports (it does not send). Add it to packaging and discovery checks and a line in docs maintenance reference.
- Also (folded in from dropped T-0187, 2026-10-06): each Moving row carries the repo's unread message ids (names only, never a body, from `.sdlc/messages/*/new/`) and the supervisor state from `.sdlc/supervisor/status.json` when present.
- Non-goals: Sending messages to conductors; filing tickets.
- Done when:
  - A planted stale row appears under Stale or stuck, not under Moving (observed negative control).
  - Every row shows its source (ticket folder, PR number or process) so a reader can trace it; a row with no source fails the render selftest.
  - Output fits 60 lines for 3 repos, no em dashes, and a repo excluded in fleet.json never appears.
  - `check.py`, `check-packaging.py` and `tickets.py check` pass; the discovery route lists the skill.

## Context
Decided by the user on 2026-10-06. Replaces the hand-built status the author session produced about 20 times (a bash loop, grep filters and a composed table). Problems to fix: rows that lie (board says building for work that never started, or verifier fail for merged work), load with no trend or verdict, 'needs you' buried, no since-last delta, hard-coded repo list. Order of the output: Machine, Needs you, Moving (with a liveness mark), Stale or stuck, Done since last report, Release state. sdlc-lite must own the rendering and not depend on the user-scoped harness rag-board skill. Reuses fleet_collect.py (T-0305) for process classes and run totals. Builds after fleet-retro (T-0305 to T-0308); target 0.21.1.

## Constraints
No model call. Read-only on every repo inspected. No em dashes. No change to any model or effort value. No push, tag or publish.

## Acceptance criteria
Run from the repository root.
1. `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest` exits 0 and its render half prints `ok:` for each of: the sections in the fixed order (Machine, Needs you, Moving, Stale or stuck, Done since last report, Release state); a planted stale row under Stale or stuck and not under Moving, then the same row with a process behind it under Moving and not under Stale or stuck (observed negative control, in a pure model and end to end through the CLI); a row with no source refused with `RenderError`; a heavy three-repo status at most 60 lines while the same data with unshrunk caps is over 60 (negative control); no em dash in titles that carry one; a repo excluded in the registry absent, also when `--repos` names it.
2. `python3 plugins/sdlc-lite/scripts/fleet_status.py render --no-write --no-gh --repos sdlc-lite,agent-ui,ui-kit-maison > /tmp/r.txt` exits 0, `wc -l < /tmp/r.txt` is at most 60, `grep -c $'\xe2\x80\x94' /tmp/r.txt` (the em dash bytes) prints 0, and every indented row and the Machine line ends with a bracketed source.
3. `render --repos sdlc-lite,maison-testing` (the registry excludes `maison-testing`) prints no `maison-testing` and notes the skip on stderr; `render --repos nope` exits 2.
4. Each repo row under Moving carries `unread N` and, when `.sdlc/supervisor/status.json` exists, the supervisor state; unread ids are file names under `.sdlc/messages/new/<receiver>/` and no message body is printed or opened (selftest end-to-end case with a planted body).
5. `plugins/sdlc-lite/skills/fleet-status/SKILL.md` runs the script, prints its output verbatim, asks at most one AskUserQuestion round for the Needs-you rows with the recommended option first, never composes a table, and says `--ping` sends nothing; `skills/sdlc-lite/SKILL.md` routes to it and `check.py` guard 36 pins both (its negative controls fire).
6. `python3 plugins/sdlc-lite/scripts/check.py`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `git diff --check` all pass.
7. `docs/references/sdlc-internals.md` names `render` and the skill in the `fleet_status.py` entry; the script's docstring lists the `render` usage and the new `collect` keys (`unread`, `supervisor`, `report_since`, `closed_since`, `merged_since`, `age_s`).
8. No model call, no message sent, no push: `grep -n "messages\." plugins/sdlc-lite/scripts/fleet_status.py` shows only `messages.ID_RE`.

## Closed

2026-10-06: built and merged on the fleet-status integration branch; verifier passed
