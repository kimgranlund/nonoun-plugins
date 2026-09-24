---
name: ticket
description: Stamp a typed ticket with the next id, or generate .sdlc/roadmap.md from ticket front matter in dependency order. NOT for free-text briefs, which stay with /handoff.
argument-hint: new <type> <slug> "title" | close <slug> [--force] | roadmap | check
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*)
---
Arguments: `$ARGUMENTS`

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc $ARGUMENTS`. With no args, run `check`.
2. On `new`, show the created path and ask the user to fill in the body sections.
3. On exit 1, report stderr.
4. `close <slug> [--force]` is normally run by `/file` after the filer, not by hand.

Rules:
- Never hand-edit `.sdlc/roadmap.md`. Change front matter and then rerun `roadmap`.
- Front matter `status` is a person's decision; build progress stays with `/board`.
