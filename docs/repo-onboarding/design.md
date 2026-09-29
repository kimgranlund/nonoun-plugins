# Repository onboarding and document reorganization

Status: proposed v0.2. Recorded: 2026-09-29. Nothing in this document is implemented.

v0.2 incorporates an independent review of v0.1 made on 2026-09-29. The review did not cover the number prefix section, which was added after it started.

## Problem

SDLC Lite on Claude Code has no setup step. The runner and ticket scripts create `.sdlc/` when they first need it, and nothing else is prepared. Codex has an opt-in install (`codex_roles.py install`) that writes managed agent files with an ownership receipt, but it prepares agents and not project context. A repository that starts using SDLC Lite therefore has:

- No guaranteed root entry file, so a role has no stated route into the project.
- No instructions inside `.sdlc/` or `docs/` explaining how their content is managed.
- Documents wherever they happened to be written, with no stated home per document type.

[Progressive Context](../../plugins/progressive-context/skills/progressive-context/SKILL.md) already defines the navigation model: small entry points that link to durable contracts and evidence. This proposal applies that model at the moment a repository adopts SDLC Lite.

## Decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| Owner | A new SDLC Lite skill, provisionally `onboard` | Progressive Context is an authoring skill with no runtime and no prescribed folder tree. Setup and file moves are execution work. |
| Navigation model | Progressive Context | It is this repository's own model. ICM is not used and is not a dependency. |
| Entry file name | `AGENTS.md` in every scoped folder | Progressive Context names `AGENTS.md` as the concise instruction and navigation entry point. |
| Docs layout | Opinionated default that a repository can override | A default removes a decision for new repositories. An existing coherent layout is kept. |
| Number prefixes | Optional, order only | A number can order documents or stages. It never stores maturity. |
| Reorganization | Read-only scan, then a move plan filed as a ticket, then approval | Moves touch links across the whole repository and may collide with concurrent work. |
| Mechanics | One deterministic script owns inventory, the link graph, refusals, and the final check | A refusal has to come from something that can be tested with a negative control. |

## Entry files

An entry file routes and instructs. It states where the reader is, what lives in the folder, which rules apply to changing it, and which linked file to read for a given task. It does not hold contracts, task history, or evaluation results.

| Location | Managed block content |
| --- | --- |
| Root `AGENTS.md` | Route lines to `docs/AGENTS.md` and `.sdlc/AGENTS.md`. Project description, shared rules, and checks are authored by the project and are outside the block. |
| Root `CLAUDE.md` | One line, `@AGENTS.md`, so Claude Code loads the same file. |
| `.sdlc/AGENTS.md` | Routes only: which SDLC Lite skill owns the handoff format, which owns tickets, that `roadmap.md` is generated, and where repository settings live (`.sdlc/config`). |
| `docs/AGENTS.md` | The layout this repository uses, the document type map, the frozen paths, and how to add a document. |
| `docs/<topic>/AGENTS.md` | What the topic covers, its documents, and any rule that differs from the parent. |

Rules for every entry file:

- A parent entry links each child entry. Reaching a child never depends on the host loading it automatically, because a file named `AGENTS.md` is not proof it was loaded.
- `.sdlc/AGENTS.md` does not restate the handoff or ticket format. Those facts are owned by the plugin's skills and would go stale in a per-repository copy after a plugin update. It names the owning skill and stops.
- `.sdlc/AGENTS.md` never contains a ticket folder path. The skill checks its own managed block for one and refuses to write it. This cannot be left to `tickets.py close`: the close scan refuses on a cite only when the citing file is visible to Git, and a repository that ignores `.sdlc/` gets no refusal and keeps the stale cite.
- When `.sdlc/` is ignored by Git, `.sdlc/AGENTS.md` is a local file. The skill reports that, and the root entry carries the route either way.
- An existing `README.md` that already owns a folder's index is kept. The entry file links to it and does not repeat it.
- A topic folder gets an entry file once it holds two or more documents. A single document is linked directly from the parent.
- Proposed size targets are 60 lines for the root entry and 30 lines for a nested one. The skill reports a file over target and never trims it. This repository's root entry is 70 lines and the SDLC Lite plugin entry is 40, so the targets are starting values to test, not established limits.

### Upsert behavior

| State | Action |
| --- | --- |
| File missing | Create it from the template. |
| File exists and already links every target the block would add | No change. |
| File exists without a managed block and lacks a target | Append one managed block holding only the missing routes. Existing content stays byte-identical. |
| File exists with a managed block | Replace only the text between the markers. |
| Only `CLAUDE.md` exists | Create `AGENTS.md` with the managed block, then append a managed block to `CLAUDE.md` holding `@AGENTS.md`. Existing `CLAUDE.md` content stays byte-identical. |

The managed block is delimited by `<!-- sdlc-lite:managed:start v<N> -->` and `<!-- sdlc-lite:managed:end -->`, where `<N>` is the template version. Every change is shown as a diff before it is written. Running the skill twice in a row produces no change.

A check mode reports managed blocks whose template version is older than the installed plugin's and writes nothing. It follows the existing `codex_roles.py install --check` pattern.

## Default docs layout

```text
docs/
  AGENTS.md        entry: layout, document type map, frozen paths
  <topic>/         one folder per concept the project reasons about
    AGENTS.md      entry, once the topic has two or more documents
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

### Number prefixes

An `NN-` prefix is optional and expresses order only. It may be used for:

- Documents in a topic that have a real reading order, as in `docs/generative-constructs/`.
- Stage folders in a reusable workflow definition, following the optional [workflow stage guidance](../../plugins/progressive-context/skills/progressive-context/references/workflow-stages.md).

A number never expresses maturity or status. Whether a capability is intended, implemented, or accepted is derived from its contract and evidence, and a folder name that stored that claim would go stale when the code or criteria change. A document does not move between numbered folders as its state changes.

Inserting an item into a numbered sequence renames the items after it. That is a move, so it follows the scan and ticket path below and is not done by hand.

### Override

`docs/AGENTS.md` states the layout the repository actually uses, including where its existing dated evidence lives. The default above is only the starting text. The scan compares files against the layout stated there, so a repository changes the layout by editing one file.

## Scan and reorganization

The skill has two modes with different risk. Setup writes entry files and is safe to repeat. Reorganization moves files and always goes through a ticket.

One script performs every mechanical step below. It has a selftest, like the other SDLC Lite scripts. The link rewriting in `tickets.py` is not reused: it replaces only the last path component of a cite, so it cannot express a move to another directory, and it does not adjust links inside a moved file.

1. **Inventory.** List tracked Markdown files and the entry files the skill manages. Classify each by path and name rules. A file the rules cannot place is listed as unclassified for the user to decide. Build the link graph. This step is read-only.
2. **Plan.** Write a move plan as a normal ticket in `.sdlc/`: each source path, its destination, the reason, every link that must change, and a digest of the inventory the plan was made from.
3. **Approve.** The user reviews the ticket. Nothing moves before approval.
4. **Apply.** The script recomputes the inventory digest and refuses when it differs from the plan's. Moves use `git mv`. Links are rewritten in citing files and inside each moved file.
5. **Check.** Every link in every file that is not frozen resolves. Frozen files are byte-identical to their state before the run.

### Frozen material

The scan never moves or rewrites:

- Ticket folders and run records under `.sdlc/`.
- Benchmark results, including stored diffs.
- Dated reports and validation evidence.
- Generated files: `.sdlc/roadmap.md`, a consumer project's `.codex/agents/`, and in this repository `plugins/sdlc-lite/adapters/codex/agents/`.
- Vendored and ignored paths.

The frozen set is the default paths above plus the paths listed in `docs/AGENTS.md`. The inventory proposes further candidates, such as a file with a date in its name or a `Recorded:` line, and the user confirms them in the plan. Detection only proposes. The list in `docs/AGENTS.md` decides.

Frozen material that does not match the layout is not a defect to fix by moving. `docs/AGENTS.md` records where it lives, and new records follow the layout.

A frozen record may cite a path that has since moved. That is accepted. The record describes the material that was assessed at the time, and rewriting it would break the binding between evidence and the revision it checked.

### Move safety

The script refuses, writing nothing, when:

- A destination collides with an existing path after case folding. macOS and Windows would overwrite silently.
- The plan would leave a broken link in any file that is not frozen.
- The plan moves or rewrites a frozen path.
- A `.run.lock` or `*.running` marker exists under `.sdlc/`, which means a role is running.

## Relationship to Progressive Context

Progressive Context stays domain-neutral and keeps its rule against a prescribed folder tree. The default layout belongs to the SDLC Lite skill. When the skill ships, the Progressive Context SDLC Lite integration reference names it by skill name. It does not link across plugins by path, because no shipped Progressive Context file does so today and an installed plugin may not have its peer at a known relative path.

Ticket closure still does not accept a capability. The onboarding skill creates routes and homes for documents. It creates no contracts, assessments, or lifecycle states.

## Validation required before shipping

Each gate needs a positive case and an observed negative control.

| Gate | Positive case | Negative control |
| --- | --- | --- |
| Skill packaging | Packaging checks, role and skill contract checks, and generated Codex agent parity pass. | The existing checks already carry their own controls. |
| Upsert | A missing file is created. A second run changes nothing. | A template change that would alter bytes outside the markers makes the selftest fail. |
| Ticket path check | A managed block with routes only is written. | A managed block containing a ticket folder path is refused. |
| Staleness check | A current block reports clean. | A block with an older template version is reported stale. |
| Move plan | A valid plan applies and every link resolves. | Each refusal is observed: frozen path, broken link, case-folded collision, running marker, and changed inventory digest. |
| Ticket closure | A numbered ticket closes in a repository that has `.sdlc/AGENTS.md`, with `.sdlc/` tracked and with `.sdlc/` ignored. | An entry file that cites the ticket blocks closure when `.sdlc/` is tracked. |
| End to end | In a throwaway project: entry files exist, the plan ticket passes verification, and no link is broken. | The same run with one broken link seeded fails the final check. |

Two items are measurements that inform the design. They are not gates until a threshold is chosen:

- Which entry files each host loads, recorded from a live run per host.
- Input tokens for a role run with and without nested entry files.

## First trial: this repository

This repository does not match the default, which makes it a realistic first case:

- Five documents sit loose in `docs/`: `claude-handoff.md`, `claude-response.md`, `codex-role-execution.md`, `plugin-compatibility.md`, and `readiness-recovery-validation.md`.
- `docs/validation/` and `docs/readiness-recovery-validation.md` are dated evidence. They are frozen, so they stay where they are and `docs/AGENTS.md` records their location.
- `docs/` and `docs/generative-constructs/` use `README.md` as their index and have no `AGENTS.md`.
- `docs/` paths are cited by the root `AGENTS.md`, the root `README.md`, `plugins/sdlc-lite/AGENTS.md`, and both plugins' `HARNESS-NOTES.md`. A move would change those cites.
- Both plugin folders already hold a one-line `CLAUDE.md` containing `@AGENTS.md`.

## Observed during review

- An `AGENTS.md` file in the `.sdlc/` root did not disturb `tickets.py` (check, roadmap, close, archive dry run), `board.py` (default, summary, lanes), or a `fanout.py` dry run. Their root enumerations read directories only. `steps.py`, `run.sh`, a real fanout run, and the Codex paths were not run.
- `tickets.py close` refused on a cite in `.sdlc/AGENTS.md` when `.sdlc/` was tracked, and did not refuse when `.sdlc/` was ignored.

## Unverified assumptions

- Claude Code loads a nested `CLAUDE.md` when it reads files in that folder and does not load a nested `AGENTS.md`. Codex loading of nested `AGENTS.md` is also untested here.
- An `@AGENTS.md` import works when it sits between HTML comment markers.
- A nested entry file adds input tokens to each role run that reads files in that folder. The amount is unmeasured.
- An installed plugin can read its own template version at run time on both hosts.

## Open questions

- Does a nested folder also need a one-line `CLAUDE.md` stub beside its `AGENTS.md`? This repository already does that for its plugin folders. The host loading measurement decides whether topic folders need it too.
- In a monorepo, does each package get its own entry file and `docs/` folder?
- Should an existing `README.md` index be converted to `AGENTS.md`, or left in place as it is in this proposal?
- Is `onboard` the right skill name?
