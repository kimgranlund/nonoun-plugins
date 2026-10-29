---
id: T-0812
title: "Decide diff-scope verifier: drop the revert step or turn it off by default"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
claimed_by: sdlc-lite-author 2026-10-29
branch: lane/T-0812-t0812
worktree: ../sdlc-lite.worktrees/T-0812-t0812
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Decide, from measurement, whether the T-0799 `Scope: diff` verifier stays the default, and act on it: drop its revert step (3) when the Outcome carries red/green evidence, or turn diff scope off by default.

## Context
- Speed experiment: diff $1.4041 vs full $1.4098 (`docs/reports/2026-10-28-speed-experiment.md`).
- Overnight MacBook run: 17 diff verifiers mean $0.498 and median 9.5 min vs 23 full L2 mean $0.479 and median 8.2 min; different tickets and hours, not controlled (`docs/reports/2026-10-29-sdlc-retro-macbook-pro/ultimate-tokens-color-science-attempts.jsonl`; `docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Finding 8).
- T-0248: a diff verifier passed a change that broke an untouched test; the land gate caught it (`docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Finding 9).
- `SCOPE_DIFF` in `plugins/sdlc-lite/scripts/dispatch.py`.

## Constraints
- Measure first on this repo's own `runs.jsonl` (diff vs full verifier cost and wall on comparable L2 tickets) and state the numbers in the Outcome.
- Smallest change that the numbers support; keep the `escalate: full` route.
- outcome metric: mean verifier cost and median wall, diff vs full, before: $0.498 / 9.5 min vs $0.479 / 8.2 min.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, including the T-0812 cases (no `verifier_scope: diff` line: no Scope: diff; a commented line does not opt in) and the T-0799 cases under the opt-in line.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
- `git diff --check` exits 0.

## Outcome
Decision: turn diff scope off by default; a repo opts in with an uncommented `verifier_scope: diff` line in `.sdlc/config` (`dispatch.verifier_scope_diff`). The `escalate: full` route (`ESCALATE_RE`, the escalate branch of `diff_scoped`) is unchanged and still applies under the opt-in.
Measured (verifier cost_usd and duration_ms from runs.jsonl):
- This repo, L2-level verifiers on L1/L2 tickets 0795 to 0809: diff n=2 (T-0805, T-0808, both sonnet) mean $0.847, median 21.1 min; full n=9 mean $0.716, median 11.4 min; sonnet-only full (0796, 0799, 0800, 0804) mean $0.802, median 19.9 min. n=2 cannot discriminate.
- MacBook overnight (ultimate-tokens attempts.jsonl, L2): diff n=16 mean $0.498, median 9.7 min (9.5 with the escalated 0286 row, which has no cost); full n=22 mean $0.479, median 8.2 min.
- Speed experiment (T-0801): diff $1.4041 vs full $1.4098 for five L1 tickets.
Step 3 (the revert) is real work, not dead text: both diff verifiers here reverted in a throwaway worktree (0805 by hand at base, 0808 at c3046bc9). Dropping it alone leaves a brief that measured no saving on any sample, so it was not the lever.
Catch rate is one sample each way: the diff verifier failed the T-0801 planted control (T-0803 has since made the full verifier fail a Goal-contradicting fix-now), and a diff verifier passed T-0248, which broke an untouched test the land gate caught. No measurable saving and no settled quality edge: the feature does not earn default status.
Red first: with the selftest change and no code change, `dispatch.py selftest` failed on exactly the two T-0812 cases.

## Outcome

2026-10-29 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 5d9eb00f334c
- Changed: see commits
- Commits: da3773e T-0812: diff-scoped verifier off by default, opt in with verifier_scope: diff; 7b84fd4 T-0812: record lane T-0812-t0812
- Check: 1 `dispatch.py selftest` exits 0 including the T-0812 cases and the T-0799 cases under the opt-in line: pass
- Check: 2 `check.py` exits 0: pass
- Check: 3 `claude_roles.py generate --check` exits 0: pass
- Check: 4 `codex_roles.py generate --check` exits 0: pass
- Check: 5 `git diff --check` exits 0: pass
- Follow-up: note: redck.py deviations printed no process deviation: line, and the... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/dispatch.py verifier_scope_diff resolves... -> notes.md
