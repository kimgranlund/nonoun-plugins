---
id: T-0065
title: "fanout.py's default lane driver does not set SDLC_ROLE, so..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0058
---

## Goal
Every fanout lane driver (the default headless conductor and any `--driver CMD`) runs with `SDLC_ROLE` set, so `hooks/block-publish.sh` blocks `git push`, `gh` writes, and package publishing inside a lane, not only the prompt. Done when the lane env sets it, the fanout selftest proves a stub driver sees it, and no doc still says only `scripts/run.sh` sets `SDLC_ROLE`.

## Context
Follow-up from T-0058 (fanout-command/filer-L1.md):

fanout.py's default lane driver does not set `SDLC_ROLE`, so `hooks/block-publish.sh` does not guard lane conductors against `git push` or `gh` writes. Only the prompt forbids them. Set `SDLC_ROLE` for lane drivers.

## Constraints
- Set it in the shared lane env in `scripts/fanout.py` `run_ticket` (next to `SDLC_HEADLESS='1'`), value `conductor` (the lane driver is a conductor session; the hook message names it). run.sh still overrides it per role run.
- block-publish.sh does not block `git commit` or `git merge`; the lane commit and merge are made by fanout.py itself, outside the driver, so they are unaffected. Do not change the hook.
- Stale-record repair in the same change: `agents/conductor.md` ("only `scripts/run.sh` sets it"), repo-root `CLAUDE.md` (block-publish and fanout bullets), `.claude/agents/sdlc-lite-author.md` if it repeats the claim, the `scripts/fanout.py` docstring/`--driver` help that lists the driver env, and `skills/fanout/SKILL.md` if it lists that env. `skills/file/SKILL.md` wording about the user's own session stays true.
- `scripts/check.sh` must stay green. No em dashes.

## Scouted locations
- `plugins/sdlc-lite/scripts/fanout.py`: lane env built in `run_ticket` (~line 382); docstring listing driver env ~line 36; `default_driver` ~line 107; selftest stub driver asserts `SDLC_HEADLESS` ~line 504.
- `plugins/sdlc-lite/hooks/block-publish.sh`: exits 0 unless `SDLC_ROLE` is set.
- `plugins/sdlc-lite/agents/conductor.md` line 24.

## Plan review
- 2026-09-25, planner-L1.md, `steps.py split` refused: step 1: acceptance criterion command does not parse: ! grep -n 'only (a backtick inside the inline code span split the command; unexpected EOF looking for matching quote). plan defect: replan this step (/chain 3). Also: the Risks line says a custom `--driver` that pushes will be blocked; it will not, since block-publish.sh is a Claude PreToolUse hook and only guards Claude sessions the driver launches.
