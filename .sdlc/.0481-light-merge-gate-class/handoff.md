---
id: T-0481
title: "fanout.py land: light gate class from light_scope globs, --light-gate, and cover with gate-ledger.jsonl (T-0480)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py land` runs a light gate set for a lane whose merged paths all match declared `light_scope` globs, and `fanout.py cover` runs the full set at the integration tip, appends a ledger entry, and gates the fast-forward.

## Intent
- Do: In `fanout.py`: a merge-time gate class `light` or `full`, computed in `merge_gate_close` from `.sdlc/config` lines `merge_gate: light` and `light_scope: <glob>...` (same `:(glob)` matching as `declared_hits`); a repeatable `--light-gate CMD` threaded through `run`, `land_preflight`, `roll` and `land_command`; `cover <integration> --gate CMD...` appending `<root>/gate-ledger.jsonl` (`{at, run_id, integration, from, to, gates, rc, merges, log}`, committed with `git add -f` in the integration tree) and printing the bisect line on red; `settle --require-covered`; the fanout skill (`plugins/sdlc-lite/skills/fanout/SKILL.md:49`) runs settle with that flag when the config declares light; the class appears in the land journal and the ticket `## Closed` note. `roll` ignores the light class and always runs `--gate`.
- Non-goals: Any change to `steps.py lane`; the light-gate commands, the globs and the cadence schedule (project side); the `board.py` view (its own ticket); loosening any repo's full-gate-before-ff rule.
- Done when: a `fanout.py selftest` case with config `merge_gate: light`, `light_scope: src/components/** src/registry.ts`, a lane touching only `src/components/x/a.txt` and `src/registry.ts`, `--gate false --light-gate true` ends `merged` with `gate: light` in the land journal; observed red first (today the flag is refused, exit 2). Negative controls in the same case: the lane also touching `README.md` stays `red: false rc=1`; the same config without the `merge_gate: light` line stays `red: false rc=1`; `--light-gate` without the declaration exits 2; `cover` appends one entry whose `merges` names the ticket; `settle --require-covered` refuses before `cover` and passes after. `fanout.py selftest` and `check.py` exit 0.

## Context
Design and risks: `docs/planning/light-merge-lane.md` (Approach and Risks). A repo adopts the class only with its owner's written approval. Risks to cover: glob matcher looser than git's; a missed `--light-gate` in the printed land line (`land_command`, `fanout.py:1723-1737`); the ledger written in the integration tree, not the primary checkout.

## Constraints
A merge is never ungated: a light class with no `--light-gate` runs the full set, and the vacuous-gate refusal at `fanout.py:1461` stays. No prompt wording change. One writer on `fanout.py` at a time.

## Closed

2026-10-12: warnings acknowledged: criterion 9 negative control ran from a cp -R copy because block-stray-worktree.sh denied git worktree add (SDLC_TMP_WORKTREES unset); builder and verifier both observed the red; verifier passed all 12 criteria

> - None of the planned steps failed. The verifier passed step 1 (L2 verifier, all 12 criteria), and no `process-deviations.md` exists.
> - The criterion-9 negative control did not run in a `git worktree add --detach` copy as the plan says. `block-stray-worktree.sh` denied the add because `SDLC_TMP_WORKTREES` is unset, so the builder and the verifier each ran it from a `cp -R` copy of `plugins/sdlc-lite`. In both runs `gate_class` forced to full made `fanout.py selftest` exit 1, with 5 `T-0481` labels under `these did not hold:`.
