# Machinery kinds

The inventory pass (capability 0) runs before any concept is drawn. One pass per kind, in this
order. Kinds are told apart in diagrams by shape and a mono prefix, never by color: color stays
state and accent.

| Kind | Detection globs | Fields to extract | Shape | Prefix |
|---|---|---|---|---|
| Skills | `**/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md` | trigger, steps, reference files, who invokes it | rounded node `( )` | `skill:` |
| Agents | `agents/*.md`, `.claude/agents/*.md`, agent blocks in settings | model, effort, tools, NOT-clauses, who dispatches whom | box `[ ]` inside an ownership subgraph | `agent:` |
| Commands | `commands/`, CLI verbs in scripts, Makefile targets, `package.json` scripts | the verb, who may run it, side effects | hexagon `{{ }}` | `cmd:` |
| Rules | CLAUDE.md, AGENTS.md, `*-rules` skills, permission entries | the must or never sentence, its owner, its rung | note attached to what it constrains | `rule:` |
| Hooks | `hooks.json`, hooks in settings, `githooks/`, `.husky/` | event, matcher, whether it blocks or warns | gate diamond `{ }` on the edge it guards | `hook:` |
| Linters and checkers | check scripts, CI workflows, selftests, pre-commit config | what fails, when it runs | gate diamond, labeled at commit or at CI | `check:` |
| Evaluators | eval suites, rubrics, scored judges, benchmarks, baselines | what is scored, the rubric or dataset, the threshold, the baseline compared against, when it runs | gate diamond, labeled scored, threshold on the edge | `eval:` |
| Verifiers | verifier agents, acceptance criteria, verdict records, pre-land and release gates | what it grades, its own evidence, its negative control, its independence from the maker (context, model family, seat) | gate diamond labeled verdict, thick result edge | `verify:` |
| Ontologies | id namespaces, label sets, state enums, glyph sets, frontmatter schemas | each term, where defined, where used | the legend plus a vocabulary table, not a node | `term:` |
| Knowledge bases | records dirs, `docs/`, ADRs, memory files, ledgers, boards | who writes, who reads, the staleness rule | cylinder `[( )]` | `kb:` |
| Also: generators and templates | template dirs, codegen scripts, scaffolds | what it emits, who regenerates it, whether output is committed | cylinder | `gen:` |
| Also: config and modes | `*.config.*`, `.sdlc/config.json`, env files, presets | each axis, its values, its default, who reads it | cylinder | `cfg:` |
| Also: state stores | runtime dirs, caches, lockfiles, job records, databases | who writes, who reads, lifetime | cylinder | `store:` |
| Also: external doors | adapters, MCP servers, API clients, webhooks | the verbs it exposes, the backend behind it, the one door rule | hexagon | `door:` |

## How to run the pass

1. Glob first, read second. Record the path of every hit before opening anything.
2. Per item, fill every field in its row. A field you cannot fill from a file is written as
   unknown, never guessed.
3. Count per kind. The count is output 1 and it is what tells you whether a kind is missing
   entirely, which is itself a finding.
4. Note who invokes each item and which record it writes. That is what output 2, the machinery
   map, is drawn from: kinds as lanes, invocation as edges.
5. Carry every rule you found straight into `enforcement-ladder.md`.

## Kind-level findings

- A kind with zero items in a system that clearly needs it, for example rules with no hooks and
  no checkers behind them.
- A skill nothing references, an agent nobody dispatches, a command no document mentions.
- A knowledge base with no writer, or with no staleness rule.
- A term used in labels but defined nowhere, or defined twice in different places.
