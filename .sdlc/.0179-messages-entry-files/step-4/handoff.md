## Task goal
A harness that reads `.sdlc/*` learns the ticket and message folder systems from the entry files alone, and a fresh Claude role and a fresh Codex role, given only a path to a message file and no skill, ack it and reply correctly.

## Step 4: Reference and design status updates
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 3 (the design status links its validation doc).

Edit only the named entries and lines, because T-0175 and T-0177 also touched these files. No em dashes.

`docs/maintenance/sdlc-internals.md`, the `scripts/messages.py` entry: append

```
`send` and `reply` call `write_entries` after validation and before delivery. It writes nine entry files (`.gitignore` holding `*`, `AGENTS.md` and `CLAUDE.md` at the mailbox root, and `AGENTS.md` and `CLAUDE.md` in each of `new/`, `read/`, and `done/`) from the inline `ENTRY_TEMPLATE` and `STAGE_TEMPLATES`, rendering `{{scripts}}` as the absolute scripts folder, and rewrites any that differ. The root `AGENTS.md` is the one authoritative mailbox procedure; the messenger agent defers to it. `selftest` adds entry-file cases: written, refreshed, none on a refused send, every command parses against `--help`, and a scripted path-only run with its negative control.
```

Same file, the `scripts/tickets.py` entry: append

```
`write_roadmap` also writes the mailbox entry files under `<root>/messages/` through `messages.write_entries`, creating the folder, and the router's Mailbox line links `messages/AGENTS.md`; `check` does not validate the entry files.
```

`docs/ticket-stages/design.md`: line 3 becomes

```
Version 0.2, 2026-09-30. Built: Option A (the router), the opt-in `tickets/` root, and the message bus (T-0177, T-0178, T-0179). The rest is a proposal.
```

and in the Message bus `Status:` paragraph, the sentence `The entry files with the live run (T-0179) are pending.` becomes

```
The entry files are built in T-0179: `messages.py send` and `reply` and `tickets.py roadmap` write `messages/AGENTS.md` and the three stage entry files, and the live run is in [Messages live run](../validation/messages-live-run.md).
```

`plugins/sdlc-lite/skills/handoff-format/SKILL.md` line 36, the `.sdlc/messages/` row of the layout block, becomes

```
.sdlc/messages/         git-ignored mailbox written by scripts/messages.py: new/, read/, done/ per receiver, shared by worktrees; never committed; its AGENTS.md (the procedures) and CLAUDE.md at the root and in each stage folder are written by messages.py send and tickets.py roadmap
```

`handoff-format` is not preloaded into any role, so no Codex agent regeneration is needed.
### Acceptance criteria
- `f=docs/maintenance/sdlc-internals.md && grep -qF "write_entries" "$f" && grep -qF "scripted path-only run" "$f" && grep -qF "messages.write_entries" "$f" && grep -qF "Mailbox line links" "$f"`
- `grep -qF "validation/messages-live-run.md" docs/ticket-stages/design.md && ! grep -qF "The entry files with the live run (T-0179) are pending." docs/ticket-stages/design.md`
- `grep -E "^\.sdlc/messages/ " plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qF "AGENTS.md"`
- (guard) `git diff "$SDLC_BASE_SHA" -- docs/maintenance/sdlc-internals.md docs/ticket-stages/design.md plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep '^+' | { ! grep -qF "$(printf '\342\200\224')"; }`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- docs/maintenance/sdlc-internals.md docs/ticket-stages/design.md plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/(messages|tickets)\.py|plugins/sdlc-lite/skills/(handoff-format|ticket)/SKILL\.md|docs/README\.md|docs/reports/messages-live-run\.md|docs/reports/messages-live-run/.*|docs/maintenance/sdlc-internals\.md|docs/ticket-stages/design\.md" | { ! grep -q .; }`
