## Task goal
Add a `/ticket` skill backed by `scripts/tickets.py`. It has four commands: `new` stamps a typed ticket with the next id, `roadmap` writes `.sdlc/roadmap.md` from ticket front matter in dependency order, `check` fails on any bad ticket or a stale roadmap, and `selftest` shows that every check failure fires.

## Step 1: /ticket skill and per-type ticket templates
level: L1
## Do
- Create `plugins/sdlc-lite/skills/ticket/templates/{feature,bug,chore,spike,idea}.md`. Copy them from `/Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite/.sdlc/_templates/<type>.md` and make these changes:
  - Each file opens with front matter using the fields in `plugins/sdlc-lite/skills/handoff-format/SKILL.md` ("Ticket front matter"). Keep these placeholder lines exactly, because the script replaces them: `id: T-0000`, `title: ""`, `created: YYYY-MM-DD`. `type:` must equal the file's type.
  - Every template carries `status: proposed`, `size:`, `priority:` and `depends: []`, plus the same inline `# allowed values` comments the feature template has.
  - Keep each template's body sections as in the reference: feature and chore have Goal/Intent/Context/Constraints, bug has Goal/Repro/Expected/Actual/Context/Constraints, spike has Question/Goal/Context/Constraints, idea has Goal/Context/Constraints. Remove any text specific to the gen-ui repo.
- Create `plugins/sdlc-lite/skills/ticket/SKILL.md`:
  - Front matter: `name: ticket`; a description covering stamping a typed ticket with the next id and generating the roadmap, with a NOT clause saying free-text briefs stay with `/handoff`; `argument-hint: new <type> <slug> "title" | roadmap | check`; `allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*)`.
  - Body, as numbered steps:
    1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc $ARGUMENTS`. With no args, run `check`.
    2. On `new`, show the created path and ask the user to fill in the body sections.
    3. On exit 1, report stderr.
  - Rules: never hand-edit `.sdlc/roadmap.md`, and change front matter and then rerun `roadmap`. Front matter `status` is a person's decision; build progress stays with `/board`.
## Acceptance criteria
- `ls plugins/sdlc-lite/skills/ticket/templates/` lists exactly `bug.md chore.md feature.md idea.md spike.md`.
- For each template, `grep -c '^id: T-0000$'`, `grep -c '^title: ""$'` and `grep -c '^created: YYYY-MM-DD$'` each print 1, and `grep '^type:'` shows the file's own type.
- `grep -n 'gen-ui\|svelte\|Panda' plugins/sdlc-lite/skills/ticket/templates/*.md` prints nothing.
- `plugins/sdlc-lite/skills/ticket/SKILL.md` contains `name: ticket`, the `tickets.py` allowed-tools entry, and a line saying the roadmap is never hand-edited.
- `plugins/sdlc-lite/scripts/check.sh` exits 0, including `ok: plugin validate`.

## Plan risks
- This repo's own backlog lives in flat files, `.sdlc/tickets/T-*.md`, not in `.sdlc/<slug>/handoff.md`. The script follows the documented handoff-format layout, so those flat tickets will not show up in a roadmap for this repo. Their ids also overlap task dirs like `ticket-intake-roadmap/` (both T-0002). Scanning both layouts would report duplicate ids. Bringing this repo's backlog under `/ticket` is left as a follow-up.
- `claude plugin validate` might object to non-SKILL `.md` files under `skills/ticket/templates/`. If it does, move the templates to `plugins/sdlc-lite/templates/tickets/` and update the lookup path in Step 2.
- The CLAUDE.md edit could break the regexes in `check.py` that read level tables. Step 3's check.sh criterion catches that.
