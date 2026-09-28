<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0100: Lint pinned shas and fixed set counts in plan criteria; add parallel-lane planner rules

## PR body
### Summary
Plan criteria broke under parallel lanes in three ways: a sha fixed at plan time went stale on the first main sync, a hard-coded count over a changing set went stale as other lanes added items, and a global aggregate budget was checked by tickets that don't own it. This change makes `steps.py split` and `lint` refuse the first two as `plan defect`s. It also teaches the planner all three rules and guards that text in `check.py`. The third rule is semantic, so it is a planner prompt rule plus a `check.py` text guard, not a lint.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`:
  - `lint_steps` runs two more regex checks on the raw text of each criterion span that parses under `bash -n`.
  - Pinned sha: the span holds `git` and a 7 to 40 char hex run. The finding reads "pins a commit sha fixed at plan time".
  - Fixed set count: the span holds a count tool (`wc -l`, `grep -c`, `grep --count`), a set source (a `*` glob, `ls`, `find`), and a comparison with a literal of 2 or more. The finding reads "compares a count over a changing set with a fixed number".
  - Each finding carries a hint line, and the module docstring names both refusals.
  - The `||` check now sets `joined = False` on a shlex error instead of skipping the span, so the new checks still run on spans shlex cannot tokenize.
  - New selftest cases: (k3) pinned sha, bare and as `<sha>..HEAD`; (k4) a glob count compared with 26; (k5) pass cases (`HEAD`, `HEAD~1`, `%H`, a `grep -c` on one file with `-eq 2`, a glob count `-eq 0`, the merge-step criterion).
- `plugins/sdlc-lite/agents/planner.md`: new rules 6 (sha fixed at plan time), 7 (derive the set at run time) and 8 (owns that budget) under `## Criteria that can pass`. The replan rules are now 9 and 10.
- `plugins/sdlc-lite/scripts/check.py`: two new `PLAN_DEFECT_DOCS` entries (`sha fixed at plan time`, `owns that budget`), and the header docstring is updated.
- `CLAUDE.md` (the `scripts/steps.py` bullet) and `.claude/agents/sdlc-lite-author.md` (the Plan-defect route line) name both new refusals.

### How verified
Step 1 passed the L2 verifier.
- Lint on a pinned sha, a `<sha>..HEAD` range, and a glob count `-eq 26` exits nonzero with the expected message and a `plan defect` line. The verifier also probed `<sha>^`, `<sha>~2`, `find | wc -l -eq 3`, `grep --count ... -ge 2` and `ls d/* | wc -l == 10`, and all are flagged.
- Lint stays clean on `HEAD`, `HEAD~1`, `%H`, `grep -c` on one file `-eq 2`, and a glob count `-eq 0`.
- The selftest output holds "pins a commit sha" and "fixed number", and the selftest is green. At base HEAD, the "pins a commit sha" selftest check and the pinned-sha lint both fail, so the tests bite.
- The doc phrases are present in planner.md, check.py, CLAUDE.md and sdlc-lite-author.md.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0, including shellcheck and plugin validate.
- planner.md rules are numbered 1 to 10 with no gaps and no stale "rule 6" or "rule 7" reference.

Known limits: both lints are heuristics on raw span text. A criterion that names a specific commit on purpose (for example `git merge-base --is-ancestor <real sha> HEAD`) is now refused. A bare `=` in a span that also has a count tool and a glob or `ls`/`find` (for example `n=26`) is also flagged.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `steps.py split` and `lint` now refuse, as a `plan defect`, an acceptance criterion that pins a commit sha or compares a count over a changing set (glob, `ls`, `find`) with a fixed number of 2 or more. The planner has three new rules on parallel-lane-safe criteria: compare against HEAD, derive sets at run time, and leave aggregate budgets to the ticket that owns them.

## Follow-ups
- Make the fixed-count lint skip a bare `=` assignment such as `n=26`, which is currently flagged when the span also has a count tool and a glob, `ls` or `find`.
- Decide how the pinned-sha lint should handle a deliberate commit reference such as `git merge-base --is-ancestor <real sha> HEAD`, which is now refused with no escape hatch.
