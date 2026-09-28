<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
No plan, builder, or verifier artifacts exist for this ticket — only `handoff.md`. The change (extending `.claude/agents/sdlc-lite-author.md` line 19) was made directly as a conductor trivial edit, per CLAUDE.md's allowance, but no independent verifier record confirms it. The handoff's own "Done" note claims `plugins/sdlc-lite/scripts/check.sh` exits 0, but this is a self-report with no verifier artifact backing it.

## PR title
T-0106: Extend sdlc-lite-author invariant to cover no-Status route and run.sh exit 3

## PR body
Summary: extends the sdlc-lite-author agent's invariant on line 19 so it also covers the builder no-Status `rebuild`/`stop` route and the `run.sh` exit-3-on-missing-section rule, bringing it in line with CLAUDE.md. Follow-up from T-0103.

Changes:
- `.claude/agents/sdlc-lite-author.md` line 19 (the "No-verdict route" invariant): added that a builder result with no done/blocked Status maps to `rebuild` at its level in `steps.py next`, is never a fail or a bump, and two in a row map to `stop`; and that `run.sh` exits 3 when a result lacks its role's required section (keeping the result file and `runs.jsonl` line), routed through `steps.py next`, never to done. Also notes these must stay in sync across `steps.py`, `board.py`, `run.sh`, chain SKILL.md, conductor.md, and CLAUDE.md.
- `.sdlc/0106-extend-claude-agents-sdlc-lite/handoff.md`: filled in Goal and Constraints, marked Done with the date.

How verified: handoff.md claims `plugins/sdlc-lite/scripts/check.sh` exits 0 as of 2026-09-26, but no verifier or check-run artifact is present in the ticket folder to confirm this independently. Treat as unverified pending an explicit check.sh run or verifier pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
Extended the sdlc-lite-author agent's invariant to also cover the builder no-Status `rebuild`/`stop` route and the `run.sh` exit-3 rule, matching CLAUDE.md (T-0106).

## Follow-ups
None.
