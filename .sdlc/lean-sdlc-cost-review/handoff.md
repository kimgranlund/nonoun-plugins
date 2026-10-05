## Goal
Independent review of docs/lean-sdlc/cost-control.md v0.1 (branch cost-control, this worktree): say whether it is ready to file four build tickets from, and list every blocker.

## Intent
- Do: read docs/lean-sdlc/cost-control.md and docs/lean-sdlc/design.md (build order, rows L1 to L16), then check every factual claim against the repository with path:line evidence. Specifically verify: (1) the "What already exists" list (steps.py lint, split --only guard timeout, review stopping after two replan verdicts, board.py cost sum, run.sh and run_lifecycle.py attempt records); (2) that item A's gap is real and its design is implementable (a `(red)` tag, a throwaway worktree under SDLC_TMP_WORKTREES, run.sh plan-reviewer pre-launch refusal) without breaking steps.py lint rules or the guard rules; (3) that item B's hash and stale-input handling fit run_lifecycle.py, steps.py next, resume and review, and that the PreToolUse hook design matches how existing hooks in plugins/sdlc-lite/hooks work; (4) item C against T-0200 (delta format) and T-0202, and that no model or effort default changes; (5) item D against board.py, run.sh and tickets.py (budget_usd must not be validated by tickets.py); (6) the one-writer-per-file ordering against the open tickets in .sdlc/ (T-0183 to T-0187 on branches or main, T-0194 to T-0208) and any file two items or tickets would both edit; (7) the cost and replan numbers: recompute from every runs.jsonl under the repo and .worktrees (dedupe by attempt_id, ts on 2026-10-04) and from the plan-reviewer-*.md findings under .worktrees/*/.sdlc/ and say whether the table, the 4 of 7 replans, the 3 of 10 mechanical findings and the targets are supported or overstated. Also look for anything missing that would make the process cheaper and that the addendum does not cover.
- Non-goals: editing any file other than your own result; building anything.
- Done when: your result lists a verdict (ready, ready after fixes, not ready), numbered findings each with severity (blocker, major, minor) and evidence as path:line, and per-item (A to D) whether it is plannable at the level the addendum states.

## Context
The author is a different model family from you (Sonnet). The addendum was written from this week's run records; the user decided to keep all model and effort defaults unchanged. Relevant records: docs/reports/lean-sdlc-design-review-2.md.

## Constraints
Read-only. No em dashes. Concrete evidence only; do not soften.
