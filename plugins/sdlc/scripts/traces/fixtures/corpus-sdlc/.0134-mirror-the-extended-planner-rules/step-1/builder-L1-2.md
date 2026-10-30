<!-- role=builder level=L1 model=sonnet effort=low -->
All criteria pass, guard exits 0. Work was already done by a prior attempt; nothing further needed.

## Status
done

## Changes
.claude/agents/sdlc-lite-author.md: appended two sentences to the "Plan-defect route" bullet mirroring planner.md rules 11 and 12 (already present from a prior uncommitted attempt; verified only, no further edit needed).

## Checks
- `grep -n "membership or structure" .claude/agents/sdlc-lite-author.md` — match found, PASS
- `grep -n "can go red" .claude/agents/sdlc-lite-author.md` — match found, PASS
- `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md` — exits 1 (dirty), PASS; `git diff HEAD -- .claude/agents/sdlc-lite-author.md | grep -c '^-[^-]'` — 0 removed lines, PASS
- `test "$(git diff --name-only HEAD -- . ':!.sdlc')" = ".claude/agents/sdlc-lite-author.md" && test -z "$(git ls-files --others --exclude-standard -- . ':!.sdlc')"` — PASS
- (guard) `plugins/sdlc/scripts/check.sh` — exit 0, PASS

## Notes
None.
