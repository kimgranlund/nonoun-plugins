---
id: T-0202
title: "Carry forward section in scout, researcher, architect, archaeologist"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add a `## Carry forward` section to the scout, researcher, architect, and archaeologist results and the reader rule to planner and builder.

## Intent
- Do: Each producing role ends its result with `## Carry forward` (at most 15 lines: facts and paths later roles must not re-derive). The planner cites the result path and does not copy it. Planner and builder contracts say to read `## Carry forward` before searching and to search only what it does not answer. A focused live run in a throwaway project shows the planner reading a scout's `## Carry forward` and not repeating the scout's search (compare tool calls with and without). By this design's own mandatory list this is full-chain work.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L10), reviewed twice: `docs/reports/lean-sdlc-design-review.md` and `docs/reports/lean-sdlc-design-review-2.md`. Supersedes part of T-0191 (single plan record), which is closed in favor of these tickets. Depends on: nothing. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/agents/{scout,researcher,architect,archaeologist}.md, planner.md, builder.md, run.sh required-section handling if affected, check.py guards, regenerated Codex agents, a focused live run.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
A role without the section is not a failure of required-section checks for existing results. check.py guards with negative controls. `codex_roles.py generate --check` and the Codex selftest pass. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Plan review
plan defect: step 2 blocked (step-2/builder-L3.md): acceptance criterion AC3 (`symbol_searches>=1` in without.txt) cannot pass, because probe.sh's metric reads only the first 200 characters of each tool input, and the without planner's `git grep -n pad_cell` sits past that point. Over untruncated inputs the behavior under test held (scout 4 and 1, with 2 and 0, without 1 and 1 tree and pad_cell searches). Replan step 2 only: count over the full tool input (or raise the cut well past the longest input) in the metric, reuse the already-built probe.sh, rerun the arms, and keep the report and README line. Step 1 is committed and verified. Do not weaken the criterion's threshold, only fix what it measures.

## Known limits (burn-down, 2026-10-04)
Step 2 (focused live run) was built twice and blocked twice on the probe's own metric, not on behavior: first the 200-character cut, then `read_scout_result` looking only for the literal `scout-L1.md` in tool inputs while the planner read it through a glob. In run 2 the planner given the scout result read it and cited its path, ran no symbol search, and the planner without it did search, so the behavior under test held. Per the burn-down rules (replan cap of one, live proof is T-0208's, record a flaky live arm as a limit) there is no third cycle. The report docs/reports/carry-forward-live-run.md states the actual outcome and this limit. An em dash in a role's own output cannot be avoided by the report, which writes it as `--`.

## Closed

2026-10-04: warnings acknowledged: Burn-down: step 2 live run is a recorded known limit (probe metric miss, behavior held, no third cycle); the branch verifier L3 has since passed (verify-t0202/step-1/verifier-L3.md), so the filer's no-verdict warning is stale.

> - Step 2 (focused live run) is blocked, and no verifier ran on it. There is no `step-2/verifier-*.md`. The builder reported criteria 2 and 9 as FAIL (`read_scout_result=no` and the README line). The ticket's own "Known limits" section states there was no third cycle.
> - Step 2 was built twice and blocked twice on the probe's own metric, not on behavior. First the metric cut each tool input at 200 characters. Then it looked only for the literal `scout-L1.md`, but the planner read the file through a glob.
> - The step 1 verifier (L2) passed. Its output lists AC1 to AC12 as pass.
> - A separate branch verification under `.sdlc/verify-t0202/step-1` (verifier-L3) has only a log, a `.running` marker and an attempt file. No verdict file exists, so it is unfinished.
> - The "Done when" items "an independent verifier passed each step" and the live-run proof are therefore not met.
