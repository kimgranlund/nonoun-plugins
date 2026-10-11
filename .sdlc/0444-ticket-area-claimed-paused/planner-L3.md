<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
A ticket can carry a validated domain `area:` and the statuses `claimed` (requires `claimed_by:`) and `paused` (requires `paused_reason:`), shown by `tickets.py roadmap`, the router block and `/board`, with a Linear and GitHub mapping table, a no-migration statement, and `check.sh` green.

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
  - The status line (line 91) becomes `status: proposed|ready|claimed|paused|blocked|done|dropped`.
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
- `docs/references/sdlc-internals.md`: in the `scripts/tickets.py` section (line 53 onward) and the board.py sentence in `## Feed` (line 47), name:
  - `area:` with the `areas:` config line;
  - the `claimed` and `paused` statuses with `claimed_by:` and `paused_reason:`;
  - the conditional Area roadmap column;
  - the board Ticket cell `<status> · <area>`.
- Left untouched on purpose: `docs/specs/ticket-stages/design.md:13` lists the five statuses as a fact of that dated design (Version 0.2, 2026-09-30). It records the state the design was written against; the live vocabulary is the router block, the handoff-format skill and the ticket templates.
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
- (guard) Only the named files changed outside `.sdlc`: `out=$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/scripts/board.py -e plugins/sdlc-lite/skills/ticket/SKILL.md -e plugins/sdlc-lite/skills/ticket/templates/bug.md -e plugins/sdlc-lite/skills/ticket/templates/chore.md -e plugins/sdlc-lite/skills/ticket/templates/feature.md -e plugins/sdlc-lite/skills/ticket/templates/idea.md -e plugins/sdlc-lite/skills/ticket/templates/spike.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e docs/specs/sdlc-lite/lane-lifecycle.md -e docs/references/sdlc-internals.md); test -z "$out"`

## Assumptions
- This replans planner-L2.md to fix one plan defect. `steps.py lint` refused the step 1 handoff because its fixture spans wrote the ticket folder as a literal path under `$d` that starts with the `.sdlc` folder name. The cited-path lint (`cited_sdlc_paths`, steps.py:1420) reads that as a repo path. The fix: every fixture keeps its ticket root in `t="$d/.sdlc"` and writes `"$t/0001-a/handoff.md"`, so no criterion or Do line spells a `.sdlc/<dir>` path that does not exist. Verified by `steps.py lint` on simulated step-1 and step-2 handoffs (`steps lint: ok`) and by a negative control: the superseded step-1 handoff placed in a step dir reproduces both `cited path does not exist` refusals. No step had passed, so both steps keep their numbers and their Do text, apart from the corrections listed here.
- Each fixture span starts with `d=$(...)`, an assignment holding `$(`, so `steps.is_command` reads it as a command. A first draft opened with `b="..." && mkdir -p`, and that form was read as prose: `steps.line_spans` returned no span, and `specgate.py red --step 1` counted 1 of 8 (red) spans. The final form counts 8 of 8. The `mkdir -p` inside the substitution handles a `$SDLC_TMP_WORKTREES` that is unset or not yet created (run.sh:35 says run.sh does not create it). A probe with a nonexistent nested dir passed.
- Fixture folders never show up in the scope guards: `git check-ignore -v .worktrees/tmp/x` matches `.gitignore:10` (`.worktrees/`), and with `$SDLC_TMP_WORKTREES` unset the fixtures go to `$TMPDIR`, outside the tree.
- The scope guards use the `grep -vxF -e <path>` form, so `steps.scope_entries` reads every allowed path (verified: 2 entries in step 1, 11 in step 2). The L2 form `(tickets|board)` was split into broken entries (see the lane line in `skips.md`).
- Status is set by hand, and no script writes `claimed_by` or the status on a claim: verified by `git grep -n claimed_by -- plugins/sdlc-lite/scripts` (tickets.py only) and `plugins/sdlc-lite/skills/run-plan/references/run-rules.md:34`.
- Validation runs one way, so live claims on `status: ready` stay valid: verified by tickets.py:1389-1395 (the claim procedure adds only `claimed_by:`) and the handoff constraint "Existing tickets stay valid with no migration required".
- An `area:` with no `areas:` config line is rejected, because the handoff says the area comes "from a list kept in .sdlc/config". This repo's `.sdlc/config` gets no `areas:` line: the handoff's example list names consumer-repo domains, and no ticket here has an `area:`.
- The Area roadmap column is conditional, so this repo's `.sdlc/roadmap.md` stays byte-identical: the precedent is board.py:416-430 (Budget column only when a budget exists).
- No ticket-status gate exists in steps.py, fleet_collect.py, fanout.py, dispatch.py, solo_run.py, supervisor.py or plan_done.py (planner-L2 search, `git grep -nE "get\('status'\)"`). The status-vocabulary search `git grep -nE "proposed ?\| ?ready ?\| ?blocked|'proposed', 'ready'"`, run outside `.sdlc` and `docs/reports`, hits only the files the steps change plus `docs/specs/ticket-stages/design.md:13`, which step 2 leaves untouched on purpose.
- Probes ran at HEAD 222f817e with `SDLC_BASE_SHA=HEAD`:
  - Step 1: all eight (red) criteria exit 1 because the behavior is missing:
    - an unknown area passes check (rc 0);
    - `paused` and `claimed` fail only as `status=... not in proposed|ready|blocked|done|dropped`, naming neither `paused_reason` nor `claimed_by`;
    - the roadmap has no Area column;
    - the board Ticket cell reads `claimed`;
    - the router has no vocabulary line.
  - Step 1 guards exit 0: the no-area header guard, `tickets.py selftest` plus `board.py selftest` (45 s), `tickets.py --root .sdlc check`, and the scope guard. The tree was unchanged after each run.
  - Step 2: the five (red) criteria exit 1. The guards `tickets.py --root .sdlc check`, `git diff --check`, `check-packaging.py` and the scope guard exit 0. `check.sh` was not run (step 2 owns it).
  - Each guard was seen red in its own command shape. The header grep returns 1 on a header that has an Area column. Each scope guard returns 1 when one extra path is fed in.
  - `steps.py lint` and `specgate.py check` pass on the plan. `specgate.py red` finds every (red) span red now: 8 of 8 in step 1 and 5 of 5 in step 2.
  - `steps.py split` writes only `## Task goal`, the goal and the step block into a step handoff (steps.py:1738). It does not copy the task handoff's `## Plan review` text, which spells the old fixture path, so that text cannot trip the link lint again.
- check.sh took 15m21s on record (`.sdlc/.0438-executor-live-run-fixes/verifier-L2.md:7`, "rc=0 after 15m21s"; planner-L2 cited the wrong file). `guard timeout: 2800` is about three times that.

## Risks
- Every lane that touches tickets regenerates `.sdlc/AGENTS.md`. If a parallel lane lands a router block written by the old code, that block goes stale after this merge. `tickets.py check` (run by check.sh) then needs one `tickets.py --root .sdlc roadmap` rerun on the integration branch. Consumer repos see `router block stale` once after upgrading, until they run `roadmap`.
- The tickets.py selftest pins router stage text in more places than the ones named. The builder must update every pinned stage string.
- The `⏸️` glyph carries a variation selector, so a terminal or table renderer may show it at a different width. Cosmetic only.
- `fanout.py prep` and the run-plan rules still claim with `claimed_by:` alone and leave `status: ready`. That stays valid, but the roadmap will not show `claimed` for those lanes until a follow-up changes them.
- `docs/specs/ticket-stages/design.md:13` still lists five statuses as a fact of that dated design. Cosmetic; a follow-up can add a dated note.
- check.sh was not run at plan time (about 15 minutes). If it is red at base, step 2 reports `inherited red`.
- The probe fixtures and the draft sit under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout/b/.worktrees/tmp/0444-planner-L3/`. They were left in place because this run never deletes.
