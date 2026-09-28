<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0073: Route a verifier result with no verdict to reverify instead of counting it as a fail

## PR body
### Summary
Before this change, a verifier result with no pass/fail `## Verdict` made `steps.py next` exit 1. That stopped /chain, and on older peers it was counted as a fail, which used up a retry and moved the step toward a level bump. `board.py` showed it as 🔴 fail. Now it gets its own `reverify` action at the same level and is never counted as a fail. A second no-verdict result in a row after the same build stops the chain. The board shows it as 🟡 no verdict.

### Changes
1. `plugins/sdlc-lite/scripts/steps.py`
   - New helper `verdict_or_none`.
   - `next_action` returns `reverify L<n>` for one no-verdict result, and `stop` for two or more in a row after the same build.
   - The fail count skips no-verdict results.
   - The docstring rules are updated, and the no-verdict entry is removed from the Errors list.
   - The selftest's old error case is replaced by five cases: reverify, stop, no verdict then fail gives rebuild, no verdict then pass gives done, and fail/rebuild/fail/no verdict gives reverify (not bump).
2. `plugins/sdlc-lite/scripts/board.py`
   - `step_row` keys pass and fail on the Verdict's first line. Anything else renders as `🟡 no verdict · builder <L> · verifier <L>, rerun verify`, so the row drops out of the `--summary` 🔴 count.
   - The docstring and the selftest section 7 case are updated.
3. Docs
   - `skills/chain/SKILL.md`: `reverify` is added to the action list, and a new rule 5 in section 4 covers the no-verdict case.
   - `agents/conductor.md`: one clause states the same rule.
   - Repo `CLAUDE.md`: the `steps.py` bullet is updated.
   - `.claude/agents/sdlc-lite-author.md`: new "No-verdict route" invariant.

### Verification
- Step 1 (builder L2, verifier L1: pass)
  - The fixture commands give `reverify L1` with the reason naming `verifier-L1.md`, `stop` for two no-verdict results, and `rebuild L2` for no verdict then a fail.
  - The old error string is gone.
  - `steps.py selftest` passes.
- Step 2 (builder L2, verifier L1: pass)
  - The fixture board row is 🟡 no verdict, with no 🔴 in the task board or in `--summary`.
  - The verifier confirmed the same fixture shows 🔴 at HEAD.
  - `board.py selftest` passes.
- Step 3 (builder L1, verifier L1 on Opus: pass)
  - The `reverify` greps pass in all four doc files, and each one fails at HEAD.
  - The em-dash diff check passes, and a red control proved it can fail.
  - `scripts/check.sh` exits 0 with every line ok or PASS.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: a verifier result with no pass/fail verdict no longer counts as a fail. `steps.py next` now returns `reverify L<n>` to rerun the verifier at the same level, and a second no-verdict result in a row after the same build stops the chain. `/board` shows it as 🟡 no verdict instead of 🔴 fail.

## Follow-ups
- board.py shows "rerun verify" for a second no-verdict result in a row, but `steps.py next` returns `stop` for that case; make the board row say stop/ask the user so the two stay in sync.
