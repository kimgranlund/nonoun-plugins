# plugins-factory v0.2.34 (plugin) — "who reviews the reviewer?" self-red-team (2026-06-13)

The catalog's plugin-lifecycle meta-tool authored and red-teamed every other plugin in `nonoun-plugins` (brand-forge, product-forge, agent-ops, harness-forge) but carried only **one** prior `reviews/` entry (`2026-06-02-plugin-red-team.md`) — so a blind spot in *its* rubric, gates, or design is silently inherited by every judgment it has ever rendered. This is the highest-leverage sibling review in the catalog (docs/PLAN.md "Next" #1). Full **9-critic panel** (`plugin-council` roster), fanned out as **parallel isolated `plugins-factory:critic-*` agents**, each cold-static-read, plugin-under-review treated as untrusted DATA (assessed, never executed). Then a deterministic **gate anchor** (plugins-factory's own gates run on plugins-factory) and a **verification pass** that confirmed or refuted each headline before any fold. Model: Claude Opus 4.8. No critic modified files.

This record is itself the answer to Charity M.'s Critical: the tool that certifies everything finally writes down a certification of itself.

## Gate anchor — the deterministic baseline (all GREEN)

`validate_plugin --strict` PASS · `reference-lint` PASS · `check-manifest-sync` PASS (0 drift) · `check-trust-boundary` 11/11 reviewers carry the untrusted-DATA guard · `context-cost` ≈ 5,028 chars / ~1,257 tok always-on over 19 components (agent 2,709 / command 827 / skill 1,492). No `.mcp.json` (static-analysis-only by design). The mechanical surface is clean — which is the point: **every finding below is something the gates structurally cannot see.**

## Verdict: STRONG PASS on the mechanized surface; the council surfaced real architecture- and verification-layer gaps the gates don't reach. 1 convergent honesty-fix folded; 4 findings escalated to tracked decisions (I-10…I-13).

Severity floor met without manufacture: **7 of 9 critics filed a Critical**; Scott W. honestly declined one (showed his work refuting four candidates); the panel converged hard on three themes. Crucially, the verification pass **refuted the most-piled-on Critical** (the "licensed fonts" claim) — a result that is itself a finding about the panel.

## Per-critic headlines

| Critic | Lens | Headline finding | Sev | Status |
| --- | --- | --- | --- | --- |
| Boris C. | context cost · vanilla | `bin/corpus-reader/` is an off-job payload wired to zero plugins-factory components, **invisible to the plugin's own `context-cost.py`** (the P6 gate measures descriptions, never `bin/` payload) | Critical | I-11 |
| Steve Y. | platform · namespacing | **Cross-plugin critic-agent name collision** — `critic-{boris-c,andrej-k,simon-w}` byte-identical `name:` across plugins-factory + agent-ops; the collision gate is scoped to commands∩skills within one plugin | Critical | **I-10 (confirmed)** |
| Elon M. | delete · smallest viable | The bundle has two jobs; `bin/corpus-reader/` + its two satellite gates (`check-bake-safety`, `sync-corpus-reader`) are a second product; `--with-mcp` built because it could be | Critical | I-11 |
| Charity M. | observability · post-install | **The judge emits no durable artifact** — every verdict evaporates into chat; `scores/<plugin>.json` specced but unshipped; `empirical_applications: 0` | Critical | I-13 (ROADMAP'd) |
| Andrej K. | verifiability · jaggedness | **`check-recall` is a closed loop** — author paraphrases matched against author regexes proves nothing about live council recall; calibration is N=1-shape on confessional fixtures | Critical | **0.2.35 (folded)** + I-13 |
| Simon W. | hook/MCP blast radius | **Executing gates' "trusted-only" boundary is prose, not a mechanism** — `check-mcp-liveness` / `context-cost --with-mcp` spawn untrusted MCP servers with full env; the reviewer holds the trifecta it grades Score-1 | Critical | **I-12 (confirmed)** |
| Scott W. | manifest · illegal states | Validator's strongest checks pass *vacuously* on plugins-factory because it under-declares itself; slug-collision scoped to a subset of the namespace | Major (no Critical, justified) | I-10 |
| Chip H. | determinism boundary | `check-recall` draws the determinism boundary one layer too high — a green gate vouching for "the council would catch this," a property no gate observes | Critical | **0.2.35 (folded)** |
| David F. | packaging · CI gate | ~~Ships licensed GT America fonts in every install~~ **(REFUTED — gitignored, untracked)**; 3 gates lack `selftest`; gate behavior can change with no version bump | Critical→refuted; Major stands | I-11 |

## Cross-critic synthesis

### Convergence (≥2 critics)

1. **`bin/corpus-reader/` is off-job for the judge** — Boris C. (Critical), Elon M. (Critical, deletion #1), Steve Y. (Major), David F. (Major), + 3 critics noted it. **The most-converged finding.** Grep-proven: no plugins-factory command/skill/agent routes to it; it exists only as the canonical source `sync-corpus-reader.py` fans into brand-forge + product-forge. Boris's sharpest sub-point stands independent of the relocation question: **`context-cost.py` is structurally blind to `bin/` payload**, so the plugin's flagship P6 gate certifies the lean loaded surface and cannot see the heavy bundle beside it — a blind spot inherited by every plugin it has scored.
2. **The verification apparatus doesn't verify** — Andrej K. (Critical) + Chip H. (Critical), independently, same mechanism: `check-recall.py` validates author-written paraphrases against author-written regexes (a closed loop), and CI scores the council only against a *frozen baseline transcript*, never a live panel. Both proposed the identical fix.
3. **Executing gates are dangerous + redundant** — Simon W. (Critical, the RCE/trifecta angle) + Elon M. (Major, the "why does `--with-mcp` exist" angle) converge on `context-cost.py --with-mcp` and `check-mcp-liveness.py`: they execute untrusted servers behind only a docstring.
4. **Self-coverage is narrower than the published rule** — Scott W. (Major×3) + David F. (Major×2) + Steve Y. (Critical, at marketplace scale): the gates pass *vacuously* on their own author because plugins-factory under-declares itself, and the cross-plugin collision the tool exists to prevent is the one it doesn't check.

### The single highest-severity finding

**Steve Y.'s cross-plugin agent collision (I-10)** — because it is (a) confirmed factually, (b) live in the maintainer's own auto-enabled repo, and (c) the exact "designed-as-if-the-only-plugin-in-the-room" failure the meta-tool red-teams others for. Honestly scoped: severity is *contingent on the runtime's bare-name resolution* (if Claude Code resolves an orchestrator's `Task("critic-boris-c")` within the invoking plugin's namespace, there is no live ambiguity; if globally, the roster is nondeterministic when agent-ops is co-enabled). Either way the bare-name dispatch is fragile and the tool ships no gate for it.

### The productive tension

**Elon M. wants to delete machinery; Charity M. wants to add it.** Elon: the council could be 5 not 9, `--with-mcp` and three gates are gold-plating. Charity: ship the `scores/*.json` writer the tool lacks. The resolution is *not* a compromise — it's a sorting rule the panel implicitly agrees on: **add durable-state where it closes an observability gap on the plugin's own job (scores), delete machinery that serves a second job (corpus-reader) or measures what a static read already gives (`--with-mcp`).** Job-fit, not count, decides.

### The blind spot all nine miss (S3)

**This very review is the closed loop Andrej and Chip flagged, one level up.** The reviewer-of-the-reviewer was plugins-factory's *own* `critic-*` council — the instrument auditing itself with itself. Andrej's C1 ("score a plugin you did not author, cold") applies to *this run*: a genuinely independent audit would use a different panel. Second blind spot, exposed only by the verification pass: **the panel piled onto a false Critical.** Four critics (David, Simon, Andrej, Scott) asserted or echoed "ships licensed fonts"; only Boris C. checked `.gitignore` and scoped around them. A council that can be wrong *together* on a checkable fact is the strongest argument for the deterministic gate anchor and the verification pass that bracket it — the critics generate hypotheses; they don't get to be the verifier of their own claims.

### 9-dimension scorecard (1–5, evidence-cited above)

**P1 3 · P2 3 · P3 3 · P4 4 · P5 3 · P6 3 · P7 2 · P8 2 · P9 2.** The jagged line: the **loaded** surface (thin DRY commands, real-TOC skills, tool-locked critics, no-MCP) is genuinely strong and every critic credited it. The defects cluster in three places the gates don't look — `bin/` (off-job payload, P6-invisible), the **verification layer** (P2/P8 — recall is a tautology, no durable verdict), and **cross-plugin / self-coverage** (P7/P9 — collision unguarded, executing gates prose-bounded). P4 is high (no runtime cross-plugin paths; the fonts that would have docked it don't ship).

## Verification pass — what the gate anchor + a cold recheck confirmed or refuted

- **REFUTED — David F. C1 "ships multi-MB licensed GT America fonts in every install."** `git ls-files | grep -iE '\.(ttf|otf)$'` → **0**; `brand-corpus/` is `.gitignore`d (`git check-ignore` confirms). The fonts are local-dev state and never reach an install. Simon m1 / Andrej n1 / Scott N1 echoed the same false premise; Boris C. alone verified and scoped around it. **The committed reader `lib/` + `demo-corpus` (~20 files) does ship** — that part of the off-job-payload finding stands; the *licensing* framing does not.
- **CONFIRMED — Steve Y. C1 collisions:** `critic-boris-c`, `critic-andrej-k`, `critic-simon-w` resolve to 2 plugins each (agent-ops + plugins-factory); `critic-garry-t` to 2 (agent-ops + product-forge).
- **CONFIRMED — Simon W. C1:** `check-mcp-liveness.py:12` "TRUSTED catalog plugins only" is a comment; `main(argv)` carries no trust flag.
- **CONFIRMED — Andrej/Chip:** `check.py:8` already carries the honest "catch-rate, not a deterministic gate" caveat; `check-recall.py` did not, and framed its corpus as "the legitimate ways a council *might* word it" — the overclaim.
- **SOFTENED — the "9 gates" count (Scott M2 / David M2):** 10 `bin/*.py` = 9 gates + `sync-corpus-reader` (not a gate), so README's "9 stdlib gates" is defensible; the real gap is that the count is *unchecked*, not that it is wrong.
- **CONFIRMED tracked — Charity C1 `scores/*.json`:** ROADMAP.md:10 [v0.2] + PLAN.md #4.

## Disposition

### Folded now — 0.2.35

- **`check-recall.py` honesty line (Andrej K. C1 + Chip H. C1, convergent).** The gate now states it validates *pattern-recall over a hand-authored corpus* and **does not** measure the council's live catch-rate — inheriting the caveat `check.py:8` already carried. The cheapest, highest-confidence, two-Critical-convergent fix: pure honesty, zero architecture risk. The deeper fix (re-source the corpus from real prior `runs/*.md` transcripts) is I-13.

### Escalated to tracked decisions (architectural — ripple catalog-wide, warrant an owner's call, not a reflexive fold)

- **I-10 — Cross-plugin critic-agent namespace collision** (Steve Y., confirmed). Detection fix (a `validate_plugin` marketplace-mode agent-`name` uniqueness check) is clean but would fail CI until the slugs are namespaced; remediation (rename `critic-*` across 3 plugins) touches the deliberate obscured-slug convention. Both together, or neither.
- **I-11 — `bin/corpus-reader/` off-job + `context-cost.py` blind to `bin/` payload** (Boris C. / Elon M. / Steve Y. / David F.). Relocate the canonical reader out of the judge plugin to repo-level shared tooling; teach the P6 gate to weigh committed `bin/` payload against the plugin's stated job.
- **I-12 — Executing gates need a code interlock** (Simon W. / Elon M.). `check-mcp-liveness` + `context-cost --with-mcp` should refuse by default and require an explicit per-invocation trust assertion (flag + CI-set env marker), turning "trusted-only" from docstring into mechanism.
- **I-13 — The judge has no durable verdict record + the council's recall is unmeasured** (Charity C1 / Andrej C2-C3). Ship the ROADMAP'd `scores/<plugin>.json` writer (to `${CLAUDE_PLUGIN_DATA}`, not the cache root); re-source recall corpora from real transcripts; score one real third-party plugin cold. Closes `empirical_applications: 0`.

### Noted, not actioned (taste / minor)

Council-of-5-vs-9 (Elon m2 — the 9th critic buys corroboration, not coverage; deliberate), advisory-hook positive heartbeat (Charity M3), `plugin.json` description hook-mechanics trim (Boris/Charity/Elon), `.DS_Store` in tree (all gitignored, clean-clone-safe). The `sync-corpus-reader` reaching into siblings (Elon M2) is dev/CI tooling, not a runtime cross-plugin dependency — moves with I-11 if the reader relocates.
