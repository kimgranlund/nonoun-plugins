## Task goal
A ticket can carry a domain `area:`, and its status can say `claimed` and `paused`, with the roadmap, board and tracker mapping showing them.

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
