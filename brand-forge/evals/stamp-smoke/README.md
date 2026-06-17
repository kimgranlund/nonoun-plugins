# stamp-smoke — the generator-output gate (S9/S10)

`bin/brand-stamp plugin` emits a child plugin "built to pass `validate_plugin.py`," but nothing
asserted the generated output actually does — the generator-untested gap the v0.2 red-team flagged
(David F., S9/S10). This fixture closes it: `corpus/` is a tiny two-layer brand corpus that CI stamps
into a plugin, then runs the harness validator (`plugins-factory/bin/validate_plugin.py --strict`) on
the result.

The check lives in CI (`.github/workflows/ci.yml`), not in either plugin: brand-forge must not depend
on plugins-factory (and vice versa) — the zero-cross-plugin-dependency rule — so CI is the only legal
place to orchestrate `brand-stamp` (brand-forge) → `validate_plugin` (plugins-factory). Reproduce locally:

```sh
python3 brand-forge/bin/brand-stamp plugin brand-forge/evals/stamp-smoke/corpus --name smoke -o /tmp/stamp
python3 plugins-factory/bin/validate_plugin.py plugin /tmp/stamp/plugin/smoke-brand --strict
```

The corpus is intentionally minimal — the gate proves the *generator's* output is structurally valid,
not that any particular brand content is good (that judgment lives in `/brand-stamp` + the council).
