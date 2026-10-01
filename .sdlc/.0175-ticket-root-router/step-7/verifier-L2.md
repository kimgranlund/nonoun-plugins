<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
fail

## Criteria
- Doc exists with a `Recorded: YYYY-MM-DD.` line: pass. Evidence: the `test -f ... && grep -qE '^Recorded: ...'` command exited 0. The file has `Recorded: 2026-09-30.` on line 3.
- README list item: pass. Evidence: `grep -qF '(validation/ticket-root-router-live-run.md)' docs/README.md` exited 0. `git diff docs/README.md` shows the item added right after "Plan reviewer live run", with the text the handoff gave.
- `## Scripted run` with the three Stages lines and `ticket_root: tickets`: pass. Evidence: the combined grep exited 0. I did not re-run the scripted arm. I read its excerpts in the doc. The role arm's end state in the temp project matches what the doc says (`- done: 1`, `check` printed `ok: 1 tickets, roadmap current`).
- `## Fresh role`, `## Limits`, and a `Result:` line: pass on form only. Evidence: the grep exited 0. The Do requires `Result: verified` only when every observation holds, so the content fails (see the next item).
- Live-run observations back the `Result: verified` line: fail.
  - What I checked. I parsed the `role.log` stream-json myself.
    - Tool calls were Read (the handoff), Bash (`ls`), Edit (adds `claimed_by: claude 2026-09-30`), and Bash (`roadmap && close ... --reason`). The log contains 0 `"name":"Skill"`. The model is `claude-sonnet-5-5`, with 5 turns, 9761 ms and $0.21.
    - Final state in the role project. The handoff has `status: done`, `claimed_by: claude 2026-09-30` and a `## Closed` section. The folder is `.0001-probe`. The router shows `- done: 1`. `tickets.py --root .sdlc check` printed `ok: 1 tickets, roadmap current`.
    - The session transcript under `~/.claude/projects/` holds `nested_memory` attachments for `.sdlc/CLAUDE.md`, `.sdlc/AGENTS.md`, `.sdlc/tickets/CLAUDE.md` and `.sdlc/tickets/AGENTS.md`. There was no Read call on `.sdlc/tickets/AGENTS.md`.
  - Why it fails. Two of the handoff's observations did not hold as the handoff describes them.
    - The role never opened the `router:` path. The router text reached it through nested-memory auto-loading.
    - The router's `, claimed by` state before the close was not captured live. `roadmap && close` ran in one Bash call. The doc shows that state only through a deterministic replay.
    - The doc says both of these itself, in the Fresh role bullets and in Limits. The `Result: verified` line contradicts that disclosure. The handoff says `Result: verified` only "when every one holds", and otherwise `Result: unverified: <what failed>`.
  - I did not re-run the replay. The `, claimed by` line is therefore taken from the doc.
  - Steelman. The builder would say that `roadmap` demonstrably ran after the claim edit, that the router text did reach the role, and that Limits discloses everything. That is a fair reading of the substance. But the Do sets a binary rule for the Result line, and a validation record that says `verified` while its own Limits lists two unobserved or different-mechanism observations overstates. The finding survives, and the fix is small.
- (guard) changed-file allowlist: pass. Evidence: the guard command exited 0.

## Out of scope changes
None. `git status` shows only `docs/README.md` (modified) and `docs/validation/ticket-root-router-live-run.md` (new), plus untracked step artifacts under `.sdlc/`. `git diff --name-only 604d7cc -- plugins` is empty. `git diff --check` is clean and the doc has no em dash (`grep -nP '\x{2014}'` found nothing). The role log is in the mktemp folder, not in the repo.

## For the next attempt
Only `docs/validation/ticket-root-router-live-run.md` needs a change. No re-run is needed.
- Change the Fresh role `Result:` line from `Result: verified` to `Result: unverified: <reasons>`, giving two reasons that match the doc's own observations.
  - The role did not read `.sdlc/tickets/AGENTS.md` through the handoff's `router:` line. It received it through Claude Code nested-memory loading.
  - The `, claimed by` router state before the close was not captured live. It was reproduced only by replay.
- Keep the rest of the doc. The README line can stay.
