# Docs schema design review

Recorded: 2026-10-05. Independent architect review of `docs/docs-schema/design.md` v0.1 for ticket T-0240.

## Run

- Role: `architect` L1 through `scripts/run.sh`, header `<!-- role=architect level=L1 model=fable effort=high -->`, recorded in `runs.jsonl` at about $8.24. The author of the design ran on Sonnet, so the reviewer was a different model family.
- Inputs and result are copied unchanged: [`handoff.md`](docs-schema-design-review/handoff.md) and [`architect-L1.md`](docs-schema-design-review/architect-L1.md) (`source: T-0240`; written in `.sdlc/0233-docs-schema-design/review/`, a folder later renumbered to `0240-docs-schema-design` because another branch filed T-0233, so the copied files still show the old number and path).
- The review was read-only. It ran the real `_parse_layout_text` on the proposed layout text and measured file counts with `git` and `grep`; its commands are named in its Carry forward section.

## Verdict

Ready after fixes: 3 blockers and 12 non-blockers. All 15 were applied to v0.2 of the design in the same change. The reviewer's "checked and clean" list (file counts, the root `AGENTS.md` line count, the parser claim, `tickets.py close` behavior, maison's layout and `budget.py`, `evals.py` and `supervisor.py` as state) matched the first draft.

## Findings and disposition

| # | Finding | Disposition in v0.2 |
| --- | --- | --- |
| 1 | B-2 contradicted `run.sh` and the design's own Promotion section | B-2 reworded: a role result stays where `run.sh` wrote it, the reader deliverable is its promoted copy |
| 2 | D-7 required an entry file `onboard.py` never writes under a home | Build ticket 2 extends the setup model to homes and nested topics; D-7 is enabled by it |
| 3 | Grandfathering by first-commit date is blind to untracked files and `git mv` | Replaced by a `## Legacy` glob list; `mode:` and `adopted:` removed |
| 4 | `mode: adopt` voided the `other/` quarantine | Resolved by 3: no global mode, legacy exempts only named checks |
| 5 | Two mechanisms bound a folder to a kind | `## Homes` is the one list; a non-default name needs a `## Kinds` line; `extra-homes:` removed |
| 6 | D-9 and the depth rule rejected real evidence | Same-stem sidecars and any depth inside an evidence folder allowed; mapping row names the report |
| 7 | B-1a missed retry files, `budget-ack.md`, `decompose/` and step-only task folders | Patterns and record list extended |
| 8 | Planning-to-archive on a status change is a status-triggered move that `repo-onboarding/design.md` forbids | The amendment is stated for exactly one transition and owned by build ticket 2; the alternative is open question 2 |
| 9 | Migration risk: `check.py` reads a docs path at run time; the rewriter covers Markdown only | Citing scan widened to code and entry files |
| 10 | `reorganization.md` freezes `docs/validation/`, the design moved it | `validation/` stays as a legacy home bound to `reports`; full move is open question 4 |
| 11 | Promotion edited a frozen `handoff.md` | `source:` key plus an optional `notes.md` line |
| 12 | B-3a would warn on 101 validation files | Legacy list covers links |
| 13 | The design's own file failed D-1 and D-4 | Mapping row `planning/docs-schema/`, legacy until moved |
| 14 | D-12 could not prove decision numbers are unique across subfolders | Uniqueness pass added |
| 15 | maison `reference/` is 30 tracked files, not 32 | Corrected |

## Limits

- One review pass. v0.2 was not reviewed again.
- The review did not measure that `git mv` resets the add date without `--follow` (it names this as unverified); the design no longer depends on it.
- Nothing in the design is implemented, and no check was run against a fixture.
