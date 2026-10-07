<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: this step's only file. It adds:
  - the `<lane>@<branch>=<id>[,<id>...]` spec, with `Lane.external` and `Lane.tip`
  - preflight checks for external lanes: the branch is registered, the ref resolves, it is not the integration branch or an `<integration>-<lane>` branch, and no two lanes share one branch; tickets come from `tickets.branch_tickets`
  - the dry-run plan line, and `setup` skipping external lanes
  - `merge_gate_close`, one helper both lane kinds call, which skips the gates when the merge leaves HEAD unchanged
  - `run_lane` skipping the wip commit when a lane has no dir
  - the external line in `report.md`
  - the docstring, the `main()` usage line, the argparse metavar and help, and selftest case 11
- `plugins/sdlc-lite/scripts/tickets.py`: changed in step 1 and still uncommitted in the tree. This step did not touch it.

## Checks
- AC1, the mixed run `alpha@ext=T-0002,T-0003 beta=T-0001`: rc=0. Two merge commits; a, b and c are done on `fanout/t`; the `ext` tip and main are unchanged; there is no `fanout/t-alpha` ref and no `alpha` dir; the only alpha log is `gate-alpha-T-0002-1-a1.log`.
- AC2, the external lane line and the report rows: rc=0.
- AC3, the unregistered branch refuses with exit 2, naming `external_branch: ext` and `.sdlc/config`, and creates nothing: rc=0.
- AC4, the dry-run plan line appears and nothing is created: rc=0.
- AC5, `--gate false`: `red: false rc=1`, the integration branch stays at its base, `ext` is unchanged: rc=0.
- AC6, the usage line holds the spec form: rc=0.
- AC7, `__doc__` holds the spec form: rc=0.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: `fanout selftest: PASS`, rc=0. I ran it after the last edit, along with AC1 to AC9.
- (guard) scope diff: rc=0. Only `fanout.py` and `tickets.py` differ outside `.sdlc`.
- `python3 plugins/sdlc-lite/scripts/check.py`: `ok: 18 role levels, 8 agents checked`, which covers the `inherited red` word the docstring must keep.
- `git diff --check -- plugins`: rc=0.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.
- Mutation test: I ran the selftest on a throwaway copy of the plugin five times, each with one check broken. Case 11 went red every time:
  1. gates always run: a second alpha gate log appears.
  2. registration check off: the no-config negative control exits 0.
  3. report line removed: the report assertion fails.
  4. two lanes on one branch allowed: that refusal exits 0.
  5. integration-branch check off: that refusal exits 0, and the run rewrites `ext`.

## Notes
- The external merge target is `refs/heads/<branch>`, not the bare `<branch>` the Do shows. The merge message stays `Merge <branch>: <id>`. The full ref stops a tag with the same name from being merged in place of the branch.
- I read "any `<integration>-<lane>` of this run" as covering every lane in the run, external ones included.
- For an external ticket whose merge brings in nothing new, such as T-0003, the Commit cell is HEAD after the no-op merge. That is the previous `close` commit, because today's rule shows `merge_sha[:7]`. On an outcome before the merge stands, the cell is the branch tip's sha7.
- The report's external line gives the branch tip read at report time, falling back to the tip preflight saw.
- Three additions the Do did not ask for:
  - A sixth selftest refusal (the external branch named as `--integration`).
  - A `say` line when gates are skipped.
  - A setup print line for external lanes.
- `docs/references/sdlc-internals.md` and the skills are step 3's scope and are not touched here.
