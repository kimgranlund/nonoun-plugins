---
name: ticket
description: Stamp a typed ticket with the next id, or generate .sdlc/roadmap.md from ticket front matter in dependency order. NOT for free-text briefs, which stay with /handoff.
argument-hint: new <type> <slug> "title" [--numbered] | close <slug> [--force] [--numbered] | roadmap [--numbered] | check [--numbered]
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*)
---
Arguments: `$ARGUMENTS`

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc $ARGUMENTS`. With no args, run `check`.
2. On `new`, show the created path and ask the user to fill in the body sections.
3. On exit 1, report stderr.
4. `close <slug> [--force]` is normally run by `/file` after the filer, not by hand.

Rules:
- Numbered folders are opt-in, by `--numbered` on `new`, `close`, `roadmap`, or `check` for one call, or a `ticket_folders: numbered` line in `.sdlc/config` for the repo (a successful `new --numbered` or `close --numbered` appends that line when it is missing, so later plain calls stay numbered; plain `check` warns, without failing, when every folder has an `NNNN-` prefix but the config lacks the line); in numbered mode `new` names the folder `NNNN-<slug>` after the id it assigns (give the bare slug), `close` does the same for each follow-up with its own id, and `check` fails and `roadmap` refuses (writing nothing) on a `NNNN-` folder whose id is not `T-NNNN`; without either, plain slugs, as before.
- Never hand-edit `.sdlc/roadmap.md`. Change front matter and then rerun `roadmap`.
- Front matter `status` is a person's decision; build progress stays with `/board`.
