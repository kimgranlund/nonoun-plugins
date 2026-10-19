# Repository onboarding: entry files and docs layout

Status: implemented v0.7. Recorded: 2026-09-29. T-0160 implements it in `plugins/sdlc-lite/scripts/onboard.py` and the `onboard` skill. Ticket: T-0160.

This document covers setup. [Document reorganization](../../planning/repo-onboarding/reorganization.md) covers moving existing files. Host loading behavior is described in the [layered context reference](../../references/layered-context-pattern.md). Evidence is in the [first review](../../reports/repo-onboarding-design-review.md), the [second review](../../reports/repo-onboarding-design-review-2.md), the [third review](../../reports/repo-onboarding-design-review-3.md), and the [loading probe](../../reports/nested-entry-file-loading.md).

## Problem

SDLC Lite on Claude Code has no setup step. The runner and ticket scripts create `.sdlc/` when they first need it, and nothing else is prepared. Codex has an opt-in install (`codex_roles.py install`) that writes managed agent files with an ownership receipt, but it prepares agents and not project context. A repository that starts using SDLC Lite therefore has:

- No guaranteed root entry file, so a role has no stated route into the project.
- No instructions explaining how `docs/` and `.sdlc/` are managed.
- No stated home per document type.

[Progressive Context](../../../plugins/progressive-context/skills/progressive-context/SKILL.md) already defines the navigation model: small entry points that link to durable contracts and evidence. This proposal applies that model at the moment a repository adopts SDLC Lite.

## Decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| Owner | A new SDLC Lite skill named `onboard` | Progressive Context is an authoring skill with no runtime and no prescribed folder tree. Setup is execution work. |
| Navigation model | Progressive Context | It is this repository's own model. ICM is not used and is not a dependency. |
| Entry file name | `AGENTS.md` | Progressive Context names `AGENTS.md` as the concise instruction and navigation entry point. |
| Guidance for `.sdlc/` | In the root entry. No `.sdlc/AGENTS.md` | SDLC Lite tells a project to ignore `.sdlc/` in Git by default, so a file there is local and a link to it breaks in a fresh clone. |
| Existing `README.md` indexes | Kept in place | The entry file links to an index that already owns the folder's contents. |
| Docs layout | Opinionated default that a repository can override | A default removes a decision for new repositories. An existing coherent layout is kept. |
| Layout location | Its own file, `docs/layout.md` | A script parses it, so it needs a strict format. Keeping it apart leaves the entry file short and lets setup create it when it is missing. |
| Number prefixes | Optional, order only | A number can order documents or stages. It never stores maturity. |
| Monorepos | Out of scope for version 1 | One root, one `docs/`, one `.sdlc/`. |
| How roles reach entries | The planner names them per step | The hosts load nested entries differently, so roles cannot depend on host loading. Ticket T-0162. |
| Who writes | One script, `scripts/onboard.py`, writes every file | All output is deterministic and testable. The model fills nothing in. |
| Git | Required | Setup stops outside a Git work tree, because tracked files and ignore rules define what it sees. |

## Files

| File | Managed block | Starter text |
| --- | --- | --- |
| Root `AGENTS.md` | Link to `docs/AGENTS.md`, the guidance for work records, and the rule that plan, build, and verify work runs through SDLC Lite | Headings for project description, shared rules, and checks |
| Root `CLAUDE.md` | `@AGENTS.md` | None |
| `docs/AGENTS.md` | How to add a document, and links to topics, homes, and loose documents | None |
| `docs/CLAUDE.md` | `@AGENTS.md` | None |
| `docs/layout.md` | None. The repository owns the whole file. The upsert table does not apply to it | The default layout and frozen paths |
| `docs/<topic>/AGENTS.md` | Link to each document in the topic | A placeholder line for what the topic covers |
| `docs/<topic>/CLAUDE.md` | `@AGENTS.md` | None |

An entry file has up to two parts. The managed block belongs to the skill and is replaced on update. Starter text is written once when the skill creates the file. After that the repository owns it and the skill never changes it. The skill never adds starter text to a file that already exists.

The template text is in [Templates](#templates).

### Definitions

- A home is a folder that `docs/layout.md` lists under `## Homes`.
- A topic is a folder directly under `docs/` that is not a home and is not matched by a frozen path.
- A document is a tracked Markdown file other than `AGENTS.md`, `CLAUDE.md`, `README.md`, and `docs/layout.md`.
- A loose document is a document directly in `docs/`.
- A topic's documents are counted through all its subfolders. A topic gets an entry file and a stub once it holds two or more documents. A topic with one document is linked from `docs/AGENTS.md` directly.
- When a topic has a `README.md`, the topic entry links to it first.
- A home, and a topic folder directly under a home, gets an entry file and a stub once it holds two or more documents (T-0242; the homes are the nine of [the docs schema](../../planning/docs-schema/design.md) plus `goals/` and `kpi/` from [goals and KPIs](goals-and-kpi.md), and `work/` from T-0634). The `work/` home never gets one from setup: `tickets.py` writes its entry. `docs/AGENTS.md` links to the home's `README.md` when it exists, to its entry when it has one, and names the folder otherwise. A report's evidence folder never gets one. A home entry lists at most 20 documents and then counts the rest.
- Setup writes nothing inside a folder that a frozen path matches.
- Setup never deletes a file. An entry stays when its topic later falls to one document.
- Setup creates no empty folders.

### Rules

- A parent entry links each child entry with an ordinary Markdown link.
- The only `@` import is `@AGENTS.md` for the file in the same folder. A parent never imports a child, because the import loads at once and pulls every child into context.
- Nested entries narrow the root rules and never contradict them. How a host settles a conflict is untested.
- Size targets are 60 lines for the root entry and 30 lines for a nested one. The skill reports a file over target and never trims it. These are starting values. This repository's own root entry is 70 lines.

### How roles reach an entry

Claude Code loads a nested `AGENTS.md` only through an `@` import in a `CLAUDE.md` that is itself loaded. Codex loads entries from the repository root down to its working directory, and SDLC Lite roles start at the root. Host loading therefore cannot be the mechanism for roles.

- For each plan step, the planner names the nearest entry file above each file the step changes. The list reaches the step handoff, and the role reads those files. Details are in ticket T-0162, and the [entry files live run](../../reports/entry-files-live-run.md) shows it on both hosts.
- A Claude Code role that reads a file in a `docs/` folder also gets that folder's entry through the stub. The entry is then in context twice. The cost is accepted. In the probe, a run with two 25-line entries used about 1,600 more input tokens on Claude Code and about 1,800 more on Codex. The probe report notes that the difference is not purely the entry files, which by size alone are about 430 tokens each.
- The stubs in `docs/` serve interactive sessions, which have no handoff.

## Commands

| Command | Effect |
| --- | --- |
| `onboard.py setup --dry-run` | Prints the diff of every change and writes nothing. |
| `onboard.py setup [--force]` | Writes the changes. Without `--init` it refreshes only the managed blocks files already hold (rows 4 with `--force` and 6) and lists on stderr each file `--init` would create or append to. |
| `onboard.py setup --init [--force]` | Also creates missing files (row 1, `docs/layout.md`) and appends to unmanaged ones (row 8). |
| `onboard.py check` | Reports the state of each file and writes nothing. |

The skill runs the dry run, shows the diff, asks the user once, and then runs setup.

Setup and check parse `docs/layout.md` when it exists, to tell topics from homes and to find frozen paths. On a parse error they stop, name the file and line number, and write nothing.

## Upsert behavior

The script decides per file, in this order. The first row that matches applies. `docs/layout.md` is outside this table: setup with `--init` creates it when it is missing and never touches it otherwise. Rows 1 and 8 apply only with `--init`.

| # | State | Action |
| --- | --- | --- |
| 1 | File missing | Create it with the managed block and the starter text. |
| 2 | Markers are malformed | Write nothing to this file and report it. |
| 3 | Block present, version newer than the plugin's | No change. Report it. |
| 4 | Block present, text edited by hand | No change. Report it. `--force` replaces it. |
| 5 | Block present, text equals the current template | No change. |
| 6 | Block present, anything else | Replace the text between the markers with the current template. |
| 7 | No block, template is the import only, file already has the import | No change. |
| 8 | No block | Append the full managed block. Existing content stays byte-identical. |

Definitions for the table:

- A marker is a whole line outside any code fence. A marker line inside a code fence is ordinary text.
- Markers are malformed when a start marker has no end marker after it, an end marker has no start marker before it, or the file has more than one block.
- The start marker is `<!-- sdlc-lite:managed:start v<N> sha256:<H> -->` and the end marker is `<!-- sdlc-lite:managed:end -->`.
- `<N>` is one version number for the whole template set. It rises when any template changes.
- The block text is the bytes strictly between the two marker lines, with line endings normalized to LF. The marker lines are not part of it, so the hash is computed before the start marker is written.
- `<H>` is the first 12 hex characters of the SHA-256 of the block text as the skill wrote it.
- A block is edited by hand when the hash of its current text differs from `<H>`.
- A file has the import when a line outside any code fence, with trailing whitespace removed, is exactly `@AGENTS.md` or `@./AGENTS.md`.
- Row 8 can repeat a link the file already has elsewhere. That is accepted, because detecting an equivalent link in free text is unreliable.

Every change is shown as a diff before it is written. A second run in a row matches row 5 or row 7 for every file and changes nothing.

Check mode writes nothing. It reports each file as current (rows 5 and 7), stale (row 6), edited (row 4), newer (row 3), malformed (row 2), missing (row 1), or unmanaged (row 8). For `docs/layout.md` it reports only present or missing. It exits nonzero when any file is not current or present. The markers and the hash are the ownership record. There is no separate receipt file.

## Default docs layout

```text
docs/
  AGENTS.md        entry: how to add a document, links to topics
  CLAUDE.md        @AGENTS.md
  layout.md        homes and frozen paths, parsed by the script
  <topic>/         one folder per concept the project reasons about
    AGENTS.md      entry, once the topic has two or more documents
    CLAUDE.md      @AGENTS.md
    design.md      approach, interfaces, rejected alternatives
    decisions/     one file per decision
  guides/          how to operate, release, and repair
  references/      stable lookup material
  reports/         dated evidence: benchmarks, validation runs, assessments
```

| Document type | Home |
| --- | --- |
| Design or specification | `docs/<topic>/` |
| Decision record | `docs/<topic>/decisions/` |
| Operating procedure | `docs/guides/` |
| Lookup material | `docs/references/` |
| Dated result or assessment | `docs/reports/` for new records, unless it sits beside the contract it assesses |
| Capability contract | Wherever its owner keeps it, often beside the implementation. The topic entry links to it. |

The `docs/reports/` home is a default of this skill. Progressive Context does not require it and allows a directory to hold a contract, its implementation, and its evidence together. What Progressive Context does require is one authoritative location per fact, so a record has one home and other places link to it.

A contract is not required per topic. One capability can span several topics and one topic can hold several capabilities. A contract keeps a stable ID, so its path is a locator and not its identity.

### Override

The layout a repository uses is whatever its `docs/layout.md` says. The repository edits that file freely, and the skill never changes it after creating it.

### Layout file

`docs/layout.md` has two sections that the script parses. Inside a section, a line is a list line when its first character after optional spaces is `-`, `*`, or `+`. Every list line must fit one of the forms below. Any other line is ignored, so the file can hold explanatory text.

```text
## Homes
- `<home>/`
- `<home>/` takes `<glob>`, `<glob>`

## Frozen paths
- `<glob>`
```

| Element | Meaning |
| --- | --- |
| `<home>/` | A folder path relative to `docs/`, ending in a slash. |
| `<glob>` under Homes | A pattern matched against a document's path relative to `docs/`. `*` matches within one path segment and `**` matches across segments. A pattern without a slash matches the file name in any folder. Setup ignores these globs. They are for document reorganization. |
| `<glob>` under Frozen paths | A pattern matched against a path relative to the repository root. A pattern ending in a slash matches everything under that folder. |

The script stops, writing nothing, and names the file and line number when:

- Either section heading is missing or appears twice.
- A list line does not fit the forms above.
- The same home is listed twice.

An empty section is valid.

### Number prefixes

An `NN-` prefix is optional and expresses order only. It may be used for:

- Documents in a topic that have a real reading order, as in `docs/specs/generative-constructs/`.
- Stage folders in a reusable workflow definition, following the optional [workflow stage guidance](../../../plugins/progressive-context/skills/progressive-context/references/workflow-stages.md).

A number never expresses maturity or status. Whether a capability is intended, implemented, or accepted is derived from its contract and evidence, and a folder name that stored that claim would go stale when the code or criteria change. A document does not move between numbered folders as its state changes. The one status-triggered move the docs schema allows is a planning document that has been superseded, which moves to `archive/` ([docs schema](../../planning/docs-schema/design.md), Planning versus specs).

Inserting an item into a numbered sequence renames the items after it. That is a move, so it follows [document reorganization](../../planning/repo-onboarding/reorganization.md).

## Relationship to Progressive Context

Progressive Context stays domain-neutral and keeps its rule against a prescribed folder tree. The default layout belongs to the SDLC Lite skill.

T-0160 adds one sentence to the Progressive Context SDLC Lite integration reference. The sentence names the `onboard` skill. It does not link to it by path, because an installed plugin may not have its peer at a known relative path.

The skill creates routes and homes for documents. It creates no contracts, assessments, or lifecycle states.

## Role routing

A consumer conductor on 0.18.0 replaced SDLC Lite roles with other plugins' agents for a full day (ticket T-0165). The conductor contract now forbids that. A session that is not the conductor has no such contract, so the root managed block carries the same rule to every session in the repository.

## Validation required before shipping

Existing checks to run, which carry their own controls: the packaging check, the role and skill contract check, generated Codex agent parity, and the Progressive Context skill validation for the one-sentence edit.

New gates. Each tests the skill's own output and needs a positive case and an observed negative control in the script's selftest, except the live run.

| Gate | Positive case | Negative control |
| --- | --- | --- |
| Create | In an empty fixture, every file in the Files table that applies is created with its block and starter text. | A fixture where `docs/` is a regular file makes the run exit nonzero and leaves the fixture unchanged. |
| Preserve | A file with user content gains a block, and the bytes outside the markers are identical. | A template variant that writes outside the markers makes the selftest fail. |
| Idempotence | A second run produces no diff. | A template variant that embeds a run counter makes the selftest fail. |
| Row order | One fixture per row of the upsert table produces that row's action. | A script variant with rows 4 and 6 swapped makes the selftest fail. |
| Import detection | `@AGENTS.md` and `@./AGENTS.md` lines count as the import, and an import inside a code fence does not. | A script variant that skips the code fence rule makes the selftest fail. |
| Layout parsing | A valid file parses into homes and frozen patterns. | A list line without backticks, a duplicate heading, and a home listed twice each stop the script with the line number. |
| Malformed markers | A well-formed block is replaced. | A start marker with no end marker leaves the file byte-identical and is reported. |
| Check mode | A current fixture exits zero. | A stale, an edited, a missing, and an unmanaged fixture each exit nonzero with the matching label. |
| Live run | In a throwaway project on Claude Code and on Codex, after setup, a session started at the root with tools disabled reports the visible marker line of the root managed block. | The same project with the root managed block deleted does not report it. |

The live run reads a visible line and not the marker comments, because Claude Code removes HTML comments from entry files before the model sees them. Codex does not. The Codex live run is a plain session, so it needs only a model the account accepts.

## Unverified assumptions

- The token cost of nested entries in a real role run, which has more turns than the probe.
- An installed plugin can read its own template version at run time on both hosts.
- How either host settles a conflict between a nested rule and a root rule.
- Whether Claude Code removes a duplicate when the same file is imported twice.

## Templates

Text in angle brackets is filled in by the script. Everything outside the markers is starter text. `<N>` and `<H>` are defined under Upsert behavior.

Root `AGENTS.md`:

```markdown
# <repository folder name>

## What this repository is

## Shared rules

## Checks

<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
## Documents

Read [the docs entry](docs/AGENTS.md) before adding or moving a document.

Managed by SDLC Lite onboard, template <N>.

## Work records

`.sdlc/` holds SDLC Lite tickets, plans, and run records.

- Pick the lane first with `steps.py lane <task dir>` (in the plugin's `scripts/` folder): `solo` is the default for ticket levels L1 and L2, `/sdlc-lite:fix` runs only when asked or when the lane script prints `fix`, and the full chain (`/sdlc-lite:chain`) needs a stated reason (an L4 or L5 step, a merge step, or cross-cutting scope). Roles launch with `run.sh`. Do not spawn another plugin's builder, planner, or reviewer agent in their place.
- Worktrees: lanes live in `../<repo>.worktrees/` (`wtroot.py root`, in the plugin's `scripts/` folder). Lane open, the solo and verifier runs in a lane, land and close write `.git` or the lane tree outside the checkout, so under Codex run them with full access, not the `workspace-write` sandbox.
- Several hosts in one repo (Claude Code, Codex, Pi): one conductor writes main; a worker writes only its locked lane, commits nothing, and runs `lanes.py ready` when done (the Lanes section of the plugin's `AGENTS.md`).
- Handoff files follow the `sdlc-lite:handoff-format` skill.
- Tickets are created, closed, and archived through the `sdlc-lite:ticket` skill.
- `.sdlc/roadmap.md` is generated. Do not edit it by hand.
- `.sdlc/messages/` is a local mailbox. Never commit it; a `.gitignore` line for it is advised.
- Do not move or rewrite a finished run record.
<!-- sdlc-lite:managed:end -->
```

`CLAUDE.md`, at the root, in `docs/`, and in a topic that has an entry:

```markdown
<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
@AGENTS.md
<!-- sdlc-lite:managed:end -->
```

`docs/AGENTS.md` and `docs/layout.md`: since T-0242 the text is `DOCS_AGENTS_TEMPLATE` and `LAYOUT_TEMPLATE` in `plugins/sdlc-lite/scripts/onboard.py`, defined by [the docs schema](../../planning/docs-schema/design.md) (`work/`, the nine homes, `goals/` and `kpi/`, the decision list, `## Kinds`, `## Decide`, and an empty `## Legacy`). The `docs/AGENTS.md` block ends with the same `## Contents` placeholders as before; `docs/layout.md` is written only when the file is missing.

The `work/` home (T-0634) holds work records, not documents: ticket and task folders (`NNNN-slug/handoff.md`, dot-renamed in place on close) and the UPPERCASE singletons `ROADMAP.md` and `NOTES.md`, all written by `tickets.py`. It is the first home in the `docs/AGENTS.md` table and the first line of Which home and `## Decide`, and its Kinds row names `tickets.py` as writer and owner. It is used when `.sdlc/config` sets `work_root: docs/work`; without that line the records stay in `.sdlc/`. `docs_check.py` skips D-7, D-9, D-12 and B-1a there and applies the record rule B-2a instead, so a ticket folder, a role-result retry file and the two singletons pass and any other loose file is flagged.

`docs/<topic>/AGENTS.md`:

```markdown
# <topic folder name>

Describe what this topic covers.

<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
## Documents

<a link to README.md when it exists, then one link per document>
<!-- sdlc-lite:managed:end -->
```
