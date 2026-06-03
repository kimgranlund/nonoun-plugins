# adia-ui-forge — ROADMAP

The build plan and current state. This is the spec the port executes against.

## Scope (signed off)

**(A) The framework's own authoring toolkit, packaged.** `adia-ui-forge` is for people working _on_ the adia-ui framework (the `@adia-ai` monorepo or a fork). It _assumes_ the monorepo's package conventions; "de-repo'ing" means stripping absolute paths and instance data, **not** generalizing the framework away. It is explicitly **not** a generic "build any component library" toolkit, and it is **not** the consumer/app-author plugin (that is `adia-ui-factory`).

Source: carved from `/Users/kimba/Projects/chat-ui/.agents/` (the monorepo's maintainer agent system), which mirrors `adia-ui-factory` as producer ↔ consumer.

## Roster (7 skills) — package-driven

| Skill | Source skill | Covers |
| --- | --- | --- |
| `adia-ui-forge` (orchestrator) | _new_ | cold-start: classify the package/concern → route to the owning skill |
| `adia-ui-authoring` | `adia-ui-authoring` | `@adia-ai/web-components` (primitives) + `@adia-ai/web-modules` (shells/clusters), tokens, traits, the LLM-bridge surface |
| `adia-ui-a2ui` | `adia-ui-a2ui` | the A2UI / gen-ui engine — the 6-pkg `a2ui` cluster (compose · corpus · retrieval · runtime · validator · mcp) + training corpus (`gen-ui-kit/data`) |
| `adia-ui-llm` | _new_ (from `adia-ui-authoring` mode 6 + the `@adia-ai/llm` package) | the LLM client — anthropic/openai/gemini adapters, SSE, model registry, the bridge, browser+node/proxy |
| `adia-ui-gen-review` | `adia-ui-gen-review` | closed-loop quality scoring of generated gen-ui output → corpus fixes |
| `adia-ui-dogfood` | `dogfood-sweep` | static + visual QA across components / apps / playgrounds / catalog |
| `adia-ui-release` | `adia-ui-release` (+ `adia-ui-migration` folded in) | release-engineering discipline (gates, changelog/notes) + MIGRATION GUIDE authoring |

**Excluded:** `adia-ui-kit` (consumer composition → that's `adia-ui-factory`); `adia-ui-ops` (exe.dev deploy + `.brain` governance — repo-infra, overlaps `ops-repo`). Repo-local scaffolding (`team/` tickets, `routines/`, `prompts/`, `agents-maintenance.md`, `.githooks`/CI) is out of scope.

## Shared infrastructure (co-located — the install copy-alone rule)

The source skills import `.agents/shared/*`; no `../shared` survives install, so the plugin bundles its own copy under `references/shared/` + `bin/lib/`, referenced via `${CLAUDE_PLUGIN_ROOT}`:

- `references/shared/content-trust.md` — the data-not-instructions trust boundary
- `references/shared/pev-rationale.md` — the Plan-Execute-Verify loop
- `references/shared/skill-conventions.md` — the structural standard (reconciled with plugins-factory `authoring/skill-architecture.md`)
- `bin/lib/audit-axes.mjs` · `teach-router.mjs` · `dry-run-irreversible.mjs` · `run-skill-evals.mjs`

The 16-pattern audit catalog was **not** carried wholesale (it was `adia-ui-ops` reference material full of illustrative broken-link/placeholder paths that only one kept skill touches). Any specific pattern `adia-ui-a2ui` genuinely references is pulled in (cleaned) during its port.

## Primitive structure (mirrors adia-ui-factory)

- **Skills** — the 7 above (depth in `references/`, loaded on demand).
- **bin/** — the de-repo'd `audit-*-roster.mjs` / native-primitive-leak / token-leak scripts + `lib/` + a `forge-lint` (advisory smell checker) + selftests.
- **Hook** — `hooks/hooks.json`: advisory `PostToolUse` authoring-lint on component/source writes (flag native-primitive leak, raw tokens, slot violations). **Never blocks (`--hook` exits 0).**
- **Commands** — thin typed entry points: `/adia-forge-orient` · `/adia-forge-author` · `/adia-forge-a2ui` · `/adia-forge-llm` · `/adia-forge-review` · `/adia-forge-dogfood` · `/adia-forge-release`.
- **MCP** — none shipped (the a2ui MCP is what this plugin _builds_; the consumer factory wires the published one).
- **Council (agents)** — deferred to a later version (source `.agents/agents/` is empty); gen-review + the audit gates cover mechanized quality for now.

## De-repo rules (applied to every ported skill)

1. Strip absolute paths (`/Users/kimba/...`); keep monorepo-relative conventions (`packages/web-components/...`) as documented assumptions of scope (A).
2. Rewrite shared-infra references to `${CLAUDE_PLUGIN_ROOT}/references/shared/...` and `${CLAUDE_PLUGIN_ROOT}/bin/lib/...`.
3. Drop instance data (ledgers, audit-history, tickets, exe.dev secrets, gallery scratch).
4. Map repo CI gates (`npm run check:*`) to documented verify targets, not hardcoded invocations.
5. Carry the trust-boundary block into every skill; conform to the plugins-factory skill-architecture standard (cold-start surface, modes, progressive disclosure, per-mode verify target, §SelfAudit, §Teach).
6. Self-contained — zero cross-plugin paths; passes `validate_plugin.py --strict` + `reference-lint.py`.

## Build phases

- [x] **0. Scaffold** — dirs, `plugin.json`, marketplace entry, README, CHANGELOG, this ROADMAP.
- [x] **1. Shared infra** — co-located `references/shared/*` (3 core docs) + `bin/lib/*` (4 scripts), de-repo'd.
- [x] **2. Orchestrator** — `adia-ui-forge` SKILL.md (cold-start classify by subsystem + route).
- [x] **3. Domain skills** — `adia-ui-authoring` (27 files), `adia-ui-a2ui` (20), `adia-ui-llm` (15, authored from the real package), `adia-ui-gen-review` (13), `adia-ui-dogfood` (5), `adia-ui-release` (33, migration folded in). All de-repo'd, shared-infra co-located, full plugin markdownlint-clean + `validate --strict` + `reference-lint` green.
- [x] **4. bin + hook** — `forge-lint` (advisory component-authoring smell checker, 11 smells + selftest) + the never-blocks `PostToolUse` hook; shared `bin/lib/*` in place.
- [x] **5. Commands** — the 7 typed entry points (`/adia-forge-orient·author·a2ui·llm·review·dogfood·release`).
- [x] **6. Validate** — `validate_plugin.py --strict` PASS · `reference-lint.py` PASS · `forge-lint selftest` PASS · markdownlint 0 · 23/23 `.mjs` parse.
- [x] **7. Red-team** — the `plugins-factory` 9-critic council ran (verdict CONDITIONAL). Folded the MUST + SHOULD findings: reconciled the build-state docs, cut the context-economy tax (dropped a redundant `trigger:` block + trimmed the longest descriptions), disclosed + guarded the release-script blast radius, synced the four description surfaces, labeled the `forge-lint` ↔ `adia-lint` duplication, and added the orchestrator routing eval. Cross-plugin items deferred. Record: `reviews/2026-06-03-v0.1-red-team.md`. **Cut 0.1.0.**

## Open questions resolved

- **`adia-ui-release`** → ship the _discipline_ (gate roster, changelog/notes authoring, peer-in-flight); the chat-ui-specific lockstep/exe.dev scripts ship as repo-targeted examples, not hardcoded gates.
- **`adia-ui-ops`** → excluded (repo-infra). Its audit-pattern catalog is **not** carried wholesale; specific patterns are salvaged into the owning skill's references only where a kept skill genuinely uses them.
- **LLM + gen-ui** → first-class: `adia-ui-llm` is its own skill; gen-ui is covered by `adia-ui-a2ui` (engine + training corpus) and `adia-ui-gen-review` (output quality).
