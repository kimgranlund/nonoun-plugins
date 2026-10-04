# Lean SDLC design review, second round

Recorded: 2026-10-04. Independent review of `docs/lean-sdlc/design.md` v0.3 (commit cafef90 on branch `lean-sdlc`), tickets T-0189 to T-0192. The reviewer was the `architect` role, `run.sh architect L1`, model `fable` effort high (from `runs.jsonl`), a different family from the author (Claude Sonnet). It was read-only in the repository except for its own result and `decompose/` output. Raw result: `.sdlc/lean-sdlc-review-2/architect-L1.md`; its 17-leaf decomposition is in `.sdlc/lean-sdlc-review-2/decompose/`. First round: [lean-sdlc-design-review.md](lean-sdlc-design-review.md).

## Verdict

Ready after fixes. Of the twelve first-round findings, nine are resolved and three are partly resolved (1, 2, 5; the build order in 8 also still overlapped). No new user decision is needed. The author applied every finding in v0.4; the applied text was not re-reviewed.

## Findings and what v0.4 did

| # | Severity | Finding | v0.4 |
| --- | --- | --- | --- |
| 1 | major | Delta covers `split` and `resolve` only; `find_plan` (`steps.py:236-243`), `cmd_lint` (`913-916`), and `review_action` (`1223-1226`) read the newest planner file alone, so `lint`, `review`, and `lane` miss a base | C1 makes `find_plan` return a merged plan for a directory target, used by every reader |
| 2 | major | A normal replan is `planner-L3.md`, not a `-k` file (`run.sh:187-192`, `steps.py:1263`); `split` without `--only` refuses when step dirs hold results (`863-889`) | `revises:` crosses levels; delta target holds for an L3 delta; replan split is `--only` after the supersede rename |
| 3 | major | Batched verification has no step-state mechanics: `next`, `resume`, `board.py`, and `order.py` read `step-<n>/` and per-dir `runs.jsonl` | New row S: a task-dir verifier result lists the builder results it verified; decision 1 now reads "after rows V and S"; defer batching if S grows |
| 4 | major | File ownership overlaps; the `skips.md` guard cannot live in `check.py` (plugin contracts); section 4 Parallelize had no build row; the guard must exempt pre-feature tickets | Guard moved to `tickets.py check` and `close` with an exemption; `fanout-overlap` row added; build order re-cut (sixteen rows) |
| 5 | major | `layout: topics` implying `ticket_root: tickets` breaks cross-tree id resolution (`tickets.py:375-420`, `board.py:213`, `traces`) | `ticket_root` stays explicit; `migrate-layout` writes both lines; `layout` governs roadmap, notes, `work/`, strays |
| 6 | major | An onboard template bump marks every existing block `stale` (`onboard.py:219, 581-582, 684`), contradicting "existing repos untouched" | Block rendered from resolved paths; a flat repo's text and version are unchanged |
| 7 | minor | Path residue: `traces/sources/tickets.py:28`, router template (`tickets.py:894`), `messages/AGENTS.md` regeneration, a cite scan for the two file moves, five dated records not to be rewritten | Named in the change table and migration step 3 |
| 8 | minor | `lane` facts: front matter has size only; `review_action` inlines its reasons; B should precede A1 | `review_required()` extracted; scope allow-list after planning; B is L2 before `lane` L5 |
| 9 | minor | A swap or widen appends `## Plan review` and flips the lane | Footprint fixture includes one swap |
| 10 | minor | Validation rows: no check builds "extra files fail"; the steps.py routing row is true only after planning; row V's control is buildable | `footprint.py check --max-files` in L1; rows corrected; row V control stated against the pre-fix output |
| 11 | minor | The reviewer read rule should follow `revises:` transitively; the `plan: 2` line is unnecessary | Reviewer reads `steps.py resolve`; no version line |

## Limits

- Read against `plugins/` identical to main (`a7c5685`). Nothing was built or run beyond the reviewer's own probes.
- Lean thresholds and footprint targets are unmeasured until `footprint.py` exists (L1).
- The author's v0.4 edits were not re-reviewed; the build tickets are filed as `proposed`, so each plan goes through plan review before any build.
