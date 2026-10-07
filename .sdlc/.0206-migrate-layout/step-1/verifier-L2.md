<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, refusal without `--rewrite-refs`: pass. Evidence: the extracted command exited 0. It lists `docs/guide.md`, `README.md` and `.sdlc/alpha/links.md`. It omits `docs/reports/r.md`, `.sdlc/beta/links.md`, `AGENTS.md` and `.sdlc/AGENTS.md`. It names `--rewrite-refs`, and nothing was written.
- Criterion 2, `--dry-run --rewrite-refs`: pass. Evidence: exit 0. All nine `move`, `rewrite` and `keep` lines are present. The tree and config are untouched, and `docs/guide.md` is unchanged.
- Criterion 3, real migration: pass. Evidence: exit 0. The output holds `ok: 2 tickets, roadmap current`. The topic folders and their entry files exist, the old paths are gone, config holds both lines, and `check` passes.
- Criterion 4, rewritten text: pass. Evidence: exit 0. The guide, README and moved links files hold the exact expected strings. `docs/reports/` has no diff against HEAD.
- Criterion 5, managed block frozen: pass. Evidence: exit 0. `onboard.py check` prints `stale AGENTS.md` after the migration and `current AGENTS.md` after `setup`, and `AGENTS.md` names `.sdlc/tickets/roadmap.md`.
- Criterion 6, idempotence: pass. Evidence: exit 0. The second run prints `nothing to migrate`, with no diff and no untracked files.
- Criterion 7, dirty tree and loose file: pass. Evidence: exit 0. A modified tracked file and an untracked file each refuse with `uncommitted changes`. A loose `pause.md` refuses and is named. The tree is unchanged.
- Criterion 8, skipped-migration and stray-folder checks: pass. Evidence: exit 0. `check` fails with `rel-x: stray entry at the root` on the topics config without moves, and with `junk: stray entry at the root` after a migration.
- Criterion 9, `ticket_root: tickets` fixture: pass. Evidence: exit 0. `alpha` is not moved, `rel-x` goes to `work/`, the roadmap moves, config holds exactly one `ticket_root` line plus `layout: topics`, and `check` passes.
- Criterion 10, docstring Usage line and selftest `run(..., 'migrate-layout'`: pass. Evidence: exit 0. The diff shows the Usage line and a `migrate-layout` entry added to the docstring.
- (guard) `tickets.py selftest`: pass. Evidence: `tickets selftest: PASS`, rc 0. I did not re-run it at the pre-build HEAD, because it is green on the built tree.
- (guard) only `tickets.py` changed outside `.sdlc`: pass. Evidence: exit 0. `git status` shows only `M plugins/sdlc-lite/scripts/tickets.py` among tracked files.
- Selftest negative controls (handoff item 9): pass. Evidence: the diff has cases for a modified tracked file, an untracked file, a cite without `rewrite_refs`, a `docs/reports/` cite, a loose file, an existing target, a root outside git, and topics config without the moves. I ran the outside-git refusal directly: rc 1, `not inside a git work tree ... nothing written`, and the root unchanged.
- The freeze check can go red: pass. Evidence: in a throwaway copy of the plugin I replaced `if fb.status == 'block':` with `if False:`. Criteria 1 and 5 then exited 1, where both exit 0 on the built tree. The biting variable is the block-freeze branch of `migrate_text`.
- Builder claims: accepted only where I re-ran them. The criteria, selftest and scope guard are confirmed above. The builder's deviation in `ensure_topics_config` is not a defect. It keeps existing all-`topics` `layout:` lines, which agrees with the idempotence rule in item 8. I confirmed it in the code and in criteria 6 and 9, which exit 0.

## Out of scope changes
None. `git diff --stat` shows only `plugins/sdlc-lite/scripts/tickets.py`. The other changes are untracked `.sdlc/` role artifacts, which the scope guard excludes.

## For the next attempt
None
