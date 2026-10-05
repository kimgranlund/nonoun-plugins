# Re-verify T-0227: the two failed criteria only

## Goal
Independently re-verify branch orient (T-0227) on the two criteria the first verifier failed; the other criteria passed and are not re-run.

## Acceptance criteria
1. The `lean-sdlc/` row of `docs/AGENTS.md` is true: `ls docs/lean-sdlc` shows only design.md, cost-control.md and README.md, the row says the folder holds the lean lane design and the cost-control addendum (not a solo design), and its link to `docs/validation/solo-vs-lean-benchmark-2026-10-04.md` resolves (relative to docs/). Every other docs/AGENTS.md row is unchanged from the first verification.
2. No added line in `AGENTS.md`, `docs/AGENTS.md`, `docs/CLAUDE.md` or `.sdlc/0227-orient-entry-files/handoff.md` contains an em dash (U+2014) (`git diff main..HEAD -- AGENTS.md docs/AGENTS.md docs/CLAUDE.md .sdlc/0227-orient-entry-files/handoff.md | grep '^+' | grep -c "$(printf '\xe2\x80\x94')"` is 0), `git diff --check main..HEAD` is clean, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0, and `python3 scripts/check-packaging.py` exits 0 (check.sh already passed in the first pass on the same code and is not re-run).

## Notes
Read-only. Report pass or fail per criterion with evidence.
