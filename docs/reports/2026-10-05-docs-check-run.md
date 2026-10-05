# Docs check, setup entries and default layout (T-0242)

Recorded: 2026-10-05. Scripts: `plugins/sdlc-lite/scripts/docs_check.py` (D-1 to D-12) and `plugins/sdlc-lite/scripts/onboard.py`.

## What changed for adopters

`onboard.py setup` now writes a different `docs/AGENTS.md` block for every adopter: the nine homes, the decision list, and the add-a-document steps replace the earlier three-step block. An existing block reads `stale` in `onboard.py check` and `setup` replaces it (an interactive `setup` prints the diff and asks once before writing; `--dry-run` only prints it, `--yes` skips the question, and a non-interactive run writes as before). Setup also writes an entry file and a `CLAUDE.md` stub for a home, and for a topic folder directly under a home, once it holds two or more documents (at most 20 documents are listed, the rest are counted). The default `docs/layout.md` written when the file is missing now lists the nine homes with `## Kinds`, `## Decide` and an empty `## Legacy`. Existing layout files are not touched.

## Read-only runs (nothing written; `git status` counts were identical before and after)

| Target | Result |
| --- | --- |
| This repository (no `docs/layout.md`, default homes) | 90 errors, 8 warnings: D-1 6, D-10 4, D-11 4, D-12 19, D-2 4, D-3 54, D-5 1, D-7 1, D-9 5. Expected before the migration (T-0244); the checker is not a gate here yet. |
| `/Users/kimgranlund/Projects/maison/ui-kit-maison` | 15 errors, 7 warnings: D-1 3, D-10 7, D-12 7, D-9 5. `onboard.py check` there reports `stale docs/AGENTS.md` and missing entries for `docs/maintenance/`, `docs/reference/` and `docs/gen-ui-evaluation/`. |

## Limits

- D-8 reads age from `date:` front matter, then file modification time; a fresh checkout resets modification times, so D-8 can under-report there.
- D-9 treats a report's evidence folder as a folder named like a sibling report (`<stem>/` next to `<stem>.md`); a folder such as `plan-skills-live-run.d/` is reported.
- The registry rendering and the drift checks R-1 and R-2 are not built (they wait for T-0248). The `docs/AGENTS.md` block says the placement effect is unproven.
- The boundary checks are recorded below (T-0243).

## Boundary checks B-1a, B-2a, B-3a (T-0243)

`docs_check.py --only boundary` runs them. B-1a flags generated-file names under `docs/` (never exempted by Legacy), B-2a warns about Markdown in `.sdlc/` outside the record types, and B-3a warns about a docs link into `.sdlc/` (exempted by Legacy). Read-only run on this repository: B-1a 61 errors (all under `docs/reports/` evidence folders such as `agent-command-live-run/arms/` and `runner-family-task-dir-live-run/fam/`, to be settled in the migration), B-2a 0, B-3a 5 warnings. The run also prints that 50 role-result retry files (`<role>-L<n>-<k>.md`) sit under `.sdlc/`, where they belong and are not flagged, and 1 under `docs/`. The design's figure of 49 was a count of the day it was written. B-2a cannot tell a design review from a role result by name, so it reports candidates only.
