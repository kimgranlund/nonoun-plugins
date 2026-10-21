---
id: T-0693
title: "briefs carry a Ports line from lanes.py port"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: [T-0682]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role working in a lane that holds a port is told that port in its brief, so it stops picking ports by hand and colliding with other lanes.

## Intent
- Do:
  1. In `prepare` (`plugins/sdlc-lite/scripts/dispatch.py`, the prompt built near line 1262): when the tree is a lane whose `.lane.json` has a port (`lanes.port_of(tree)`, lanes.py:1784), add a line after the `Tree:` line: `Ports: SDLC_LANE_PORT=<n> (this lane's own port; start any server on it or on a port derived from it, never a fixed one)`. No port, no line.
  2. In `solo_run.py` (`plugins/sdlc-lite/scripts/solo_run.py`, the `Tree:` insertion near line 193): add the same line for a solo whose tree or worktree is a lane with a port.
  3. Add a selftest case in each script: a lane tree with `port: 47410` in `.lane.json` gets the `Ports: SDLC_LANE_PORT=47410` line, and a tree with no port gets none.
- Non-goals: repo-specific variable names (such as `CONFORMANCE_PORT`); allocating more than one port per lane; `lane_setup` (T-0692).
- Done when: the criteria pass.

## Context
Source: GitHub issue #41, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- The conductor wrote "private port 4800 to 4999" into every solo brief by hand, and 4 role results in 0.27 hit `Port 4317 is already in use` or a stale server.
- On main (8624f984): `lane_ports: <lo>-<hi>` in `.sdlc/config` gives each lane a port in its `.lane.json` (lanes.py:1403), `lanes.py port [<path>]` prints it (lanes.py:1981), and `fanout.py run` exports it as `SDLC_LANE_PORT` to the headless driver and gates (fanout.py:1419). Sub-agent briefs from `prepare` and `solo_run.py` carry no port line, so a sub-agent lane never learns its port.
- T-0682 also edits the solo brief lines in `solo_run.py`; land it first to avoid a conflict on the same lines.

## Constraints
A brief for a tree with no lane port is unchanged byte for byte.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new case, and the case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0 with the new case, and the case fails with the change reverted.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.
