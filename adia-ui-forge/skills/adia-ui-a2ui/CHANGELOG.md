# Changelog — adia-ui-a2ui

## [1.2.1] stable

Ported into the adia-ui-forge plugin as a self-contained, de-repo'd skill. Faithful port — the full generation-engine depth is preserved (compose strategies, chunk corpus, retrieval, validator, runtime, MCP server, fragment graphs, calibration playbook).

De-repo changes from the source maintainer skill:

- Shared infrastructure cited via `${CLAUDE_PLUGIN_ROOT}/references/shared/` (content-trust, pev-rationale) instead of monorepo-only vision/feedback docs.
- `scripts/audit-a2ui-roster.mjs` and `scripts/teach-route.mjs` resolve the shared libs at `${CLAUDE_PLUGIN_ROOT}/bin/lib/` (audit-axes, teach-router) via the `CLAUDE_PLUGIN_ROOT` env var with a script-relative fallback; skill layout is `skills/adia-ui-a2ui/`.
- §Teach decision tree mechanized in `scripts/teach-route.mjs` (prose retained in `references/teach-protocol.md` for worked examples + anti-patterns).
- §Posture gained content-trust (chunk JSON / MCP inputs are data), MCP-schema-change authorization, and substrate-bound declarations; `skill.json` declares `environment.portable: false`.
- `evals/` corpora added (routing, adversarial/behavioral, deterministic §Teach routing).
- §Status reduced to a CHANGELOG pointer; phantom `assets/case-studies/` removed from §FileMap.
- Cross-references to skills excluded from this plugin (`adia-ui-kit`, `adia-ui-ops`) reworded or dropped; surviving sibling references point at `adia-ui-authoring` / `adia-ui-release` / `adia-ui-dogfood` / `adia-ui-gen-review` / `adia-ui-llm`. Monorepo conventions (`packages/a2ui/`, `@adia-ai/*`, the chunk corpus) are kept by design.
- Instance data dropped (commit hashes, dated journal pointers, `.brain/notes` references, rot-prone version literals); durable pipeline knowledge retained.

### Inherited history (substrate skill)

- **§Plan-Execute-Verify elevated to a load-bearing first-class citizen** — a top-band `## §Plan-Execute-Verify` H2 with a per-mode real-product verify-target table (eval thresholds: zettel cov≥40 / avg≥85 / MRR≥0.94; free-form cov≥90 / avg≥83 / F1≥55; MCP smoke; test:a2ui; smoke render). §SelfAudit and verify-the-output are distinct disciplines; both required.
- **§Teach H2 + WHAT+WHEN+NEG description** — the extensibility binding (decision tree, 5-step landing, anti-patterns) with a negative "Does NOT trigger for" clause for routing accuracy.
- **Audit script rewired to a shared axis library** — universal axes (manifest, reference graph, capability-menu drift, version-literal parity, phase-label absence, fence-leak, content currency, CLI-helper currency) composed from the shared lib, plus a skill-specific absorbed-roster currency axis.

### Origin — rollup of three standalone skills

The 4th rollup in the senior-skill set. Absorbs:

- `a2ui-pipeline` — A2UI generation pipeline source internals: generator, pattern-library, chunk-library, fragment graphs, composition library. (Previously absorbed `fragment-extraction`, `training-data-flow`, `eval-gap-diagnosis`.)
- `adia-ui-training` — MCP pipeline operator view: generate_ui → validate_schema → a2ui-to-html → check_anti_patterns flow.
- `zettel-internals` — zettel composition engine internals: calibration constants, scope drift, semantic-fail lifting. (Previously absorbed `semantic-fail-lifting`.)

Their content is preserved in this skill's 12-file `references/` topology; the substrate scripts they cite (`npm run eval:diff`, `harvest:chunks`, `smoke:engines`, `packages/a2ui/mcp/server.js`, `test:a2ui`, etc.) stay at the monorepo level — the skill cites them, doesn't own them.
