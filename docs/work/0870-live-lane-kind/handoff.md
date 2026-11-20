---
id: T-0870
title: "Live mode's documented lane flow works without a ticket: open a registered lane, see it in overlap and list, m"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0860]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Live mode's documented lane flow works without a ticket: open a registered lane, see it in overlap and list, mark it ready, and land it with `finish --no-ticket`.

## Intent
- Do: add a ticket-free lane kind `live` to `lanes.py open`, let `ready` pin a ticketless live lane, and fix the commands in `agents/live.md`.
- Non-goals: changing fanout, solo or integration kinds; counting a live lane as factory evidence in `who()`.
- Done when: the criteria below hold.

## Context
- #100: `lanes.py open live-docs --no-claim --base ui-kit-migration --into ui-kit-migration` prints `kind fanout needs --ticket: no ticket, no lane`; the reporter fell back to plain `git worktree add`, so `list --overlap`, `ready`, `finish` and `close` did not know the lanes. Suggested: "a ticket-free lane kind for live mode (for example `--kind live`), which registers the worktree, its branch and an owner without claiming a ticket".
- `plugins/sdlc/scripts/lanes.py`: `KINDS` (line 284); `open_lane` (line 1803) refuses fanout and solo without ids (line 1811) and builds the leaf from the first ticket (lines 1831-1835); the lock is set for fanout and solo (line 1868). `ready` (line 2072) refuses a lane with no local ticket (lines 2088-2090) and pins `refs/sdlc/ready/<ticket>`. `who()` counts only fanout and solo lanes (line 2263); keep live out. `overlap` (line ~2290) already covers every plugin lane. `lane_states` flags a branch outside `NAMESPACES` (line 288) as legacy. `finish --no-ticket` (`finish_ticketless`, line 1547) already lands a lane with no ticket; the only ticketless open in the selftest uses `--kind integration` (`case_finish_no_ticket`, line 4506).
- Design: kind `live`: no ticket needed; leaf `slug(name)`; branch `lane/<leaf>`; into `--into`, else `lane_into:`, else main; locked like solo with the `<host>:<session>` holder; no ticket record lines written. `ready` on a live lane with no ticket pins `refs/sdlc/ready/<leaf>`, skips the acceptance-criteria check, and sends the same factory message; `list --ready` shows it. `close`, `sweep` and `finish --no-ticket` treat it like a solo lane with no ticket.
- `agents/live.md` lines 28, 41 and 44 name the commands; change them to `lanes.py open live-<slug> --kind live [--into <branch>]`. Check `agents/hybrid.md` for the same command. Update the kind table in the `lanes.py` docstring (lines 39-52) and `docs/specs/sdlc/lane-lifecycle.md` section 17 where it lists kinds.
- After T-0860, put the new cases in the lanes selftest shard that holds `case_finish_no_ticket`.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` and its Lanes section first.

## Do
1. Add kind `live` to `open_lane` and the CLI choices, with branch, leaf, into and lock as above.
2. Let `ready` and `list --ready` handle a ticketless live lane.
3. Add selftest cases: open with no ticket succeeds and is locked; `list --overlap <path>` from another tree names it; `ready` pins `refs/sdlc/ready/<leaf>`; `finish <leaf> --no-ticket` lands it; `who()` does not list it; fanout and solo still refuse with no ticket.
4. Update `agents/live.md`, the docstring, `lane-lifecycle.md` and the CHANGELOG `[Unreleased]`; run `codex_roles.py generate` if `live.md` is mapped there.

## Acceptance criteria
- The lanes selftest shard holding the new cases exits 0 (name the command), and `python3 plugins/sdlc/scripts/lanes.py selftest` with no shard option exits 0 once at the end. With the `live` branch of `open_lane` removed, the open case fails (state the observed red).
- In a throwaway repo: `lanes.py open live-docs --kind live` exits 0 with no ticket and prints `locked:`; `lanes.py list --json` shows kind `live`.
- `python3 plugins/sdlc/scripts/check.py`, `python3 plugins/sdlc/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc/scripts/claude_roles.py generate --check` exit 0.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- A live lane never writes a ticket file or a claim ref.
- Fanout and solo still need `--ticket`.
