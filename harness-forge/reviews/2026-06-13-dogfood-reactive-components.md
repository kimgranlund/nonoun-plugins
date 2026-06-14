# `/harness-assess` dogfood — `rce` (reactive-components), 2026-06-13

The first real-world application of the v0.5.1 **assess** cold start, run cold on an external project (`/Users/kimba/Projects/fable-tests/reactive-components`) to validate that survey → seed recommendation actually produces a sound, usable assessment — the "calibrate against reality" discipline applied to the newest feature. Model: Claude Opus 4.8.

## The project

`rce` — a zero-runtime-dependency UI framework (signals + tagged templates + custom elements, ~5 kB gz, v1.0). Built "gate-by-gate with probe lists written before code"; 491 probes, 53 real-Chromium smoke checks, `tsc --strict` clean. A mature, deeply test-driven library.

## Step 1 — the mechanical survey (`bin/survey.py`)

```
Stack:  JavaScript (76), TypeScript (22)  ·  manifests: package.json
Layers: ● ontology ● spec ● rubric ● capability ● methodology ● protocol ● ledger ● pattern   ○ policy
Frontier (ABSENT): policy
```

Accurate: pruned `node_modules` (54 dirs), found README/CLAUDE.md/docs/tests/CHANGELOG/ROADMAP, detected the stack.

## Step 2 — read the present docs (the judgment)

The footholds the harness should **reuse, not re-derive**:

- **rubric/capability — the crux.** `package.json` ships a rich verifier surface the harness can mint signals from directly: `npm test` (491 probes, `node --test`), `npm run check` (`tsc -p tsconfig.json --strict`), `npm run smoke` (Chromium), **`npm run size`** (the ~5 kB budget gate), chained in `prepublishOnly`. These are *validated* external checks — `validate.py <cell> -- npm test` mints a real signal from exit status. This is the strongest possible foothold: a project that already verifies itself.
- **spec.** The acceptance criteria are the `gateN-probes.md` + `*-spec.md` files (probe lists written before code) — the harness's define step, already done by hand.
- **methodology.** `CLAUDE.md` + the probes-first/gate-by-gate discipline **is** the engine's define→create→validate loop, run manually. harness-forge would mechanize the *bookkeeping between cells* (lattice state, ledger, gate enforcement), not the judgment inside them.
- **ledger.** CHANGELOG + git + `docs/release-audit.md`.

## Step 3 — recommended seed

**Intent:** shape (b) is the strongest fit — **build an agent that extends `rce` control-by-control under its own gate discipline.** The project already runs a manual harness loop; the win is making it semi-autonomous with the existing verifiers wired.

- **First slice:** one next `ui-*` control (or the next gate) → `spec.task.<control>` carrying its probe list as checkable acceptance; `rubric.task.<control>` = `npm test && npm run check && npm run size`.
- **Scope:** `task` (one control), then widen to `workflow` only from a validated control.
- **Footholds seed mature:** ontology (the framework vocab), rubric/capability (the verifiers, effectively `validated`), methodology (CLAUDE.md), protocol (the `types/` `.d.ts` public surface), ledger (CHANGELOG).
- **Frontier:** `policy` — and on reading, the real policy (the 5 kB size budget, zero-runtime-deps) lives in `README` + `size.mjs`, not a `SECURITY.md`; the first slice should make those a typed `policy` cell the gate enforces (a size regression is a budget breach).
- **Wire:** yes — an unattended control-extension loop is exactly the shape the blocking gates protect; `validate.py` mints from `npm test`/`size`, `gate-budget` bounds the run.

## Findings folded back (survey.py, 0.5.2)

The survey is "a starting map, not a verdict," and reading recovered what the heuristics missed — but the misses were general (library projects are a huge class), so they were fixed:

1. **spec missed the real specs** — the criteria were `gate8-spec.md` / `gateN-probes.md`, but the matcher only caught a literal `spec.md`. Now matches `*[-_](spec|probes|acceptance).(md|txt)`.
2. **protocol false-negative for a library** — the API contract is the `types/` + `.d.ts` surface, not OpenAPI/proto. Now `.d.ts` + `types/`/`typings/` feed protocol.
3. **pattern false-negative** — `case-study-spreadsheet.md` + demos are the patterns. Now matches `case[-_ ]?study` + `demo`/`demos`/`recipes` dirs.

After the fix, the frontier narrowed correctly from `policy, protocol, pattern` to just `policy` — the genuinely thin layer.

## Verdict

`/harness-assess` works on a real, unfamiliar project: the survey was accurate, and the recommendation was specific and actionable (not boilerplate) — it identified the exact verifier commands, the right intent shape, and a concrete first slice. The dogfood also *improved the instrument* (library-aware detection). This is `empirical_applications: 1` for the assess feature.
