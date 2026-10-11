## Task goal
A ticket can carry a domain `area:`, and its status can say `claimed` and `paused`, with the roadmap, board and tracker mapping showing them.

## Step 1: Ticket vocabulary in tickets.py and board.py
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `.sdlc/AGENTS.md`
### Do
Depends on: none.

Implementation targets, all in `plugins/sdlc-lite/scripts/tickets.py` unless named:
- `ENUMS['status']` (tickets.py:246) becomes, in this order, `('proposed', 'ready', 'claimed', 'paused', 'blocked', 'done', 'dropped')`. The order matters for two reasons. `stage_lines` (tickets.py:1496) prints one `- <stage>: <count>` line per status in ENUMS order. The check error `status=... not in a|b|c` also joins ENUMS. Every status keeps its own stage line (no conditional lines).
- `GLYPH` (tickets.py:255) gains `'claimed': '🟡'` and `'paused': '⏸️'` (U+23F8 U+FE0F). `render` indexes GLYPH, so a status without a glyph raises KeyError.
- `ACTIVE` (tickets.py:1465) becomes `('proposed', 'ready', 'claimed', 'paused', 'blocked')`. The follow-up dedupe in `cmd_close` hardcodes the open-ticket tuple `('proposed', 'ready', 'blocked')` twice (tickets.py:2041 and 2052). Both places use `ACTIVE` instead.
- Validation in `problems()` (tickets.py:1034) runs one way only:
  - `status: claimed` with no non-empty string `claimed_by` fails with a line naming `claimed_by`.
  - `status: paused` with no non-empty string `paused_reason` fails with a line naming `paused_reason`.
  - A `claimed_by:` or `paused_reason:` on a ticket of any other status stays valid and is not validated. Live tickets carry `claimed_by:` on `status: ready` today: the claim procedure at tickets.py:1389-1394 and `plugins/sdlc-lite/skills/run-plan/references/run-rules.md:34` add only that line. The handoff also requires that existing tickets stay valid with no migration.
  - Status is set by hand in the front matter. There is no new claim, release or pause command. No script writes `claimed_by` today: `git grep -n claimed_by -- plugins/sdlc-lite/scripts` hits tickets.py only.
- Area:
  - A new `config_areas(root)` reads `<root>/config` lines of the form `areas: a, b, c`: comma separated, whitespace stripped, blank and `#` lines ignored. This follows the style of `config_numbered` at tickets.py:353.
  - An optional `area:` front matter value must be a non-empty string in that list. Otherwise check fails with a line naming the ticket, the value and the allowed list.
  - With no `areas:` line in config, any `area:` fails with a line saying to add `areas: <name>, ...` to `<root>/config`. An absent `area:` is always valid.
  - Pass the list into `problems()` through a new keyword argument from every caller that has the root (`git grep -n "problems(" -- plugins/sdlc-lite/scripts/tickets.py`).
  - An area is a ticket's domain and is never a lane or branch name (`lane/<ticket>-<slug>`). Say so in the docstring.
- Roadmap (`render`, tickets.py:1337):
  - When at least one ticket has a non-empty `area`, the header is `| ID | Ticket | Title | Type | Area | Size | Pri | Depends on | Status |`. A ticket without an area gets an empty Area cell.
  - With no area anywhere, the output stays byte for byte as today. The precedent is the conditional Budget column in board.py:416-430.
  - A `paused` Status cell is `⏸️ paused (<paused_reason>)`, with `|` escaped as titles are. Every other status renders as today.
- Router:
  - In `stage_lines`, a paused ticket's line ends `, paused: <paused_reason>`, after any `, claimed by ...`.
  - `ROUTER_PROCEDURES` (tickets.py:1381) gains a `Ticket fields:` heading with one line that reads exactly `status: proposed | ready | claimed | paused | blocked | done | dropped`. It also explains `area:` (optional, one of the `areas:` in `config`, not a lane) and `paused_reason:`.
  - In "Claim a ticket", step 2 adds `status: claimed` together with the `claimed_by:` line. Release removes `claimed_by:` and sets `status: ready`. Pause sets `status: paused` with a one-line `paused_reason:`.
  - Remove the sentence that `status` stays a person's decision (tickets.py:1395) only where it now contradicts the claim step.
  - Update the module docstring (tickets.py:185-200) to match. Include the no-migration statement: an absent `area` is valid and every existing status stays valid.
- `plugins/sdlc-lite/scripts/board.py`:
  - `ALWAYS_SHOWN` (board.py:341) gains `claimed` and `paused`. Board's selftest at board.py:948 fails while an ENUMS status is unclassified.
  - The Ticket cell (board.py:440-450, `render`) shows `<status> · <area>` when the ticket has a non-empty `area`, else `<status>` as today.
  - Read the area with a new helper beside `ticket_of` (board.py:307). Leave `ticket_of`'s `(id, status)` tuple unchanged, because budget.py, dispatch.py, fleet_status.py and solo_run.py use it.
  - Update the "Ticket columns" paragraph in board.py's docstring.
- After the code change, regenerate this repo's managed files with `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`. This rewrites `.sdlc/AGENTS.md`. `.sdlc/roadmap.md` stays unchanged because no ticket here has an area.

Contract dependents. Found with `git grep -n "ENUMS\['status'\]\|tickets.ACTIVE\|'proposed', 'ready', 'blocked'" -- plugins` and by reading the selftests:
- The tickets.py selftest pins exact router stage text at tickets.py:4314-4365 and 4417, for example `'- proposed: 1\n  - T-0001 Alpha (alpha)\n- ready: 0\n- blocked: 0\n- done: 0\n'`. It also builds one ticket per status (tickets.py:3676, 4347). Update every pinned stage string to the new stage lines, not only the cited lines.
- The board.py selftest (board.py:948) compares the visibility sets with `tickets.ENUMS['status']`.
- Add tickets.py selftest cases, negative controls included:
  - an unknown area is rejected;
  - an `area:` with no `areas:` line is rejected;
  - `paused` without `paused_reason` is rejected;
  - `claimed` without `claimed_by` is rejected;
  - `claimed_by` on a `ready` ticket stays valid;
  - the Area column appears only when an area exists;
  - the paused reason shows in the roadmap and the router.
- Add a board.py selftest case for the `<status> · <area>` cell.

Left untouched on purpose:
- `steps.py` reads ticket status only as `== 'done'` (steps.py:2023-2025).
- `fleet_collect.py` has no ticket-status counter. `grep -n status plugins/sdlc-lite/scripts/fleet_collect.py` shows only attempt and builder statuses.
- `fleet_status.py` treats every status other than `blocked`, `done` and `dropped` as open work (fleet_status.py:717-744). Its schema types `ticket_status` as a free string (`plugins/sdlc-lite/skills/fleet-status/resources/fleet-status.schema.json:190`). So `claimed` behaves like `ready`, and `paused` is not a Needs-you item because it carries its reason.
- `fanout.py`, `dispatch.py`, `solo_run.py`, `supervisor.py` and `plan_done.py` gate on no open status. `git grep -nE "get\('status'\)"` on them hits only `('done', 'dropped')` and attempt states.
- The ticket templates and docs belong to step 2.

The fixture criteria below build a throwaway ticket root in a fresh `mktemp -d` folder under `$SDLC_TMP_WORKTREES` (gitignored through `.worktrees/`), falling back to `$TMPDIR`. The root path lives in the variable `t`, so no criterion spells a ticket folder path. Each fixture writes one ticket, `T-0001`, in the folder `0001-a` of that root, and a `config` with `areas: ui-kit, back-end`.

Validation scope: the fixture criteria below, `tickets.py selftest`, `board.py selftest`, and `tickets.py --root .sdlc check`. `check.sh` runs in step 2.
### Acceptance criteria
- (red) An unknown area is rejected: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $t" && fm ready "area: nope\n" && $T roadmap >/dev/null 2>&1; $T check >/dev/null 2>"$d/e"; r=$?; test $r -eq 1 && grep -q "area" "$d/e"`
- (red) A listed area shows in an Area column: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $t" && fm ready "area: ui-kit\n" && $T roadmap >/dev/null && $T check >/dev/null && grep -q "| Area |" "$t/roadmap.md" && grep -qF "| ui-kit |" "$t/roadmap.md"`
- (red) `paused` without a reason is rejected naming `paused_reason`: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $t" && fm paused "" && $T roadmap >/dev/null 2>&1; $T check >/dev/null 2>"$d/e"; r=$?; test $r -eq 1 && grep -q paused_reason "$d/e"`
- (red) `paused` with a reason passes and the reason shows in the roadmap: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $t" && fm paused "paused_reason: waiting on vendor\n" && $T roadmap >/dev/null && $T check >/dev/null && grep -qF "waiting on vendor" "$t/roadmap.md"`
- (red) `claimed` without `claimed_by` is rejected naming `claimed_by`: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $t" && fm claimed "" && $T roadmap >/dev/null 2>&1; $T check >/dev/null 2>"$d/e"; r=$?; test $r -eq 1 && grep -q claimed_by "$d/e"`
- (red) `claimed` with `claimed_by` passes and the router counts it: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $t" && fm claimed "claimed_by: claude 2026-10-11\n" && $T roadmap >/dev/null && $T check >/dev/null && grep -qE "^- claimed: 1$" "$t/AGENTS.md"`
- (red) The board Ticket cell shows status and area: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && fm claimed "claimed_by: claude 2026-10-11\narea: ui-kit\n" && SDLC_BOARD_STATE_DIR="$d/bs" python3 plugins/sdlc-lite/scripts/board.py --root "$t" | grep -F "T-0001" | grep -qF "claimed · ui-kit"`
- (red) This repo's router lists the vocabulary: `grep -qF "status: proposed | ready | claimed | paused | blocked | done | dropped" .sdlc/AGENTS.md`
- (guard) A root with no area keeps today's roadmap header: `d=$(b="${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}"; mkdir -p "$b" && mktemp -d "$b/t0444.XXXXXX") && t="$d/.sdlc" && mkdir -p "$t/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$t/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$t/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $t" && fm ready "" && $T roadmap >/dev/null && $T check >/dev/null && grep -qF "| ID | Ticket | Title | Type | Size | Pri | Depends on | Status |" "$t/roadmap.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest && python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) Only the two scripts changed outside `.sdlc`: `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/scripts/board.py); test -z "$out"`
