# dev-kit-app — the application family kit (the boundary proof)

A second `dev-factory` family, whose real purpose is the kernel/kit boundary's **falsification test** (TDD §5): adding it required **zero edits to `dev-kernel`**. A different family — `app` instead of `corpus` — with its own ontology, rubric manifest (`test-suite`, `contract-tests`), validation harness (a passing test suite, not a doc check), and dispatch policy (bisect for bugs, a tracer-bullet team for capabilities) — all bound through the *same* kernel contracts (`kit.schema.json`, `adapter.schema.json`, `dispatch-policy.schema.json`).

If adding this kit had required changing a kernel bin or schema, the boundary would have leaked. It didn't:

```bash
python3 ../dev-kernel/bin/check-kit-conform.py kit .   # exit 0 = binds the kernel, forks nothing
```

That a `corpus` kit and an `app` kit coexist over one unchanged kernel is the architecture's central claim, made checkable.

## Bind it — step by step

To run dev-factory with the **app** family (capability/protocol cells validated by a passing test suite):

```bash
# 1. install dev-kernel + dev-kit-app (project-local); 2. init the instance:
python3 ../dev-kernel/bin/lattice.py init --dir .agents/dev-factory
# 3. bind THIS kit when you start the server:
DEV_FACTORY_KIT=$PWD DEV_FACTORY_DIR=/path/to/project/.agents/dev-factory \
  DEV_FACTORY_HEARTBEAT=1 uvicorn dev-server.app:app --port 8731
```

Now capability/protocol cells validate against `test-suite-check` (the runner's real exit status), and bug tickets dispatch as a `bisect` loop per `dispatch-policy.json`. Sample prompt: *"create a ticket to advance the auth-service capability cell"*.

## Also ships: the `ui-layout-decomposer` skill

Building shippable apps includes laying out their UIs, so the app kit ships a UI-layout decomposition skill (`skills/ui-layout-decomposer/`). It carries the **two-axis method** developed while building the dev-server cockpit — **OUTSIDE-IN** (macro→micro layout: frame → regions → groups → atoms) × **INSIDE-OUT** (feature-actions → feature-surfaces: verbs → bindings → feedback → coherence) — as a **gated rubric** (`A1·A2·B1·B2` are gates; the rest reviews) plus an **ASCII-wireframe library** of four shell archetypes: `productivity-shell` · `saas-dashboard` · `marketing-site` · `mobile-app`. Three modes: **DECOMPOSE** (read a UI → named region map + a two-axis grade) · **DESIGN** (intent → wireframe) · **GRADE**. It's a general technique — kept here because UI layout is app-building knowledge, not a kernel concern (`check-kit-conform` is unaffected: a skill is not a kernel fork).
