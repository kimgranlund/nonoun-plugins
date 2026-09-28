<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
`board.py`'s `step_row` reports a step as stopped, asking the user, when two or more consecutive verifier results after the newest build have no verdict. This matches `steps.py next`. A single no-verdict result still reads "rerun verify".

## Step 1: Board row says stop for consecutive no-verdict verifiers
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`, change the no-verdict branch of `step_row`.
- Count consecutive no-verdict verifier results the way `steps.py next` does. Walk `reversed(order.ordered(step, 'verifier'))`. Skip results where `not order.counts_after(w, last_build)`. Stop at the first result whose `section(w, 'Verdict')` starts with `pass` or `fail`. Count the rest.
- If the count is 2 or more, return `('🟡', f'stop · no verdict x{n} · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}, ask the user{tries}', LADDER['built'])`.
- If the count is 1, keep the existing 🟡 "no verdict ... rerun verify" text unchanged.
- Do not touch `steps.py`.

Extend the `board.py` selftest, next to the existing `noverdict` fixture:
- (a) One no-verdict verifier gives a row starting `no verdict` and containing `rerun verify`.
- (b) Two consecutive no-verdict verifiers (`verifier-L1.md` and `verifier-L1-2.md`, with a `runs.jsonl` record order) give a row starting `stop` and containing `ask the user`.
- (c) A fail followed by two no-verdict verifiers after a rebuild counts only the ones after the newest build.

Update the docs that describe the no-verdict rendering:
- the `board.py` docstring (line ~26)
- the CLAUDE.md Layout feed line, if it mentions no-verdict
- `skills/board/SKILL.md`, if it mentions no-verdict

### Acceptance criteria
- `grep -q "ask the user" plugins/sdlc-lite/scripts/board.py`
- `python3 plugins/sdlc-lite/scripts/board.py selftest`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/steps.py` (guard)
- `plugins/sdlc-lite/scripts/check.sh`
- The selftest output contains a passing case for one no-verdict result ("rerun verify") and a passing case for two consecutive no-verdict results ("stop" / "ask the user"). Observe this in the `board.py selftest` output.

## Risks
- `by_level` may not order verifier results by `runs.jsonl` record order. The builder should use `order.ordered` for the count.
- The `git diff` guard on `steps.py` is only meaningful on an uncommitted tree. If the step commits, the verifier should compare against the base commit instead.
