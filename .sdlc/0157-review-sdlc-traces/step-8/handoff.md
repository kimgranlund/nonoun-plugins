## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 8: Ticket reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/tickets.py` (inside the package; a plain `import tickets` there still names the scripts-folder module, since implicit relative imports do not exist): `read(root)` returns `by_slug` = {slug: (id, status)} from `tickets.load(root)` (which includes closed `.NNNN-<slug>` folders), `problems` = `tickets.problems(ts, tickets.config_numbered(root))`, `external` = `tickets.external_branches(root)`, and `notes` = True when `<root>/notes.md` exists. Register the `tickets` cases: a root with `0001-a` (T-0001, ready), `.0002-b` (T-0002, done), and `0003-c` reusing T-0001 yields slug to id and status for all three folders and exactly one problem line holding `duplicate id T-0001`; a root without a config gives `external` empty.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets | grep -q '^ok: tickets: '`
- `grep -q 'tickets.load' plugins/sdlc-lite/scripts/traces/sources/tickets.py && grep -q 'tickets.problems' plugins/sdlc-lite/scripts/traces/sources/tickets.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
