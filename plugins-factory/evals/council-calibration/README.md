# Council-calibration eval

Does the critic council actually find the right defects? The deterministic gates (`behavioral-gates.py`) prove the harness catches _structural_ defects (`../`-deps, slug collisions, drift). They cannot test the council's headline job: catching the _architecture-judgment_ defects no regex can see. This eval does — by running the council on a fixture with **planted** judgment defects and scoring whether it surfaces them.

It is **not a CI gate.** The council is an LLM panel, so its output is non-deterministic; this is a periodic, recorded **calibration** — a catch-rate over a known-bad fixture, not a pass/fail build step.

## The fixture

`build-fixture.py <dir>` writes `mega-helper` — a plugin that **passes every deterministic gate** (valid kebab manifest, no `../`, no command↔skill collision, parsable `.mcp.json`) but carries two defects only judgment catches:

| Planted defect | Dimension | Expected verdict |
| --- | --- | --- |
| Four unrelated domains in one plugin (PDF tooling · brand strategy · recipe search · deployment) | **P3** Boundary Cohesion | kitchen-sink — score ≤ 2; recommend splitting |
| A bundled MCP that is a 1:1 wrapper over REST endpoints (one tool per verb × resource, 25 tools) | **P2** Component Fit | the API-wrapper anti-pattern — score ≤ 2 |

A healthy council must **name both**. If it misses one, that is a real finding about the instrument — record it.

## Protocol

```text
1. python3 build-fixture.py /tmp/mega-helper          # build the known-bad fixture
2. confirm the deterministic gates PASS it:           # the defects are judgment, not structure
     python3 ../../bin/validate_plugin.py plugin /tmp/mega-helper --strict   # PASS
     python3 ../../bin/check-manifest-sync.py /tmp/mega-helper               # PASS
3. run the council over it (with plugins-factory enabled):
     /plugin-critique /tmp/mega-helper
   …or invoke the `plugin-council` orchestrator agent on that path.
4. save the council's report to a file, then score it:
     python3 check.py <transcript-file>               # reports the catch-rate
5. record the run under runs/ (date, model, catch-rate, any missed defect).
```

`check.py` matches concept-level phrasings (it is tolerant of how the council words things) and reports `N/2 planted defects caught`. Recorded baselines live in `runs/`.

## Catch-rate over N=3 cold runs

| Run | Verdict | check.py | Notes |
| --- | --- | --- | --- |
| 2026-06-04 baseline | BLOCKED | 2/2 | full 9-critic panel |
| 2026-06-10 run2 | BLOCKED | 2/2 | the real `plugin-council` agent; dispatch degradation recorded (no spawn tool in context → per-critic prompt sections run lens-isolated) |
| 2026-06-10 run3 | BLOCKED | 2/2 | as run2; independently re-converged on the same instrument blind spot (runtime liveness) |

**Per-defect catch-rate: 2/2 at 3/3 runs (100%), BLOCKED ×3.** Both 06-10 runs also independently surfaced the same emergent Criticals beyond the planted set (the dead MCP server; the unspecified `/deploy`) and independently named the same panel blind spot — *liveness* (the panel verifies wiring, never execution) — plus run2's "the rubric measures bloat; emptiness sails through." Both are recorded instrument-improvement candidates (a `tools/list` smoke gate; a hollowness probe), cross-referenced in `../rubric-calibration/README.md`.
