<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q 'files this step changed' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: ran the grep, printed `ok`. Rule 6 is at builder.md line 15, seen in the git diff.
- `grep -q 'PIDs you started' plugins/sdlc-lite/agents/builder.md`: pass. Evidence: ran the grep, printed `ok`. Rule 7 is in the git diff.
- `grep -q 'files this step changed' plugins/sdlc-lite/scripts/check.py`: pass. Evidence: ran the grep, printed `ok`. The phrase is in `SCOPE_PHRASES`.
- `grep -q 'PIDs you started' plugins/sdlc-lite/scripts/check.py`: pass. Evidence: ran the grep, printed `ok`.
- `grep -q 'builder scope guard negative control' plugins/sdlc-lite/scripts/check.py`: pass. Evidence: ran the grep, printed `ok`. The negative control emits `check.py: builder scope guard negative control not flagged`, and it runs once per phrase.
- `grep -q 'block-pattern-kill.sh' CLAUDE.md`: pass. Evidence: ran the grep, printed `ok`. The diff adds a Layout bullet after block-background and names the hook in the check.sh line.
- `grep -q 'block-pattern-kill.sh' .claude/agents/sdlc-lite-author.md`: pass. Evidence: ran the grep, printed `ok`. The diff adds it to the check.sh line and to a new Hazards bullet.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py "$PWD/plugins/sdlc-lite"`: pass. Evidence: printed `ok: 18 role levels, 8 agents checked`, exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0. The tail shows the hook selftest, hook live probe selftest, shellcheck and plugin validate all passing.
- Verifier observes the guard bites: pass. Evidence: I copied the built tree (`plugins` and `CLAUDE.md`) into `$SDLC_TMP_WORKTREES/bite`, an ordinary directory rather than a git worktree, since the built tree is uncommitted. There I changed `PIDs you started` to `PIDs one started` in builder.md and ran that copy's check.py. It printed `FAIL agents/builder.md: builder scope rule missing "PIDs you started"` and exited 1. The unmodified tree exits 0, so the guard goes red only on the removal. I then removed the copy.

Steelman: a possible fail is that the copy is not a git worktree, but the criterion says only "a throwaway worktree ... holding the built tree". The built tree is uncommitted, so a `git worktree add` at HEAD could not hold it. The finding does not hold and is dropped.

## Out of scope changes
`plugins/sdlc-lite/hooks/hooks.json`, `scripts/check.sh`, `scripts/hook-selftest.sh` and the new `hooks/block-pattern-kill.sh` are also uncommitted in the tree. They are the step-1 hook work, not step 2. The step-2 diff itself touches only builder.md, check.py, CLAUDE.md and sdlc-lite-author.md, all named in the handoff. I did not diff the step-1 files against step 1's output, so I cannot vouch for them here. `.sdlc` artifacts (planner-L2.md, runs.jsonl, step dirs) are run records, not project changes.

## For the next attempt
None
