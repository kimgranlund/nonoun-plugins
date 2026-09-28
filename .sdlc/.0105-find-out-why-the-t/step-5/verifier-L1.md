<!-- role=verifier level=L1 model=sonnet effort=medium -->
All numbering consistent, all criteria pass. All checks clean.

## Verdict
pass

## Criteria
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: command run directly, exit 0.
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/verifier.md`: pass. Evidence: command run directly, exit 0.
- Negative-control criterion (`... sed -i ... verifier.md && ! python3 check.py ... `): pass. Evidence: ran the exact command against a temp copy; check.py printed `FAIL agents/verifier.md: foreground rule missing "never end the turn while background work runs"` and `FAIL: 18 role levels, 8 agents checked`, so `!` inverted its nonzero exit to success (exit 0 overall). This also proves the check can go red (checks-that-bite): red on the mutated copy, green on the real tree (below).
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: `ok: 18 role levels, 8 agents checked`, exit 0.

## Out of scope changes
`plugins/sdlc-lite/hooks/block-background.sh`, `hooks/hooks.json`, `scripts/fanout.py`, `scripts/hook-selftest.sh`, `scripts/run-selftest.sh`, `scripts/run.sh`, and `.sdlc/0105-find-out-why-the-t/handoff.md` / `runs.jsonl` are modified in the working tree, plus untracked `step-1` through `step-6` and `planner-L2.md`. Checked: read `step-1/handoff.md` through `step-4/handoff.md`'s `### Do` sections and confirmed each modified file's changes match that step's own Do (run.sh timeout env vars from step-1, stream-json parsing from step-2, fanout.py driver env check from step-3, block-background.sh Monitor guard and hooks.json/hook-selftest.sh from step-4). These are prior steps' already-built-and-verified work in this same chain, not new changes introduced by step-5's builder (whose own diff, confirmed via `git diff plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/scripts/check.py`, touches only the three files the Do names). Not out of scope for step 5.

## For the next attempt
None
