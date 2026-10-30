# Document standards registry

One row per document type: where it lives, the standard it follows, its card, its template or schema, and the check that reads it. Read the row, then the one card it names. The shared rules for every type are in [core.md](core.md); [the glossary](../../references/glossary.md) holds the terms. The dated source of this registry is `docs/planning/doc-standards/source-list.md`.

| Type | Home | Standard | Card | Template or schema | Check | Enforcement |
|---|---|---|---|---|---|---|
| Goals | `goals/` | OKR shape, each key result names a KPI ID; STE sentences | [intent.md](intent.md) | - | docs_check G-1 to G-5 | enforced |
| KPI / metric definitions | `kpi/` | Metric schema as data, dbt semantic layer and MetricFlow style; glossary terms | [intent.md](intent.md) | [kpi.json](../../assets/schemas/kpi.json) | docs_check G-1 to G-5, docs_check S-1 | enforced |
| Spec / requirements (SPEC, SRS) | `specs/` | EARS templates, INCOSE rules, stable IDs, Gherkin acceptance | [intent.md](intent.md) | - | docs_check S-2 | enforced |
| PRD | `planning/` | Plain Language (ISO 24495) narrative; EARS or user stories; KPI IDs | [intent.md](intent.md) | - | - | advisory |
| HLD / architecture | `specs/` | C4 model, diagrams as code, one ADR per decision | [design.md](design.md) | - | - | advisory |
| LLD | `specs/` | Interface contracts first; DITA reference shape; EARS or Design-by-Contract invariants | [design.md](design.md) | - | - | advisory |
| API docs | `references/` | OpenAPI as source of truth; Microsoft or Google developer style; one runnable example per endpoint | [design.md](design.md) | - | - | advisory |
| Runbooks / procedures | `guides/` | Full STE; DITA task shape; warning before, expected result after | [knowledge-ops.md](knowledge-ops.md) | [runbook.tmpl](../../assets/templates/runbook.tmpl) | docs_check S-4 | enforced |
| Agent task / ticket / work order | `.sdlc/` | Fixed schema: goal, context, constraints, definition of done, out of scope, verification command | [work-items.md](work-items.md) | [ticket.json](../../assets/schemas/ticket.json) | - | advisory |
| System prompts / agent instructions | host prompt files | Plain Language, imperative, one rule per line, priority order, glossary terms, eval cases | [prompts.md](prompts.md) | - | - | advisory |
| Test plans / cases | `specs/` | Gherkin or a typed test schema with requirement traces | [knowledge-ops.md](knowledge-ops.md) | [test-case.json](../../assets/schemas/test-case.json) | - | advisory |
| Report / analysis | `reports/` | Pyramid Principle; Plain Language; traceable numbers; claims and evidence marked apart | [knowledge-ops.md](knowledge-ops.md) | - | docs_check S-6 | enforced |
| Research notes / literature | `reports/` | Structured abstract; evidence-level tags; resolvable citations; open questions listed | [knowledge-ops.md](knowledge-ops.md) | - | - | advisory |
| Postmortem / incident | `reports/` | Blameless template; timestamped timeline; action items with owners | [knowledge-ops.md](knowledge-ops.md) | [postmortem.tmpl](../../assets/templates/postmortem.tmpl) | - | advisory |
| Decision records | `decisions/` | ADR, Nygard shape; one per file; immutable once accepted | [design.md](design.md) | [adr.tmpl](../../assets/templates/adr.tmpl) | docs_check S-3 | enforced |
| Changelog / release notes | `CHANGELOG.md` | Keep a Changelog with Conventional Commits categories; semantic versioning | [delivery.md](delivery.md) | - | - | advisory |
| Glossary / ontology | `references/` | One term, one part of speech, one definition, unapproved aliases | [knowledge-ops.md](knowledge-ops.md) | - | - | advisory |
| Policies / guardrails | `specs/` | RFC 2119 keywords; one rule per statement; EARS for conditional rules | [knowledge-ops.md](knowledge-ops.md) | - | docs_check S-5 | enforced |
| Bug report | tracker or `.sdlc/` | Fixed template; STE reproduction steps; severity on a defined scale | [work-items.md](work-items.md) | [bug.tmpl](../../assets/templates/bug.tmpl) | - | advisory |
| Feature request / enhancement | tracker or `.sdlc/` | Plain Language problem; user story with Gherkin acceptance; no solution in the body | [work-items.md](work-items.md) | [feature-request.tmpl](../../assets/templates/feature-request.tmpl) | - | advisory |
| Task / chore ticket | tracker or `.sdlc/` | The agent-task schema; done checkable by a command or test | [work-items.md](work-items.md) | [ticket.json](../../assets/schemas/ticket.json) | - | advisory |
| Epic / parent issue | tracker | OKR objective; child IDs in dependency order; no implementation detail | [intent.md](intent.md) | - | - | advisory |
| Issue titles | tracker | Typed prefix, scope, imperative summary under 72 characters | [work-items.md](work-items.md) | - | - | advisory |
| Spike / investigation | tracker or `.sdlc/` | Question, time box, decision fed, deliverable; closes with the finding | [work-items.md](work-items.md) | [spike.tmpl](../../assets/templates/spike.tmpl) | - | advisory |
| PR title and body | host PR | Conventional Commits title; fixed body: what, why, how to verify, risks, checklist | [delivery.md](delivery.md) | [pr-body.tmpl](../../assets/templates/pr-body.tmpl) | - | advisory |
| Commit messages | git history | Consumer repos: Conventional Commits; this repo: plain imperative subject and Co-Authored-By trailer | [delivery.md](delivery.md) | - | - | advisory |
| PR review comments | host PR | Conventional Comments with blocking or non-blocking decorations | [delivery.md](delivery.md) | - | - | advisory |
| Issue / PR labels | tracker | Closed documented vocabulary, one axis per family: type, priority, status, area | [work-items.md](work-items.md) | - | - | advisory |
| Definition of done / acceptance checklist | issue template | Gherkin or a yes or no checklist, every item verifiable | [work-items.md](work-items.md) | - | - | advisory |
| Release / milestone | `CHANGELOG.md` | Keep a Changelog scoped to one version; closed issues by ID | [delivery.md](delivery.md) | - | - | advisory |
| Agent file | `plugins/sdlc/agents/` | Role body: numbered rules, closed-step line, result keys from results.py | [prompts.md](prompts.md) | - | prompt_lint P-1, P-2, P-3, P-5, P-6 | enforced |
| Skill | `plugins/sdlc/skills/` | When to use, then the procedure; every script call real | [prompts.md](prompts.md) | - | prompt_lint P-2, P-3, P-6; check.py argument hints (H-1 to H-7) | enforced |
| Overlay | `plugins/sdlc/overlays/` | One section per level band: gap defaults low, goal, KPI and budget high | [prompts.md](prompts.md) | - | prompt_lint P-1, P-2, P-3, P-4, P-6 | enforced |
| Handoff | `.sdlc/` | Self-contained brief with runnable acceptance criteria | [prompts.md](prompts.md) | - | - | advisory |
| Tool description | host tool definition | What it does, when to call it, when not to | [prompts.md](prompts.md) | - | - | advisory |

Home is a folder under `docs/` unless it names another place. Enforcement is `enforced` when a check.sh gate fails on at least one rule in the row's Check cell, and `advisory` otherwise; the tier of each rule is below. A row whose Check is `-` is advisory.

## Rules

docs_check S-* and G-* errors fail check.sh's repository gate (`docs_check.py --root`). S-2, S-4, S-5, and S-6 read only a file that opts in with `doc-type:` ([core.md](core.md)).

- S-1 (enforced): each `docs/kpi/NNN-slug.md` front matter has every key in the `required` list of [kpi.json](../../assets/schemas/kpi.json).
- S-2 (enforced): in a `doc-type: requirements` file, a `shall` line starts with a stable ID and a colon, and each requirement has an `Acceptance:` line.
- S-3 (enforced): a decision record in `decisions/` has exactly one `## Decision` heading.
- S-4 (enforced): a `doc-type: runbook` file has at least one numbered step line.
- S-5 (enforced): a `doc-type: policy` file writes must, shall, should, and may in upper case only.
- S-6 (enforced): in a `doc-type: report` file in `reports/`, each relative link and path code span resolves.
- S-7 (enforced): this registry links every card in its folder, its card and asset links resolve, its header is the one above, and each row's Enforcement is `enforced` or `advisory`, `advisory` when Check is `-`.

prompt_lint P-1 to P-3 errors fail check.py item 53; P-4 to P-6 never change an exit code ([prompts.md](prompts.md)).

- P-1 (enforced): a `rule N` cite in an agent file or overlay names a top-level numbered line of the role body.
- P-2 (enforced): a plugin script subcommand and each `--flag` named in a code span or fenced command exist in that script.
- P-3 (enforced): each plugin-root path and bare script path in a prompt file resolves.
- P-4 (advisory, warning): an overlay's smallest-level section holds `### Gap defaults`; its largest-level section holds `### Goal`, `### KPI`, and `### Budget`.
- P-5 (advisory, warning): a role body has a closed-step or closed-ticket line, and the first line under its key section holds only statuses that results.py allows.
- P-6 (advisory, information): counts of prohibitions, upper-case NEVER, and vague words.
