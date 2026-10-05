# Docs schema and the docs/.sdlc boundary

Status: draft v0.4, recorded 2026-10-05, after one independent architect review of v0.1 ([record](../validation/docs-schema-design-review.md)). v0.2, v0.3 and v0.4 were not reviewed by the architect again; v0.4 adds the context registry pattern, which is grounded in cited evidence and has placement unproven until T-0248 passes. Design only: nothing here is implemented, and no file moves in any repository because of this document. Ticket T-0240.

Every choice marked **(user may change)** is a default I picked and justified. The rest follows from the repository's own files.

## Resolved decisions

The user decided these on 2026-10-05. They override any older sentence below that says otherwise.

1. **Planning and specs stay two homes,** split by purpose (what is not built versus what is built or accepted). A superseded plan moves to `archive/`.
2. **Names are plural,** and `guides/` replaces `maintenance/`. This repository's and maison's `maintenance/` content maps to `guides/` or `references/` by what it is (see Mappings).
3. **`docs/validation/` is renamed to `docs/reports/` now.** The user chose this against the earlier default (a legacy home bound to `reports`). There is no legacy home for validation any more. The move is its own ticket, T-0246, which waited for the `reorg-inventory` merge (landed as 24fdd8c) and amends the freeze sentence in `docs/repo-onboarding/reorganization.md`. The `## Legacy` mechanism stays, only for files that are really grandfathered, such as existing report names that do not follow the date rule.
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

## The context registry pattern

Added 2026-10-05 at the user's request: any harness or session must be able to adopt the organizing principles from the folders alone. The pattern below is one scheme used identically for `docs/` and `.sdlc/`. It is grounded in cited evidence and its placement effect is **unproven** until the placement proof (T-0248) passes. This design counts the pattern as proven only after that test, and every claim below carries a label.

### Need, and what grounds it

Progressive Context says to "add no registry ... without an actual need" (`plugins/progressive-context/skills/progressive-context/SKILL.md`, line 24). The need here is placement: a session that must put a new document or record somewhere has no stated rule. This repository's `docs/` holds 7 folders and 5 loose files, and the review counted that only 8 of 69 `docs/validation/` names carry a date. That shows the rule is missing, not that a registry fixes it, so the placement proof decides whether the registry stays. The registry is owned by SDLC Lite and not by Progressive Context, which keeps its rule against a prescribed folder tree.

| Claim | Label | Source |
| --- | --- | --- |
| Claude Code loads a nested `CLAUDE.md` when a file in its folder is read, loads a parent folder's `CLAUDE.md`, does not load a nested `AGENTS.md` without a `CLAUDE.md` beside it, and `@AGENTS.md` in a nested `CLAUDE.md` works | observed here | `docs/validation/nested-entry-file-loading.md`, one trial per arm, Claude Code 2.1.284 |
| Codex loads `AGENTS.md` files from the root down to the working directory, not a nested entry when a file there is only read, not a sibling folder's, and not `CLAUDE.md` | observed here | same file, Codex CLI 0.154.0 |
| A fresh Claude Code role and a fresh Codex role, given only a path and no skill, followed the folder's `AGENTS.md` procedures and acted correctly; a wrong injected `AGENTS.md` was followed and the run failed | observed here | `docs/validation/messages-live-run.md` (T-0179), one trial per arm |
| A role on a plan step reads the entry files that govern the files it changes, when the handoff lists them | observed here | `docs/validation/entry-files-live-run.md` (T-0162), one trial per arm |
| A generated managed block keeps user text byte-identical, and a block that differs from its template reads `stale` or `edited` | observed here | `onboard.py check` and `onboard.py selftest` run on 2026-10-05; the record `docs/validation/onboard-live-run.md` shows only that the block reaches the model |
| The parser in `onboard.py` ignores a `## Kinds` table and a `## Decide` list and returns the same homes and frozen paths | observed here | run on 2026-10-05 with `onboard._parse_layout_text` on a layout holding both sections |
| Authored fields are separate from computed ones, a projection is generated or verified against its source and records its source revision, and shared generation detects defined classes of drift without proving behavior | observed here (as stated design) | `docs/generative-constructs/progressive-context-plugin.md`, "Manifest ownership and projections" |
| Instructions in retrieved documents are data and cannot change harness policy; entry files are harness-loaded context | observed here (as stated design) | `docs/generative-constructs/04-context-and-harness.md`, "Trust and authority" |
| Nested per-folder `AGENTS.md` files read by several coding agents, the nearest one to the edited file taking precedence | established elsewhere (the agents.md convention), not re-verified here, and the Codex row above shows the loading rule differs by host | named only |
| Four documentation kinds: tutorials, how-to guides, reference, explanation | established elsewhere (Diataxis, by Daniele Procida), not re-verified here | named only; mapping below |
| A short numbered record of one decision with status, context, decision and consequences, superseded and not edited | established elsewhere (Michael Nygard's architecture decision records, and the MADR template), not re-verified here | named only |
| The nine homes, the registry columns, the `## Decide` list, the render rule and the drift check | our convention | this design |
| A session given only a path inside a registry folder places a new document in the right home more often than without the registry | unproven | T-0248 |

Two consequences of the observed rows. First, Codex run from the repository root does not load a home's own entry, so the compact registry in the parent entry (`docs/AGENTS.md`, `.sdlc/AGENTS.md`) must be enough to place a document by itself; the home's entry adds detail for sessions that work inside it. Second, a home entry is only auto-loaded on Claude Code when a `CLAUDE.md` imports it, which the existing entry-file rule already requires.

Diataxis mapping, where it fits: `guides/` is how-to, `references/` is reference, `specs/` and `planning/` are explanation, and a tutorial has no home (a repository that needs one puts it under `guides/`). Our `decisions/`, `reports/`, `assets/`, `archive/` and `other/` are records and holding areas that Diataxis does not cover, and `planning/` versus `specs/` (built versus not built) is our split and not a Diataxis one.

### One schema, one layout, one render, one drift check

**Registry row (one schema).** Eleven fields, the same for a docs home and a `.sdlc` record type:

| Field | Meaning |
| --- | --- |
| `id` | the folder (`specs/`) or file (`notes.md`) the row governs |
| `kind` | one of the fixed kinds for docs, or a record kind for `.sdlc` |
| `holds` | what belongs here |
| `not` | what does not, each with the place it goes instead |
| `why` | the principle, one phrase |
| `writer` | who writes it and when |
| `form` | naming and required front matter or file shape |
| `life` | how it ends: promote, supersede to `archive/`, `review-by`, close, expire |
| `entry` | the folder's own `AGENTS.md`, or none |
| `read` | read when |
| `owner` | the command or check that owns it |

Required and optional in the `## Kinds` table of a layout file: the header must name all eleven columns in this order. `id`, `kind`, `holds`, `not`, `why`, `form` and `read` are required in every row. `writer`, `life`, `entry` and `owner` are optional and may be `-` (shown as blank on the card), except that `entry` is required where the home has an entry file and `owner` is required for `other/`. A row for a home missing from `## Homes`, an unknown `kind` for docs, or a duplicate `id` is `malformed`. The parser change is T-0241.

**Two projections of one row.** The `row` projection (fields `id`, `holds`, `not`, `why`, `form`, `read`) is a table line in the parent entry. The `card` projection (all eleven fields) is the first block of the folder's own `AGENTS.md`, followed by user-owned local rules. A cell is one short phrase; the check reports a cell over 70 characters. Detail lives in this design, linked, and not in the entry.

**The root registry is unconditional.** The topic rule (a folder gets its own entry file at two or more documents) does not apply to the root registry: `docs/AGENTS.md` and `.sdlc/AGENTS.md` list every home and every record kind from the layout regardless of how many documents each holds, so a session can place a first document in an empty home. Only the per-home card follows the two-document rule.

**One entry-file layout.** `AGENTS.md` holds one managed block and then user text. The block of a parent entry holds, in this order: what this system is (one sentence), how to use it (read the registry, pick one home, read one file), the `row` table, the `## Decide` list, and the add-a-document checklist. A home entry holds the `card`. `CLAUDE.md` is one line, `@AGENTS.md`. This is the layout `onboard.py` already writes for entry files, with the block content defined here.

**One source of truth.** The machine-readable registry is `## Kinds` in `docs/layout.md` for docs, and `## Kinds` in `.sdlc/layout.md` for `.sdlc/`: a Markdown table whose header names the eleven fields. The decision list is `## Decide`, ordered lines of the form `N. <question>? yes -> \`id\``, ending in one `otherwise -> \`id\``. The same parser reads both files. For `.sdlc/` the smaller choice is a new `.sdlc/layout.md`: `.sdlc/config` is a plain `key: value` file read by `tickets.py` with its own line rules, and a table in it would risk breaking that reader, while a second file of the same shape needs no new parser. The default content of each file is shipped by the plugin and written once when the file is missing, like `docs/layout.md` today.

**One render mechanism.** A single function, `render_registry(layout, projection)`, in the shared module that `onboard.py` and `tickets.py` already share (`TEMPLATE_VERSION` is shared today), produces the block text, the `row` table, the `## Decide` list and the `card`. Two callers: `onboard.py setup` renders the docs entries and the `.sdlc` entries; `tickets.py roadmap` (also run by `new` and `close`) re-renders the `.sdlc/AGENTS.md` block it already regenerates, with the registry as one more section of that block. This is the smaller choice against a second managed block, which would need a name in the marker and a parser change. Authored fields are only in `layout.md`; the entries are projections that carry the layout's digest, as the generative-constructs material describes.

**One drift check, the existing one.** This extends the check `onboard.py check` already runs (it labels each entry file and reads `docs/layout.md`); it is not a second mechanism and `docs_check.py` does not repeat it. `onboard.py check` recomputes each registry block and card from the layout and compares it with the file: a mismatch reads `stale`, the existing word, and `setup` fixes it. It reports a malformed row (missing field, unknown kind, over-long cell, a `not` with no target) as `malformed`. The same code runs on both layouts and also reads `## Legacy` (a glob that no longer matches any path reports `stale`), so the checks R-1 (drift) and R-2 (row shape) apply identically to `docs/` and `.sdlc/`.

**Size.** `onboard.py`'s target is 60 lines per entry (`ROOT_SIZE_TARGET`). Eleven rows and the three lists fit when cells stay short: about 13 lines of table, 8 of decision list, 6 of checklist and 6 of how-to. The `.sdlc/AGENTS.md` block already lists tickets by stage and is near the target, so T-0243 collapses a stage's ticket list to a count above a small number of entries; that is a generator change in `tickets.py` and is the main size risk.

### Worked examples side by side

Both are first drafts for this repository, in the one schema, with the `row` projection. The `card` for `specs/` and for `messages/` is shown after, also in the one layout.

**docs/** (`## Kinds` of `docs/layout.md`)

| id | holds | not | why | form | read |
| --- | --- | --- | --- | --- | --- |
| `specs/` | what the system is and must do; built or accepted designs | unbuilt plans -> `planning/`; dated evidence -> `reports/` | one place to trust as current | kebab-case; `status`, `date` | when changing or using the feature |
| `planning/` | proposals and designs under review, not built | built behavior -> `specs/` | plans must not read as fact | `status` proposed, accepted, rejected or superseded | before building new work |
| `decisions/` | one decision with its reason | steps -> `guides/` | keep the why | `NNNN-slug.md`; superseded, not edited | when a choice looks odd |
| `references/` | lookup facts: APIs, schemas, glossaries | narrative -> `specs/` | facts you look up, not read through | kebab-case; no steps | when you need a fact |
| `guides/` | how-to steps a person follows | lookup -> `references/` | one task, one procedure | verb-first title; numbered steps | when doing the task |
| `reports/` | dated evidence: reviews, audits, benchmarks, releases | living rules -> `specs/` or `guides/` | evidence stays as recorded | `YYYY-MM-DD-slug.md`; dated corrections only | when judging a claim |
| `assets/` | non-Markdown files a doc cites | Markdown -> its home | keep binaries out of text | named for the doc that cites it | when a doc embeds one |
| `archive/` | superseded or retired material | current material | history without clutter | `git mv`; one line says what replaced it | only when asked |
| `other/` | unsorted documents, as a quarantine | permanent homes | nothing is lost while sorting | `owner:` and `review-by:` required | only to sort it |

**.sdlc/** (`## Kinds` of `.sdlc/layout.md`)

| id | holds | not | why | form | read |
| --- | --- | --- | --- | --- | --- |
| `NNNN-slug/` | a ticket and its work: `handoff.md`, `step-N/`, role results, `runs.jsonl`, `skips.md` | reader docs -> `docs/` | one folder per unit of work | `handoff.md` front matter; results `<role>-L<n>.md` | when claiming or continuing it |
| `<task>/` | work folders with no ticket: `verify-*`, `merge-*`, `release-*` | tickets -> `NNNN-slug/` | same shape as a ticket folder | handoff plus results | when told to |
| `.NNNN-slug/` | a closed ticket | open work -> `NNNN-slug/` | finished work leaves the listing | renamed by `tickets.py close` | only when asked |
| `messages/` | the git-ignored mailbox | anything that must last -> ticket or `notes.md` | hand work between harnesses | front matter `send_time`, `sender`, `receiver`, `topic` | when mail waits for you |
| `evals/` | dated model and effort experiments | the tables themselves | a table change needs evidence | `evals.py` file format | before changing a model table |
| `proposals/` | candidate changes mined from runs | decisions -> `docs/decisions/` | nothing applied without evidence | `proposals.py` format | when triaging |
| `supervisor/` | idle-host watcher config and state, created by `supervisor.py init` | tickets | keep watcher state apart | `hosts.local.json` | when waking a host |
| `notes.md` | follow-ups not filed, one block per closed ticket | open work -> a ticket | nothing is dropped at close | `## T-NNNN: title (date)` | when sweeping open items |
| `roadmap.md` | the generated queue | edits by hand | one ordered view | generated | when choosing next work |
| `config` | repo-owned `key: value` lines | records | tool settings | `ticket_folders`, `ticket_root`, `external_branch` | by tools |

The `.sdlc` `## Decide` list is the placement rule between the two systems:

1. Does a script or role write it while work runs? yes -> its record type row above.
2. Is it a deliverable a reader returns to? yes -> `docs/`, then the docs `## Decide` list.
3. Must a result outlive its ticket? yes -> promote a copy to `docs/reports/` with `source:`, and the `.sdlc` copy stays.
4. Is it a design that outlived its ticket? yes -> promote a copy to `docs/planning/` or `docs/specs/`.
5. otherwise -> it stays in its ticket folder.

The docs `## Decide` list, ordered:

1. Is it not Markdown? yes -> `assets/`.
2. Is it retired or replaced? yes -> `archive/`.
3. Is it a dated record of something that happened (a run, review, audit, benchmark, release)? yes -> `reports/`.
4. Is it one decision with its reason? yes -> `decisions/`.
5. Is it steps a person follows to do a task? yes -> `guides/`.
6. Is it lookup material (a table, API, glossary)? yes -> `references/`.
7. Does it describe something not built yet? yes -> `planning/`.
8. Does it describe what the system is or must do? yes -> `specs/`.
9. otherwise -> `other/`, with `owner:` and `review-by:`.

**Card layout, identical for both** (a managed block at the top of the folder's `AGENTS.md`, then local rules):

```text
## Registry row
- id: `specs/`            - id: `messages/`
- kind: specs             - kind: mailbox
- holds: ...              - holds: ...
- not: ...                - not: ...
- why: ...                - why: ...
- writer: ...             - writer: ...
- form: ...               - form: ...
- life: ...               - life: ...
- entry: `specs/AGENTS.md` - entry: `messages/AGENTS.md`
- read: ...               - read: ...
- owner: ...              - owner: `messages.py`
## Local rules
(user-owned text)
```

The two columns are one layout; only the data differs. The labels in this design apply to these examples: the rows are our convention and carry no evidence until T-0248 passes. The managed block of `docs/AGENTS.md` and `.sdlc/AGENTS.md` must say so in one line while that holds: "placement effect unproven; see docs-schema design".

Cross-references, built separately and not part of this design: T-0252 (records which context a run loaded, which is the measurement a later placement study would use), T-0253 (an entry-file resolver in `onboard.py check`, which R-1 should reuse once it exists), T-0254 (lints and a citation resolver, for D-10), T-0255 (one capability contract) and T-0256 (spec vocabulary). They do not change the registry schema; if T-0253 lands first, the render and drift code use its resolver.

### Placement proof (T-0248)

The test that decides whether the pattern is "proven":

- **Fixture:** a throwaway repository with `docs/` holding one existing document in each of the nine homes, the registry and cards in place, and a control copy with the registry and cards removed and the entry files otherwise unchanged. Built by hand first, so the proof does not wait for the render machinery.
- **Briefs:** 12 short briefs, each describing one new document or record whose correct home is hidden from the sessions and fixed before the run (at least 1 per home, 2 boundary briefs with accepted alternates declared in advance, and 3 for `.sdlc` versus `docs/`).
- **Sessions:** fresh, given only a path inside the folder and the brief, with no skill and no other instruction: Claude Code headless `claude -p`, a Claude headless role (the `solo` agent), Codex `codex exec` run in `docs/`, a Codex native subagent, and an interactive Claude session where one can be driven. A session type that cannot be run is recorded as a limit, not skipped silently.
- **Score:** exact home match per brief, per session type, with the registry and with the control. Evidence is the placement each session wrote, committed.
- **Pass rule, set before the run:** proven for a session type only if the with-registry accuracy is at least 10 of 12 and beats the control by at least 3 briefs; "proven across all session types" requires every run type to pass. N is small and each cell is one run, so no significance is claimed; the record says so.
- **Negative control:** the control copy must misplace more than the registry copy. If it does not, the registry is not shown to help, and the design recommends dropping it, as Progressive Context's own rule says.
- **Until it passes,** the status of the pattern is "grounded in the cited evidence, placement unproven", and the worked examples must not claim more.

## Overriding: docs/layout.md

The parser in `plugins/sdlc-lite/scripts/onboard.py` (`_parse_layout_text`) reads the two required sections `## Homes` and `## Frozen paths`, raises a `LayoutError` on a list line under `## Homes` that does not fit `` `<home>/` [takes `<glob>`, ...] ``, and ignores any other heading of level 2 or less. The review ran the parser on the text below and confirmed that new sections are ignored by it, so a **new section is backward compatible** and a new form inside `## Homes` is not.

`## Homes` stays the single list of top-level folders. Two new sections add meaning to it:

```text
## Kinds
| id | kind | holds | not | why | writer | form | life | entry | read | owner |
| `design-system/` | specs | the design system | unbuilt plans -> `planning/` | one place to trust | people | kebab-case | supersede to `archive/` | `design-system/AGENTS.md` | when using it | `docs_check.py` |

## Legacy
- `reports/old-notes/**`
- `imported-wiki/**`
```

The lines above are an example of the forms, not this repository's file.

- `## Kinds` is the registry table (see The context registry pattern). It binds a home to one of the nine fixed kinds. The earlier line form `` `design-system/` is `specs` `` is dropped before anything shipped it; the table row carries the kind. A home that uses a default name needs no line. A home with a non-default name needs one, and the check reports it as an informational line, so an exception is visible and not forbidden. There is no second mechanism for custom homes.
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
| R-1 | (run by `onboard.py check`, not `docs_check.py`) A registry block or card in an entry file that differs from the one rendered from `## Kinds` of the layout (`stale`); same code for `docs/layout.md` and `.sdlc/layout.md` | error |
| R-2 | A registry row with a missing field, an unknown kind, a cell over 70 characters, or a `not` with no target (`malformed`) | error |

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
| `docs/validation/` (385 tracked files on 2026-10-05, about 325 to 329 other tracked files cite it) | `reports/` | Renamed as a whole by T-0246, waited for the `reorg-inventory` merge, which has landed; file names are kept (8 of 69 top-level names contain a date, so most existing names are covered by a `## Legacy` glob and the date rule applies to new reports only). Historical tags and published release pages keep the old paths. T-0246 amends the freeze sentence in `docs/repo-onboarding/reorganization.md`. |
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
- The validation rename touches 385 files and rewrites citations in about 325 to 329 others, including dated release records. The path-token-aware rewrite, the commit per batch and the stale-reference check with its negative control are the mitigation; the accepted cost is that published release pages and tags keep the old paths.
- B-2a will misclassify some `.sdlc/` files. It is a warning for that reason.
- D-9 would still reject an evidence file with no named report. The mapping row for each such folder must name its report.

## Open questions, with safe defaults

Questions 1 to 4 of the earlier draft are resolved (see Resolved decisions). Still open:

5. Is the 90-day `review-by` horizon right? Default 90 days.
6. Should `README.md` stay optional? Default optional.
7. Is a separate `.sdlc/layout.md` right, or should `.sdlc/config` grow a table? Default a separate file, since `config` is read by `tickets.py` as plain `key: value` lines.
8. If T-0248 shows the registry does not help placement, drop it and keep the nine homes and the `## Decide` list in `docs/AGENTS.md` prose. Default: drop, as Progressive Context line 24 says.

## Validation plan

Each check gets a fixture repository with a positive case and a negative control:

- A clean fixture reports no findings. A fixture with an unknown top-level folder fails D-1, and a mutated script that drops D-1 fails the selftest.
- The same pattern for D-2 to D-12 and B-1a to B-3a.
- `parse_layout` accepts a file with `## Kinds` and `## Legacy`, and the current parser still reads the same file without error (the review ran it). A `## Kinds` or `## Legacy` line outside the forms fails with the file and line.
- Legacy scope: a path matched by `## Legacy` passes D-3, D-4, D-9 and D-12 without the file-name or front matter rule, an unlisted or untracked path fails, and D-5, D-6, B-1a and B-2a still fire on a legacy path.
- A decision number used twice under `decisions/` fails D-12.
- R-1 and R-2: a clean render passes, an edited block fails `stale`, a row missing a field fails `malformed`, and a mutated renderer that skips a row fails the selftest. The same cases run for `docs/layout.md` and `.sdlc/layout.md`.
- Placement proof T-0248 (see The context registry pattern). Until it passes the pattern is "grounded in the cited evidence, placement unproven".
- A read-only run of `docs_check.py` on this repository and on maison reports each finding with the rule id, and writes nothing there.

## Build tickets

Each is size S or M and fits one solo step. They are filed as `proposed`.

1. **Schema format and parser (T-0241):** the `## Kinds` registry table (eleven columns), `## Decide` list, and `## Legacy` in `onboard.py`'s `parse_layout`, `Layout` gains `kinds` and `legacy`, with the selftest. Depends on nothing.
2. **`docs_check.py`, the setup model and the default template (T-0242):** checks D-1 to D-12, entry files for homes and topics under a home (D-7) written by setup only after a dry-run diff and one question (decision 4), the updated default layout and `docs/AGENTS.md` text, and the two sentence amendments in `docs/repo-onboarding/design.md` (the no-entry-for-homes sentence and the Number prefixes sentence). Also the shared `render_registry` function and R-1 and R-2. Depends on 1.
3. **The `.sdlc` boundary checks and registry (T-0243):** B-1a, B-2a and B-3a in `docs_check.py` with `check.sh` wiring, the new `.sdlc/layout.md` record-type registry rendered into `.sdlc/AGENTS.md` by `tickets.py roadmap` through the same render function, and the ticket-list size handling. Depends on 2.
4. **This repository's migration (T-0244):** inventory, plan and gated apply to the layout above, except the validation move, including the widened citing scan. Depends on 2 and on the gated apply ticket from the reorganization project.
6. **Rename `docs/validation/` to `docs/reports/` (T-0246):** the one-off mechanical rename the user asked for now, with the reference rewrite, the stale-reference check and the freeze amendment. Depends on the `reorg-inventory` merge only, not on tickets 1 to 5.
5. **Promotion helper (T-0245):** a small script that copies a `.sdlc` artifact to a `docs/` home with the `source:` front matter. Depends on 1.
7. **Placement proof (T-0248, proposed, size M, solo):** the test in The context registry pattern, built on a hand-made fixture so it does not wait for machinery, run on the session types listed there. It gates the registry parts of T-0242 and T-0243 (the `render_registry` function, R-1, R-2, and the `.sdlc/layout.md` registry): they start only after the proof reports a pass. The T-0241 parser and the other checks do not wait.
