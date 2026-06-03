# Changelog — `adia-ui-release` skill

## [0.1.0] stable — 2026-06-03

**Initial cut in the `adia-ui-forge` plugin.** Faithful, de-repo'd, self-contained port of the @adia-ai monorepo's maintainer `adia-ui-release` skill, with the former `adia-ui-migration` skill folded in as the producer-side migration-guide-authoring section. Preserves the release-engineering depth (the gate roster, recovery paths, peer-in-flight discipline, ledger schema, notes craft) — this is a port, not a rewrite.

### Ported

- **SKILL.md** — the mode menu (now 11 modes), §Mission, §Posture (load-on- demand + content-trust citing `${CLAUDE_PLUGIN_ROOT}/references/shared/`), §Plan-Execute-Verify (per-mode real-product verify table), §ReleaseInvariants, §LoadingProtocol, §Recon, §Teach (stub → `teach-protocol.md`), §SelfAudit, §FileMap, §Status.
- **11 references** — `cycle-happy-path.md`, `multi-agent-baseline.md`, `gates-catalog.md`, `recovery-paths.md`, `changelog-discipline.md`, `notes-authoring.md`, `rollup-notes.md`, `exe-deploy.md`, `ledger-discipline.md`, `teach-protocol.md`, plus the new `migration-guide-authoring.md` (the fold-in).
- **8 scripts** (pure Node, stdlib only, `node --check` clean) — `bump.mjs`, `promote-unreleased.mjs`, `insert-stub.mjs`, `tag-lockstep.mjs`, `dispatch-publish.mjs`, `make-ledger.mjs`, `release-pack.mjs`, `audit-gate-roster.mjs`.
- **9 case studies** (worked-example cycles) + the lockstep stub template + `evals/evals.json`.

### Folded in — `adia-ui-migration` (producer side)

The release skill now owns **producer-side** migration: mode 11 + §MigrationGuideAuthoring + `references/migration-guide-authoring.md` — authoring the `MIGRATION GUIDE.md` section when a cut breaks an API (before→after + audit grep + sweep recipe per item, manual-review classes for semantic flips, the version-coverage table, the in-repo sweep-verification audit) and sweeping the framework's own demo / playground / catalog surfaces. The **consumer** side (sweeping a downstream app against a published guide) deliberately stays in the separate consumer/app-author plugin; mode 11 declines + redirects for "migrate our app" requests.

### Scope discipline (de-repo)

- The portable release DISCIPLINE is the core. The @adia-ai monorepo's concrete **9-package lockstep**, **`check:*` gate roster**, and **`ui-kit.exe.xyz` demo-site deploy** are kept as the clearly-labeled **worked example** (header notes in `cycle-happy-path.md`, `gates-catalog.md`, `exe-deploy.md`; package/tag counts marked as the example in §ReleaseInvariants), NOT presented as universal gates.
- Absolute paths (`/Users/...`) stripped; `$REPO` / `${CLAUDE_PLUGIN_ROOT}` used instead. Shared-infra references point at `${CLAUDE_PLUGIN_ROOT}/references/shared/` (content-trust, pev-rationale, skill-conventions). Skill-owned script invocations point at `${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/scripts/`.
- Instance data dropped: hardcoded repo slug → `--repo-slug <org>/<repo>` flag in `make-ledger.mjs` + `<org>/<repo>` placeholder in `ledger-discipline.md`; dated version-by-version skill history from the source's 1.x CHANGELOG dropped (durable knowledge + templates kept; the 9 case studies are retained as worked examples with absolute paths stripped).
- Excluded-skill cross-references rewritten: `adia-ui-kit` → "the consumer/app-author plugin"; `adia-ui-ops` / `exe-dev-ops` → "a long-running-ops concern (separate; not in this plugin)"; `dogfood-sweep` → the present sibling `adia-ui-dogfood`; `a2ui-pipeline` → the present sibling `adia-ui-a2ui`; monorepo-only docs (`VISION-extensibility.md`, `trainable-skill-ecosystem-design`) → the shared `skill-conventions.md` / `pev-rationale.md`.
