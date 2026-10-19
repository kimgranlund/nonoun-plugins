---
id: T-0016
title: "Opt-in numbered ticket folders (NNNN-<slug>)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
With numbered folders on, `new` names the folder after the id it assigns, `close` does the same for follow-ups, and `check` fails when a folder's NNNN- prefix disagrees with its front matter id.

## Intent
Literal ask: with numbered folders on, `new` names the folder after the id it assigns, `close` does the same for follow-ups, and `check` fails when a folder's NNNN- prefix disagrees with its front matter id.
Deltas:
- How numbered mode is switched on: (gap: ticket offers a flag or a config key; default: both. A `<root>/config` file line `ticket_folders: numbered` turns it on for the repo, and a `--numbered` flag on `new` and `close` turns it on for one call. No config file or any other value means plain slugs, exactly as today.)
- Folder name format: defaulted: `NNNN-<slug>` where NNNN is the 4-digit number of the assigned id (T-0017 → `0017-<slug>`), matching the gen-ui repo.
- What the user types in numbered mode: defaulted: `new <type> <slug>` takes the bare slug; the tool adds the prefix. A slug that already starts with `NNNN-` in numbered mode is an error (no double prefix).
- `close` argument: defaulted: `close` takes the folder name as it exists on disk (`0016-foo` or `foo`); its follow-up tickets get numbered folders when numbered mode is on, each with its own new id.
- When `check` enforces the prefix: (revised after step 3 blocked: an always-on rule rejects plain-mode digit-led slugs like `0007-gamma`, which the Constraints keep legal; default: enforce only in numbered mode, matching the Goal's "with numbered folders on". `check` gains `--numbered`, and `<root>/config` `ticket_folders: numbered` turns it on. In numbered mode every ticket folder whose name matches `^\d{4}-` must carry id `T-<same 4 digits>`; plain-slug folders are not checked for a prefix. In plain mode `check` output is unchanged. `new` and `close` in numbered mode run the same rule on the tickets they write.)
Do: add the opt-in numbered mode to `scripts/tickets.py` (`new`, `close`, `check`), with selftest cases that prove each new behavior and the new check failure fire (including a negative control that plain mode is unchanged); update `skills/ticket/SKILL.md` argument hint and rules, and the tickets.py line in the repo CLAUDE.md and `.claude/agents/sdlc-lite-author.md` if they describe the commands.
Non-goals: renaming this repo's existing `.sdlc/` folders; a `rename`/migrate command; changes to board.py or roadmap output format; making numbered the default.
Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes with new cases covering numbered `new`, numbered `close` follow-ups, the prefix/id mismatch failure, and plain mode unchanged; `plugins/sdlc-lite/scripts/check.sh` passes; `tickets.py check` on this repo's `.sdlc` still passes.

## Context
Requested by the setup-sdlc-lite-generative-ui session. /Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite renamed every ticket folder to `NNNN-<slug>` (`.sdlc/0002-cli-harness/` holds T-0002) so folders list in ticket order; 0.2.2 already accepts these names (SLUG_RE), and check, roadmap and board ID columns pass there. Missing: `new` makes the user type the number by hand, nothing ties prefix to id, and `close` derives follow-up slugs from the first five words. Suggested opt-in: a `--numbered` flag or a `.sdlc/config` key such as `ticket_folders: numbered`. Numbered mode stays opt-in; plain slugs keep working.

## Constraints
Plain-slug behavior of new, close, check, roadmap stays byte-for-byte the same. Existing tickets and the ticket id format (T-NNNN) do not change.
