# dev-kit-app — the application family kit (the boundary proof)

A second `dev-factory` family, whose real purpose is the kernel/kit boundary's **falsification test** (TDD §5): adding it required **zero edits to `dev-kernel`**. A different family — `app` instead of `corpus` — with its own ontology, rubric manifest (`test-suite`, `contract-tests`), validation harness (a passing test suite, not a doc check), and dispatch policy (bisect for bugs, a tracer-bullet team for capabilities) — all bound through the *same* kernel contracts (`kit.schema.json`, `adapter.schema.json`, `dispatch-policy.schema.json`).

If adding this kit had required changing a kernel bin or schema, the boundary would have leaked. It didn't:

```bash
python3 ../dev-kernel/bin/check-kit-conform.py kit .   # exit 0 = binds the kernel, forks nothing
```

That a `corpus` kit and an `app` kit coexist over one unchanged kernel is the architecture's central claim, made checkable.
