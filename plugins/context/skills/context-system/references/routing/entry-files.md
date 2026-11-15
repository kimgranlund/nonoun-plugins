# Entry files

Load when writing, restructuring or reviewing a file an agent or person opens first: a repository's `AGENTS.md`, `CLAUDE.md` or `README.md`, a package's local entry, an `AUTHORING.md`, or a skill's `SKILL.md`. The principles behind it are in [the tier model](tier-model.md#entry-intent-and-ownership); the fill-in skeleton is [the local entry template](../../templates/local-entry.md).

Contents: [Shape](#shape) · [Route table](#route-table) · [Contents line](#contents-line) · [Budgets](#budgets) · [Host and skill entries](#host-and-skill-entries) · [Placement](#placement) · [Anti-patterns](#anti-patterns) · [Enforcement ladder](#enforcement-ladder) · [Checks](#checks)

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

## Placement

Where a rule or fact lives is decided by who must receive it, when, and whether it must hold whatever the reader
decides. Take the first row that fits. The home is one place; every other surface routes to it.

| The rule or fact | Lives in | Because |
|---|---|---|
| Must hold whatever the agent decides | A check that blocks or reports ([enforcement ladder](#enforcement-ladder)), with the rule stated once in its contract | Text is advisory on every host |
| Applies to every task and every agent, delegated ones included | The root entry, or a file the host loads with it | Only the always-loaded set reaches every start |
| Governs one scope or one kind of task | A contract in the corpus, reached by a route row with a load condition | A nested entry or a scoped rule may carry it too, but a host may deliver those only after the first read or write in the scope |
| Is a procedure used on some tasks, in more than one corpus | A skill; its description is its route | The body loads only on use |
| Is about one person or one machine | The host's personal memory, or a local uncommitted file | It reaches no other person, machine or delegated agent |

Memory, a local file or a skill is never the only home of a rule the corpus's other readers need. What each surface
delivers, and when, is host behaviour: read it from the [host adapter](hosts/claude-code.md), do not assume it.

## Anti-patterns

- A wall of rules before any route; rules with no named check.
- "Read everything first" or a mandatory read list for every task.
- Tables copied from their owning file, inventories and counts typed by hand.
- Links with no load condition, so every link looks required.
- Authors and consumers mixed in one sequence of steps.
- History, changelogs and dated evidence in the entry instead of linked records.

## Enforcement ladder

A rule in an entry or a contract is advisory. An agent acts against it when the conversation says to, when the rule
was never delivered, or when it was summarized away. The check a rule names sits on one of three rungs:

| Rung | The check | What happens to a breach |
|---|---|---|
| Stated | None: the sentence alone, marked as judgement | Nothing; it relies on the reader |
| Detected | A lint, validator or test, run by hand or as a CI gate | Reported after the act; a gate keeps it from merging |
| Blocked | A host hook or permission rule that refuses the action | Prevented, whatever the agent was told |

Put a rule on the lowest rung whose failure the corpus can afford, and name that rung's check beside the rule. A
blocked rule is still stated once in its contract, and the block's message says what to do instead. A block covers
only the actions it matches (a hook on file edits does not see a shell command). Its negative control is the same
request with the block removed: the breach must happen without it and must not happen with it.

## Checks

- Every link resolves, including anchors (a link checker or the repository's packaging check).
- Every route row names a representative task; test a sample statically or with a fresh agent ([routing review](../review/briefs-and-acceptance.md)).
- Every invariant names the check that enforces it and its rung ([enforcement ladder](#enforcement-ladder)), or is marked as judgement.
- Generated inventories pass their drift check; for registries, run `scripts/check_registry.py` ([manifests](../manifests.md#registries)).
