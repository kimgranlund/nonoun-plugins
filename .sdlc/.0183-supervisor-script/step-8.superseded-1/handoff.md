## Task goal
A deterministic script, with no model call, that notices new mail for a harness whose host is idle and resumes that host from a headless call, inside hard limits, and can be stopped.

## Step 8: Router line, implementation reference, layout list, and status lines
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `.sdlc/AGENTS.md`
### Do
Depends on: steps 1 to 7. The docs describe the behavior as the live run left it.

1. `plugins/sdlc-lite/scripts/tickets.py`:
   - In `ROUTER_TEMPLATE`, right after the `- Mailbox:` line, add:

     `- Supervisor: `supervisor/` holds the idle-host watcher's limits, host map, and status once `python3 <plugin-root>/scripts/supervisor.py init` creates it; follow `supervisor/AGENTS.md` to start, stop, or check the watcher.`

   - In the module docstring paragraph that starts `write_roadmap also writes the mailbox entry files`, add the sentence: `The router's Supervisor line links supervisor/AGENTS.md, which supervisor.py init writes; roadmap never creates that folder.`
   - In the selftest, next to `router: the router links messages/AGENTS.md` (line 3622), add `expect('router: the router links supervisor/AGENTS.md', ...)`, checking a `- Supervisor:` line holding `supervisor/AGENTS.md` in `block_of(rm / 'AGENTS.md')`.
2. Regenerate this repo's router with `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`.
   - Contract dependents: `.sdlc/AGENTS.md`, kept current by this regeneration (`check` fails on a stale block), plus `tickets.py selftest` and `tickets.py --root .sdlc check`, both run below.
   - Left untouched on purpose:
     - `onboard.py`'s root template: the supervisor folder ignores its own runtime files through the `.gitignore` that `init` writes, so a consumer's root entry needs no new rule, and changing the template moves its version and digest.
     - `messages.py` `ENTRY_TEMPLATE`: its statements about subagents and `wait` stay true, and the router line covers discovery. Also a ticket non-goal.
3. `docs/maintenance/sdlc-internals.md`:
   - Add a section `## `scripts/supervisor.py`` after the `messages.py` section. It holds one paragraph in the same style, covering:
     - commands;
     - the folder beside the mailbox, its files, and its git-ignore;
     - limits with defaults, floors, and caps;
     - modes and argv;
     - the D4 prompt with its Claude Code sentence;
     - the env scrub;
     - the D8 decision order;
     - success and stranded mail;
     - backoff and `failed`;
     - depth;
     - active signals;
     - `status.json` fields;
     - selftest coverage with its controls.
   - In the `tickets.py` paragraph, after the mailbox sentence, add the same "The router's Supervisor line links ..." sentence.
4. `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: in the layout block, after the `.sdlc/messages/` line, add:

   `.sdlc/supervisor/       idle-host watcher folder beside the mailbox (the main checkout's, shared by worktrees), written by scripts/supervisor.py init: AGENTS.md and CLAUDE.md (the procedures), limits.json, and the git-ignored hosts.local.json, status.json, state.json, lock, STOP, and wakes/ (its own .gitignore lists them)`
5. `plugins/sdlc-lite/AGENTS.md`:
   - Under Verification add `- Idle-host watcher: `python3 plugins/sdlc-lite/scripts/supervisor.py selftest`.`.
   - Under Behavioral invariants add `- `scripts/supervisor.py` never calls a model and never touches a message file; wakes run from fixed argument lists. Its folder contract is the `AGENTS.md` that `supervisor.py init` writes.`
6. Status lines:
   - `docs/README.md` line 11 becomes `- [Idle-host watcher design](ticket-stages/watcher-design.md): the external watcher, built as plugins/sdlc-lite/scripts/supervisor.py (T-0183), that resumes an idle host when a message arrives, with its limits and validation plan.`
   - `docs/ticket-stages/README.md` line 6 becomes `- [Idle-host watcher design](watcher-design.md): the external process, built as plugins/sdlc-lite/scripts/supervisor.py (T-0183), that resumes an idle host when a message arrives, with its safety limits and validation plan.`
   - In `docs/ticket-stages/watcher-design.md`, the header line keeps its `Version 0.2, 2026-10-01.` start. Its status sentence becomes `Built in T-0183 as plugins/sdlc-lite/scripts/supervisor.py; live run in ../validation/supervisor-live-run.md.`, written as a link.
7. No em dash in any file this step touches.
### Acceptance criteria
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import tickets; assert any(l.startswith("- Supervisor:") and "supervisor/AGENTS.md" in l and "scripts/supervisor.py init" in l for l in tickets.ROUTER_TEMPLATE.splitlines())'`
- `grep -E "^- Supervisor: " .sdlc/AGENTS.md | grep -qF "supervisor/AGENTS.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `out=$(python3 plugins/sdlc-lite/scripts/tickets.py selftest) && test "$(printf '%s\n' "$out" | tail -n 1)" = "tickets selftest: PASS" && grep -qF "router: the router links supervisor/AGENTS.md" plugins/sdlc-lite/scripts/tickets.py && grep -qF "Supervisor line links" plugins/sdlc-lite/scripts/tickets.py`
- `grep -qE "^## .scripts/supervisor\.py.$" docs/maintenance/sdlc-internals.md && grep -qF "Supervisor line links" docs/maintenance/sdlc-internals.md`
- `grep -qE "^\.sdlc/supervisor/ " plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF "supervisor.py selftest" plugins/sdlc-lite/AGENTS.md`
- `grep -F "ticket-stages/watcher-design.md" docs/README.md | grep -qF "built as" && grep -F "(watcher-design.md)" docs/ticket-stages/README.md | grep -qF "built as" && grep -qF "Built in T-0183" docs/ticket-stages/watcher-design.md`
- (guard) `for f in plugins/sdlc-lite/scripts/tickets.py docs/maintenance/sdlc-internals.md plugins/sdlc-lite/skills/handoff-format/SKILL.md plugins/sdlc-lite/AGENTS.md docs/README.md docs/ticket-stages/README.md docs/ticket-stages/watcher-design.md .sdlc/AGENTS.md; do ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh -e docs/README.md -e plugins/sdlc-lite/scripts/tickets.py -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/ticket-stages/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxE "plugins/sdlc-lite/scripts/supervisor\.py|docs/reports/supervisor-live-run\.md|docs/reports/supervisor-live-run/(probe\.py|AGENTS\.md|CLAUDE\.md|[a-z-]+\.txt)")"`
