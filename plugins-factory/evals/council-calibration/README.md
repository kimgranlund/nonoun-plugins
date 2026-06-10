# Council-calibration eval

Does the critic council actually find the right defects? The deterministic gates (`behavioral-gates.py`) prove the harness catches _structural_ defects (`../`-deps, slug collisions, drift). They cannot test the council's headline job: catching the _architecture-judgment_ defects no regex can see. This eval does — by running the council on a fixture with **planted** judgment defects and scoring whether it surfaces them.

It is **not a CI gate.** The council is an LLM panel, so its output is non-deterministic; this is a periodic, recorded **calibration** — a catch-rate over a known-bad fixture, not a pass/fail build step.

## The fixtures (two shapes)

Each fixture **passes every deterministic gate** (valid kebab manifest, no `../`, no command↔skill collision, parsable `.mcp.json`, version↔CHANGELOG synced) but carries planted defects only judgment catches. The two shapes are complementary — one fails by **excess**, one by **vacancy** — so together they exercise opposite failure modes.

### `mega-helper` (`build-fixture.py`) — failure by excess

| Planted defect | Dimension | Checker |
| --- | --- | --- |
| Four unrelated domains in one plugin (PDF tooling · brand strategy · recipe search · deployment) | **P3** Boundary Cohesion | `check.py` |
| A bundled MCP that is a 1:1 wrapper over REST endpoints (one tool per verb × resource, 25 tools) | **P2** Component Fit | `check.py` |

### `docs-studio` (`build-fixture-hollow.py`) — failure by vacancy _(added 2026-06-10)_

Built to prove the two probes the council named as its own blind spots on `mega-helper` (now folded into the rubric as AP-P6/AP-P7 and into the prompt corpus as PF5/CF5). It is a **coherent single job** with a **task-shaped 3-tool MCP**, so it deliberately does NOT trip P3/P2 — isolating the new probes:

| Planted defect | Dimension | Checker |
| --- | --- | --- |
| Components whose bodies are thinner than their descriptions promise (one-sentence skills under rich blurbs; a command that names an action it doesn't implement) | **AP-P6 / PF5** Hollowness | `check-hollow.py` |
| A wired MCP whose server defines tools and exits — green to every static gate, 100% non-functional | **AP-P7 / CF5** Liveness | `check-hollow.py` |

A healthy council must **name both** defects of whichever fixture it reviews. A miss is a real finding about the instrument — record it.

## Protocol

```text
1. build the fixture:
     python3 build-fixture.py /tmp/mega-helper            # excess shape
     python3 build-fixture-hollow.py /tmp/docs-studio     # vacancy shape
2. confirm the deterministic gates PASS it (the defects are judgment, not structure):
     python3 ../../bin/validate_plugin.py plugin <dir> --strict   # PASS
     python3 ../../bin/check-manifest-sync.py <dir>               # PASS
3. run the council over it (with plugins-factory enabled):
     /plugin-critique <dir>
   …or invoke the `plugin-council` orchestrator agent on that path.
4. save the council's report to a file, then score it with the matching checker:
     python3 check.py <transcript>          # mega-helper   → N/2
     python3 check-hollow.py <transcript>   # docs-studio   → N/2
5. record the run under runs/ (date, model, catch-rate, any missed defect).
```

Both checkers match concept-level phrasings (LLM panel → catch-RATE, not a deterministic gate). Recorded runs live in `runs/`.

## Catch-rates over cold runs

**`mega-helper` — N=3, per-defect 2/2 at 3/3 runs (100%), BLOCKED ×3:**

| Run | Verdict | check.py | Notes |
| --- | --- | --- | --- |
| 2026-06-04 baseline | BLOCKED | 2/2 | full 9-critic panel |
| 2026-06-10 run2 | BLOCKED | 2/2 | the real `plugin-council` agent; dispatch degradation recorded (no spawn tool → per-critic sections run lens-isolated) |
| 2026-06-10 run3 | BLOCKED | 2/2 | as run2; independently re-converged on the same liveness blind spot |

Both 06-10 runs independently surfaced the same emergent Criticals beyond the planted set (the dead MCP server; the unspecified `/deploy`) and named the same two panel blind spots — *liveness* ("the panel verifies wiring, never execution") and *hollowness* ("the rubric measures bloat; emptiness sails through"). **Those two blind spots are now closed**: folded into `../../references/rubrics/plugins-holistic.md` (AP-P6/AP-P7 + hard tests 11–13) and `../../references/critics/eval-prompts.md` (PF5/CF5), and given their own fixture below.

**`docs-studio` — N=3, per-defect 2/2 at 3/3 runs (100%), BLOCKED ×3:**

| Run | Verdict | check-hollow.py | Notes |
| --- | --- | --- | --- |
| 2026-06-10 run1 | BLOCKED | 2/2 | the real `plugin-council` agent reading the updated corpus; P3 scored **4** — the coherent-scope isolation held |
| 2026-06-10 run2 | BLOCKED | 2/2 | as run1; found a sharper liveness sub-finding (the *silent-success* failure: a dead server that exits 0 reads "green" until first call) |
| 2026-06-10 run3 | BLOCKED | 2/2 | P3 held at 4; with liveness+hollowness now *covered* probes, the panel named the **next** blind spot — "no critic owns 'prove it works once' end-to-end" — exactly the S3-intended behavior |

The new fixture proves the folded-back probes work: the council caught **hollowness and liveness on a plugin the old panel would have waved through** (gates green, scope coherent, MCP tool-shapes correct), at 100% across all three runs. All runs also independently flagged the unscoped `apply_style` repo-wide rewrite — genuine review beyond the planted set.

## Instrument note — checker precision (2026-06-10)

Cross-applying `check.py` (the excess checker) to the `docs-studio` transcripts surfaced a **precision** finding (the mirror of the agent-ops recall finding): bare dimension-label patterns (`\bp2\b`/`\bp3\b`) matched the scorecard of *any* review, and the kitchen-sink/wrapper phrasings matched **negated** mentions ("unlike a kitchen sink", "the inverse of the API-wrapper"). The bare labels were removed (mega-helper still scores 2/2 on substantive phrasings). The negated-mention sensitivity is an inherent limit of concept-regex matching and is bounded in practice: **each checker is valid only against its own fixture's transcripts** (the use CI and the protocol prescribe), where its findings are genuine.
