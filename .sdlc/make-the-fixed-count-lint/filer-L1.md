<!-- role=filer level=L1 model=sonnet effort=medium -->
All checks pass, single step, verifier verdict pass. Ready to draft the filer output.

## Warnings
None

## PR title
T-0109: Make the fixed-count lint skip a bare `n=26` assignment

## PR body
Summary: `steps.py`'s fixed-count lint (`fixed_set_count`/`COMPARE_RE`) no longer treats a bare shell assignment like `n=26` as a comparison, so a plan criterion span with a count tool, a glob/`ls`/`find`, and a bare assignment no longer gets refused as "compares a count over a changing set with a fixed number." Real comparisons (`-eq 26`, `= 26`, `== 26`, `!= 26`) in the same kind of span are still flagged.

Changes:
- `plugins/sdlc-lite/scripts/steps.py`: `COMPARE_RE`'s bare `=` alternative now requires preceding whitespace (`(?<=\s)=`), so `name=value` words (`n=26`, `export N=26`), `--flag=26`, and `${n:=26}` no longer count as comparisons, while `[ "$x" = 26 ]` / `test "$x" = "26"` still do.
- `plugins/sdlc-lite/scripts/steps.py`: added a `(k6)` `selftest()` group with one pass case (`n=26` and `export N=26` spans alongside a count tool and a glob/find pass the lint) and four refusal cases (`-eq 26`, `= 26`, `== 26`, `!= 26` forms, including one with a bare assignment feeding a separate real comparison, still refuse).
- `plugins/sdlc-lite/scripts/steps.py`: module docstring's `lint` paragraph gains a clause naming the `n=26` exception.
- `CLAUDE.md`: the `scripts/steps.py` Layout bullet gains the matching clause.

How verified: one plan step (L2, Opus low), built and independently verified (verifier L1, Sonnet medium, verdict pass). The verifier ran each criterion in a throwaway HEAD worktree to confirm red-before/green-after (`fixed_set_count` positive cases, the `(k6)` selftest group, both doc greps), confirmed the four `(k4)`/`(k6)` regression-guard forms stay flagged in both trees, ran the full `scripts/check.sh` to green (~13m45s), and confirmed the diff and untracked-file guards show only `steps.py` and `CLAUDE.md` changed under `plugins/CLAUDE.md/.claude`. The task's own `.sdlc/` chain artifacts (a documented prior split refusal and replan) were flagged as out-of-scope-looking but correctly dismissed as normal process output outside the step's diff-scope guard.

Note: an earlier planner-L1 attempt was refused by `steps.py split`'s own lint (its acceptance criteria quoted a full sample span verbatim, tripping the very rule under test) and triggered a planner-L3 replan, recorded under the task handoff's `## Plan review`; the replanned criteria route the count tool and comparison operators through string concatenation to avoid embedding a literal flaggable span in the criterion text itself.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
`steps.py`'s fixed-count lint no longer flags a bare shell assignment such as `n=26`; a real comparison (`-eq`, `-ne`, `-ge`, `-gt`, `-le`, `-lt`, `=`, `==`, `!=`) is still refused.

## Follow-ups
None
