# The Kit Contract — kit.schema.json, adapter.schema.json, and the Boundary's Falsification Test

`Cell: spec.system.kit-contract · Status: defined · Register: established (plugin/contract design, adapter pattern, exit-status-as-signal); the kernel/kit/instance tiering is house synthesis`

dev-factory is a three-tier substrate plus a runtime (TDD §5). Authority flows one way; value flows back the other.

```
nonoun-kernel  (plugin · invariant machinery · stateless)        — defines contracts
      ▲ defines                                  implements ▼
dev-kit-corpus / dev-kit-app  (stateless)                        — bind + accrete
      ▲ binds + accretes
Instance repo  (the ONLY tier that holds state)                  — reads/writes
      ▲
dev-server  (Python runtime · the heartbeat)                     — dispatches workers
```

The kernel owns cell/ticket/ledger schemas, the two state machines, the engine + compass, the gate hooks, and the base roster — and **nothing project-specific**. A kit owns one family's ontology, rubric manifests, validation **harness adapters**, dispatch policy, and seed patterns — and **no instance state**. This reference is the contract a kit binds to.

## The boundary's falsification test (the one law, restated)

> **A kernel that needs editing for a new family has leaked — that is a boundary defect.**

The kernel/kit split is only real if it is *falsifiable*, and its falsification test is mechanical: **adding a kit must require ZERO kernel edits.** The kernel ships invariant capability that could be vendored into many runtimes; a kit binds it to a family without altering it. If a new family forces a kernel change, either the contract was incomplete (fix it upstream in the kernel, re-vendor — never a local edit) or the kit reached past its tier (re-author the kit to bind an existing contract). The second kit (`dev-kit-app`) exists to *prove* the boundary: adding it with zero kernel edits is the "Fly" milestone (§19). `check-kit-conform.py` asserts this property as a CI check — a kit cannot self-certify the boundary; the gate does.

## kit.schema.json — the `Kit` object

A kit is a `Kit` (`$id: Kit`), `additionalProperties: false`, with five **required** fields plus an ontology and seed patterns:

| Field | Req | Shape | Purpose |
| --- | --- | --- | --- |
| `name` | yes | `^dev-kit-[a-z0-9]+(?:-[a-z0-9]+)*$` | the kit plugin name — `dev-kit-{family}` |
| `family` | yes | kebab slug | the family this kit serves (corpus, app, …); binds its dispatch policy + adapters |
| `kernel_compat` | yes | semver range | the dev-kernel version range this kit binds; `kit-conform` rejects an incompatible bind |
| `ontology` | no | cell-id[] | the family's controlled-vocabulary cells the kit seeds |
| `rubric_manifest` | yes | object[] | which validated rubric cell gates which `(layer, scope)` — see below |
| `adapters` | yes | `Adapter`[] | the two adapter species — how the family validates and dispatches |
| `dispatch_policy` | yes | kit-relative path | the family's `DispatchPolicy` (the deterministic unit→plan map) |
| `seed_patterns` | no | string[] | pattern artifacts / cell ids that warm the pattern layer + the compass cold-start priors |

### The rubric manifest

Each entry binds a `layer` (and optional `scope`) to a `rubric_cell` — the validated rubric that gates that layer of the family's work. The load-bearing rule: **a `rubric_cell` must reach `validated` before it gates anything** (the verifier of the work is itself verified). A ticket's `acceptance.rubric_cell` is resolved against this manifest, so the manifest is the family's "what counts as done, per layer." Binding an unvalidated rubric is "scoring vibes" and the partial order (`ontology + spec → rubric, …`) forbids it.

## adapter.schema.json — the two species

An `Adapter` (`$id: Adapter`, `additionalProperties: false`) is discriminated by `kind`. Both carry a kebab `name` unique within the kit.

### Validation adapter (`kind: validation`)

Binds a `(layer, scope)` to a concrete verifier — *how a kit makes "validated" mean something for its family*.

| Field | Purpose |
| --- | --- |
| `target` | which cells this adapter validates: `{layer, scope}`; **omitted axes are wildcards** |
| `verifier` | the command (argv) `validate.py` runs; **exit 0 = pass**; the signal is minted from the **exit status**. Tokens `{cell}`, `{asset}`, `{worktree}` substituted at dispatch |

The verifier's reference material is **pristine** — the worker cannot reach it (pristine-reference scoring). This is the anti-reward-hacking invariant in the adapter contract: the verdict comes from an external check the worker cannot reach or edit, never the worker's opinion. The kernel's `validate.py` runs the verifier and mints the `Signal` from the exit status, advancing `instantiated → validated` only on pass — and a worker is mechanically deny-on-write to `signals/`.

### Dispatch adapter (`kind: dispatch`)

Binds the server's dispatch boundary (§9.2, OD-003) to a concrete agent runtime — *how a worker is actually launched in a hermetic worktree under active gates*.

| Field | Purpose |
| --- | --- |
| `runtime` | `claude-agent-sdk` · `headless-claude-code` · `mock`. `mock` is the deterministic CI runtime (no live model); the live bindings are **pinned against current product docs, never guessed** (OD-003) |
| `invocation` | the command (argv) that launches the worker; tokens `{ticket}`/`{cell}`/`{worktree}`/`{skill_surface}`/`{budget}` substituted |
| `guarantees` | the runtime guarantees the contract **requires** (§9.2): `hermetic_worktree`, `gates_active`, `event_stream`, `stop_on` (a subset of `signal`/`budget`/`no-progress`). `kit-conform` checks they are all asserted true |

The dispatch boundary is the integration seam the kernel deliberately leaves abstract: the kernel defines only the contract, and a kit/instance supplies the concrete binding *pinned against current product docs at build time*, so the architecture stays correct even as a runtime's invocation interface changes. dev-server ships a deterministic `MockAdapter` (a real subprocess, no live model) so the whole loop is CI-verifiable, and a `HeadlessClaudeAdapter` pinned to the June-2026 Claude Code headless docs — a kit's dispatch adapter is the typed declaration of which of these (or which SDK binding) a family uses.

## DispatchPolicy — the unit→plan map (referenced by the kit)

`dispatch_policy` points at a `DispatchPolicy` (`dispatch-policy.schema.json`): a deterministic, ordered match-rule map from unit characteristics (`ticket_type`, `target_layer`, `target_scope`, `risk_band`, `autonomy_tier`) to an `ExecutionPlan` (`orchestration_shape`, `loop_strategy`, `context_plan`, `effort`, `delegation`), with a `default` when none match. **Selection is policy, not a model decision** — the compass reads the policy to assemble each dispatch. The posture is `collapse-to-justify`: default to maximal decomposition along real seams (orchestrator-workers/team/parallelization), collapsing to a simpler shape only when justified by the *absence* of real structure, never by timidity; width is maximized, depth is bounded by `delegation.max_depth`, and budget always binds. The kernel defines the strategy vocabulary; the kit supplies the rules for its family.

## What `check-kit-conform.py` asserts (the gate this skill references)

The conformance check is a sibling kernel gate (`dev-kernel/bin/check-kit-conform.py`, built by the kernel-tooling task — **this skill references it, never re-implements it**). It validates a kit against the schemas above and asserts the boundary holds:

1. the `Kit` is schema-valid (required fields, `name` pattern, `additionalProperties: false`);
2. every adapter is a schema-valid `Adapter` of its species (validation → `target` + `verifier`; dispatch → `runtime` + `invocation` + all required `guarantees`);
3. `rubric_manifest` entries resolve to real rubric cells (each `validated` before it gates);
4. `dispatch_policy` resolves to a schema-valid `DispatchPolicy`;
5. **zero kernel edits** — authoring the kit touched nothing under the kernel (the falsification test, mechanized).

A kit that fails any of these is not conformant and does not ship. The authoring posture is to write *toward a green gate*.

## Kit-Contract Failure Modes

**A kit that forces a kernel edit** (the boundary leaked — bind an existing contract, or fix the kernel upstream and re-vendor; never a local edit). **A kit that ships instance state** (`lattice.json`, tickets, signals, the ledger belong to the instance, the only stateful tier). **Re-implementing the vendored lattice/validation kernel** (it is byte-identical-vendored from harness-forge; `bin/VENDOR.md` — never fork it). **Binding an unvalidated rubric in the manifest** (scoring vibes; the partial order forbids a rubric gating before its spec validates). **A guessed dispatch `runtime` invocation** (OD-003 requires it be pinned against current product docs, not invented). **A verifier the worker can reach or edit** (pristine-reference scoring is the anti-reward-hacking invariant — a clean board produced by editing the scorer is the canonical hack). **Coining a new naming atom at a call site** (a new vocabulary atom enters only by a ledgered `regenerating` transition on `ontology.fleet.naming`).
