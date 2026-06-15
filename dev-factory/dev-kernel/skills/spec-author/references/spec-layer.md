# Why the spec layer is upstream of everything

The lattice's nine layers are **partially ordered**, and the spec layer (with `ontology`) sits at the source:

```
  ontology + spec ──▶ rubric, policy, capability ──▶ methodology, protocol ──▶ ledger ──▶ pattern
        │                                                                                      │
        └──────────────────────────── feedback (regeneration) ─────────────────────────────────┘
```

The order is not stylistic — it is **enforced** (`lattice.py validity` refuses an out-of-order advance). Every other layer reads *down* from the spec: a `rubric` encodes *what done means for this spec*; a `capability` is built *to satisfy this spec's intent*; a `methodology` is the playbook *for delivering it*; the `ledger` records *runs against it*; a `pattern` is distilled *from those runs*. There is no layer the spec depends *on* except `ontology` (the shared vocabulary the spec is written in). It is the headwater.

## Intent loss here multiplies downstream

Because every downstream layer is *derived from* the spec, an error in the spec is not a local defect — it is a **multiplier**. A fuzzy intent does not stay fuzzy in one place; it is re-expressed, amplified, by each layer that reads it:

- a vague acceptance criterion becomes a rubric that scores the **wrong property** — and now the verifier is wrong;
- a missing non-goal becomes a capability built **past the boundary** — scope creep, mechanized;
- an un-captured intent becomes a methodology that delivers, fast and well, the **wrong thing** — the engine converges confidently on a mistake;
- and the ledger faithfully records, and the patterns faithfully distill, that wrong thing — so the error compounds into the factory's *learned* substrate.

This is why the spec is the **highest-leverage failure point** in the system: fuzzy intent upstream multiplies into wasted work downstream, and the further downstream the error surfaces, the more derived work has already been built on it. A unit of clarity spent here saves a layer's worth of rework everywhere below. The cheapest place to fix the wrong thing is before anything was built to satisfy it.

## Why a spec is rubric-gated like any other cell

A layer this leveraged cannot be trusted on prose. So a spec earns `validated` exactly like any other cell — it binds a **validated** rubric (`spec-quality`, in `dev-kit-corpus`), and the validation path mints its signal from that gate's exit status, not from the author's read of their own draft. The author never writes the signal that validates its own spec (the generator/critic split). The verifier of specs is itself verified: a rubric cannot gate until it is `validated`, so a spec bound to an unvalidated rubric is "scoring vibes" and `lattice.py validity` refuses it.

And because the spec is upstream, a spec change is **never local**: when a `validated` spec is revised (the UPDATE mode), `propagate-staleness` flips every dependent cell to `stale` — they were validated against a definition of done that just moved. The partial order makes that cascade mechanical: staleness is graph computation, not a judgment call. Gating the headwater, and propagating from it, is how the factory keeps a small upstream change from silently de-trusting everything built below it.
