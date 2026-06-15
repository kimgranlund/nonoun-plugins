# Changelog

All notable changes to **dev-kernel** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.2.0] — 2026-06-15

The `spec-author` skill — the factory's intake boundary, finally implemented, and a new way to manage specs.

### Added

- **`spec-author` — the spec lifecycle skill (specs as skills).** The design spec defined a `spec-author` skill (the intake boundary — where intent becomes a typed spec) but the build shipped only the orphaned `spec-architect` agent; this implements it as dev-kernel's **8th skill** (7 core lattice + 1 meta). A spec is now managed across its **whole life** — **AUTHOR** (intent / PRD / notes → a spec), **REVIEW** (the mechanical gate + an adversarial council), **REFINE** (fix from findings), **UPDATE** (a ledgered regeneration of a validated spec) — not authored once and abandoned.
- **Specs as SKILL-format artifacts.** The advanced form the lifecycle produces: a spec **is a mini-skill** — front-matter (the routable intent surface) + a brief body + the embedded ```json contract the gate reads + optional `references/` depth (and the folder form `spec/<slug>/SKILL.md`). `references/spec-format.md` is the definition. Backward-compatible: a legacy json-only spec still passes the gates (valid-but-minimal); the SKILL shape is what AUTHOR/UPDATE produce.
- **The `spec-council`** — REVIEW's adversarial half: a `spec-council` orchestrator that fans out **6 read-only lens-critics** in parallel isolated contexts (`critic-completeness · critic-testability · critic-entailment · critic-ambiguity · critic-scope · critic-hackability`), each carrying the trust-boundary guard, synthesizing an APPROVED/CONDITIONAL/BLOCKED verdict. The roster grows 12 → 19 agents.
- **Two rubrics — build-against vs the gate.** `rubric/spec-authoring.rubric.json` (in the skill) is the GUIDANCE standard a spec is authored + maintained against, bridging each dimension to its gate dimension + council lens; `dev-kit-corpus`'s `spec-quality` rubric stays the GATE that ships it. The same split skills-studio draws.

### Changed

- **`spec-architect` given its home** — no longer an orphaned roster agent; it is the `spec-author` skill's author/decomposer actor, producing SKILL-format specs and handing decomposition to `lattice-architect` + `roadmap-planner` (no redundant `spec-decomposer`).
- **The NOT-boundary clauses in `verification` / `regeneration`** now correctly name the **`spec-author` skill** (the 0.1.1 NEW-3 fix had re-pointed them at the bare agent, masking the missing skill).
- **Counts**: 7 → 8 skills, 12 → 19 agents — manifests, README skill-layering, sample prompts, and the naming-schema doc list updated.

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
- **Instance state carried no kernel-version anchor + mis-attributed its producer** (the council's named "blind spot" — Charity M., deferred at APPROVED, now closed via an upstream cross-over). The vendored `lattice.py` never stamped `kernel_version` (so a future breaking kernel bump would silently corrupt a live `.agents/dev-factory/` instance rather than be a *detected* migration) and hard-coded `produced_by="harness-forge"` (so dev-factory state claimed the wrong producer). Fixed in harness-forge `0.5.11` (re-vendored, drift-gate green): `lattice.save()` stamps the writing `KERNEL_VERSION` into every `lattice.json`, `lattice.kernel_compat()` is the boot-time version handshake, and `produced_by` reads `LATTICE_PRODUCED_BY`. dev-factory's single-writer (`dev-server/api.py`) now stamps `produced_by="dev-factory"` on init and runs `kernel_compat` on boot (warns on skew). `KERNEL_VERSION` unchanged (additive). The one item the APPROVED council had tracked-as-deferred is now closed.

### Added

- **`/factory-init` command** (the council's recurring "zero user-typable entry points" finding — Boris C., Steve Y.) — dev-kernel now ships ONE typed command, the single deterministic setup action: scaffold an instance under `.agents/dev-factory/` (the nine layer dirs + `signals/` + `ledger/` + `lattice.json` + the coordination dirs), stamped with `produced_by=dev-factory` + the kernel version, then hand off to the `lattice-management` skill for cell-seeding. Thin by construction (2.2KB, well under the integration-contract budget) — it routes to `bin/lattice.py` + the skill, never re-contains them. The 7 skills stay model-invoked; this is the one deterministic action a human wants to type. README "no slash commands" claims reconciled.
- **Reverse-morphism eval** (`evals/reverse-morphism/`) — the council found the central biconditional was half-proven (`tracer-bullet` only proved the forward direction, `done ⟹ cell-advanced`). This proves the **reverse**: a cell cannot reach `validated` out-of-band — `lattice.json` + `signals/` are deny-on-write to workers (R1/R2), the only path LEDGERS the advance (R3), and a `validated`-without-signal cell is structurally rejected (R4). With the forward direction, `board ⟺ lattice` holds in both directions. Wired into the dev-factory CI.

### Changed

- **`factory-ops` moved out of the kernel** (council M2, re-review non-blocking — 4 critics converged that a README reframe wasn't the move they asked for) — the runtime-operations skill is **gone from `dev-kernel/skills/`**; its operational substance (boot, arming the bounded heartbeat, worktree lifecycle, monitoring, the crash-recovery runbook) is consolidated into **`../dev-server/RUNBOOK.md`**, shipping with the `heartbeat.py`/`dispatch.py`/`store.py` code it documents — the same line already drawn for the system-evals in `../dev-server/evals/`. dev-kernel is now **7 skills**: 6 core lattice skills + **1 meta** skill (`kit-authoring`, which authors against the kernel's own `check-kit-conform` gate, so it stays). README *Skill layering* section, sample prompts, and all "8 skills" count claims updated.
- **Context tax trimmed** (council M3 + the second re-review's aggregate-inert finding, Boris C.) — first all 7 over-budget skill descriptions were trimmed under the 1024-char threshold; then the **12-agent roster descriptions** (the largest standing-cost pool, ~7,577 chars — dispatched by dev-server *by name*, so a verbose description is pure always-on tax with no routing value in a kernel-only install) were trimmed to terse role + write-perimeter + tier lines (~4,635 chars), every agent's trust-boundary guard kept (it lives in the body, not the description). Always-on cost across the whole arc: 16,660 → **11,623 chars** (~4,165 → ~2,905 tok); `context-cost` WARN-free.

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
