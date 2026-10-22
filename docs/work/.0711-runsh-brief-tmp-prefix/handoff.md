---
id: T-0711
title: "run.sh prompts name the literal throwaway prefix"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role launched by `run.sh` (Claude or Codex backend) gets a prompt line naming its throwaway prefix as a literal path, the same way a `dispatch.py prepare` brief does.

## Intent
- Do: in `plugins/sdlc-lite/scripts/run.sh`, add to both prompt strings (Claude about line 477, Codex about line 483) one line: `Throwaway worktrees only under <wt_tmp> (git worktree add --detach "<wt_tmp>/<name>" HEAD); write that path literally.` `wt_tmp` is set at about line 565, after the prompt is built: compute it before the prompt (or build the prompt after it) without changing its value. Keep `SDLC_TMP_WORKTREES` exported as now. Update any run.sh selftest or dry-run check that pins the prompt text.
- Non-goals: dispatch.py briefs, hooks, role definitions.
- Done when: the criteria pass.

## Context
T-0709 (landed) makes the role definitions say "the throwaway prefix your brief names". T-0709 verifier-L2:
- decide: plugins/sdlc-lite/scripts/run.sh:710 passes the prefix to a run.sh-launched role only as the `SDLC_TMP_WORKTREES` env var; the run.sh prompt has no throwaway-prefix line. A role launched that way with a brief that names no prefix has to infer from the parenthetical that the variable's value is its prefix.

## Acceptance criteria
1. `SDLC_DRY_RUN=1 bash plugins/sdlc-lite/scripts/run.sh builder L1 <a throwaway handoff>` (or the existing run.sh dry-run selftest) prints a prompt containing `Throwaway worktrees only under ` followed by the same path run.sh exports as `SDLC_TMP_WORKTREES`; same for `SDLC_BACKEND=codex`.
2. The run.sh selftest that `plugins/sdlc-lite/scripts/check.sh` runs for run.sh passes (name the command in the Outcome); `python3 plugins/sdlc-lite/scripts/check.py` exits 0; `python3 scripts/check-packaging.py` passes; `git diff --check <base sha>` exits 0.

## Outcome
- `plugins/sdlc-lite/scripts/run.sh`: the `toplevel`..`wt_tmp` block moved above the prompt (value unchanged); both the Claude and the Codex prompt gain `Throwaway worktrees only under <wt_tmp> (git worktree add --detach "<wt_tmp>/<name>" HEAD); write that path literally.`; header comment notes it; `SDLC_TMP_WORKTREES` export unchanged.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: dry-run cases for both backends (line text plus the sibling `.worktrees/tmp/builder-` prefix), and the real-run stub records its prompt and `want_wt` asserts the prompt line names exactly the `SDLC_TMP_WORKTREES` value the stub saw.
- Criterion 1: dry run with role `scout` (a builder dry run is refused by the lane guard on this L1 ticket) printed the line for `SDLC_BACKEND=claude` and `codex`.
- Criterion 2: `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- bash plugins/sdlc-lite/scripts/run-selftest.sh` PASS (the run.sh selftest check.sh runs as `run-selftest`); `dispatch.py selftest` PASS; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check 9b1c7a3b` exit 0.

## Outcome

2026-10-21 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 9b1c7a3bf299
- Changed: see commits
- Commits: 2cca66e T-0711: run.sh prompts name the literal throwaway prefix
- Check: 1 run.sh dry run prints a prompt with `Throwaway worktrees only under ` followed by the path export...: pass
- Check: 2 run.sh selftest passes; check.py exits 0; check-packaging.py passes; `git diff --check <base sha>...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/run.sh:43 the new header comment sentence... -> notes.md
- Follow-up: note: redck.py deviations printed no process-deviation lines; the... -> notes.md
