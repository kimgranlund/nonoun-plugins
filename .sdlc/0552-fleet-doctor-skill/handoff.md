---
id: T-0552
title: "fleet-doctor skill: diagnose slow or stuck runs and offer resolutions"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:fleet-doctor` tells the person why runs are slow or stuck, with evidence, and offers ranked resolutions it carries out only on a yes. The name avoids Claude Code's built-in `/doctor`.

## Intent
- Do: `scripts/fleet_doctor.py collect` writes one JSON snapshot with no model call: load average and core count, the top CPU processes, each live lane and role (age, newest transcript write, child process tree), and per-role durations from `runs.jsonl` in the records dirs.
- Do: `fleet_doctor.py detect` applies fixed rules and prints one finding per hit with its evidence: `stdin-wait` (a role child such as `cat` or `read` idle on stdin for more than 5 min), `stalled` (no transcript write and no child-process change for more than 20 min), `slow-check` (`check.sh` running longer than 2 times its recorded median), `overloaded` (load above 1.5 times the cores), `runaway-proc` (a long-lived system process above 80% CPU), `heavy-peer` (another repo's lane running browser or test work), `replan-cost` (planning above 40% of a ticket's time).
- Do: skill `skills/fleet-doctor/SKILL.md`: render the findings, map each rule to fixed resolutions with cost and risk (kill one named pid; restart a process only from a list of daemons the OS respawns, e.g. `fontd`; a one-line throttle message to a busy conductor; file or link a ticket), ask once with AskUserQuestion of at most 4 items, recommendation first, then act only on approval. It never kills by name except for listed daemons, and never stops a role, lane, or another repo's process without a yes. Headless: list findings, act on nothing.
- Non-goals: replacing `/fleet-status` (what is moving) or `/fleet-retro` (what went wrong over a window); any automatic action.
- Done when: `fleet_doctor.py selftest` has a positive case and an observed negative control per rule; the skill passes packaging and skill checks; one live run on a machine with a planted stdin-wait reports it and kills only that pid on approval.

## Context
Maintainer request 2026-10-14, after a manual diagnosis in the maintainer session: the T-0543 step 2 builder hung 39 min on `cat > /tmp/x` (T-0548); `check.sh` took 47 min against an 18 min norm with load average 54 on 20 cores; `fontd` at 101% CPU for 26 days; maison Playwright lanes were the heavy peer. The fixes applied by hand: kill the one pid, `killall fontd`, a one-line throttle message to the maison, agent-ui and gen-ui-kit conductors, tickets T-0548 and T-0551. Name `fleet-doctor` (joins `/fleet-status` and `/fleet-retro`), so it does not collide with Claude Code's built-in `/doctor` (user decision).

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fleet_doctor.py selftest` exits 0: for each of the 7 rules a positive fixture fires exactly that rule and a negative-control fixture just short of it is observed silent; collect over stubbed ps, lsof and runs records; resolve refuses a pid in no finding, a reused pid, a name outside `DAEMONS`, and a daemon with no finding.
2. `test "$(python3 plugins/sdlc-lite/scripts/fleet_doctor.py selftest | grep -c 'negative control: silent')" -eq 7` exits 0.
3. `bash .sdlc/0552-fleet-doctor-skill/live-probe.sh` exits 0: on the live machine a planted idle `cat` under the session is reported as `stdin-wait` with its pid, resolve refuses the sibling writer pid, and resolve kills the reader while the writer survives. The approval step itself needs a person and is not exercised headless.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 with `skills/fleet-doctor/SKILL.md` present.
5. `python3 scripts/check-packaging.py` exits 0.
6. `python3 plugins/sdlc-lite/scripts/prompt_lint.py` exits 0.
7. `test -z "$(git diff --name-only HEAD -- . ':(exclude).sdlc')"` exits 0: no tracked file outside `.sdlc` changes (new files only).
8. `python3 -c "import sys; sys.exit(any(chr(0x2014) in open(p).read() for p in sys.argv[1:]))" plugins/sdlc-lite/scripts/fleet_doctor.py plugins/sdlc-lite/skills/fleet-doctor/SKILL.md` exits 0: no em dash in the new files.

## Constraints
The failing selftests land before or with the rules. Ships in 0.23.0 (maintainer, 2026-10-14). New files only (script, skill), so it runs beside wave 71.
