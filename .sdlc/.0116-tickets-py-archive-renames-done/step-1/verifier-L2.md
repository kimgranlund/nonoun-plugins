<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: exit 0 in the tree. It is also green at pre-build HEAD (exit 0 in a throwaway worktree). Gate criterion, so it holds before and after.
- A committed cite makes archive refuse and leaves the folder in place: pass. Evidence: the criterion command exits 0 in the tree. At HEAD in a throwaway worktree it exits 1, so the check bites.
- The refusal names the citing file: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- `--rewrite-refs` rewrites and renames: pass. Evidence: exit 0 in the tree, exit 2 at HEAD (argparse rejects the unknown flag).
- `--force` renames and leaves the cite: pass. Evidence: exit 0 in the tree, exit 2 at HEAD.
- The dry run with `--rewrite-refs` lists the file and writes nothing: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- The dry run without flags names the citing file and writes nothing: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- A cite between two folders archived in the same run is rewritten, and both folders are renamed: pass. Evidence: exit 0 in the tree, exit 2 at HEAD.
- (guard) Outside git there is no scan and archive still renames: pass. Evidence: exit 0 in the tree. It is also exit 0 at HEAD, as a guard should be.
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' plugins/sdlc-lite/scripts/tickets.py`: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- `grep -qE "run\(root, 'archive'.*rewrite_refs=True" ...`: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- `grep -qE "run\(root, 'archive'.*force=True" ...`: pass. Evidence: exit 0 in the tree, exit 1 at HEAD.
- Every existing `close` selftest expect line is still present unchanged: pass. Evidence: `git diff HEAD -- plugins/sdlc-lite/scripts/tickets.py | grep '^-[^-]'` gives 10 removed lines:
  - the old usage line (which contains `[--expect DIGEST]`; grep matched it, and it is not a selftest expect);
  - 2 lines of the `archive` docstring paragraph;
  - the 3 `rewrite_now` loop lines;
  - the old `cmd_archive` def line;
  - 2 replaced return lines;
  - the old archive `--dry-run` help line.
  No `expect(...)` line was removed. The usage, docstring and help edits are required by Do items 7 and 8, so they are not out-of-scope removals.
- Repo-wide check (goal "check.sh is green"): pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` exits 0, with run selftest, hook selftest, hook live probe selftest, shellcheck and plugin validate all ok. (`scripts/check.sh` at the repo root does not exist; the script lives under the plugin folder.)
- Steelman of the one concern I considered filing, that the builder's Notes flag the `outside_refs` docstring still saying "for a numbered close": the rebuttal holds, because the Do says to edit only `tickets.py` and to keep `close` behavior unchanged, and a stale docstring is a minor wording issue. Dropped.

## Out of scope changes
None. Only `plugins/sdlc-lite/scripts/tickets.py` is modified among the tracked project files. The other `git status` entries are `.sdlc` task artifacts (`handoff.md`, `planner-L2.md`, `runs.jsonl`, `step-1/`, `step-2/`). Docs are deferred to step 2 per the builder's Notes.

## For the next attempt
None
