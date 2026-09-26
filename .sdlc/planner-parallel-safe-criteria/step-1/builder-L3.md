<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: `lint_steps` has two new checks on the raw text of each span that parses. A criterion that pins a commit sha is caught with `GIT_WORD_RE`/`SHA_RE` and `pins_sha`. A fixed-number count over a changing set is caught with `COUNT_TOOL_RE`/`SET_SOURCE_RE`/`COMPARE_RE` and `fixed_set_count`. Each finding has a hint line. The `lint` and `split` paragraphs of the module docstring name both refusals. New selftest cases: (k3) a pinned sha, bare and as `<sha>..HEAD`, refused by split and lint; (k4) a glob count compared with 26, refused by split and lint; (k5) the pass cases.
- `plugins/sdlc-lite/agents/planner.md`: new rules 6 (sha fixed at plan time), 7 (derive the set at run time) and 8 (owns that budget). The replan rules are now 9 and 10.
- `plugins/sdlc-lite/scripts/check.py`: two new `PLAN_DEFECT_DOCS` entries (`sha fixed at plan time` and `owns that budget`), and item 5 of the header docstring mentions them.
- `CLAUDE.md`: the `scripts/steps.py` bullet names both new split refusals, including the phrase "pins a commit sha".
- `.claude/agents/sdlc-lite-author.md`: the Plan-defect route line names both new lint checks.

## Checks
- Acceptance criteria 1, 2 and 3 (lint on a pinned sha, a `<sha>..HEAD` range, and a glob count `-eq 26`): exit nonzero with the expected stderr text, so all PASS.
- Guards 4, 5 and 6 (HEAD / `%H`, `grep -c` on one file `-eq 2`, glob count `-eq 0`): lint ok, PASS.
- `steps.py selftest | grep -q "pins a commit sha"`: PASS. `| grep -q "fixed number"`: PASS. `steps.py selftest` exits 0: PASS.
- `grep -q` for the three phrases in planner.md, the two in check.py, and "pins a commit sha" in CLAUDE.md and sdlc-lite-author.md: all PASS.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. This includes the check.py merge-step lint, shellcheck and plugin validate.
- Observable: planner.md rules under `## Criteria that can pass` are numbered 1 to 10 with no gaps. `grep -nE "rule [67]"` in planner.md finds nothing. No other file in the plugin, CLAUDE.md or `.claude/agents` refers to planner rule numbers ("rule N").

## Notes
- The pinned-sha check needs `git` as a standalone word; `.gitignore` and `git-foo` do not count. The count check accepts combined flags such as `wc -lc` and `grep -qc`.
- The count check also treats a bare `=` as a comparison, so a span with a count tool, a glob or `ls`/`find`, and an assignment like `n=26` would be flagged too. The step asks for `=` in the list, and no current fixture or template hits this.
- The existing `||` check now sets `joined = False` on a shlex error instead of `continue`, so the two new checks still run on spans shlex cannot tokenize.
- Nothing committed.
