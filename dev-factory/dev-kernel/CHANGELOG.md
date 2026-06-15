# Changelog

All notable changes to **dev-kernel** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.1.1] — 2026-06-14

The 0.1.0 dogfood council's three Majors, closed — then the re-review council (BLOCKED → **CONDITIONAL**, no new Critical) its two blocking prose-vs-code gaps + the mechanical residuals, then the non-blocking Majors it raised (`factory-ops` moved out of the kernel to the dev-server runbook; gates that failed open on a malformed payload now fail closed). One non-blocking item remains by design: the `kernel_version`/`produced_by` vendoring run-time migration contract, which needs an upstream harness-forge change (the vendored `lattice.py` owns both) rather than a local edit — tracked, not silently dropped.

### Fixed

- **`gate-budget` phantom prose** (re-review, Charity M. + Chip H.) — `skills/cell-engine/methodologies/engine.md` and `agents/cell-advancer.md` described `gate-budget` as if it denied writes *from this kernel*, but the gate ships with the runtime (dev-server) and is consent-wired — dev-kernel ships only the detector (`ledger.py no-progress`) + the flag (`lattice.py block`). Both surfaces now carry the same honest scope as `gate-signal` ("the bounds become mechanical once dev-server wires them").
- **Forked false-pass function** (re-review, Chip H.) — `autonomy.false_pass` (consumed by `tier_for`) and `ledger.false_pass_rate` (cited by 7 governance docs) were two functions with different formulas. Reconciled to ONE: `ledger.false_pass_rate` is now the single canonical refuter-gated implementation (refuter-disagreements ÷ independent-refuter-checks, `unmeasured` until a refuter re-checks), and `autonomy.false_pass`/`refuter_checks` delegate to it — the documented formula and the consumed formula can no longer diverge.
- **Two post-move broken refs** (re-review, Scott W. — the C1 residual) — `agents/kit-architect.md` + `agents/rubric-architect.md` carried bare `methodologies/…` refs the agent-relocation missed; both now resolve to `../skills/<skill>/methodologies/…`.
- **"Six gates" drift** (re-review, David F.) — the marketplace entry, `dev-factory/README.md`, and `bin/VENDOR.md` still said "six gates"; corrected to "four protective gates + two lifecycle predicates" (matching the manifest).
- **VENDOR.md under-reported the vendored set** (re-review, Andrej K.) — the sync tool pins **three** files but the table listed two; `schemas/cell.schema.json` (the cell contract the reverse-morphism R4 proof stands on) is now documented.
- **Manifest description trimmed** (re-review, Boris C.) — `plugin.json` description 1,756 → 1,010 chars, keeping the substrate/consent-wired honesty + the reconciliation thesis, dropping the README-in-a-slot bloat.
- **Gates failed OPEN on a malformed payload** (re-review non-blocking, Simon W.) — `_gates.py` returned the write as ALLOWED when the PreToolUse payload was unparseable, and the Bash write-redirect heuristic (only `>`/`tee`/`rm`) missed `cp`/`mv`/`sed -i`. Now: an unparseable payload **fails closed** (deny — the gate must never allow a write it cannot inspect), the verb set covers the genuine file-MUTATING commands, and the decision logic is a pure `path_gate_verdict()` the selftest exercises for the fail-closed case, a `cp`-evasion, and (no-false-deny) a `Read` and an interpreter-flag READ of a protected path. `gate-naming` carries the same fail-closed guard.
- **Bash gate over-matched interpreter-flag READS** (second re-review, Simon W. — NEW-1, a regression the broadening above introduced) — `-c `/`-e ` had been added to the write-verb set, but they are interpreter flags, not write verbs, so a legitimate `python3 -c 'open("…/lattice.json").read()'` or `grep -e validated …/signals/…` (exactly what `cell-validator` shells) tripped the gate. The set is now the genuine mutating verbs only (no interpreter flags); a regression guard in the selftest asserts both reads are allowed. The residual inline-interpreter-write evasion is already closed by the no-Bash tool-scope on the *forging* worker (`cell-advancer`).
- **`spec-author` named a non-existent actor** (second re-review, NEW-3, Elon M.) — two skill NOT-boundary clauses (`skills/verification/SKILL.md`, `skills/regeneration/SKILL.md`) referenced `spec-author`, which is neither a skill nor an agent; the real spec-authoring agent is `spec-architect`. Both corrected.

### Added

- **Reverse-morphism eval** (`evals/reverse-morphism/`) — the council found the central biconditional was half-proven (`tracer-bullet` only proved the forward direction, `done ⟹ cell-advanced`). This proves the **reverse**: a cell cannot reach `validated` out-of-band — `lattice.json` + `signals/` are deny-on-write to workers (R1/R2), the only path LEDGERS the advance (R3), and a `validated`-without-signal cell is structurally rejected (R4). With the forward direction, `board ⟺ lattice` holds in both directions. Wired into the dev-factory CI.

### Changed

- **`factory-ops` moved out of the kernel** (council M2, re-review non-blocking — 4 critics converged that a README reframe wasn't the move they asked for) — the runtime-operations skill is **gone from `dev-kernel/skills/`**; its operational substance (boot, arming the bounded heartbeat, worktree lifecycle, monitoring, the crash-recovery runbook) is consolidated into **`../dev-server/RUNBOOK.md`**, shipping with the `heartbeat.py`/`dispatch.py`/`store.py` code it documents — the same line already drawn for the system-evals in `../dev-server/evals/`. dev-kernel is now **7 skills**: 6 core lattice skills + **1 meta** skill (`kit-authoring`, which authors against the kernel's own `check-kit-conform` gate, so it stays). README *Skill layering* section, sample prompts, and all "8 skills" count claims updated.
- **Context tax trimmed** (council M3) — all 7 over-budget skill descriptions trimmed under the 1024-char threshold (doctrine the bodies disclose on demand was cut; every `Triggers on` routing phrase + `NOT for` boundary kept). Always-on cost: 16,660 → 15,539 chars (~4,165 → ~3,884 tok); `context-cost` now WARN-free.

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
