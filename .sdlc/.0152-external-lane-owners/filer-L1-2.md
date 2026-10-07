<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0152: External agents (Codex) get lane integration and reserved ticket ids

## PR body
### Summary
A branch owned by an outside agent (for example Codex) can now join fanout as a lane without a hand-made `lane/<x>` ref. Ticket ids committed on such a branch can no longer collide with ids that `tickets.py` mints.

One registration line does both jobs: `external_branch: <branch>` in `<root>/config`, the file `config_numbered` already reads. Both `fanout.py` and `tickets.py` read it. Id ranges were not needed.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`
  - Adds `external_branches`, `branch_tickets` and `unknown_branches`.
  - `id_floor` now also counts ticket ids committed on registered branches, read from git objects with no checkout. This covers both the `new` id and the close follow-up id.
  - `check` warns (exit 0) when a registered name is not a local branch.
  - Docstring updated. Unregistered repos and non-git roots keep today's result.
- `plugins/sdlc-lite/scripts/fanout.py`
  - Adds the lane spec `<lane>@<branch>=<id>[,<id>...]`.
  - An external lane creates no worktree, no `<integration>-<lane>` branch and runs no driver.
  - The outside branch is never written. It is merged `--no-ff` under the lock, gated, and closed like any lane. A conflict reports `merge conflict` and leaves both the integration branch and the outside branch unchanged.
  - Gates run only when the merge produced a new commit, so a second ticket on the same branch merges nothing new and skips the gates.
  - Preflight refuses an unregistered branch (exit 2, naming the `external_branch:` line and the config path), a missing ref, the integration branch or an `<integration>-<lane>` branch as the external branch, and two lanes on one branch.
  - Dry-run plan line, report lane line, usage text, docstring and selftest case 11 cover the new form.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`, `plugins/sdlc-lite/skills/ticket/SKILL.md`, `docs/references/sdlc-internals.md`: updated for the external lane form and the registration line.
- Existing `<lane>=<id>` lanes, their branch naming and refusals behave as before. Main is untouched and nothing is pushed or fetched.

Design note: the architect chose not to sync the outside branch, because it is usually checked out in the outside agent's worktree. This deliberately differs from the ticket's default wording ("syncs ... like any lane"). The outside agent reconciles a diverged branch on their side.

### How each was verified
- Step 1 (tickets.py, verifier pass): acceptance-criteria spans ran green on the built tree and red at the base SHA; `tickets.py selftest` PASS, including unregistered-copy negative controls that mint the colliding T-0002; `check.py` and `git diff --check` clean. The verifier did not re-run the builder's six mutations.
- Step 2 (fanout.py, verifier pass): the mixed run, the external-only report rows, the unregistered refusal, dry-run and `--gate false` cases all passed and failed at the base SHA. `fanout selftest` PASS. The verifier confirmed two mutations turn case 11 red (gates always run; registration check off). A merge-conflict probe and a resume run also behaved as designed.
- Step 3 (skills and docs, verifier pass): the greps passed, with base counts of 0 where the check should go red. `check.py`, `scripts/check-packaging.py` and `git diff --check` passed. The verifier did not read the `sdlc-internals.md` diff, so that file is checked by the greps only.
- Step 4 (gates, verifier pass): `bash plugins/sdlc-lite/scripts/check.sh` exit 0 with all selftests and plugin validate passing, `check-packaging.py` exit 0 and `git diff --check` clean. Shellcheck was not installed and was skipped.
- Step 5 (docstring wording, verifier pass): the Commit-cell wording matches in `fanout.py` and `sdlc-internals.md`. The docs half of the check bites against a rebuilt pre-step text. `fanout selftest` PASS.
- Live-host validation on Codex was not run. Behavior lives in the shared scripts.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added external lanes to `fanout`: `<lane>@<branch>=<ids>` merges, gates and closes an outside agent's existing branch with no worktree, no driver and no `<integration>-<lane>` branch. Register the branch with `external_branch: <branch>` in the ticket root's `config`; `tickets.py` then counts ids committed on that branch, so `new` cannot mint a colliding id.

## Follow-ups
- note: For an external ticket whose merge brings in nothing new (a second ticket on the same branch), the report's Commit cell shows the previous close commit, not a merge commit. Step 5 reworded the docs to say so.
- note: Live host validation on Codex was not run for this change. Only the shared-script selftests and `check.sh` covered it.
- note: The step 1 builder's six mutation checks and three of the step 2 builder's five were not re-run by the verifiers. The base-SHA red runs and two re-run mutations cover the behavior.
