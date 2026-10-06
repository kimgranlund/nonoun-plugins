---
id: T-0311
title: "fleet_status.py: liveness join, load trend and snapshot"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0305, T-0310]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Collector additions that decide whether each board row is really moving, plus the load trend and a snapshot for the since-last section.

## Intent
- Do: Extend scripts/fleet_collect.py or add scripts/fleet_status.py `collect` with: liveness per ticket row (a live process whose command names the ticket folder or its worktree, a `.running` marker with a live pid, or activity in the last N minutes by file mtime of runs.jsonl and logs; marks `live`, `idle`, `dead` for a marker with no process, `stale` for a board row with none of these); load samples appended to .sdlc/runtime/load.jsonl on every call with a trend (1, 5 and 15 minute loads, direction arrow, cores, verdict against a configurable stop line, default 14), top consumers by class (chromium, hooks, claude, watchers); needs-you extraction from tickets with status blocked and an `owner` found in their notes (user or conductor) and from open PRs waiting on a merge via gh; release state (local main vs origin/main, last tag, unpushed commits); a snapshot file .sdlc/runtime/fleet-status.json and a `delta` since the previous snapshot (rows that changed state, tickets closed, PRs merged).
- Non-goals: Rendering; conductor messaging.
- Done when:
  - Fixture repo: a board row with a live process is `live`; a row with a `.running` marker whose pid is dead is `dead`; a row with no process, marker or recent activity is `stale` (three observed cases, plus the negative control that removing the marker changes `dead` to `stale`).
  - Load: two samples a minute apart give a trend; a load above the stop line gives the `over` verdict.
  - Run on /Users/kimgranlund/Projects/maison/ui-kit-maison flags T-0039, T-0043 and T-0105 as not `live` if no process or recent activity exists for them (compare with the conductor's own audit) and writes no file in that repo.
  - Snapshot delta lists a ticket that closed between two runs.
  - `check.py` and `tickets.py check` pass.

## Context
Decided by the user on 2026-10-06. Replaces the hand-built status the author session produced about 20 times (a bash loop, grep filters and a composed table). Problems to fix: rows that lie (board says building for work that never started, or verifier fail for merged work), load with no trend or verdict, 'needs you' buried, no since-last delta, hard-coded repo list. Order of the output: Machine, Needs you, Moving (with a liveness mark), Stale or stuck, Done since last report, Release state. sdlc-lite must own the rendering and not depend on the user-scoped harness rag-board skill. Reuses fleet_collect.py (T-0305) for process classes and run totals. Builds after fleet-retro (T-0305 to T-0308); target 0.21.1.

## Constraints
No model call. Read-only on every repo inspected. No em dashes. No change to any model or effort value. No push, tag or publish.

## Acceptance criteria
Run from the repository root. The ui-kit-maison checks read that repo as it is on the day: T-0039 and T-0043 are closed tickets there whose board rows still show built work, and T-0105 has no process or recent run record; a process that later names T-0105's folder makes the third `not live` line fail for a good reason. `collect` there writes its state under a throwaway `--state-dir`, never into the repo.
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_status.py selftest) && printf '%s\n' "$out" | grep -qx 'fleet_status selftest: ok'`
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_status.py selftest) && for n in 'live: a process naming the ticket folder' 'dead: a marker whose pid is gone' 'stale: a board row with no process, marker or activity' 'negative control: removing the marker changes dead to stale' 'load: two samples a minute apart give a rising trend' 'load: above the stop line is over' 'negative control: the same load under a higher stop line is not over' 'delta: a ticket closed between two runs is listed once as closed, by id' 'read-only: collect changes no file under the inspected repo'; do printf '%s\n' "$out" | grep -qxF "ok: $n" || exit 1; done`
- `d=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/fleet_status.py collect /Users/kimgranlund/Projects/maison/ui-kit-maison --no-gh --state-dir "$d" 2>/dev/null | python3 -c "import json,sys; rows={r['id']: r for r in json.load(sys.stdin)['repos'][0]['rows']}; sys.exit(0 if all(i in rows and rows[i]['state'] != 'live' for i in ('T-0039','T-0043','T-0105')) else 1)"`
- `d=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/fleet_status.py collect /Users/kimgranlund/Projects/maison/ui-kit-maison --no-gh --state-dir "$d" 2>/dev/null | python3 -c "import json,sys; rows={r['id']: r for r in json.load(sys.stdin)['repos'][0]['rows']}; sys.exit(0 if all(rows[i]['state'] == 'stale' and 'ticket-done-board-open' in rows[i]['flags'] for i in ('T-0039','T-0043')) else 1)"`
- `a=$(git -C /Users/kimgranlund/Projects/maison/ui-kit-maison status --short) && python3 plugins/sdlc-lite/scripts/fleet_status.py collect /Users/kimgranlund/Projects/maison/ui-kit-maison --no-gh --state-dir "$(mktemp -d)" >/dev/null 2>&1 && b=$(git -C /Users/kimgranlund/Projects/maison/ui-kit-maison status --short) && test "$a" = "$b" && test ! -e /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/runtime/load.jsonl && test ! -e /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/runtime/fleet-status.json`
- `d=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/fleet_status.py collect . --no-gh --state-dir "$d" 2>/dev/null | python3 -c "import json,sys; x=json.load(sys.stdin); l=x['machine']['load']; sys.exit(0 if all(k in x for k in ('time','machine','repos','needs_you','delta','snapshot')) and all(k in l for k in ('load1','load5','load15','cpus','arrow','verdict','stop_line')) and all(k in x['machine']['consumers'] for k in ('chromium','hooks','claude','watchers')) and 'release' in x['repos'][0] else 1)" && test -s "$d/load.jsonl" && test -s "$d/fleet-status.json"`
- `grep -qF 'fleet_status.py" selftest' plugins/sdlc-lite/scripts/check.sh && grep -q 'scripts/fleet_status.py' docs/maintenance/sdlc-internals.md`
- `! grep -n "$(printf '\xe2\x80\x94')" plugins/sdlc-lite/scripts/fleet_status.py docs/maintenance/sdlc-internals.md .sdlc/0311-fleet-liveness/handoff.md`
- `git diff --check`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
