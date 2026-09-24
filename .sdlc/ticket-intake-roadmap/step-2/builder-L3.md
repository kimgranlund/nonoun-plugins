<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py` (new, executable, stdlib only): `new`, `roadmap`, `check` and `selftest`, with `--root` defaulting to `.sdlc` in the cwd. There is no `close` command.
- `plugins/sdlc-lite/scripts/check.sh`: added `python3 "$root/scripts/tickets.py" selftest || fail=1` after the coverage_check line, and updated the header comment.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: exit 0, printed `tickets selftest: PASS`.
- To prove the selftest can fail, I ran it against temp copies of the script with one check switched off each time:
  - Cycle detection off: selftest exit 1, listed cycle and self-cycle as not biting.
  - Duplicate-id check off: selftest exit 1, listed duplicate id.
  - Stale check off: selftest listed both stale cases as not biting.
- Fixture run with `R=$(mktemp -d)/s`:
  - `new feature alpha "Alpha"` and `new bug beta "Beta"` both exit 0. alpha has `id: T-0001`, `title: "Alpha"`, `created: 2026-09-24`. beta has `id: T-0002`, `type: bug`. `roadmap.md` exists.
  - After changing alpha to `depends: [T-0002]`, `check` exits 1 with `roadmap.md: stale or missing, ...`.
  - `roadmap` then `check` exits 0 with `ok: 2 tickets, roadmap current`. The T-0002 row comes before the T-0001 row.
  - Running `roadmap` twice then `cmp` exits 0.
- Negative controls, each on a copy of the passing fixture. Every one gave `check` exit 1 with stderr naming the problem, and none printed a traceback:
  - `type: epic` → `alpha: type='epic' not in ...`
  - `status: wip` → `alpha: status='wip' not in ...`
  - `size:` line deleted → `alpha: missing size`
  - `id: T-12` → `alpha: id 'T-12' is not T-NNNN ...`
  - beta given `id: T-0001` → `beta: duplicate id T-0001, also used by alpha`
  - `depends: [T-0099]` → `alpha: depends on T-0099, which no ticket has`
  - `from: T-0099` added → `alpha: from T-0099, which no ticket has`
  - beta depends on T-0001 while T-0001 depends on T-0002 → `alpha: dependency cycle T-0001 -> T-0002 -> T-0001`
  - Line appended to `roadmap.md` → stale message
- Added `plain/handoff.md` with no front matter, then ran `roadmap` and `check`: exit 0.
- `new idea alpha`: exit 1 (`already exists; nothing written`). The md5 of `alpha/handoff.md` was the same before and after.
- `new epic gamma`: exit 1, `available types: bug, chore, feature, idea, spike`. No `gamma/` dir was created.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Output includes `tickets selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
  - My first edit of the header comment failed shellcheck (SC1073), because a comment line starting with "shellcheck" is read as a directive. I reworded it and reran; the exit 0 is from that rerun.
- `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc`: exit 0.

## Notes
- `new` prints only the created path on stdout, so a script can use it directly.
- `new` checks the new ticket in memory before writing it. If a template would produce a bad ticket (for example it has no `id: T-0000` line), nothing is written.
- Newlines in a title are collapsed to spaces, and `"` becomes `'`.
- Row order uses Kahn's algorithm with a min-heap by id. That gives dependency order with ties broken by id ascending. The reference script used a DFS, which can order ties differently.
- Cycles are found from the ids that Kahn's algorithm cannot place. `check` reports each cycle once, under the slug of its lowest id, and a self-cycle as `cycle T-0001 -> T-0001`.
- `check` only compares the roadmap for staleness when there are no ticket problems, because the roadmap cannot be rendered while tickets are broken.
- Beyond the handoff, `check` also flags a `depends` that is not a list and a `from` that is a list, and the selftest also covers: bad `created`, a bad slug, `|` escaped in titles, a quoted `"Fix #12"` title keeping its `#`, `roadmap` and `new` refusing when a ticket is bad, and zero tickets passing.
- Templates under `skills/ticket/templates/` did not trip `claude plugin validate`, so the move listed in Plan risks is not needed.
