# Docs schema and the docs/.sdlc boundary

Status: draft v0.3, recorded 2026-10-05, after one independent architect review of v0.1 ([record](../validation/docs-schema-design-review.md)). v0.2 and v0.3 were not reviewed again. Design only: nothing here is implemented, and no file moves in any repository because of this document. Ticket T-0240.

Every choice marked **(user may change)** is a default I picked and justified. The rest follows from the repository's own files.

## Resolved decisions

The user decided these on 2026-10-05. They override any older sentence below that says otherwise.

1. **Planning and specs stay two homes,** split by purpose (what is not built versus what is built or accepted). A superseded plan moves to `archive/`.
2. **Names are plural,** and `guides/` replaces `maintenance/`. This repository's and maison's `maintenance/` content maps to `guides/` or `references/` by what it is (see Mappings).
3. **`docs/validation/` is renamed to `docs/reports/` now.** The user chose this against the earlier default (a legacy home bound to `reports`). There is no legacy home for validation any more. The move is its own ticket, T-0246, which runs after the `reorg-inventory` branch is merged and amends the freeze sentence in `docs/repo-onboarding/reorganization.md`. The `## Legacy` mechanism stays, only for files that are really grandfathered, such as existing report names that do not follow the date rule.
4. **Setup writes entry files under every home** (`AGENTS.md` plus a `CLAUDE.md` import), after a dry-run diff and one question before it writes. That changes `docs/AGENTS.md` for every adopter, maison included. The setup-model change is in T-0242.

## Problem

- The current default layout is thin. `docs/repo-onboarding/design.md` names three homes (`maintenance/`, `reference/`, `reports/`) and says everything else is a free-form topic folder. Its document-type table sends a design to `docs/<topic>/`, a procedure to `maintenance/`, and a dated result to `reports/` "unless it sits beside the contract it assesses".
- This repository does not follow even that. `docs/` holds 7 folders and 5 loose documents directly in `docs/` (`claude-handoff.md`, `claude-response.md`, `codex-role-execution.md`, `plugin-compatibility.md`, `readiness-recovery-validation.md`), besides its entry files. `docs/validation/` has 69 entries (48 Markdown files, 19 folders, 2 other files), and only 8 of those names contain a date.
- The maison repository (`/Users/kimgranlund/Projects/maison/ui-kit-maison/docs`) uses `reference/` (singular), `reports/` with date-prefixed names, `maintenance/` holding one dated audit folder, `gen-ui-evaluation/` holding a plan, and `assets/`.
- `.sdlc/` is stricter by construction. Its router (`.sdlc/AGENTS.md`) names tickets, stages, procedures, `messages/`, `evals/`, `proposals/` and `notes.md`. But nothing says what may not be written there, so verification records and design reviews already sit in both places.

## Principles

1. **One meaning per folder.** A folder name answers "what kind of document is this", never "how finished is it".
2. **Two worlds.** `docs/` is durable knowledge written for readers. `.sdlc/` is work records and runtime state written by scripts and roles while work runs.
3. **One authoritative copy.** A fact has one home. The other places link to it.
4. **Strict names, small footprint.** The folder names are fixed. A repository creates only the folders it needs.
5. **Checks that can fail.** Every rule below that can be mechanized has a named deterministic check with a negative control. Rules that cannot be mechanized are marked advice.
6. **Progressive context.** Small entry files, routing by task, no giant index.

## The boundary: docs versus .sdlc

| | `docs/` | `.sdlc/` |
| --- | --- | --- |
| Holds | Durable knowledge for readers: specs, plans for decisions, decisions, lookups, guides, dated evidence | Work records and runtime state: tickets, task folders, handoffs, plans, role results, step folders, `runs.jsonl`, `skips.md`, messages, notes, roadmap, evals, proposals, supervisor state, config |
| Written by | A person or a role, deliberately, then reviewed | `tickets.py`, `run.sh`, `steps.py`, `messages.py`, `fanout.py`, `budget.py`, roles and the conductor, as a side effect of work |
| Lifetime | Outlives the ticket that produced it | Lives with the ticket; closed ticket folders are renamed `.NNNN-slug` and hidden |
| Edited | In place, by a change that updates the doc | Appended or regenerated; a generated block is never hand-edited |
| Read by default | Only the folder the task needs | Only the router and the stage the task needs |

Rules (checks in the Enforcement section):

- **B-1** Nothing generated per run lives in `docs/`. That includes a role result, a `runs.jsonl`, a verifier result, a `skips.md`, a message and a roadmap.
- **B-2** A finished Markdown deliverable written for a reader does not live in `.sdlc/`, but a role result stays where `run.sh` wrote it: `run.sh` writes each role result into the handoff folder, and `steps.py` and `order.py` read it there. A design review or verifier result is therefore first a work record, and the reader deliverable is its promoted copy. A report, benchmark, audit or release record that is written for readers is written directly into `docs/reports/`.
- **B-3** `docs/` cites a ticket by id (`T-0240`) as text, never by path. A closed ticket folder is renamed to `.NNNN-slug`, and `tickets.py close` already refuses when a file cites its path without `--rewrite-refs`. `.sdlc/` may link into `docs/` by path.
- **B-4** A ticket's plan, handoff and step folders stay in `.sdlc/`. A plan is a work record even when it is long.
- **B-5** State a script reads or writes (`evals/table-lock.json`, `config`, `supervisor/`) stays in `.sdlc/`. A person-readable summary of an eval, if wanted, is a report in `docs/reports/`.

### Promotion

A `.sdlc/` artifact that should outlive its ticket (an architect result, a design, a verification record, a benchmark) is promoted by copy:

1. Copy it to the target home in `docs/` with front matter that names the source: `source: T-0240` (ticket id) and the original file name.
2. The `docs/` copy is the authoritative one. The `.sdlc/` copy stays as the record and gets no further edits.
3. The promoted file's `source:` key is the link back. The ticket's `handoff.md` is not edited, because it is frozen once a role reads it and hidden after the ticket closes. A line in `.sdlc/notes.md` may record the promotion.
4. Which home: a design that is accepted goes to `specs/`, a record of one choice goes to `decisions/`, evidence goes to `reports/`.

Promotion is advice in version 1 and a small script later (build ticket 5). A check cannot know what "should outlive" a ticket, so it only checks a promoted file's front matter.

## The docs schema

### Homes

All names are plural, lowercase and kebab-case. **(user may change)** Plural matches `.sdlc/tickets/`, `.sdlc/messages/`, `.sdlc/evals/` and `.sdlc/proposals/`, and it matches the names you wrote (`specs`, `references`). maison's `reference/` becomes `references/`.

| Home | Kind | Holds | Never holds | Mandatory front matter |
| --- | --- | --- | --- | --- |
| `specs/` | specs | What the system is and must do: requirements, contracts, interface and behavior descriptions, designs that were accepted. Living documents, edited in place. | Proposals under review, dated evidence, how-to steps | none; `status: draft\|active\|deprecated` optional |
| `planning/` | planning | Documents whose purpose is to decide or schedule future work: proposals, RFCs, designs for review, roadmaps, plans. | Anything describing what exists | `status: proposed\|accepted\|rejected\|superseded` |
| `decisions/` | decisions | One decision per file, numbered, immutable once accepted. | Narrative design, evidence | `status: proposed\|accepted\|superseded`, number in the file name |
| `references/` | references | Lookup material: API and schema listings, glossaries, tables, how a component is wired. No narrative and no steps. | Procedures, opinions | none |
| `guides/` | guides | How-to and operating procedures: setup, release, maintenance, runbooks. Steps a person follows. | Lookup tables, design | none |
| `reports/` | reports | Dated evidence: validation records, reviews, audits, benchmarks, release records. Immutable. | Instructions, living specs | date in the file name (new files) or `date:` |
| `assets/` | assets | Non-Markdown files only: images, diagrams, data files cited by a document. | Markdown | not applicable |
| `archive/` | archive | Superseded or retired documents kept for history. Excluded from default reads. | Live documents | `status: superseded\|retired`, `superseded-by:` when known |
| `other/` | other | A quarantine inbox for documents nobody has sorted. Never a permanent home. | Anything with a clear home | `owner:`, `review-by: YYYY-MM-DD` |

### Planning versus specs: kind, not state

`docs/repo-onboarding/design.md` (the Number prefixes section) says a number never expresses maturity or status, because a folder name that stored that claim would go stale, and that a document does not move between numbered folders as its state changes. `planning/` and `specs/` are not numbered, but a status-triggered move into `archive/` is in the same spirit. The split is therefore by purpose, and the principle is amended for exactly one transition:

- `planning/` holds documents whose job is to get a decision made or work scheduled. They are consumed by that decision.
- `specs/` holds documents whose job is to define the system. They are maintained for as long as the system exists.
- A planning document is never moved into `specs/`. When a proposal is accepted and built, its durable content is written into a spec (or the spec is updated), the choice is recorded in `decisions/` if one was made, and the planning document gets `status: superseded` and moves to `archive/`. That one move is the amendment: build ticket 2 rewrites the quoted sentence in `docs/repo-onboarding/design.md` to allow it.
- The check **D-8** flags a planning document whose status is `accepted`, `rejected` or `superseded` and which has sat in `planning/` longer than a threshold (default 30 days, **(user may change)**).
- The alternative that needs no amendment is one home, `specs/`, with `status: proposed|accepted|...` and no move at all. It loses the fixed-name signal you asked for, so I did not choose it. See open question 2.

### Which home: decision table

The first row that matches wins. Rows are about the document's purpose, which a person or a model judges; the checks only read names and front matter.

| If the document is | Home |
| --- | --- |
| A picture, diagram source or data file | `assets/` |
| Evidence of something that happened on a date (a run, a review, an audit, a benchmark, a release) | `reports/` |
| One choice with its reasons and alternatives | `decisions/` |
| A proposal, roadmap, plan or design under review | `planning/` |
| Steps a person follows | `guides/` |
| A table, listing, glossary or wiring description you look things up in | `references/` |
| A description of what the system is or must do | `specs/` |
| Retired or superseded | `archive/` |
| None of the above, or unsure | `other/` with an owner and a review-by date |

Tie-breaks: a document that is both a guide and a reference is split into two, or goes where its first section points. A report that contains a recommendation stays a report and the recommendation becomes a planning document that links to it.

### Naming, depth, size, links

- Folder and file names: lowercase, kebab-case, `.md`, no spaces and no version suffix. Exceptions: `AGENTS.md`, `CLAUDE.md`, `README.md`, and the `NN-` prefix the existing design allows for a real reading order.
- `reports/` new files: `YYYY-MM-DD-slug.md`. A report may have a sibling evidence folder of the same stem, `YYYY-MM-DD-slug/`, for small text evidence files (the repository's `docs/validation/`, `docs/reports/` after T-0246, already pairs `<name>.md` with `<name>/`). Evidence files are capped at 200 KB each by default. **(user may change)**
- `decisions/` files: `NNNN-slug.md`, four digits, never reused.
- Depth: `docs/<home>/<topic>/<file>`. A topic folder is optional and only in `specs/`, `planning/`, `references/`, `guides/` and `decisions/`. Nothing deeper except a report's evidence folder.
- Size: an entry file has a 60-line target, the one `onboard.py check` already reports (`size AGENTS.md: 78 lines, over the 60-line target` for this repository's root file, which it does not trim). Other documents have a soft limit of 400 lines that produces a warning. **(user may change)**
- Links: relative links only, no absolute paths. A link to a file that does not exist is broken. `docs/` never links into `.sdlc/` by path (B-3).
- `README.md` is optional and is a human-facing summary. `AGENTS.md` is the harness entry.

### Front matter

Front matter is a leading `---` YAML block with flat string keys. The schema fixes only these keys:

| Key | Used in | Meaning |
| --- | --- | --- |
| `status` | `planning/`, `decisions/`, `archive/`, optionally `specs/` | Lifecycle value from the table above |
| `date` | `reports/` when the file name has no date | `YYYY-MM-DD` |
| `owner` | `other/` (mandatory), anywhere (optional) | A person or a team |
| `review-by` | `other/` | `YYYY-MM-DD` |
| `ticket` | anywhere (optional) | A ticket id, `T-NNNN` |
| `source` | promoted copies | The `.sdlc` artifact's ticket id and file name |
| `superseded-by` | `archive/` | A path relative to `docs/` |

Existing documents mostly have no front matter. The review counted 4 documents with YAML front matter, all fixtures under `docs/validation/`, and 45 files with a `Recorded: YYYY-MM-DD.` line near the top. The report date is read from the file name, then `date:`, then a `Recorded:` line in the first 10 lines. Only the first two count as schema-conformant for new files.

### Entry files

- `docs/AGENTS.md` and `docs/CLAUDE.md` (`@AGENTS.md`) exist in every adopting repository: a routing table, no document list longer than a screen.
- A home gets its own `AGENTS.md` and `CLAUDE.md` once it holds two or more documents, as the existing design says for topics. `assets/` and `archive/` are exempt, except `archive/AGENTS.md` is one line: do not read unless asked.
- Today `onboard.py` writes no entry file under a listed home (`onboard.py` line 463 skips every path under a home, and `docs/repo-onboarding/design.md` says a home gets no entry file in version 1). Build ticket 2 extends the setup model to write entries for homes and for topics nested under a home, and amends that sentence. That changes the `docs/AGENTS.md` output for every adopter, and row 6 of the upsert table replaces their managed blocks on the next setup.
- `reports/AGENTS.md` carries a routing rule and no per-file list. Reports sort by name, so a list would only go stale. This keeps the "no giant index" rule.

## Overriding: docs/layout.md

The parser in `plugins/sdlc-lite/scripts/onboard.py` (`_parse_layout_text`) reads the two required sections `## Homes` and `## Frozen paths`, raises a `LayoutError` on a list line under `## Homes` that does not fit `` `<home>/` [takes `<glob>`, ...] ``, and ignores any other heading of level 2 or less. The review ran the parser on the text below and confirmed that new sections are ignored by it, so a **new section is backward compatible** and a new form inside `## Homes` is not.

`## Homes` stays the single list of top-level folders. Two new sections add meaning to it:

```text
## Kinds
- `design-system/` is `specs`
- `runbooks/` is `guides`

## Legacy
- `reports/old-notes/**`
- `imported-wiki/**`
```

The lines above are an example of the forms, not this repository's file.

- `## Kinds` binds a home to one of the nine fixed kinds. A home that uses a default name needs no line. A home with a non-default name needs one, and the check reports it as an informational line, so an exception is visible and not forbidden. There is no second mechanism for custom homes.
- `## Legacy` lists globs of existing paths that are exempt from most checks (see Enforcement), in the same backticked form as `## Frozen paths`. It replaces a global warn-only mode and a date cutoff. A path that is not listed, or is not tracked yet, is new and fully checked. The migration shrinks the list and never grows it silently: the apply step rewrites it like any other citer.
- Anything else in these sections is an error that names the file and line, like the existing parser.

Parser change (build ticket 1): `Layout` in `onboard.py` gains `kinds` and `legacy`, the two sections are parsed, the `Homes` and `Frozen paths` forms stay unchanged, and the selftest gets cases with negative controls.

## Enforcement

A new script `plugins/sdlc-lite/scripts/docs_check.py` (not built) imports `parse_layout` from `onboard.py` and runs these checks against a repository root. `onboard.py check` is left unchanged, since its job is entry-file ownership. Each check has a selftest case and a negative control. Any error exits 1. A `## Legacy` glob exempts a path from D-1, D-2, D-3, D-4, D-9, D-10, D-11, D-12 and B-3a. It never exempts D-5, D-6, B-1a or B-2a.

| ID | Check | Default |
| --- | --- | --- |
| D-1 | A top-level folder under `docs/` that is not one of the nine default homes or a home listed in `## Homes` with a `## Kinds` line | error |
| D-2 | A file directly in `docs/` other than `AGENTS.md`, `CLAUDE.md`, `README.md`, `layout.md` | error |
| D-3 | A file in `reports/` or a home bound to `reports` with no date in the name and no `date:` | error |
| D-4 | A file in `planning/` or `decisions/` with no `status:` or an invalid value | error |
| D-5 | A file in `other/` with no `owner:` or `review-by:`, or with `review-by` more than 90 days ahead | error |
| D-6 | An `other/` file past its `review-by` date | error |
| D-7 | A home, or a topic folder under a home, with two or more documents and no `AGENTS.md` or `CLAUDE.md` (enabled once `onboard.py` creates them, build ticket 2) | error |
| D-8 | A `planning/` file with status `accepted`, `rejected` or `superseded` older than the threshold | warning |
| D-9 | A Markdown file in `assets/`, or a non-Markdown file outside `assets/`, outside a report's evidence folder (any depth) and outside a same-stem sidecar of a report (`<report>.sha256`, `<report>.json`) | error |
| D-10 | A relative link that does not resolve | warning |
| D-11 | An entry file over its 60-line target, or a document over 400 lines | warning |
| D-12 | A file name that breaks the naming rules (case, spaces, version suffix, report date format, decision number), or a decision number used twice anywhere under `decisions/` | error |
| B-1a | A path under `docs/` that matches a generated-file name: `runs.jsonl`, `skips.md`, `<role>-L<n>.md` and retries `<role>-L<n>-<k>.md`, `budget-ack.md`, `*.attempt.json`, `*.request.json`, `*.running`, `*.log` | error |
| B-2a | In `.sdlc/`, a Markdown file outside the record types: a folder that is not a ticket folder, a task folder (a `handoff.md` at its root or `step-<n>/` folders), `messages/`, `evals/`, `proposals/`, `supervisor/`, `_templates/`, a role's `decompose/` folder, and a loose `.md` other than `AGENTS.md`, `CLAUDE.md`, `notes.md`, `roadmap.md`, `board.md` | warning |
| B-3a | A `docs/` file that links to a path under `.sdlc/` | warning |

The role-result file-name patterns in B-1a come from `run.sh` and `steps.py`, which write `<role>-L<n>.md`, retries as `<role>-L<n>-<k>.md` (49 tracked files in this repository), and `runs.jsonl`. The review reported that 101 files in `docs/validation/` cite `.sdlc/` paths, so B-3a depends on a `## Legacy` glob covering those existing records once they sit in `reports/` (new reports are fully checked). B-2a cannot tell a design review from a role result by name, so it reports the candidates and does not block. That is a limit of a deterministic check: it finds where a file is, not what it is for.

`check.sh` would run `docs_check.py` on this repository once this repository has migrated, with a selftest in the same step. A check that only runs on a fixture would not catch drift here.

## How the reorganization inventory uses the schema

The reorganization project (branch `reorg-inventory`, script `inventory.py`) is being built by another agent, so this section defines the contract and does not depend on its internals.

1. **Placement by name.** The inventory reports each document's current home and the home the schema would pick from its path, file name and front matter alone: a date in the name means `reports`, a four-digit number means `decisions`, `status: proposed` means `planning`. These are the deterministic hints.
2. **Violations.** It reuses the `docs_check.py` rules D-1, D-2, D-3, D-4, D-7, D-9 and D-12 as flags, so a flag and a check mean the same thing.
3. **The plan.** A model session reads the inventory and the decision table above, and proposes a move for each document the hints cannot place. Each proposal cites its inventory row. The model decides purpose, a script decides names and paths, and a gated apply (a separate ticket) executes only an approved plan.
4. **Boundary findings.** The inventory runs B-1a, B-2a and B-3a and lists the matches as candidates, never as moves.

## Mappings

These come from folder and file names only. The inventory and a person decide anything that depends on content.

### This repository

| Today | Becomes | Note |
| --- | --- | --- |
| `docs/validation/` (385 tracked files on 2026-10-05, 327 other tracked files cite it) | `reports/` | Renamed as a whole by T-0246, run after the `reorg-inventory` merge; file names are kept (8 of 69 top-level names contain a date, so most existing names are covered by a `## Legacy` glob and the date rule applies to new reports only). Historical tags and published release pages keep the old paths. T-0246 amends the freeze sentence in `docs/repo-onboarding/reorganization.md`. |
| `docs/lean-sdlc/` | `specs/lean-sdlc/` | The lane design and cost-control addendum describe shipped behavior. |
| `docs/ticket-stages/` | `specs/ticket-stages/` | Router, messages and watcher designs describe built features. |
| `docs/repo-onboarding/design.md` | `specs/repo-onboarding/` | Built (T-0160). |
| `docs/repo-onboarding/reorganization.md` | `planning/repo-onboarding/` | A draft with `Nothing in this document is implemented`; status `proposed`. |
| `docs/repo-onboarding/layered-context-pattern.md` | `references/` | A reference on how hosts load nested entry files. |
| `docs/generative-constructs/` | `specs/generative-constructs/` | `docs/README.md` describes the folder as including browser and A2UI proposals, so files 05 and 06 are candidates for `planning/`; the inventory decides. The numbered reading order stays. |
| `docs/maintenance/sdlc-internals.md`, `claude-hooks.md` | `references/` | Implementation references, not steps. The name `maintenance/` is retired; step-by-step procedures from it, if any, go to `guides/`. |
| `docs/codex-role-execution.md`, `plugin-compatibility.md` | `references/` | Loose files in `docs/`. |
| `docs/readiness-recovery-validation.md` | `reports/readiness-recovery-validation.md` | It was frozen only because it travelled with `docs/validation/`. Moved by T-0246 with its name kept. |
| `docs/claude-handoff.md`, `claude-response.md` | `other/` | Loose notes between sessions; owner and review-by needed. |
| `docs/other/orchestration-optimization-question.md` | `other/` | Needs `owner:` and `review-by:`. |
| `docs/docs-schema/` (this design) | `planning/docs-schema/` | Status `proposed`; until it moves it is a tenth top-level folder and fails D-1, so it is listed in `## Legacy`. |

### maison

| Today | Becomes | Note |
| --- | --- | --- |
| `docs/reference/` | `references/` | Rename, 30 tracked files. |
| `docs/reports/` | `reports/` | Already date-prefixed. |
| `docs/maintenance/gen-ui-audit-2026-10-03/` | One report `reports/2026-10-03-gen-ui-audit.md` (from `gen-ui-gap-analysis.md`) with a sibling evidence folder for the 3 JSON files, and `planning/` for `implementation-plan.md` | A dated audit whose JSON has no same-stem Markdown today. The plan names which Markdown file is the report. |
| `docs/gen-ui-evaluation/` | `planning/gen-ui-evaluation/` | maison's `AGENTS.md` calls it "proposed; future evaluation plan". |
| `docs/assets/` | `assets/` | Already. |

## Migration

- **Opt-in and never automatic.** A repository with an existing coherent layout keeps it. Adopting means binding its non-default homes in `## Kinds` and listing the paths it will not touch in `## Legacy`. New files are fully checked from that point.
- **Order:** inventory (read-only), then a plan, then a gated apply that moves in batches with a citing-file scan, one commit per batch and undo by `git revert`. The apply gate is the follow-up ticket from the reorganization project and is not part of this design.
- **The citing scan covers code and entry files, not only Markdown.** `check.py` reads `docs/maintenance/claude-hooks.md` by path at run time, and root `AGENTS.md`, `plugins/sdlc-lite/AGENTS.md`, `README.md` and the two `HARNESS-NOTES.md` files cite moving paths. The rewriter in the reorganization draft covers tracked Markdown, so ticket 4 widens it.
- **The validation move is separate and earlier.** The user decided to rename `docs/validation/` to `docs/reports/` now. T-0246 does it as a one-off mechanical rename with the apply step's safety properties (dry-run list, citing scan, one commit per batch, undo by `git revert`), because the gated apply tool does not exist yet. It amends the reorganization draft's frozen list. T-0244 covers the rest of this repository's moves and no longer includes validation.
- **Published artifacts keep old paths.** Tags and already-published GitHub release pages cite `docs/validation/...`; they cannot change, and the next release record says so in one sentence.
- **This repository goes last.** It is the test of the tooling, so its migration depends on the apply ticket.
- **No stubs.** A moved file leaves no stub. The apply step rewrites links.

## Risks

- A fixed set of nine homes will not fit every project. The mitigation is a visible `## Kinds` line for each non-default home.
- The planning-to-spec step needs a person or a model to write the spec. If nobody does, `planning/` fills with accepted documents. D-8 reports it.
- The `## Legacy` list can go stale if a migration renames files without updating it. The apply step rewrites it like any other citer.
- Extending setup to homes and nested topics changes the `docs/AGENTS.md` output for every adopter, maison included. Row 6 of the upsert table replaces their managed blocks on the next setup.
- If the user keeps `planning/` and the principle sentence is not amended, two live documents contradict each other, and a later role follows whichever it read first. Ticket 2 owns the amendment.
- The validation rename touches 385 files and rewrites citations in 327 others, including dated release records. The path-token-aware rewrite, the commit per batch and the stale-reference check with its negative control are the mitigation; the accepted cost is that published release pages and tags keep the old paths.
- B-2a will misclassify some `.sdlc/` files. It is a warning for that reason.
- D-9 would still reject an evidence file with no named report. The mapping row for each such folder must name its report.

## Open questions, with safe defaults

Questions 1 to 4 of the earlier draft are resolved (see Resolved decisions). Still open:

5. Is the 90-day `review-by` horizon right? Default 90 days.
6. Should `README.md` stay optional? Default optional.

## Validation plan

Each check gets a fixture repository with a positive case and a negative control:

- A clean fixture reports no findings. A fixture with an unknown top-level folder fails D-1, and a mutated script that drops D-1 fails the selftest.
- The same pattern for D-2 to D-12 and B-1a to B-3a.
- `parse_layout` accepts a file with `## Kinds` and `## Legacy`, and the current parser still reads the same file without error (the review ran it). A `## Kinds` or `## Legacy` line outside the forms fails with the file and line.
- Legacy scope: a path matched by `## Legacy` passes D-3, D-4, D-9 and D-12 without the file-name or front matter rule, an unlisted or untracked path fails, and D-5, D-6, B-1a and B-2a still fire on a legacy path.
- A decision number used twice under `decisions/` fails D-12.
- A read-only run of `docs_check.py` on this repository and on maison reports each finding with the rule id, and writes nothing there.

## Build tickets

Each is size S or M and fits one solo step. They are filed as `proposed`.

1. **Schema format and parser (T-0241):** `## Kinds` and `## Legacy` in `onboard.py`'s `parse_layout`, `Layout` gains `kinds` and `legacy`, with the selftest. Depends on nothing.
2. **`docs_check.py`, the setup model and the default template (T-0242):** checks D-1 to D-12, entry files for homes and topics under a home (D-7) written by setup only after a dry-run diff and one question (decision 4), the updated default layout and `docs/AGENTS.md` text, and the two sentence amendments in `docs/repo-onboarding/design.md` (the no-entry-for-homes sentence and the Number prefixes sentence). Depends on 1.
3. **The `.sdlc` boundary checks (T-0243):** B-1a, B-2a and B-3a in `docs_check.py` with `check.sh` wiring. Depends on 2.
4. **This repository's migration (T-0244):** inventory, plan and gated apply to the layout above, except the validation move, including the widened citing scan. Depends on 2 and on the gated apply ticket from the reorganization project.
6. **Rename `docs/validation/` to `docs/reports/` (T-0246):** the one-off mechanical rename the user asked for now, with the reference rewrite, the stale-reference check and the freeze amendment. Depends on the `reorg-inventory` merge only, not on tickets 1 to 5.
5. **Promotion helper (T-0245):** a small script that copies a `.sdlc` artifact to a `docs/` home with the `source:` front matter. Depends on 1.
