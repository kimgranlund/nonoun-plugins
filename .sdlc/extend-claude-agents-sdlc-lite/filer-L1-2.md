<!-- role=filer level=L1 model=sonnet effort=medium -->
All artifacts checked: verifier pass with all four criteria confirmed independently. This is a rerun after that verification landed.

## Warnings
None.

## PR title
T-0106: Extend sdlc-lite-author invariant to cover no-Status route and run.sh exit 3

## PR body
Summary: extends the sdlc-lite-author agent's invariant on line 19 so it also covers the builder no-Status `rebuild`/`stop` route and the `run.sh` exit-3-on-missing-section rule, bringing it in line with CLAUDE.md. Follow-up from T-0103.

Changes:
- `.claude/agents/sdlc-lite-author.md` line 19 (the "No-verdict route" invariant): now states that a builder result with no done/blocked Status maps to `rebuild` at its level in `steps.py next`, is never a fail or a bump, and two in a row map to `stop`; and that `run.sh` exits 3 when a result lacks its role's required section (keeping the result file and `runs.jsonl` line), routed through `steps.py next`, never to done. Also notes these must stay in sync across `steps.py`, `board.py`, `run.sh`, chain SKILL.md, conductor.md, and CLAUDE.md.
- `.sdlc/extend-claude-agents-sdlc-lite/handoff.md`: Goal and Constraints filled in, marked Done with the date.

How verified: an independent L1 verifier (`verify/verifier-L1.md`) checked the edit against the ticket's four acceptance criteria and returned a pass on all of them:
- Line 19 mentions `rebuild`, `stop`, `exits 3`, and `run.sh` (confirmed by `grep -q` per term, with a negative-control line proving the check bites).
- Every claim on line 19 was cross-checked against `plugins/sdlc-lite/scripts/steps.py:64-66`, `run.sh:238-247` and its exit-3 comment, `agents/conductor.md:24`, `skills/chain/SKILL.md:38`, and `CLAUDE.md:23`, with no contradictions found.
- `git diff --stat -- .claude/agents/sdlc-lite-author.md` showed exactly one file, one line changed, no other invariant touched.
- `(guard) plugins/sdlc-lite/scripts/check.sh` exited 0, full selftest suite passing.

The verifier noted two untracked, out-of-scope files (`handoff.md` edits and the earlier filer draft) as pre-existing ticket-workflow artifacts, not defects.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Extended the sdlc-lite-author agent's invariant to also cover the builder no-Status `rebuild`/`stop` route and the `run.sh` exit-3 rule, matching CLAUDE.md (T-0106).

## Follow-ups
None.
