<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0152: External agents (Codex) get lane integration and reserved ticket ids

## PR body
### Summary
A branch owned by an outside agent (for example Codex) can now join fanout as a lane without a hand-made `lane/<x>` ref. Ticket ids committed on such a branch can no longer collide with ids that `tickets.py` mints.

The mechanism is one registration line in the ticket root's config, `external_branch: <branch>`. Both `fanout.py` and `tickets.py` read it. No id ranges were needed.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`
  - Adds `external_branches`, `branch_tickets` and `unknown_branches`.
  - `id_floor` now also counts ticket ids committed on registered branches, read from git objects with no checkout. This covers the `new` id and the close follow-up id.
  - `check` warns when a registered name is not a local branch.
  - Unregistered repos keep today's result.
- `plugins/sdlc-lite/scripts/fanout.py`
  - Adds the lane spec `<lane>@<branch>=<id>[,<id>...]`.
  - An external lane creates no worktree, no `<integration>-<lane>` branch and no driver.
  - The outside branch is never written. It is merged `--no-ff` under the lock, gated, and closed like any lane. A conflict reports `merge conflict` and leaves the integration branch and the outside branch unchanged.
  - Preflight refuses these cases:
    - an unregistered branch (exit 2, naming the `external_branch:` line)
    - a branch that does not resolve
    - the integration branch or an `<integration>-<lane>` branch used as the external branch
    - two lanes on one branch
  - `merge_gate_close` is one helper both lane kinds call. It skips the gates when the merge leaves HEAD unchanged, so a second ticket on the same branch merges nothing new and gates once.
  - The dry-run plan, `report.md`, docstring, usage line and argparse help are updated.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`, `plugins/sdlc-lite/skills/ticket/SKILL.md` and `docs/maintenance/sdlc-internals.md` describe the external lane form and the registration line.

Two deliberate deviations from the ticket's default wording:
- The external lane does not sync the outside branch first. The branch is usually checked out in the outside agent's worktree, so `git worktree add` would refuse it, and moving the ref would desync that agent's index.
- The merge target is `refs/heads/<branch>`, so a tag with the same name cannot be merged in its place.

### Verification
All four steps have a `pass` verdict.
- Step 1 (`tickets.py`): the acceptance checks pass on the built tree and fail at the base SHA. `tickets.py selftest` passes, and its new cases include unregistered negative controls that mint the colliding T-0002. The builder ran 6 mutations on a scratch copy and each turned the selftest red. The verifier did not re-run them.
- Step 2 (`fanout.py`): a mixed run of `alpha@ext=T-0002,T-0003 beta=T-0001` gave two merge commits and unchanged `ext` and main tips. No `fanout/t-alpha` ref, no `alpha` dir and no driver run appeared, and only one alpha gate log was written. The unregistered-branch refusal, `--dry-run`, `--gate false`, the merge conflict and resume were also exercised. The same checks fail at the base SHA. `fanout.py selftest` passes with the new case 11. The verifier re-ran two of the builder's five mutations and both went red. The other three are unverified.
- Step 3 (skills and docs): the greps for the registration line and the spec form pass, the `--lanes` count is above base, and `check.py` and `check-packaging.py` pass. The verifier did not read the `sdlc-internals.md` diff, which was truncated in the tool output. That file was checked by grep only.
- Step 4 (gates): `bash plugins/sdlc-lite/scripts/check.sh` exits 0, and so do `scripts/check-packaging.py` and `git diff --check`. Shellcheck was skipped because it is not installed on the host. The step-4 verifier ran no negative control for `check.sh`, because the gate was green and there was no red baseline.
- The gen-ui-system-svelte-lite evidence repo was not available. Behaviour follows from the scripts and the selftests.

Nothing was pushed or fetched. Main was not touched.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- fanout: a lane can now run a branch owned by an outside agent with `<lane>@<branch>=<ids>`. The branch must be registered with `external_branch: <branch>` in the ticket root's `config`. The lane has no worktree or driver, and the branch is never written. `tickets.py` counts ids committed on registered branches, so `new` and close follow-ups do not collide with them. `tickets.py check` warns about a registered name that is not a local branch.

## Follow-ups
- note: An external close needs a `filer-L*.md` on the outside branch. Without one, each close reports `merged, close refused` and the merge stands. This was inferred because the evidence repo was unavailable, and a `--reason` fallback would be its own ticket.
- note: `id_floor` now runs git once per registered branch on every `new` and `close`, so many registrations on a large root add latency. A deleted registered branch only draws a `check` warning.
- note: The lane spec splits on the last `=` and the first `@`, so a branch name containing `=` cannot be given in the external form.
- note: For a no-op external merge, such as a second ticket on the same branch, the report's Commit cell shows the previous `close` commit and not a merge commit. The docstring wording ("the merge commit when merged") is looser than that.
