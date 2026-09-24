---
id: T-0016
title: "Opt-in numbered ticket folders (NNNN-<slug>)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
With numbered folders on, `new` names the folder after the id it assigns, `close` does the same for follow-ups, and `check` fails when a folder's NNNN- prefix disagrees with its front matter id.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Requested by the setup-sdlc-lite-generative-ui session. /Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite renamed every ticket folder to `NNNN-<slug>` (`.sdlc/0002-cli-harness/` holds T-0002) so folders list in ticket order; 0.2.2 already accepts these names (SLUG_RE), and check, roadmap and board ID columns pass there. Missing: `new` makes the user type the number by hand, nothing ties prefix to id, and `close` derives follow-up slugs from the first five words. Suggested opt-in: a `--numbered` flag or a `.sdlc/config` key such as `ticket_folders: numbered`. Numbered mode stays opt-in; plain slugs keep working.

## Constraints
What must not change. "None" if none.
