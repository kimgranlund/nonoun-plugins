<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/fanout.py: added `planned_scope(root, slug)` and `plan_overlap(ctx)`. `print_plan` now prints the planned-scope overlap lines after the lane blocks and before the gate lines. Also added the `--dry-run` docstring paragraph, the case 14 docstring entry and selftest case 14 with its negative control.

## Checks
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS
- `grep -qF 'overlap (planned scope): alpha T-0001 and beta T-0002: shared.txt' plugins/sdlc-lite/scripts/fanout.py`: exit 0
- `grep -qF 'overlap (planned scope): none' plugins/sdlc-lite/scripts/fanout.py`: exit 0
- `grep -qF 'overlap (planned scope): not planned, checked at merge time: T-0003' plugins/sdlc-lite/scripts/fanout.py`: exit 0
- Scope guard (`test -z "$( { git diff --name-only "$SDLC_BASE_SHA" ...; git ls-files --others ...; } | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py)"`), with SDLC_BASE_SHA=79bb56d: exit 0
- Negative control: in a mktemp copy of `plugins/sdlc-lite` outside the repo, `planned_scope` was made to return `None` first. That copy's selftest exited 1 with a single miss, starting "case 14 planned scope: dry run exits 0 with the alpha/beta shared.txt pair line...". The copy was then removed and the real tree was not touched.
- `git diff --check`: clean

## Notes
- Case 14 checks its lines by exact match against each stdout line, not by substring.
- The "none" line prints whenever no different-lane pair intersects, even if some tickets are unplanned. In that case the "not planned" line follows it.
- An external lane's tickets are always listed as not planned, because their step folders live on the external branch.
