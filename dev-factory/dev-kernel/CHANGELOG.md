# Changelog

All notable changes to **dev-kernel** are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [0.2.10] — 2026-06-17

### Changed

- **Re-vendored `lattice.py` + `cell.schema.json` from harness-forge `0.5.19`** — the cell stop flag is now a **discriminated union `block: {reason}`** (replacing the independent `blocked`/`blocked_reason` pair, so a reason-without-stop is unconstructable). The vendored `load()`/`check()` migrate a legacy cell → the union on read; a dual-read `is_blocked`/`block_reason` accessor keeps readers correct on old + new instances. **`KERNEL_VERSION` 0.5.2 → 0.5.3** (the cell data model changed) — dev-factory instances stamped 0.5.2 read as a skew via `kernel_compat` until re-validated, while the on-read migration keeps them correct meanwhile.
- **dev-factory consumers updated to the union:** `factory-query-mcp.py` + `dev-server/store.py` now dual-read via `_lat.is_blocked`/`_lat.block_reason` (so the blocked count + the `[BLOCKED]` markers stay correct after the field change); `reports.py` reads the store's computed column downstream, unchanged. dev-kernel + dev-server selftests green.

plugin.json 0.2.9 → 0.2.10.

## [0.2.9] — 2026-06-17

### Changed

- **Re-vendored `lattice.py` from harness-forge `0.5.16`** — the global run-budget axis now **self-heals on a crashed run**: `gate-budget` consults new `lattice.run_dead(d, now)` when the budget is exhausted, so a crashed/finished run's leftover budget (no genuine loop activity within `LOOP_TTL_S`) stops wedging writes, while a LIVE loop over budget is still denied (liveness = the loop's own ledger activity, `hook:*` records excluded — unforgeable, can't fail open). Behavior-neutral for dev-kernel's existing axes. Drift gate green; `KERNEL_VERSION` stays **0.5.2** (additive — `run_dead` is a new function). plugin.json 0.2.8 → 0.2.9.

## [0.2.8] — 2026-06-17

### Changed

- **Re-vendored `lattice.py` from harness-forge `0.5.15`** — the run budget gained a **token/$ axis** (`max_cost`): `run_budget_exhausted` sums the ledger's reported `cost.tokens` since `start_ts` against a ceiling, and a `max_cost`-only budget is a valid non-vacuous budget. Behavior-neutral for dev-kernel's existing axes (iterations/cells/wall-clock unchanged; absent cost never trips the new cap). Drift gate green; `KERNEL_VERSION` stays **0.5.2** (additive — `run_budget_start` gained an optional kwarg, the return shape is unchanged). plugin.json 0.2.7 → 0.2.8.

## [0.2.7] — 2026-06-16

### Changed

- **Re-vendored `lattice.py` + `cell.schema.json` from harness-forge `0.5.14`** — the kernel's SETTLED foothold-maturity set (the maturities that require non-empty `signal_refs`: `validated`/`operating`) is now single-sourced from `cell.schema.json`'s new `x-settledMaturities` annotation, with the module constant as the portable fallback (drift-guarded in `lattice.py selftest`). Behavior-neutral for dev-kernel — the vendored `check()` enforces the same contract, now sourced from the cell schema dev-factory already adopts. Drift gate green; `KERNEL_VERSION` stays **0.5.2** (additive). Also catches the vendored pin up through harness-forge `0.5.13` (`lattice.reached()`, DF-7). plugin.json 0.2.6 → 0.2.7.

## [0.2.6] — 2026-06-16

### Changed

- **The self-heal substrate is gate-protected.** A caught false pass now SELF-HEALS (the dev-server folds the refuter's failing checks into the cell's `verify.mjs`, re-arms a fresh independent refuter, stales + un-ships, and re-authors against the strengthened gate — decision #123, "full self-heal + new oracle"). The fold derives from a per-cell **verify-spec** (`coordination/verify-spec/*` = exports + acceptance + refute); since that spec drives the gate, `_gates.VERIFIER` now protects it deny-on-write to workers (alongside the refuters), so a worker cannot pre-empt the fold by editing the spec it will be re-gated against. Kernel-side change is the one protected glob; the orchestration lives in the dev-server (`verify_gen.py` + `dispatch.self_heal_cell`). plugin.json 0.2.5 → 0.2.6.

## [0.2.5] — 2026-06-15

### Changed

- **`spec-author` gains the PRD (outside-in) → SPEC (inside-out) axis.** A product is defined twice: a **PRD** defines it from the **outside-in** (jobs · UX · user-facing acceptance as a usage narrative), gated by `prd-quality`; a **SPEC** defines it from the **inside-out** (modules · contracts · decomposition · buildable acceptance) and **realizes the PRD** (the SPEC cell `depends_on` the PRD; its technical acceptance must entail the PRD's outside-in acceptance), gated by `spec-quality`. Both are spec-layer SKILL-format cells (the PRD's slug ends `-prd`) — no kernel-layer change. The skill now says: author the PRD first, then the SPEC that realizes it, rather than collapsing a raw PRD straight into a tech spec. The loop is **bi-directional**: a technical learning revises the SPEC; a product/UX gap (or a SPEC that can't realize the PRD) revises the PRD, whose staleness cascades back down. plugin.json 0.2.4 → 0.2.5.

## [0.2.4] — 2026-06-15

The generator/critic split extended to per-cell code harnesses (the DF-9 enabler).

### Changed

- **`_gates.VERIFIER` protects `{NS}/*/*/verify.mjs`** — a cell's per-cell **critic harness** (`{layer}/{slug}/verify.mjs`). When a kit authors multi-file code (dev-kit-app: a capability is a source directory graded by `node {asset}/verify.mjs`), the harness is the gate the worker's code must PASS — so a gate-wired worker must never be able to write it (else it grades its own homework). The worker can write the cell's source (`index.mjs`, …); a write to `verify.mjs` is denied in-process. Same immutable-boundary mechanism as `signals/`/`rubric/`/`lattice.json`; selftest + the `debug-coldstart` replay prove a worker write to `verify.mjs` is denied while ordinary source is allowed. plugin.json 0.2.3 → 0.2.4.

## [0.2.3] — 2026-06-15

Free-form intake — the contract half of the dev-server's two-mode ticket creator (prompt | instruction).

### Added

- **`prompt` + `instruction` ticket kinds** (`schemas/ticket.schema.json`). Two free-form intake kinds that carry a `body` and **no `target_cell`** until handled — the schema already allowed a cell-less ticket (issues), so this widens the `type` enum and documents the routing: a **prompt** is a free-form brief triaged into structured tickets (the cold-start/intake path); an **instruction** is literal steps folded into the dev-server's guidance buffer. `lifecycle.gate_ticket_ready` generalises the untriaged-issue guard to all three (`issue`/`prompt`/`instruction`), so a free-form intake ticket is a legal parked draft but is **denied `draft → active`** until triaged — it cannot dispatch a worker against no cell. The dev-server's `api.create_ticket` mints them with the `iss-` (intake) id prefix. Proven in `api.py`/`lifecycle.py` selftests and the `debug-coldstart` replay (a PROMPT ticket is seeded, triaged into a hydrated lattice, and the build runs). plugin.json 0.2.2 → 0.2.3.

## [0.2.2] — 2026-06-15

Operator-dogfooding fix (full log in `docs/tickets/dev-server-ui-fixes.md`) — the morphism half.

### Fixed

- **DF-7 — an author ticket couldn't close `done` once `validate.py` overshot its cell to `validated`.** The build is two tickets — author (`defined→instantiated`) then validate (`instantiated→validated`) — but `validate.py` auto-steps `defined→instantiated→validated` in one pass, so a validate-first run drove the cell **past** the author ticket's `instantiated` target. Closing the author ticket then hit `_author_advance`'s bare `transition_ok(validated, instantiated)` (False — `validated` never steps back) and was denied *"illegal maturity advance validated → instantiated"*, wedging a ticket whose authoring work was demonstrably done. **Fix:** `_author_advance` now recognizes a target the cell has **already reached** on the linear maturation axis (`lattice.reached`, vendored from harness-forge `0.5.13`) as a **satisfied no-op** — distinct from an illegal advance, and checked *before* the asset still exists. The no-op closes the ticket without mutating maturity. Crucially **tight, not permissive**: `reached()` is False for off-axis states, so an author advance on a `deprecated`/`stale` cell is **still denied**. New falsifiable replay `evals/done-overshoot/` proves both (O1 the overshoot closes, **O2 a genuinely illegal advance still fails** — the load-bearing guard against a blanket bypass); pinned in `lifecycle.py selftest` case 6. Re-vendored `lattice.py`; drift gate green; `KERNEL_VERSION` unchanged (additive helper).

## [0.2.1] — 2026-06-15

Operator-dogfooding fixes (full log in `docs/tickets/dev-server-ui-fixes.md`) — the dev-kernel half. The dev-server-side fixes (DF-1/2/4/5) live in `../dev-server` (not a plugin), uncounted here.

### Fixed

- **DF-3 — agent model tiers were unresolvable.** The 11 agents that carried `model: deep` / `model: fast` (a dev-factory tier vocabulary Claude Code can't resolve) failed to launch via the Task tool — *"the selected model (deep) may not exist"* — so the `spec-council`, `rubric-architect`, and the critic path were dead on arrival wherever `deep` wasn't provisioned. Remapped to concrete, resolvable models preserving the cost-tiering: `deep → opus`, `fast → sonnet`. (The dev-server adapter's own `small/mid/large`→model map was already concrete; this was the orchestrator/Task path.)
- **DF-6 — `validate.py` reported a misleading `→ validated`.** Re-vendored from harness-forge `0.5.12`: a passing verifier on a cell that can't reach `validated` directly (e.g. a `stale` cell — the FSM routes `stale → regenerating → validated`) printed `→ validated` and exited 0 while the cell stayed `stale`. It now reports the ACTUAL `before → after` maturity and names the `regenerating` route. Drift gate green; `KERNEL_VERSION` unchanged (message-only).

## [0.2.0] — 2026-06-15

The `spec-author` skill — the factory's intake boundary, finally implemented, and a new way to manage specs.

### Added

- **`spec-author` — the spec lifecycle skill (specs as skills).** The design spec defined a `spec-author` skill (the intake boundary — where intent becomes a typed spec) but the build shipped only the orphaned `spec-architect` agent; this implements it as dev-kernel's **8th skill** (7 core lattice + 1 meta). A spec is now managed across its **whole life** — **AUTHOR** (intent / PRD / notes → a spec), **REVIEW** (the mechanical gate + an adversarial council), **REFINE** (fix from findings), **UPDATE** (a ledgered regeneration of a validated spec) — not authored once and abandoned.
- **Specs as SKILL-format artifacts.** The advanced form the lifecycle produces: a spec **is a mini-skill** — front-matter (the routable intent surface) + a brief body + the embedded ```json contract the gate reads + optional `references/` depth (and the folder form `spec/<slug>/SKILL.md`). `references/spec-format.md` is the definition. Backward-compatible: a legacy json-only spec still passes the gates (valid-but-minimal); the SKILL shape is what AUTHOR/UPDATE produce.
- **The `spec-council`** — REVIEW's adversarial half: a `spec-council` orchestrator that fans out **6 read-only lens-critics** in parallel isolated contexts (`critic-spec-completeness · critic-spec-testability · critic-spec-entailment · critic-spec-ambiguity · critic-spec-scope · critic-spec-hackability`), each carrying the trust-boundary guard, synthesizing an APPROVED/CONDITIONAL/BLOCKED verdict. The roster grows 12 → 19 agents.
- **Two rubrics — build-against vs the gate.** `rubric/spec-authoring.rubric.json` (in the skill) is the GUIDANCE standard a spec is authored + maintained against, bridging each dimension to its gate dimension + council lens; `dev-kit-corpus`'s `spec-quality` rubric stays the GATE that ships it. The same split skills-studio draws.

### Changed

- **`spec-architect` given its home** — no longer an orphaned roster agent; it is the `spec-author` skill's author/decomposer actor, producing SKILL-format specs and handing decomposition to `lattice-architect` + `roadmap-planner` (no redundant `spec-decomposer`).
- **The NOT-boundary clauses in `verification` / `regeneration`** now correctly name the **`spec-author` skill** (the 0.1.1 NEW-3 fix had re-pointed them at the bare agent, masking the missing skill).
- **Counts**: 7 → 8 skills, 12 → 19 agents — manifests, README skill-layering, sample prompts, and the naming-schema doc list updated.

### Fixed (two 0.2.0 plugin-council passes — CONDITIONAL → these closed)

Second confirmation pass (it verified the first round held, then caught a surviving instance + a hole):

- **A surviving over-claim** (council, Charity M. + Andrej K.) — `spec-review.md` was the file the fix-1 round touched least and it self-contradicted: line 64 said the bound rubric's validated-ness is "read from `lattice.json` **by the gate**" (false — the gate never reads the lattice), and line 14 carried the smaller "validated `rubric_cell`" instance. Both now attribute the maturity precondition to the lattice, matching the corrected surfaces.
- **The vacuous-cell hole** (council, Scott W. + Andrej K.) — the `layer == spec` / maturity / skill-shape checks sat behind `if cell is not None`, so a spec asset *omitting* its cell passed the spec-layer invariant vacuously. `_gate_schema_valid` now **requires** a cell id; two negative selftest fixtures (a non-spec-layer cell, a cell-less asset) lock it so fix-2 cannot silently revert.
- **The 6 critic names namespaced** `critic-* → critic-spec-*` (council Critical, Steve Y.) — they were the only undifferentiated critic names in the estate; collision-resistant at the *registration* layer now (not just plugin-scoped at dispatch). dev-factory CI also gained the `validate_plugin marketplace` collision gate.

First pass:

- **Gate over-claim (council CRITICAL-A, Chip H.)** — three docs claimed the spec gate verifies the bound rubric is itself `validated`; the standalone verifier checks only the *binding*. Clarified across `spec-format.md`, `SKILL.md`, `spec-review.md`, and `spec-quality.rubric.json`: the binding is the gate's; the rubric-**maturity** precondition is enforced by the **lattice** (`lattice.py` validity + `gate-ticket-ready`), which really does refuse a cell advancing against a non-validated verifier. The claim is true — at the layer that enforces it.
- **The spec gate now asserts `layer == spec`** (council, Andrej K.) — `_gate_schema_valid` rejected only malformed/maturity-encoding cells, never a wrong layer; a non-spec cell asset is now rejected. The `skill-shape` doc claim corrected to what's checked (slug + layer, not scope).
- **The `spec-format.md` decomposition template crashed the entailment check** (council MAJOR, Chip H.) — the example showed cells-as-strings + a ticket *count*, the shape `_entailment_check.py` raises `TypeError` on. Replaced with the correct, tested shape (cells-as-objects, tickets-as-list with `target_cell`/`acceptance`/`covers`; entails 3/3) + a note that `decomposition` is optional.
- **Context regression closed** (council, Boris C.) — the SKILL description trimmed under the 1024-char budget; the 6 critic descriptions de-boilerplated (the read-only/dispatch stamp lives in `tools:`/the orchestrator, not 6× in the descriptions). Always-on tax 15.4K → 14.6K chars.

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
