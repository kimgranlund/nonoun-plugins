# Authoring a Family Kit — From Ontology to a Green Conformance Gate

`Cell: methodology.system.kit-authoring · Status: defined · Register: established (contract-first plugin design, adapter pattern, golden-fixture verification); the kernel/kit boundary discipline is house synthesis`

A kit is the binding that makes the kernel's invariant machine stamp out a new family with **zero kernel edits**. Authoring one is contract-first work: you do not extend the machine, you discover the contract it already offers and bind to it. The pipeline below produces a conformant `dev-kit-{family}` and ends, every time, at a green `check-kit-conform.py`.

```
  ONTOLOGY ──▶ RUBRIC MANIFEST ──▶ HARNESS ADAPTERS ──▶ DISPATCH POLICY ──▶ SEED PATTERNS ──▶ CONFORM
  family       which validated     validation (verifier)  unit→execution-     warm the          check-kit-
  vocabulary   rubric gates which  + dispatch (runtime)    plan match map      pattern layer     conform.py
  cells        layer                                                           + cold-start      (the gate)
            ◀──────────── re-author on any leak (a kernel edit means STOP) ────────────────────┘
```

The discipline that wraps the whole pipeline: **if any step makes you want to edit the kernel, stop.** A kit that needs a kernel change has leaked the boundary — find the existing contract, or escalate a genuine missing capability as an upstream kernel change re-vendored, never a local edit.

## Step 1 — Family ontology

Decide the family (`corpus`, `app`, …) and seed its **controlled-vocabulary cells** — the typed terms the family's work is named in. These are real cells (`ontology.{scope}.{slug}`) the kit declares in `Kit.ontology`. The naming itself is governed: a new vocabulary atom enters only by a ledgered `regenerating` transition on `ontology.fleet.naming`, never an ad-hoc coinage at a call site. The ontology is what makes the rest of the kit *typed* — the rubric manifest, adapters, and policy all reference these terms.

## Step 2 — Rubric manifest (what counts as done, per layer)

Build `Kit.rubric_manifest`: for each `(layer, scope)` of the family's work, name the **validated rubric cell** that gates it. The load-bearing rule: **the rubric must reach `validated` before it gates anything** — the verifier of the work is itself verified. A ticket's `acceptance.rubric_cell` is resolved against this manifest, so the manifest *is* the family's doneness contract. Respect the partial order: a rubric depends on its spec; nothing binds a rubric before its spec validates (the kernel's `lattice.py validity` enforces this, and "scoring vibes" is the failure it prevents). If the family's rubrics are not yet validated, the kit is not ready — author/calibrate them first (the `verification` skill's job), then bind them here.

## Step 3 — Harness adapters (the two species)

Author the `Kit.adapters` — each an `Adapter` (`adapter.schema.json`):

- **Validation adapters** (`kind: validation`) — for each layer the family validates, bind a `target` `(layer, scope)` to a `verifier` argv that `validate.py` runs (**exit 0 = pass**; the signal is minted from the exit status). Substitution tokens `{cell}`, `{asset}`, `{worktree}` are filled at dispatch. **Keep the verifier's reference material pristine** — out of the worker's reach. This is the anti-reward-hacking invariant: the verdict is an external check the worker cannot reach or edit. Omitted `target` axes are wildcards, so one adapter can cover a whole layer.
- **Dispatch adapter** (`kind: dispatch`) — bind the runtime: pick `runtime` (`mock` for CI/Crawl; a live binding `claude-agent-sdk`/`headless-claude-code` for real work, **pinned against current product docs, never guessed** — OD-003), an `invocation` argv (tokens `{ticket}`/`{cell}`/`{worktree}`/`{skill_surface}`/`{budget}`), and assert every required `guarantee` true: `hermetic_worktree`, `gates_active`, `event_stream`, and the `stop_on` set. dev-server already ships a deterministic `MockAdapter` and a docs-pinned `HeadlessClaudeAdapter`; the kit's dispatch adapter is the typed declaration of which the family uses. The conformance gate checks all four guarantees are asserted.

## Step 4 — Dispatch policy (selection is policy, not inference)

Author the family's `DispatchPolicy` (`dispatch-policy.schema.json`) and point `Kit.dispatch_policy` at it (a kit-relative path). It is an **ordered match-rule map** from unit characteristics (`ticket_type`, `target_layer`, `target_scope`, `risk_band`, `autonomy_tier`) to an `ExecutionPlan`, with a `default`. **First matching rule wins.** The plan sets `orchestration_shape`, `loop_strategy`, `context_plan`, `effort`, and `delegation`. Follow the `collapse-to-justify` posture: default to maximal decomposition along real seams (orchestrator-workers / team / parallelization), collapse to a simpler shape only when justified by the *absence* of real structure (an irreducible unit, no independent seams, depth past the fidelity limit) — never by timidity. Width is maximized; depth is bounded by `delegation.max_depth`; budget always binds. The compass reads this policy to assemble each dispatch — **selection is policy, never a model decision at dispatch time.**

## Step 5 — Seed patterns (warm the family)

Ship `Kit.seed_patterns`: pattern artifacts (or cell ids) that warm the family's pattern layer and the compass **cold-start priors**. Before the ledger has history, `risk_concentration` and `probe_cost` have no evidence; the kit's seed patterns supply the priors the compass uses until the ledger replaces them with measured values (OD-002, leaning kit-priors refined by triage, replaced by ledger evidence). Seed honestly — a seed pattern is a prior, not a validated claim.

## Step 6 — Conform (the gate, not a self-claim)

Run the conformance gate (`dev-kernel/bin/check-kit-conform.py`, the sibling kernel-tooling gate — **this methodology references it, never re-implements it**). It asserts the kit is schema-valid, every adapter conforms to its species, the rubric manifest resolves to validated rubric cells, the dispatch policy is a valid `DispatchPolicy`, and — the falsification test — **authoring the kit touched zero kernel files.** A failing gate means the kit is not conformant; iterate until it is green. Conformance is the gate's verdict, never the kit's prose claim. The end state is a `dev-kit-{family}` that the same kernel and the same server can drive against a new family with no kernel change — the boundary proven, not asserted.

## Self-Application

The factory's own corpus family is the first kit (`dev-kit-corpus`): its ontology is the agentic-systems vocabulary, its rubric manifest binds the spec/rubric/… verifiers, its validation adapters bind the corpus verifiers, and its dispatch policy routes corpus units. The second kit (`dev-kit-app`, a test/CI harness family) is authored by this exact pipeline and, by reaching a green conformance gate **with zero kernel edits**, proves the kernel/kit boundary — the "Fly" milestone. Authoring the second kit *is* the boundary's falsification test, run for real.

## Kit-Authoring Failure Modes

**Editing the kernel to make the kit fit** (the boundary leaked — re-author to bind an existing contract, or fix upstream and re-vendor; the gate's zero-kernel-edits check catches it). **Shipping instance state in the kit** (a kit is stateless — `lattice.json`/tickets/signals/the ledger live in the instance). **Binding an unvalidated rubric** (scoring vibes; validate the rubric first, the partial order requires it). **A guessed dispatch runtime invocation** (OD-003 requires pinning against current product docs). **A verifier the worker can reach or edit** (defeats pristine-reference scoring — the canonical reward-hack). **A dispatch policy that timidly collapses** (the posture is maximal decomposition justified by structure; collapse only on the *absence* of seams). **Asserting conformance in prose** (conformance is `check-kit-conform.py`'s verdict — write toward a passing gate, never claim it).
