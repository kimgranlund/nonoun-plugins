---
id: T-0654
title: "fanout.py sync brings a lane up to date with the integration branch"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A running lane can be brought level with its integration branch in one command: `fanout.py sync <lane>` merges the integration branch in, resolves generated and hash-bound files without a hand merge, runs light gates, and names only the real conflicts. A guidance-only form carries new repo skills and AGENTS.md to running lanes.

## Intent
- Do: (1) Add `cmd_sync` to `plugins/sdlc-lite/scripts/fanout.py`: `sync <lane branch or tree> [--integration BRANCH] [--gate CMD]... [--regen CMD] [--paths P,...]`. It finds the lane worktree in `git worktree list --porcelain` (as `cmd_settle` does), takes the integration branch from --integration or the lane's `.lane.json` `into`, and under `<lanes dir>/merge.lock` runs `merge_generated` (sdlc generated files) in the lane tree. A conflict only in paths matching `tickets.hash_bound_globs` takes the integration side and then runs `--regen CMD` when given and stages its output; any other conflict aborts the merge, exits 2 and prints `sync conflict: <paths>` (the conductor hands those to an L2 builder). With the merge committed as `sync: <integration> <sha7> into <lane branch>`, each `--gate` runs in the lane tree; red exits 1 with the merge kept. (2) `--paths .agents/,AGENTS.md,.claude/` does a guidance-only sync: `git checkout <integration> -- <paths>` in the lane tree and one commit `sync guidance: <integration> <sha7>`, no full merge; an uncommitted change under those paths refuses (exit 2). (3) Usage text, the module docstring, `skills/fanout/SKILL.md` (one line: after landing a ticket that touches `.agents/`, `AGENTS.md` or `.claude/`, run `sync --paths` on each running lane), and a selftest.
- Non-goals: `land` calling `sync` first (a separate ticket if wanted). No change to the pre-ticket `git merge --ff` sync inside `run`, to `settle --forward`, or to `merge_generated` itself.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #14, ui-kit-neue audit 2026-10-20.
- Evidence: 59 merge or land relays by the conductor (T-0043 and T-0032 needed 3 rounds each); 7 plan steps did nothing but merge ($5.02). Conflict hotspots were generated or hub files (`packages/core/src/index.ts` 41, `packages/geometry/fixtures/extension.json` 31). A repo skill that landed on the integration branch at 13:46Z reached a running kit lane only at 15:42Z, through a builder that merged the integration branch itself.
- In this repo: `merge_generated` at `plugins/sdlc-lite/scripts/fanout.py:1580` already merges with `--no-commit`, resolves `notes.md` by union and the roadmap, router and mailbox files by `--ours`, and regenerates them with `tickets.py roadmap`; `generated_files` is at `fanout.py:1569`. `settle_forward` (`fanout.py:2682`) is the closest existing caller: merge under the merge lock, commit, gate. The pre-ticket `git merge --ff --no-edit <integration>` of `run` is at `fanout.py:1415` and is not reused by sub-agent lanes.
- `hash_bound:` globs are read by `tickets.hash_bound_globs` (`plugins/sdlc-lite/scripts/tickets.py:707`, regex at `tickets.py:405`). Today they only pick the merge class (`fanout.py:86`, `fanout.py:2564`); no command regenerates them, so `--regen CMD` is the caller's regeneration command.
- `cmd_settle` worktree lookup pattern: `fanout.py:2662` to `fanout.py:2666`. Subcommand parsers start at `fanout.py:5386`; usage string at `fanout.py:5360`.
- Lane records: `lanes.py` `lane_of` (`plugins/sdlc-lite/scripts/lanes.py:433`) reads `.lane.json` and its `into`.

## Constraints
`run`, `land`, `roll`, `settle` and `cover` behavior is unchanged. `sync` never pushes and never touches main. A merge `sync` cannot finish is aborted, leaving the lane tree as it was.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with new cases on a throwaway repo: (a) a lane behind its integration branch, with the roadmap changed on both sides and a `hash_bound: gen/*` file changed on both sides, `sync <lane> --regen 'echo regen > gen/out.txt' --gate true` exits 0, the lane tip is a merge commit whose second parent is the integration tip, and `gen/out.txt` holds `regen`; (b) a conflict in a non-generated, non-hash-bound file exits 2, prints `sync conflict:` naming it, and leaves the lane tip and tree unchanged; (c) `sync <lane> --paths .agents/` copies a skill file added on the integration branch into the lane as one commit and touches no other path. Case (a) fails with the hash-bound resolution removed (observed negative control, recorded in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/fanout.py sync --help` exits 0 and names `--paths`, `--regen` and `--gate`.
3. `grep -n 'sync --paths' plugins/sdlc-lite/skills/fanout/SKILL.md` finds the post-land line.
4. `git diff --check` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Outcome
- `fanout.py sync <lane> [--integration BRANCH] [--root] [--lanes-dir] [--gate CMD]... [--regen CMD] [--paths P,...]` added (`cmd_sync`), with the module docstring usage line and a `sync (T-0654)` section, the `USAGE` string, and the `main()` parser. The integration branch comes from `--integration` or the lane record's `into` (lanes.discover, so host records work too).
- Deviation from the Non-goal "no change to merge_generated": it returns `conflict` before it resolves the generated files, so hash-bound resolution could not be layered on top without copying its notes.md and roadmap logic. It gained an optional `theirs=()` pathspec argument (conflicts it matches take ref's side); every existing caller passes nothing and behaves as before.
- `--regen` runs only when the merge staged a hash-bound path; its output under the `hash_bound:` globs is staged into the merge commit.
- `skills/fanout/SKILL.md`: the post-land `sync --paths .agents/,AGENTS.md,.claude/ <lane>` line in step 4, and Arguments rows for `--paths` and `--regen` (check.py H-5).
- Selftest: T-0654 cases (a) merge with roadmap and `gen/out.txt` changed on both sides, (b) README.md conflict exits 2 with the lane unchanged, (c) `--paths .agents/` one commit touching only the skill file, plus an uncommitted-file refusal for `--paths`.
- Negative control (observed): with `cmd_sync` calling `merge_generated(wt, sha, root)` (no hash-bound resolution) the selftest failed: `T-0654 sync: exit 0, ... got rc=2 out='sync conflict: gen/out.txt\n'`. Restored, it passes.
- Checks: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0; `python3 plugins/sdlc-lite/scripts/fanout.py sync --help` exit 0 (names --paths, --regen, --gate); `grep -n 'sync --paths' plugins/sdlc-lite/skills/fanout/SKILL.md` exit 0; `git diff --check` exit 0; `python3 scripts/check-packaging.py` exit 0.
- Open: `check.py` on this lane's base still reports H-5 for `--force` and `--forward`; main fixed that in 28ba049c (Arguments rows), so it clears when the lane lands. No other check.py finding.
