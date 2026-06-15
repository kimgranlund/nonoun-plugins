# Changelog

All notable changes to **dev-kernel** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.1.0] — 2026-06-14

Initial cut — the invariant kernel of dev-factory.

### Added

- **11 schemas** — cell · ticket · ledger-entry · activity · dispatch-policy/execution-plan · budget · lattice · roadmap · kit · adapter · naming.
- **The vendored kernel** — harness-forge's `lattice.py` + `validate.py`, byte-identical, drift-gated by `tools/sync-dev-kernel.py`, pinned at harness-forge `@3ff1fbb` (`KERNEL_VERSION` 0.5.2).
- **Native bins** — `lifecycle` (the ticket machine + the `done ⟺ cell-advances` morphism), `compass` (deterministic selection), `execplan` (dispatch-policy → execution plan), `autonomy` (trust tiers 0-3 + mechanical demotion), `distill` (the regeneration scan), the **tamper-evident hash-chained** `ledger`, and `check-kit-conform`.
- **The gates** — 4 protective scripts (`gate-signal · gate-verifier · gate-ledger · gate-naming`) + 2 lifecycle transition predicates (`gate-ticket-ready · gate-dispatch`); the immutable/rewritable boundary.
- **A read-only `factory-query` MCP** (8 tools).
- **A 12-agent roster** across **8 compound skills**.
- The morphism proven by `evals/tracer-bullet/`; the system arc (Crawl · Walk · Run · Fly · demotion · integration · server-smoke) proven in `../dev-server/evals/`.

### Reviewed

- Red-teamed by the **plugins-factory 9-critic council** (BLOCKED → fixes folded): moved the 12-agent roster to a top-level `agents/` dir (it was inert + collision-gate-invisible under `skills/*/agents/`); re-scoped the manifest's safety claims to "once wired" and declared the dev-server dependency; reconciled the gate enumeration (4 scripts + 2 predicates, not "six gates"); pinned the harness-forge source SHA in `VENDOR.md`; added a `ledger verify` stand-alone signal; and added this README + CHANGELOG. The remaining council findings (a dev-factory CI pipeline, the layering of `factory-ops`/`kit-authoring`, the always-on context tax) are tracked as follow-ups.
