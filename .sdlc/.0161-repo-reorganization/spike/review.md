# Review of the trial plan

Plan reviewed: `plan.json` from `reorg_plan.py --layout layout.md --json` on base `9d6ca64`. 16 candidates: 12 placed, 4 moves, 0 unplaced, 0 ambiguities. 14 rewrites, 2 links broken before any move.

## Moves

| Path | Mark | Reason | Verdict a person would give |
| --- | --- | --- | --- |
| `docs/claude-handoff.md` | wrong | it is point-in-time correspondence bound to commit `d4ad342`, so it is a record, not a report to file | Freeze it in place. Moving it also rewrites its link to `readiness-recovery-validation.md`, which edits a record. |
| `docs/claude-response.md` | wrong | it opens with `Date: 2026-09-28` and reviews named commits, so it is a dated record that the `Recorded:` rule did not flag | Freeze it in place, together with `docs/claude-handoff.md`. |
| `docs/codex-role-execution.md` | ok | it is a living setup and usage guide that the root and plugin entry files route to | Accept the move to `docs/reference/`. All seven link cites stay valid: six are rewritten, and the one from `docs/plugin-compatibility.md` needs none because both files move together. Its two backticked cites are in `docs/claude-response.md` and `docs/repo-onboarding/reorganization.md`. |
| `docs/plugin-compatibility.md` | ok | it is maintained (it has a Maintenance section) and is cited as the current packaging reference | Accept the move to `docs/reference/`. All five link cites are rewritten. `reports/` is arguable because the root `AGENTS.md` calls it a "report", but its content is kept current. |

## Unplaced

None. Every loose document outside the frozen list matched a glob.

## What the review shows

- Globs moved every loose file, but two of the four moves are wrong for a reason no glob can see: the files are records. Neither was a frozen candidate, because one has `Date:` instead of `Recorded:` and the other has no date line at all.
- The 12 placed files are right: they sit in the two topics and in `maintenance/`, and no glob pulls them out.
- Of the 18 cites of moved files in non-frozen files, 12 are inline Markdown links (all handled), 6 are backticked paths, and 0 use any other form. Four of the six backticked cites are in `docs/repo-onboarding/reorganization.md` line 142, which describes the files where they sit today; rewriting them would make that sentence false. The other two are in the correspondence that should be frozen. Frozen files, almost all under `.sdlc/`, hold 25 more mentions, which the design leaves stale on purpose.
- The 2 baseline-broken links are the two expected cites of the sibling UI project, in `docs/generative-constructs/README.md` and `docs/generative-constructs/progressive-context-plugin.md`.
- None of the N2 ambiguities occur with this layout. A throwaway probe layout showed that the detection fires: `claude-*.md` on two homes gives `multi_home` (and also pulls `docs/maintenance/claude-hooks.md`), and a home named `validation/` gives `into_frozen`. An in-process probe that added a simulated tracked path `docs/reports/Claude-Handoff.md` gave a case-folded `name_collision`. The two-sources-one-destination case was not exercised, because no two documents under `docs/` share a file name.
