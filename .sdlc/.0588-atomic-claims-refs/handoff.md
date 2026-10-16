---
id: T-0588
title: "Atomic ticket claims and ids through git refs"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Two hosts can never both claim one ticket or stamp one id. `tickets.py claim` creates `refs/sdlc/claims/T-NNNN`, and `new` reserves `refs/sdlc/ids/T-NNNN`, with `git update-ref <ref> <sha> ""` (create only if absent). The loser gets a refusal naming the holder. The front matter `status: claimed` and `claimed_by: <host>:<session> <date>` stay as the readable record.

## Context
Maintainer decision 2026-10-15: Claude Code, Codex and Pi work tickets in one repo at once. The design is in the conversation summary: claims and ids are atomic through git refs, which every worktree and host shares; lanes are locked with their owner; workers signal ready with a pinned sha; one conductor per repo writes main. Workers commit nothing (Codex workspace-write cannot write .git); the conductor commits. `tickets.py` has no lock today (0 `flock` calls); `cmd_claim` (around line 1764) edits front matter in whichever tree runs it, and `new` takes the max id across worktrees without reserving it.

## Intent
- Do:
  1. Claim: create the claim ref, pointing at a blob or commit holding `<host>:<session> <date>`, before writing front matter. Refuse when it exists, naming its content. `--handover` replaces it with the old value as the expected one. `release` and close delete it.
  2. New: reserve the id ref before writing; retry the next id on a collision.
  3. Host detection for `claimed_by`: an `SDLC_HOST` env var, else `claude` / `codex` from the existing role env, else `--by`.
  4. `tickets.py check` warns when front matter and refs disagree.
- Non-goals: remote refs or pushing them.
- Done when: the criteria pass.

## Constraints
Outside git, behavior is as today. Existing claimed tickets without a ref keep working (check warns and `claim --handover` repairs).

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new cases show: two claims of one ticket from two worktrees, where the second refuses naming the first holder; two concurrent `new` calls (two processes) that get distinct ids; release and close removing the ref; and `check` warning on a front matter claim with no ref. Each case failed before the change.
2. `bash plugins/sdlc-lite/scripts/run-selftest.sh` and `git diff --check` exit 0.

## Outcome

2026-10-15 · lane: full L3 · verdict: closed by reason (delivered by the solo agent (level L3); one independent batched verifier passed before the merge; gate: full; verifier notes: note: tickets.py `claim_by` orders `--by`, then `SDLC_HOST`, then host detection, the reverse of Intent item 3's literal order. It still meets the Goal: ref content and front matter both read `<holder> <date>`, auto-detection yields `claude:<session8>` or `codex:<thread>`, and existing selftests and the router keep `claimed_by: <agent> <date>`. Observed: `SDLC_HOST=pi claim T-0001` wrote `claimed_by: pi <date>`. | note: outside git (a temp dir with no repo) `new`, `claim`, a refused second claim, `check` and `release` behave as before and write no refs, so that Constraint holds. Existing claims without a ref are handled by the selftest cases: `check` warns and `claim --handover --reason` writes the ref. | note: tickets.py `cmd_new` leaves the `refs/sdlc/ids/<id>` reservation in place when a later step fails after the mkdir (only the mkdir failure rolls it back). The id is then simply burned, which is the safe direction. | note: docs/references/sdlc-internals.md:55 still describes `claim <id> --by <agent>` without the ref behavior. It is not wrong, only incomplete, so not filed as a defect.) · verifier: verifier-L2 (sonnet) · base: 54da3a91c1af
- Changed: see commits
- Commits: ed2e8f0 T-0588: Atomic ticket claims and ids through git refs; 5498cf0 T-0588: record lane T-0588-t0588
- Check: 1 tickets.py selftest exits 0 with new cases for two-worktree claim refusal, concurrent `new`, rele...: pass
- Check: 2 `bash plugins/sdlc-lite/scripts/run-selftest.sh` and `git diff --check` exit 0: pass
