---
id: T-0692
title: "lane_setup config commands run by lanes.py open"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A repo can declare its lane setup (install, codegen, builds) once in `.sdlc/config` and every lane `lanes.py open` creates is ready for gates without hand-run setup.

## Intent
- Do:
  1. `lanes.py` `config()` (`plugins/sdlc-lite/scripts/lanes.py:323`): collect every `lane_setup:` line in order (today a second line silently replaces the first), and `open_lane` (lanes.py:1475) runs them in order in the new tree, stopping at the first failure; record `setup: ok` or `setup: failed rc=<n> (<command>)` and print the setup line on success too.
  2. Add a lanes.py selftest case: a config with two `lane_setup:` lines both run in order (a marker file holds both lines), and a failing first line records `failed` and skips the second.
  3. Document `lane_setup:` beside `lane_ports:` in the Lane lifecycle paragraph of `plugins/sdlc-lite/skills/fanout/SKILL.md` (line 39) and update the Config block of the lanes.py docstring (line 211).
- Non-goals: a separate `lanes.py prep <lane>` command; running setup in the integration tree, which `fanout.py` adds with a plain `git worktree add` (fanout.py:1227); ports in briefs (T-0693).
- Done when: the criteria pass.

## Context
Source: GitHub issue #41, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- Every lane needed `npm ci`, `node scripts/gen_barrels.mjs` and a geometry and styles build before gates or dev servers worked. The conductor ran setup for 12 lanes in one hand-written loop; the peer did it by hand in 8 lanes.
- The issue's claim that `lanes.py open` runs no setup is false on main (8624f984): `lane_setup: <cmd>` exists since T-0451 (lanes.py docstring line 211, `CONFIG_KEYS` line 239, run with `shell=True` in the new tree at lanes.py:1475-1483, recorded in the lane record's `setup` field). Fanout lanes get it too, since `fanout.py setup` opens each lane through `lanes.open_lane` (fanout.py:1233). The real gaps: no skill or agent file mentions `lane_setup` (only `lane_ports` is in fanout SKILL.md:39), only the last `lane_setup:` line counts, success prints nothing, and no selftest covers it.

## Constraints
A config with one `lane_setup:` line behaves as today apart from the printed `setup: ok`. A setup failure still keeps the lane.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with the new case, and the case fails with the change reverted.
2. `grep -n "lane_setup" plugins/sdlc-lite/skills/fanout/SKILL.md` prints at least one line.
3. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. `git diff --check <base sha>` exits 0.
