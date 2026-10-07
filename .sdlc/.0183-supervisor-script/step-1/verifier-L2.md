<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Version line (`grep -qE "^Version 0\.2, "`): pass. Evidence: exit 0 on the built tree. `grep -cE` finds 0 matches in the HEAD copy and 1 now, so the check can go red.
- Findings table (`## Review findings applied` heading plus rows `| 1 |` to `| 17 |`): pass. Evidence: exit 0. I read `watcher-design.md` lines 316-338: header `| # | Finding | Applied in |` and rows 1 to 17, each naming D tags.
- Tags `(D1)` to `(D21)`: pass. Evidence: exit 0. Each tag appears exactly once (a per-tag count loop gave 1 for every tag). The HEAD copy has 0 `(D1)`, so the check bites.
- Required strings (sandbox_mode, network_access, exclude_slash_tmp, approval_policy, dontAsk, strict-mcp-config, plugin-dir, stream-json, no-session-persistence, `codex exec resume`, `SDLC_ROLE=supervisor`, `SDLC_HEADLESS=1`, `hosts.local.json`, `git-common-dir`, `lstart`, `111,431`): pass. Evidence: exit 0. `111,431` is absent from HEAD and present now.
- All 11 limits keys: pass. Evidence: exit 0. Lines 119-129 list each key with its default and range, matching D7.
- Five `supervisor.py` commands: pass. Evidence: exit 0. They appear at lines 77-83 and 85-97.
- Removed phrases absent (`Owned session (default)`, `which the watcher may call`, `about 17,600`, `four blockers open`): pass. Evidence: exit 0. Each phrase is in the HEAD copy once and in the built file 0 times.
- Prompt text: pass. Evidence: exit 0. Line 63 holds the full D4 text.
- `## Applied` in the review doc mentions `Version 0.2`: pass. Evidence: exit 0. The diff adds only the `## Applied` section and one paragraph (4 lines), so the review's findings above it are unchanged.
- (guard) no em dash in either file: pass. Evidence: exit 0. I fed the guard a file containing an em dash and it detected it, so it can go red.
- (guard) scope, only the two docs changed outside `.sdlc`, with no untracked files outside `.sdlc`: pass. Evidence: exit 0, run with `SDLC_BASE_SHA=5774f07`, which equals the step's `base-sha` file and HEAD.
- Content checked beyond the greps, as the builder's claims are unverified:
  - Wake commands, scrub list, limits ranges, poll order, and the D9 to D18 statements match the handoff text.
  - The remaining mentions of `expire`, `--session-id`, and "owned" are negations or review-finding records, not contradictions. Examples are line 198, line 55, and table row 4. Line 38 is a v0.1 evidence row about `--session-id`.
  - `git diff --check -- docs/` is clean.

## Out of scope changes
None outside `.sdlc/`. The docs diff is only `docs/planning/ticket-stages/watcher-design.md` and `docs/reports/idle-host-watcher-design-review.md`. The `.sdlc` changes (`runs.jsonl` and the untracked step and plan artifacts) are run records and are excluded by the scope guard. The extra "Status fields" row in the D20 table is within the design doc and the builder disclosed it.

## For the next attempt
None
