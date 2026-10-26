# Synthetic scenario suite

The suite exercises the same shell across nine distinct purposes. Every fictional scenario has a separate project identity, intent, candidate measure, guardrail and surface inventory. It contains 60 pages/states and 150 decision units with three proposals each.

| Scenario | Responsibility | Coverage |
| --- | --- | --- |
| Marketing: Relay | Support a qualified evaluation through narrative and evidence | Home, product, use case, pricing, illustrative story, pilot request |
| Platform: Common Ground | Explain participants, dependencies and adoption | Overview, architecture, integrations, developer entry, staged adoption, governance |
| Content: Fieldnotes | Support discovery, comprehension and return | Library, topic, search, explanation, collection, saved reading |
| Mobile: Trailmark | Preserve accurate work through short and interrupted sessions | Access, today/resume, permission denial, capture, review/queue, sync conflict, preferences |
| Product: Workshop | Support a delivery object through its lifecycle | Registration, onboarding, orientation, editing, approval, dashboard, personal preferences, shared customization |
| Dashboard: Signal Desk | Connect a question to evidence and intervention | Monitoring, drill-down, comparison, alert response, report, data health |
| Agentic research: Observatory | Commission and challenge a supported decision | Mission, brief, research approval, alternatives, claims/citations, activity, dossier |
| Agentic operations: Switchyard | Govern an autonomous recovery within bounded authority | Exception desk, policy, plan diff, simulation, verification, execution pause, outcome |
| Agentic creation: Atelier | Steer creative branches from a learning goal to a reviewed artifact | Direction desk, brief, concepts, bounded iteration, critique, provenance, release/memory |

## Generate and inspect

Resolve SKILL_DIR to the installed skill folder. No dependency installation is required to build:

```sh
node "$SKILL_DIR/scripts/build-demo-suite.mjs" /absolute/path/to/demo-suite
```

Open `demo.html`. Each scenario has an editable manifest, a self-contained review HTML and its own export. `suite-brief.md` contains evaluation tasks and limitations. The small `starter-demo.html` remains a concise introduction to the shell. The builder preserves an existing demo index once as `previous-demo.html`; choose a new output folder to preserve an entire earlier suite revision.

Optional rendered acceptance with an existing Playwright installation:

```sh
node "$SKILL_DIR/scripts/check-demo-suite.mjs" /absolute/path/to/demo-suite /absolute/path/to/playwright
```

This checks all page proposals at desktop and mobile preview sizes, navigation targets, static rendering, feedback export and narrow shell layout. Screenshots go into the output folder. It does not prove content quality, native behavior or domain task completion.

## Authoring choices and boundaries

Marketing narratives compose independently reviewable modules with explicit order changes and context-dependent conversion points. Application screens remain coherent surface units to avoid implying that arbitrary fragments form a working flow. Links connect representative states; a mixed selection does not enforce cross-state compatibility.

Proposals vary ordering, hierarchy, grouping, task focus or disclosure. Surface-specific hypotheses describe the actual structure and take precedence over the broad scenario lens. The renderer is a specimen generator, not a mandatory design pattern catalog. Extend it when a new task needs a structure it cannot express.

All copy, prices, people, records and statistics are fictional. Measures are candidates with unknown baselines and targets. In-preview product controls, authentication, search, filtering, synchronization, permissions and editing persistence are not implemented. Only review feedback and selections are persisted/exported. The suite deliberately includes consequential conditions, but it is not an exhaustive state matrix.

Use the collection to find limits: cross-surface relationships remain in the briefs and comments; native APIs and state transitions require a working prototype; cross-project feedback is exported separately. Do not describe these as implemented capabilities.

## Agent-first examples

The three agent-first demos are featured at the top of the atlas. Each contains seven supervisory surfaces and three interface hypotheses: a decision inbox, a shared mission canvas and a directive briefing. Those are alternatives to explore, not a prescribed agent UI.

- Observatory centers on epistemic work: commission a question, inspect claim-level support, preserve dissent, compare recommendations and decide whether more research is worthwhile.
- Switchyard centers on authority and execution: set an autonomy envelope, simulate options, bind approval to a plan version and affected set, stop on changed conditions, reconcile receipts and keep compensating actions explicit.
- Atelier centers on judgment and production: direct a creative brief, compare concept branches, retain selected strengths, bound an iteration, inspect critique and provenance, and keep publication and persistent memory separately reviewable.

Confidence indicators distinguish rubric completion, scoped evidence support, operational readiness and human judgment. Their labels expose their basis. None is presented as a calibrated success probability. Citation links lead to clearly synthetic source records with scope limits and counterevidence. Reasoning logs contain authored summaries of evidence, decisions and observable actions, not private model reasoning.

Mission controls illustrate directions and dispositions; approval is visibly non-executing. The review shell's A/B/C choices concern interface design, not the candidate strategies inside a mission. Mission form entries do not enter the feedback export. Use annotations to give durable feedback on them.

The proposed control model keeps recommendation, reviewed approval, attempted action, verified receipt, accepted artifact and observed outcome distinct. Consider which distinctions matter for a new project rather than adding every panel by default. A mission may need one compact checkpoint; consequential parallel work may need much deeper evidence and authority inspection.

The [Jev / System One notes](jev-pattern-notes.md) distinguish verified primitive semantics from design interpretation. Each agent-first example now includes a different typed signal: Choice routing, Noul detection or Score evaluation. Those model-like distributions are authored examples; operational readiness and evidence-support counts are separate indicators.

## Marketing rhythm and registry

Marketing includes twelve rendered content-pattern families and three header composition hypotheses. Product uses the aligned head/body/footer sidebar. The content registry contains 22 patterns; the navigation registry covers 17 patterns plus four marketing header compositions. The atlas links to both registries and `marketing-headers.html`. Current revision IDs are in each generated manifest. Prior revisions are preserved under `revisions/<scenario>/<revision>/`; old feedback requires explicit mapping before import into a new revision.
