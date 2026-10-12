## Task goal
One script owns the lane lifecycle: open, close, sweep, list, check and port, with the landed test and truth table of the design.

## Step 2: check.sh line, internals entry, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: step 1.

1. In `plugins/sdlc-lite/scripts/check.sh`, add `python3 "$root/scripts/lanes.py" selftest || fail=1` among the other selftest lines, right after the `gate_lock.py` line. Also add `lanes.py` to the selftest list in the header comment. Only one writer at a time may change this file (handoff Context).
2. In `docs/references/sdlc-internals.md`, add a section headed ``## `scripts/lanes.py` ``. This matches the file's heading form, for example ``## `scripts/gate_lock.py` ``. Place it before the `scripts/fanout.py` section. The section:
   - states what the script owns;
   - says the kinds table, truth table, close steps and record fields live in the `lanes.py` docstring (`python3 plugins/sdlc-lite/scripts/lanes.py --help`), and copies no table (section 5);
   - names the importable API: `open_lane`, `close_lane`, `sweep`, `list_lanes` and `still_open`;
   - notes that ticket A2 adds the worktree lock and worktree config;
   - lists each `.sdlc/config` key in the form `<key>: <value>` with its default: `lanes_root:`, `lane_into:`, `lane_setup:`, `lane_ports:`, `lane_stale_days:`, `lane_min_age_hours:`, `lane_keep:`, `lane_names:` and `lane_sweep:` (fanout reads the last one, ticket B);
   - links the design `docs/specs/sdlc-lite/lane-lifecycle.md` with a relative link that resolves.
3. Run every gate:
   - `bash plugins/sdlc-lite/scripts/check.sh`, which runs `check.py`, `docs_check.py --root`, every selftest including the new line, shellcheck and plugin validate;
   - `python3 scripts/check-packaging.py`.

   Fix any red that step 1 or this step introduced, and only in lanes.py, check.sh or the internals entry. A gate already red at the build-start HEAD is reported as Status `inherited red`.

Left unchanged on purpose:
- The `## Lanes` section of `plugins/sdlc-lite/AGENTS.md` still names `~/.claude/lane/sweep.py` (line 43). Ticket G replaces it (17.9 row G).
- No `check.py` item is added. The ticket asks for none, and C14 lands with ticket G.
### Acceptance criteria
- (red) `grep -qF 'lanes.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- (red) `grep -qE '^## .scripts/lanes\.py.$' docs/references/sdlc-internals.md`
- (red) `for k in lanes_root lane_into lane_setup lane_ports lane_stale_days lane_min_age_hours lane_keep lane_names lane_sweep; do grep -qF "$k:" docs/references/sdlc-internals.md || exit 1; done`
- (red) `grep -qF 'lanes.py --help' docs/references/sdlc-internals.md`
- `python3 scripts/check-packaging.py`
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/lanes.py -e plugins/sdlc-lite/scripts/check.sh -e docs/references/sdlc-internals.md)"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
