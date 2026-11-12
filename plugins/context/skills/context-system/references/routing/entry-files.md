# Entry files

Load when writing, restructuring or reviewing a file an agent or person opens first: a repository's `AGENTS.md`, `CLAUDE.md` or `README.md`, a package's local entry, an `AUTHORING.md`, or a skill's `SKILL.md`. The principles behind it are in [the tier model](tier-model.md#entry-intent-and-ownership); the fill-in skeleton is [the local entry template](../../templates/local-entry.md).

Contents: [Shape](#shape) · [Route table](#route-table) · [Contents line](#contents-line) · [Budgets](#budgets) · [Host and skill entries](#host-and-skill-entries) · [Anti-patterns](#anti-patterns) · [Checks](#checks)

## Shape

An entry routes; it does not teach. In this order:

1. **Purpose** (one or two sentences): what this scope is, who it is for, what it is not for.
2. **Mode split**, when authors and consumers both arrive here: one line each, "Using … → …; changing … → …" ([authoring and consuming](../manifests.md#authoring-and-consuming)).
3. **Contents**, when the file has four or more sections or runs past one screen: one line of anchor links.
4. **Route table:** task or question → file to read → when to load it (or when to stop).
5. **Invariants:** only the rules that hold across every route, each short and each naming its check.
6. **Commands:** how to verify ("done means green") and the one or two commands every task runs.
7. **Map and index:** where things live, linking a generated inventory rather than listing items by hand.

Everything else (procedures, rationale, history, examples) lives in the files the routes point at.

## Route table

| Column | Rule |
|---|---|
| Task / question | Phrased as the reader's need ("Add a component", "Why is X shaped like this?"), not as a file name |
| Read next | One authoritative file or section per row; link the section anchor when the file is long |
| Load when / stop when | The condition that makes the file necessary, so a reader can skip it otherwise |

Each row ends at an authoritative source within a bounded number of reads; a route that passes through summaries must still deliver the governing content ([traversal](traversal.md)). No row restates a rule that its target owns. Order rows by frequency of use, and keep author rows and consumer rows apart.

## Contents line

A contents line lists the file's own sections as anchor links on one line (`Contents: [Shape](#shape) · …`), directly under the purpose. It is not a second route table: it orients a reader inside one file. Generate it, or check it, when the file changes often; a stale anchor is a broken route.

## Budgets

- The root entry fits in about one screen; detail moves into linked files with a load condition.
- An always-loaded set (host instructions, the root entry) stays minimal: everything in it costs every task.
- A skill's `SKILL.md` stays under the host's re-injection limit and routes to references; each reference link says when to load it.
- Inventories (components, skills, endpoints) are generated into an index file and linked, never copied into the entry; copied counts go stale.

## Host and skill entries

- One canonical, tool-neutral entry (`AGENTS.md`); host files (`CLAUDE.md`, Codex instructions) import or point to it and add only host-specific facts.
- A nested entry covers its own scope and links up to the root for shared rules; it never repeats them.
- A skill's frontmatter `description` is its routing surface: what it does, when to use it, and the nearest cases it does not cover. Its body opens with purpose, contents and a route table, like any entry; trigger cases live in its eval suite.

## Anti-patterns

- A wall of rules before any route; rules with no named check.
- "Read everything first" or a mandatory read list for every task.
- Tables copied from their owning file, inventories and counts typed by hand.
- Links with no load condition, so every link looks required.
- Authors and consumers mixed in one sequence of steps.
- History, changelogs and dated evidence in the entry instead of linked records.

## Checks

- Every link resolves, including anchors (a link checker or the repository's packaging check).
- Every route row names a representative task; test a sample statically or with a fresh agent ([routing review](../review/briefs-and-acceptance.md)).
- Every invariant names the check that enforces it, or is marked as judgement.
- Generated inventories pass their drift check; for registries, run `scripts/check_registry.py` ([manifests](../manifests.md#registries)).
