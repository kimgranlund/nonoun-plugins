<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
A ticket can carry a validated domain `area:` and two new statuses: `claimed` (requires `claimed_by:`) and `paused` (requires `paused_reason:`). `tickets.py roadmap`, the router block and `/board` show them. A Linear and GitHub mapping table and a no-migration statement are added, and `check.sh` stays green.

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
  - A `claimed_by:` or `paused_reason:` on a ticket of any other status stays valid and is not validated. Live tickets carry `claimed_by:` on `status: ready` today: the claim procedure at tickets.py:1389-1394 and `skills/run-plan/references/run-rules.md:34` add only that line. The handoff also requires that existing tickets stay valid with no migration.
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
  - Remove the sentence that `status` stays a person's decision only where it now contradicts the claim step.
  - Update the module docstring (tickets.py:185-200) to match. Include the no-migration statement: an absent `area` is valid and every existing status stays valid.
- `plugins/sdlc-lite/scripts/board.py`:
  - `ALWAYS_SHOWN` (board.py:341) gains `claimed` and `paused`. Board's selftest at board.py:948 fails while an ENUMS status is unclassified.
  - The Ticket cell (board.py:440-450, `render`) shows `<status> · <area>` when the ticket has a non-empty `area`, else `<status>` as today.
  - Read the area with a new helper beside `ticket_of` (board.py:307). Leave `ticket_of`'s `(id, status)` tuple unchanged, because budget.py, dispatch.py, fleet_status.py and solo_run.py use it.
  - Update the "Ticket columns" paragraph in board.py's docstring.
- After the code change, regenerate this repo's managed files with `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`. This rewrites `.sdlc/AGENTS.md`. `.sdlc/roadmap.md` stays unchanged because no ticket here has an area.

Contract dependents. Found with `git grep -n "ENUMS\['status'\]\|tickets.ACTIVE\|'proposed', 'ready', 'blocked'" -- plugins` and by reading the selftests:
- The tickets.py selftest pins exact router stage text at tickets.py:4314-4365, for example `'- proposed: 1\n  - T-0001 Alpha (alpha)\n- ready: 0\n- blocked: 0\n- done: 0\n'`. It also builds one ticket per status (tickets.py:3676, 4347). Update those expectations to the new stage lines.
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
- `fleet_status.py` treats every status other than `blocked`, `done` and `dropped` as open work (fleet_status.py:717-744). Its schema types `ticket_status` as a free string (`skills/fleet-status/resources/fleet-status.schema.json:190`). So `claimed` behaves like `ready`, and `paused` is not a Needs-you item because it carries its reason.
- `fanout.py`, `dispatch.py`, `solo_run.py`, `supervisor.py` and `plan_done.py` gate on no open status. `git grep -nE "get\('status'\)"` on them hits only `('done', 'dropped')` and attempt states.
- The ticket templates and docs belong to step 2.

Validation scope: the fixture criteria below, `tickets.py selftest`, `board.py selftest`, and `tickets.py --root .sdlc check`. `check.sh` runs in step 2.
### Acceptance criteria
- (red) An unknown area is rejected: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $d/.sdlc" && fm ready "area: nope\n" && $T roadmap >/dev/null 2>&1; $T check >/dev/null 2>"$d/e"; r=$?; test $r -eq 1 && grep -q "area" "$d/e"`
- (red) A listed area shows in an Area column: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $d/.sdlc" && fm ready "area: ui-kit\n" && $T roadmap >/dev/null && $T check >/dev/null && grep -q "| Area |" "$d/.sdlc/roadmap.md" && grep -qF "| ui-kit |" "$d/.sdlc/roadmap.md"`
- (red) `paused` without a reason is rejected naming `paused_reason`: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $d/.sdlc" && fm paused "" && $T roadmap >/dev/null 2>&1; $T check >/dev/null 2>"$d/e"; r=$?; test $r -eq 1 && grep -q paused_reason "$d/e"`
- (red) `paused` with a reason passes and the reason shows in the roadmap: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $d/.sdlc" && fm paused "paused_reason: waiting on vendor\n" && $T roadmap >/dev/null && $T check >/dev/null && grep -qF "waiting on vendor" "$d/.sdlc/roadmap.md"`
- (red) `claimed` without `claimed_by` is rejected naming `claimed_by`: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $d/.sdlc" && fm claimed "" && $T roadmap >/dev/null 2>&1; $T check >/dev/null 2>"$d/e"; r=$?; test $r -eq 1 && grep -q claimed_by "$d/e"`
- (red) `claimed` with `claimed_by` passes and the router counts it: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $d/.sdlc" && fm claimed "claimed_by: claude 2026-10-11\n" && $T roadmap >/dev/null && $T check >/dev/null && grep -qE "^- claimed: 1$" "$d/.sdlc/AGENTS.md"`
- (red) The board Ticket cell shows status and area: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && fm claimed "claimed_by: claude 2026-10-11\narea: ui-kit\n" && SDLC_BOARD_STATE_DIR="$d/bs" python3 plugins/sdlc-lite/scripts/board.py --root "$d/.sdlc" | grep -F "T-0001" | grep -qF "claimed · ui-kit"`
- (red) This repo's router lists the vocabulary: `grep -qF "status: proposed | ready | claimed | paused | blocked | done | dropped" .sdlc/AGENTS.md`
- (guard) A root with no area keeps today's roadmap header: `d=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/t0444.XXXXXX") && mkdir -p "$d/.sdlc/0001-a" && printf "ticket_folders: numbered\nlayout: flat\nareas: ui-kit, back-end\n" > "$d/.sdlc/config" && fm() { printf -- "---\nid: T-0001\ntitle: \"A\"\ntype: feature\nstatus: %s\nsize: L2\npriority: P2\ndepends: []\ncreated: 2026-10-11\n%b---\n\n## Goal\nx\n" "$1" "$2" > "$d/.sdlc/0001-a/handoff.md"; } && T="python3 plugins/sdlc-lite/scripts/tickets.py --root $d/.sdlc" && fm ready "" && $T roadmap >/dev/null && $T check >/dev/null && grep -qF "| ID | Ticket | Title | Type | Size | Pri | Depends on | Status |" "$d/.sdlc/roadmap.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest && python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) Only the two scripts changed outside `.sdlc`: `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/(tickets|board)\.py"); test -z "$out"`

## Step 2: Docs, templates, tracker mapping, gates green
level: L2
guard timeout: 2800
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/specs/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: step 1. The vocabulary, the `areas:` config line and the render formats are settled there: copy them, do not restate them differently.

- `plugins/sdlc-lite/skills/ticket/templates/{bug,chore,feature,idea,spike}.md`: the status comment becomes `# proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)`. Add no `area:` line to the templates, because area is optional and needs an `areas:` config line.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (front matter block at lines 85-104 and the paragraphs after it):
  - The status line becomes `status: proposed|ready|claimed|paused|blocked|done|dropped`.
  - Add the optional line `area: <name>   # optional, one of the areas: line in .sdlc/config; a domain, never a lane`. It must start with `area: `.
  - Add the line `paused_reason: <one line>   # required when status is paused`.
  - Say that `claimed` requires `claimed_by:`.
  - Update the paragraph at line 109 that calls status a person's decision, so it names claimed and paused.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add one short paragraph naming `area:` with the `areas:` config line, `claimed` with `claimed_by:`, and `paused` with `paused_reason:`. It also says existing tickets need no migration.
- `docs/specs/sdlc-lite/lane-lifecycle.md`: add `### 8.2 Ticket fields on Linear and GitHub` right after section 8.1 (before `## 9.`), with a mapping table holding these rows:

  | Field | Linear | GitHub |
  |---|---|---|
  | status proposed | Backlog | open, label `status:proposed` |
  | status ready | Todo | open, label `status:ready` |
  | status claimed | In Progress, with the assignee | open, the assignee, label `status:claimed` |
  | status paused | a `Paused` state when the team has one, else Backlog with label `paused` | open, label `status:paused`, the `paused_reason` as a comment |
  | status blocked | label `blocked` (Linear has no default blocked state) | open, label `status:blocked` |
  | status done | Done | closed as completed |
  | status dropped | Canceled | closed as not planned |
  | area | a team when the workspace has one team per area, else label `area:<name>` | label `area:<name>` |
  | size L1 to L4 | estimate 1 to 4 on the linear scale | labels `size:L1` to `size:L4` |

  L5 is reserved and unmapped. State that this is mapping text only and no integration is built (a handoff non-goal). Add a no-migration statement: existing tickets need no migration, an absent `area` is valid and every existing status stays valid. Do not use the one-letter size words, because check.py's RETIRED_VOCAB item flags them.
- `docs/references/sdlc-internals.md`: in the `## scripts/tickets.py` entry (line 53 onward) and the board.py sentence in `## Feed` (line 47), name:
  - `area:` with the `areas:` config line;
  - the `claimed` and `paused` statuses with `claimed_by:` and `paused_reason:`;
  - the conditional Area roadmap column;
  - the board Ticket cell `<status> · <area>`.
- Gates: run `bash plugins/sdlc-lite/scripts/check.sh` (about 15 minutes on record) and `python3 scripts/check-packaging.py`. Fix any red that step 1 or this step introduced, within the scope criterion. A gate already red at the build-start HEAD is reported as `inherited red`.
### Acceptance criteria
- (red) The spec has a mapping section with every field and a no-migration statement: `s=$(awk '/^### 8\.2 /{f=1} /^## /{f=0} f' docs/specs/sdlc-lite/lane-lifecycle.md) && test -n "$s" && for w in Linear GitHub claimed paused area L4 estimate; do printf "%s\n" "$s" | grep -qF "$w" || exit 1; done && printf "%s\n" "$s" | grep -qi "no migration"`
- (red) `grep -qF "status: proposed|ready|claimed|paused|blocked|done|dropped" plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qE "^area: " plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (red) `for f in bug chore feature idea spike; do grep -qF "# proposed | ready | claimed | paused | blocked | done | dropped" plugins/sdlc-lite/skills/ticket/templates/$f.md || exit 1; done`
- (red) `grep -qF "paused_reason" plugins/sdlc-lite/skills/ticket/SKILL.md && grep -qF "areas:" plugins/sdlc-lite/skills/ticket/SKILL.md`
- (red) `grep -qF "paused_reason" docs/references/sdlc-internals.md && grep -qF "areas:" docs/references/sdlc-internals.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) Only the named files changed outside `.sdlc`: `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/(tickets|board)\.py|plugins/sdlc-lite/skills/(ticket|handoff-format)/.+\.md|docs/specs/sdlc-lite/lane-lifecycle\.md|docs/references/sdlc-internals\.md"); test -z "$out"`

## Assumptions
- Status is set by hand, and no script writes `claimed_by` or the status on a claim: verified by `git grep -n claimed_by -- plugins/sdlc-lite/scripts` (tickets.py only) and `skills/run-plan/references/run-rules.md:34`.
- Validation runs one way, so live claims on `status: ready` stay valid: verified by tickets.py:200 (`claimed_by` is not validated) and the handoff constraint "Existing tickets stay valid with no migration required".
- An `area:` with no `areas:` config line is rejected, because the handoff says the area comes "from a list kept in .sdlc/config". This is a planner decision. This repo's `.sdlc/config` (only `ticket_folders: numbered`) gets no `areas:` line: the handoff's example list (ui-kit, front-end, back-end, data-lake, agent-os) names consumer-repo domains, and no ticket here has an `area:`.
- The Area roadmap column is conditional, so this repo's `.sdlc/roadmap.md` stays byte-identical: the precedent is board.py:416-430 (Budget column only when a budget exists), and step 1's header guard was green at HEAD.
- No ticket-status gate exists in steps.py, fleet_collect.py, fanout.py, dispatch.py, solo_run.py, supervisor.py or plan_done.py: verified by `git grep -nE "get\('status'\)"` on those files and by the fleet-status schema (`ticket_status` is `{"type": "string"}`).
- Every criterion was run at HEAD, except check.sh:
  - The seven `(red)` fixture spans and the router grep exit 1 because the behavior is missing. At HEAD an unknown area passes check, and `paused` and `claimed` fail only as "not in proposed|ready|blocked|done|dropped".
  - Step 2's five `(red)` doc criteria exit 1.
  - These guards exit 0 and left the tree unchanged: the header guard, `tickets.py selftest` (42 s), `board.py selftest`, `tickets.py --root .sdlc check`, `git diff --check`, `check-packaging.py`, and both scope guards.
  - The draft passed `steps.py lint`.
- check.sh takes about 15m21s, recorded in `.sdlc/.0432-plan-done-script/verifier-L3.md` ("rc=0 after 15m21s"). `guard timeout: 2800` is about three times that.

## Risks
- Every lane that touches tickets regenerates `.sdlc/AGENTS.md`. If a parallel lane lands a router block written by the old code, it goes stale after this merge. `tickets.py check` (run by check.sh) then needs one `tickets.py --root .sdlc roadmap` rerun on the integration branch. Consumer repos see `router block stale` once after upgrading, until they run `roadmap`.
- The tickets.py selftest pins router stage text in more places than the ones named (tickets.py:4314-4365, 4417). The builder must update every pinned stage string, not only the cited lines.
- The `⏸️` glyph carries a variation selector, so a terminal or table renderer may show it at a different width. Cosmetic only.
- `fanout.py prep` and the run-plan rules still claim with `claimed_by:` alone and leave `status: ready`. That stays valid, but the roadmap will not show `claimed` for those lanes until a follow-up changes them.
- check.sh was not run at plan time (15 minutes). If it is red at base, step 2 reports `inherited red`.
- The draft plan and the probe fixtures sit under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/.worktrees/tmp/0444-planner-L2/`. They were left in place, because this run never deletes; `run.sh` removes that directory when the run ends.
