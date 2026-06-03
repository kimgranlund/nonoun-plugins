# Changelog — adia-ui-authoring

## [1.9.2] stable

De-repo'd port into the `adia-ui-forge` plugin from the framework monorepo's maintainer skill. This is a faithful port: the full mode set, references, scripts, evals, and worked examples are preserved; only repo-instance data was dropped and substrate-only paths rewired.

### What this skill is

The authoring lane of the adia-ui forge — the guard rail for code that lands INSIDE the `@adia-ai` monorepo. Eight cold-start modes, each with its own reference:

1. Author a new primitive (`primitive-audit.md` → `authoring-cycle.md`)
2. Modify an existing primitive (`authoring-cycle.md`)
3. Author a shell (`shell-patterns.md`, ADR-0023 bespoke-children)
4. Promote inline → module (`module-promotion.md`, 5-phase arc)
5. Audit a component for drift (`token-contract.md` + `anti-patterns.md`)
6. Extend the `@adia-ai/llm` bridge (`llm-bridge.md`)
7. Teach the skill new knowledge (`teach-protocol.md`, §Teach extensibility)
8. Author a composite/module demo (`composite-demo-protocol.md`, 6-phase mandatory gate)

Deep references: `api-contract.md`, `yaml-contract.md`, `css-patterns.md`, `lifecycle-patterns.md`, `code-style.md`, `common-gotchas.md`, `canonical-pattern-index.md`, `worked-example.md`. Scripts: `audit-authoring-roster.mjs` (§SelfAudit) and `build-canonical-pattern-index.mjs`. Evals: `routing-corpus.json` (30 cases) and `adversarial-design-plan-gates.json` (8 mode-8 gate-pressure cases).

### De-repo notes

- Shared-infra references rewired to `${CLAUDE_PLUGIN_ROOT}/references/shared/{content-trust,pev-rationale,skill-conventions}.md`.
- `audit-authoring-roster.mjs` resolves the universal audit-axes library via `${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs` (env var, with a script-relative fallback); paths resolve from the script's own location instead of hardcoded `.agents/skills/...`.
- Monorepo path conventions kept by design (`packages/web-components/`, `packages/web-modules/`, `packages/llm/`, `packages/a2ui/`, the `@adia-ai/*` scope, `docs/specs/*`, ADR numbers).
- Cross-references to excluded skills rewritten: consumer-side composition → the **adia-ui-factory** plugin; `a2ui-pipeline` → **adia-ui-a2ui**; `dogfood-sweep` → **adia-ui-dogfood**; deployment/ops → described generically (out of this plugin's scope).
- Instance data dropped: per-version dated narration, commit hashes, memory-entry pointers, `.brain/` postmortem/findings links, and two session-ledger case studies (a specific demo-cohort recovery sprint). Durable worked examples retained: Mode 6 (maxTokens discovery), Mode 3 (admin-shell decomposition), Mode 4 (theme-panel promotion).

### Provenance

The full per-version history of this skill (the rollup of `primitive-audit` + `component-token-audit` + code-bestpractices + `bespoke-shell-children` + `promote-inline-to-module` + `llm-bridge-extension`, and the iterative composite-demo-protocol hardening) lived in the source monorepo and is not carried here — only the durable knowledge it produced.
