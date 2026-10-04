## Goal
Review docs/lean-sdlc/design.md (v0.1, branch lean-sdlc) as an independent architect and say whether it is ready to build.

## Intent
- Do: check every factual claim against the repository (the baseline numbers in the Baseline table, the cited steps.py rule near line 103 and the plan-review conditions, run.sh verifier family enforcement, the ticket_root and board.py behavior, fanout.py lacking ticket_root, hooks naming no .sdlc paths, the 38-file count), and judge the design: does the lean lane preserve verifier independence and the plan-review invariants; can result files stay while plans shrink; is replan-by-delta compatible with steps.py split, order.py newest-result ordering and steps.py next; does migrate-layout break references, fanout worktree id uniqueness, traces, board, statusline, or Codex parity; are the build order, plan levels and negative controls sound and are any ticket too big; what is missing or contradicted by the code.
- Non-goals: editing any file other than your own result and decompose output; building anything.
- Done when: your result lists a verdict (ready, ready after fixes, or not ready), numbered findings each with severity (blocker, major, minor), evidence as path:line or command output, and the user decisions still needed.

## Context
The design answers feedback from another repo: planner/builder/verifier granularity excessive; .sdlc/ should always use topic sub-folders; too many planning docs, later steps should not repeat research and planning; the conductor should find the fastest path including batching reviews. Tickets T-0189 to T-0192 (.sdlc/0189-lean-chain through 0192-conductor-batching). The author is Claude Sonnet, so you must not share its family.

## Constraints
Read-only. No em dashes. Be concrete and do not soften.
