# Changelog

All notable changes to **dev-kit-app** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.2.0] — 2026-06-15

The app family builds **real, shippable, multi-file software** (the DF-9 fix), graded by per-cell harnesses.

### Added / Changed

- **Multi-file code authoring** — `kit.json` gains a top-level `authoring` declaration: a `capability` is a real source **directory** (`{layer}/{slug}/`), not one `.md`. The dispatcher (`dispatch.py _authoring_for`) routes such a cell to a multi-file authoring prompt (industrial module boundaries, named exports, pure-logic ES modules + a thin shell). The kit/kernel stay generic; `check-kit-conform` ignores the kit-local `authoring` field.
- **The capability verifier is the per-cell critic harness** — the `capability` validation adapter's verifier is now `["node", "{asset}/verify.mjs"]`: each capability is graded by its own `verify.mjs` (planner-authored, worker-deny via dev-kernel 0.2.4), exit-status-minted by `validate.py`. This is the proven dark-factory-test pattern (a pristine reference + checkable `[gate]` predicates the worker can't see). The integrator cell `capability.system.app` uses the same mechanism as the **SHIP** gate (composes every capability + the spec's acceptance + a real-browser smoke).
- **A spec gate for the family** — a `spec`-layer validation adapter asserts the spec declares a real acceptance contract (`acceptance_criteria` + `non_goals`), so MILESTONE 1 is a measurable gate, not a file-exists check.
- Proven by the `/debug/` harness + the `debug-coldstart` replay (brief → 3 dynamic milestone rubrics → per-capability code cells → the integrator → SHIPPED, with bi-directional spec revision). plugin.json 0.1.0 → 0.2.0.

## [0.1.0] — 2026-06-14

Initial cut — the app family kit: the second family binding the kernel's contracts (the "Fly" milestone — a new family with zero kernel edits). Ontology · rubric manifest · the test-suite validation verifier · dispatch policy · seed patterns; `check-kit-conform` proves the boundary holds.
