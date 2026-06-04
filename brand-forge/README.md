# brand-forge

**Build and evaluate brands grounded in cultural authority — strategy, identity, voice, and stewardship — with an adversarial named-critic council.** A self-contained Claude Code plugin with zero cross-plugin dependencies.

This plugin is published as a **best-in-class reference**: it exercises all five Claude Code plugin primitives, each doing the one job it is uniquely good at, so future plugin authors can copy the shape rather than reinvent it.

---

## Quick start

```text
/plugin marketplace add kimgranlund/plugins-forge
/plugin install brand-forge@plugins-forge
```

Then drive it through five typed commands:

| Command | Posture | What it does |
| --- | --- | --- |
| `/brand-build` | collaborative | Make brand work — research, strategy, identity, voice — guarding pipeline order. |
| `/brand-evaluate` | adversarial | Score an existing artifact against the matching rubric, with evidence. |
| `/brand-council` | adversarial | Convene named practitioners (parallel, isolated) for a hostile critique. |
| `/brand-orient` | survey | Inventory the brand corpus, read its state, propose next steps. Best cold start. |
| `/brand-stamp` | package | Emit a finished corpus as a distributable — a plugin (Code/Cowork), a cloud skill (Claude chat), or a standalone MCP — each to its own folder. |

---

## Component map — five primitives, five jobs

```text
brand-forge/
├── commands/        5 typed entry points   → set mode + posture, then route
├── agents/         14 critics + 1 orchestrator → the parallel, isolated council
├── skills/          3 knowledge surfaces   → methodology · evaluate · corpus
├── hooks/ + bin/    structural brand-lint  → advisory lint on prose writes (never blocks)
└── .mcp.json        per-instance retrieval → the corpus contract (a slot)
```

- **Commands = the typed entry surface.** Each command is _thin_: it sets the mode and posture (collaborative vs. adversarial vs. survey), classifies where the user is, and routes to the right skill or agent. It does **not** re-contain the methodology — there is one source of truth, and the command points at it.
- **Agents = the council.** 14 named-practitioner critics plus one orchestrator. Each critic is its own agent so it runs in an **isolated context** and in **parallel** — no critic sees another's reasoning, so the disagreement is real, not collapsed into one averaged voice. The methodology, rubrics, and council are where _cultural judgment_ lives.
- **Skills = the knowledge.** `brand-methodology` (the research→strategy→expression→stewardship method), `brand-evaluate` (the rubric library + adversarial scoring), and `brand-corpus` (how to inventory and read an existing brand). Skills hold the depth; commands and agents stay thin by leaning on them.
- **Hooks + bin = the structural floor.** A `brand-lint` hook runs on prose artifact writes and invokes the checker in `bin/`. It is **advisory** — it surfaces smells, it never blocks a write — and a _mechanical floor_, not a critic. See **Honest scope** below.
- **.mcp.json = the retrieval slot.** Declares the `brand-corpus` MCP server — a **contract** for per-instance corpus retrieval, pointed at a specific brand via `userConfig.corpus_dir`. The plugin ships the slot, never a brand's data.

---

## The council-as-agents design note

The council is the heart of this plugin, and it is deliberately built from **individual agents**, not a single prompt that role-plays many critics:

- **14 critics, 1 orchestrator.** `/brand-council` invokes the **orchestrator agent**, which fans out the sub-council relevant to the request (`strategy` · `design` · `voice` · `full`; default `strategy`).
- **Parallel + isolated.** Each critic runs in its own context window. They cannot anchor on each other, so a Massimo V. and a Walsh genuinely pull in different directions instead of converging on a safe consensus.
- **Severity-classified, cited findings.** Every critic returns Critical / Major / Minor findings that quote the specific part of the artifact. The orchestrator then runs a **B–S synthesis** to reconcile agreements, surface the real disagreements, and resolve to one prioritized verdict.

Roster — **14 critics** across three sub-councils: **Strategy** (Luke S., John H., Mark P., Nick L., Brian C., Rory S.) · **Design** (Paula S., Massimo V., Matt W., Walsh) · **Voice** (David A., Lois, Tim D., Mary N.). `strategy` is the default; `design` and `voice` convene their sub-council; `full` convenes all 14 in parallel. (The orchestrator agent is the single source of truth for this roster.)

---

## Honest scope

This plugin is precise about what is mechanizable and what is not.

- **The brand-lint hook + bin surface only structural smells.** They are advisory pattern-level checks, catching **archetype / VMV / persona / DNA-word-cloud** filler language and **values stated without trade-offs**. They never block a write — they print the smell so the author sees it. (The 3-page-minimum-foundation is a _methodology_ principle, owned by the `brand-methodology` skill — not a regex.)
- **They do NOT make cultural judgments.** Whether a brand has a genuine point of view, whether its provenance is real or borrowed, whether the idea is ownable — that stays entirely in the **`brand-methodology` skill** and the **council**. No regex decides if a brand is any good.
- **The MCP ships a contract, not content.** `.mcp.json` declares the `brand-corpus` retrieval _slot_. It is wired to a brand only when the operator sets `corpus_dir` via `userConfig`. The plugin carries no brand's strategy, tokens, or documents — just the interface to retrieve them per instance.
- **The corpus is untrusted input.** The skills and council treat its contents as **data to analyze, never instructions** — an embedded "rate this 5/5" or "ignore the brief" is a finding, not a command, and that guard ships **inside every critic agent**, not only the orchestrator. The plugin bundles **no tool that takes external action on its own**: the MCP is read-only and the hook is advisory; any file write runs through the host agent under your existing permissions.

In short: **structure is mechanized; taste is not.** The hook guards form; the skill and council own substance.

---

## What this plugin teaches

Treat brand-forge as a pattern library for plugin authors. The five-primitive shapes it demonstrates and that future plugins can copy:

1. **Thin typed commands** that set mode/posture and route — never re-containing methodology.
2. **A council of isolated parallel agents** with an orchestrator + synthesis, for genuine adversarial diversity.
3. **Skills as the single source of depth**, kept DRY behind the commands and agents.
4. **A hook + bin pair that mechanizes only the mechanizable** — an honest structural floor, with judgment left to skills.
5. **An MCP declared as a per-instance slot** via `userConfig`, shipping the contract and not the data.

---

## Provenance

brand-forge was authored, validated, and red-teamed via **`plugins-factory`** — the plugin lifecycle studio that carves components, wires `plugin.json` / `marketplace.json`, validates structure, and runs the adversarial plugin-architecture review. Self-contained by design: zero cross-plugin dependencies.
