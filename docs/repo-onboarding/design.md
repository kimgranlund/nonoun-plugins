# Repository onboarding: entry files and docs layout

Status: proposed v0.4. Recorded: 2026-09-29. Nothing in this document is implemented. Ticket: T-0160.

This document covers setup. [Document reorganization](reorganization.md) covers moving existing files. Host loading behavior is described in the [layered context reference](layered-context-pattern.md). Evidence is in the [design review](../validation/repo-onboarding-design-review.md) and the [loading probe](../validation/nested-entry-file-loading.md).

## Problem

SDLC Lite on Claude Code has no setup step. The runner and ticket scripts create `.sdlc/` when they first need it, and nothing else is prepared. Codex has an opt-in install (`codex_roles.py install`) that writes managed agent files with an ownership receipt, but it prepares agents and not project context. A repository that starts using SDLC Lite therefore has:

- No guaranteed root entry file, so a role has no stated route into the project.
- No instructions inside `.sdlc/` or `docs/` explaining how their content is managed.
- No stated home per document type.

[Progressive Context](../../plugins/progressive-context/skills/progressive-context/SKILL.md) already defines the navigation model: small entry points that link to durable contracts and evidence. This proposal applies that model at the moment a repository adopts SDLC Lite.

## Decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| Owner | A new SDLC Lite skill named `onboard` | Progressive Context is an authoring skill with no runtime and no prescribed folder tree. Setup is execution work. |
| Navigation model | Progressive Context | It is this repository's own model. ICM is not used and is not a dependency. |
| Entry file name | `AGENTS.md` in every scoped folder | Progressive Context names `AGENTS.md` as the concise instruction and navigation entry point. |
| Existing `README.md` indexes | Kept in place | The entry file links to an index that already owns the folder's contents. |
| Docs layout | Opinionated default that a repository can override | A default removes a decision for new repositories. An existing coherent layout is kept. |
| Number prefixes | Optional, order only | A number can order documents or stages. It never stores maturity. |
| Monorepos | Out of scope for version 1 | One root, one `docs/`, one `.sdlc/`. Per-package entries can follow the layered context reference later. |
| How roles reach entries | The planner names them per step | The hosts load nested entries differently, so roles cannot depend on host loading. Ticket T-0162. |

## Entry files

An entry file routes and instructs. It states where the reader is, what lives in the folder, which rules apply to changing it, and which linked file to read for a given task. It does not hold contracts, task history, or evaluation results.

Each entry file has two parts:

- A managed block that the skill owns and replaces on update.
- Starter text that the skill writes once when it creates the file. After that the repository owns it and the skill never changes it.

| File | Managed block | Starter text |
| --- | --- | --- |
| Root `AGENTS.md` | Links to `docs/AGENTS.md` and `.sdlc/AGENTS.md` | Headings for project description, shared rules, and checks |
| Root `CLAUDE.md` | `@AGENTS.md` | None |
| `.sdlc/AGENTS.md` | Which skill owns the handoff format, which owns tickets, that `roadmap.md` is generated, and that settings live in `.sdlc/config` | None |
| `docs/AGENTS.md` | How to add a document and a link to each topic entry | The layout and the frozen paths |
| `docs/<topic>/AGENTS.md` | None | What the topic covers and a link to each document |
| `CLAUDE.md` beside a nested `AGENTS.md` in `docs/` | `@AGENTS.md` | None |

The template text is in [Templates](#templates).

### Rules

- A parent entry links each child entry with an ordinary Markdown link.
- The only `@` import is `@AGENTS.md` for the file in the same folder. A parent never imports a child, because the import loads at once and pulls every child into context.
- Nested entries narrow the root rules and never contradict them. How a host settles a conflict is untested.
- `.sdlc/` gets no `CLAUDE.md`. A stub there would load the entry into every Claude Code role run that reads a handoff. This is revisited when the token cost in a real role run is measured.
- `.sdlc/AGENTS.md` does not restate the handoff or ticket format. It names the owning skill, so it cannot go stale when the plugin updates.
- `.sdlc/AGENTS.md` never contains a ticket folder path. The skill checks its own managed block for one and refuses to write it. `tickets.py close` cannot be relied on for this, because it does not see a file that Git ignores.
- When Git ignores `.sdlc/`, `.sdlc/AGENTS.md` is a local file. The skill reports that, and the root entry carries the link either way.
- A topic folder gets an entry file once it holds two or more documents. A single document is linked directly from the parent.
- Size targets are 60 lines for the root entry and 30 lines for a nested one. The skill reports a file over target and never trims it. These are starting values. This repository's own root entry is 70 lines.

### How roles reach an entry

Claude Code loads a nested entry only through a `CLAUDE.md` beside it. Codex loads entries from the repository root down to its working directory, and SDLC Lite roles start at the root. Host loading therefore cannot be the mechanism for roles.

- For each plan step, the planner names the entry file of every folder the step changes. The list reaches the step handoff, and the role reads those files.
- A Claude Code role that reads a file in a `docs/` folder also gets that folder's entry through the stub. The entry is then in context twice. The cost is accepted: it is bounded by the 30-line target, about 400 tokens per entry in the probe.
- The stubs in `docs/` serve interactive sessions, which have no handoff.

The planner and handoff change is its own ticket, T-0162, because it alters role behavior and needs a live run.

### Upsert behavior

A target is a link or import that the managed block would add.

| State | Action |
| --- | --- |
| File missing | Create it with the managed block and the starter text. |
| File exists and already contains every target | No change. |
| File exists without a managed block and lacks a target | Append one managed block holding only the missing targets. Existing content stays byte-identical. |
| File exists with a managed block | Replace only the text between the markers. |
| `CLAUDE.md` exists and `AGENTS.md` does not | Create `AGENTS.md`, then treat `CLAUDE.md` by the rows above. |

A target counts as present when the file contains a Markdown link whose path resolves to the target file, or for an import, a line that is exactly `@AGENTS.md`.

The managed block is delimited by `<!-- sdlc-lite:managed:start v<N> -->` and `<!-- sdlc-lite:managed:end -->`, where `<N>` is the template version. Every change is shown as a diff before it is written. Running the skill twice in a row produces no change.

Check mode reports managed blocks whose template version is older than the installed plugin's and writes nothing. It follows the existing `codex_roles.py install --check` pattern.

## Default docs layout

```text
docs/
  AGENTS.md        entry: layout, frozen paths, how to add a document
  CLAUDE.md        @AGENTS.md
  <topic>/         one folder per concept the project reasons about
    AGENTS.md      entry, once the topic has two or more documents
    CLAUDE.md      @AGENTS.md
    design.md      approach, interfaces, rejected alternatives
    decisions/     one file per decision
  maintenance/     how to operate, release, and repair
  reference/       stable lookup material
  reports/         dated evidence: benchmarks, validation runs, assessments
```

| Document type | Home |
| --- | --- |
| Design or specification | `docs/<topic>/` |
| Decision record | `docs/<topic>/decisions/` |
| Operating procedure | `docs/maintenance/` |
| Lookup material | `docs/reference/` |
| Dated result or assessment | `docs/reports/` for new records, unless it sits beside the contract it assesses |
| Capability contract | Wherever its owner keeps it, often beside the implementation. The topic entry links to it. |

The `docs/reports/` home is a default of this skill. Progressive Context does not require it and allows a directory to hold a contract, its implementation, and its evidence together. What Progressive Context does require is one authoritative location per fact, so a record has one home and other places link to it.

A contract is not required per topic. One capability can span several topics and one topic can hold several capabilities. A contract keeps a stable ID, so its path is a locator and not its identity.

### Override

The layout a repository uses is the `## Layout` section of its `docs/AGENTS.md`. That section is starter text, so the repository edits it freely and an update never overwrites it. The default above is only what the skill writes on creation.

### Number prefixes

An `NN-` prefix is optional and expresses order only. It may be used for:

- Documents in a topic that have a real reading order, as in `docs/generative-constructs/`.
- Stage folders in a reusable workflow definition, following the optional [workflow stage guidance](../../plugins/progressive-context/skills/progressive-context/references/workflow-stages.md).

A number never expresses maturity or status. Whether a capability is intended, implemented, or accepted is derived from its contract and evidence, and a folder name that stored that claim would go stale when the code or criteria change. A document does not move between numbered folders as its state changes.

Inserting an item into a numbered sequence renames the items after it. That is a move, so it follows [document reorganization](reorganization.md).

## Relationship to Progressive Context

Progressive Context stays domain-neutral and keeps its rule against a prescribed folder tree. The default layout belongs to the SDLC Lite skill. When the skill ships, the Progressive Context SDLC Lite integration reference names it by skill name. It does not link across plugins by path, because an installed plugin may not have its peer at a known relative path.

The skill creates routes and homes for documents. It creates no contracts, assessments, or lifecycle states.

## Validation required before shipping

Each gate needs a positive case and an observed negative control.

| Gate | Positive case | Negative control |
| --- | --- | --- |
| Skill packaging | Packaging checks, role and skill contract checks, and generated Codex agent parity pass. | A skill folder with a broken route fails the packaging check. |
| Create | Each missing file is created with its managed block and starter text. | A run against a read-only target reports the failure and writes nothing else. |
| Preserve | A file with user content gains a block and the content outside the markers is byte-identical. | A template change that alters bytes outside the markers makes the selftest fail. |
| Idempotence | A second run produces no diff. | A template that writes a timestamp makes the selftest fail. |
| Target detection | A file that already links every target is left unchanged. | A file that links a different path with the same name still gains the block. |
| Ticket path check | A managed block with routes only is written. | A managed block containing a ticket folder path is refused. |
| Staleness check | A current block reports clean. | A block with an older template version is reported stale. |
| Ticket closure | A numbered ticket closes in a repository that has `.sdlc/AGENTS.md`, with `.sdlc/` tracked and with `.sdlc/` ignored. | An entry file that cites the ticket blocks closure when `.sdlc/` is tracked. |
| Live run | In a throwaway project on each host, the skill creates the entry files and a following role run completes. | The same project with the root import removed shows the root entry absent from a Claude Code session. |

## Unverified assumptions

- The token cost of nested entries in a real role run, which has more turns than the probe.
- An installed plugin can read its own template version at run time on both hosts.
- How either host settles a conflict between a nested rule and a root rule.

## Templates

Text in angle brackets is filled in by the skill. Everything outside the markers is starter text.

Root `AGENTS.md`:

```markdown
# <repository name>

## What this repository is

## Shared rules

## Checks

<!-- sdlc-lite:managed:start v1 -->
## Routes

- Documents: read [the docs entry](docs/AGENTS.md).
- Tickets, plans, and run records: read [the work entry](.sdlc/AGENTS.md).
<!-- sdlc-lite:managed:end -->
```

`CLAUDE.md`, at the root and beside a nested entry in `docs/`:

```markdown
<!-- sdlc-lite:managed:start v1 -->
@AGENTS.md
<!-- sdlc-lite:managed:end -->
```

`.sdlc/AGENTS.md`:

```markdown
<!-- sdlc-lite:managed:start v1 -->
# Work records

This folder holds SDLC Lite tickets, plans, and run records.

- Handoff and result formats are owned by the `sdlc-lite:handoff-format` skill.
- Tickets are created, closed, and archived through the `sdlc-lite:ticket` skill.
- `roadmap.md` is generated. Do not edit it by hand.
- Repository settings live in `config`.
- Do not move or rewrite a finished run record.
<!-- sdlc-lite:managed:end -->
```

`docs/AGENTS.md`:

```markdown
# Documents

## Layout

- `<topic>/`: designs, specifications, and decisions for one concept
- `maintenance/`: operating procedures
- `reference/`: lookup material
- `reports/`: dated results and assessments

## Frozen paths

- `reports/`

<!-- sdlc-lite:managed:start v1 -->
## Adding a document

1. Pick the home from the layout above.
2. Link the document from the entry of its folder.
3. Put dated evidence in its own file. Do not add it to an entry file.

## Topics

<one link per topic entry>
<!-- sdlc-lite:managed:end -->
```

`docs/<topic>/AGENTS.md`:

```markdown
# <topic>

<one sentence on what the topic covers>

## Documents

<one link per document, with a short description>
```
