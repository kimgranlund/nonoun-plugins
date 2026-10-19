---
id: T-0557
title: "check.sh runs selftests in parallel and offers a fast tier"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`check.sh` finishes much faster: selftests run in parallel, and a fast tier covers the common gate in a few minutes.

## Intent
- Do: run independent selftests concurrently (bounded by cores and the T-0556 slot when present), keeping output per selftest and the first failure's name; add `check.sh --fast` for the structural and quick selftests, used by builders (T-0551) and the CI workflow (T-0554); full `check.sh` stays the land gate.
- Non-goals: dropping any selftest from the full run.
- Done when: full `check.sh` wall time drops measurably on an idle machine (record before and after); `--fast` runs in under 5 minutes; a planted failing selftest still fails both tiers (negative control).

## Context
2026-10-14: `check.sh` took 18 min idle and 47 min under load, and runs in every builder, verifier, and gate.
2026-10-14 (solo, 20 cores, machine not idle): before, sequential full run 1843s, exit 0 (load 27 to 15); after, parallel full run 440s, exit 0, 54 jobs (load 37 to 29); `--fast` 99s, 45 jobs. Negative control: a planted failing `budget.py selftest` (fast) and `gate_lock.py selftest` (full only) gave `--fast` exit 1 naming budget and full exit 1 naming gate_lock first; the plants were reverted.

## Constraints
Ships in 0.23.0 (maintainer, 2026-10-14). The failing selftest lands before or with the change.

## Acceptance criteria
- The pool runs jobs concurrently, honors the job bound, and a planted failing job fails the run with its name first and its output kept: `python3 plugins/sdlc-lite/scripts/check_pool.py selftest`
- The full tier passes, every earlier check still queued: `bash plugins/sdlc-lite/scripts/check.sh`
- The fast tier passes in under 5 minutes: `python3 -c "import subprocess, sys, time; t = time.time(); rc = subprocess.run(['bash', 'plugins/sdlc-lite/scripts/check.sh', '--fast']).returncode; print('fast tier %.0fs' % (time.time() - t)); sys.exit(rc or time.time() - t >= 300)"`
- An unknown flag is refused: `! bash plugins/sdlc-lite/scripts/check.sh --bogus`
- Packaging and whitespace stay clean: `python3 scripts/check-packaging.py` and `git diff --check`

## Outcome

2026-10-14 · lane: full L3 · verdict: pass · verifier: verifier-L2 (sonnet) · base: none
- Changed: see commits
- Commits: none
- Check: 1 pool selftest: pass
- Check: 2 full tier passes, every earlier check still queued: pass
- Check: 3 fast tier under 5 minutes: pass
- Check: 4 unknown flag refused: pass
- Check: 5 packaging and whitespace clean: pass
- Follow-up: decide: The planted-failure copy lacked repo context docs and .claude, so... -> notes.md
