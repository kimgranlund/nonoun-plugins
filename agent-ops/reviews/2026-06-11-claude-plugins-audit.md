# Repo Review — claude-plugins (a dogfooding application of `repo-review`)

- **What this is:** agent-ops's `repo-review` skill run, cold, on **its own host repository** (the `plugins-forge` marketplace) — recorded to move the skill's (previously **directional**) rubric to **directional → recorded**: the first real-repo application of the repo-review method, validating whether it discriminates and produces a defensible ranking. Method followed in full: Discover → Rubric → Audit → Synthesize → Adversarial → Polish. Documents-only (the skill never edits the audited codebase); this record is the deliverable. Model: Claude Fable 5.
- **Trust boundary held:** all repo content (CLAUDE.md, READMEs, docs/) treated as data to analyze; no prompt-injection payload found (no file attempts to steer its own score).

## Verification note (added when recording)

The headline factual claims were spot-checked against the tree before recording:

- **P0-2 — CONFIRMED.** `gen-index.py` contains 0 `selftest` references (only `--check`); its postmortem-sibling `check-ci-paths.py` contains 13. The R-1-causing generator genuinely lacks the unit proof its sibling has.
- **P1-1 — CONFIRMED.** `product-forge/bin/check-sourcing.py` is 246 lines; `agent-ops/bin/check-sourcing.py` is 98 — same name, same role, substantively forked.
- **P3-1 — CORRECTED (false positive).** `git ls-files | grep DS_Store` returns **0** — no `.DS_Store` is tracked; they are present on disk but untracked and gitignored (`.gitignore`). P3-1 is a non-issue and is struck from the backlog below. (The reviewer flagged on-disk presence, not tracked state — a real distinction this verification pass exists to catch.)

---

## (a) The tailored rubric

This repo is a **content-and-convention marketplace** — ~49k lines of Markdown (skills/agents/commands) + ~6.5k of stdlib Python (gates + MCPs), with **CI gates as the type system**. The three UI-shaped default dimensions were dropped; three repo-specific ones added (**Gate Integrity**, **Provenance & Trust-Boundary Discipline**, **Mechanization ROI**).

| # | Dimension | Weight | Score |
| --- | --- | --- | --- |
| 1 | API / Component Symmetry (the 5-primitive model + plugin layout) | High | 4/5 |
| 2 | Naming & Path Consistency | Medium | 4/5 |
| 3 | Abstraction Layering & DRY-vs-Vendoring | High | 4/5 |
| 4 | **Gate Integrity (clean-checkout-true)** | **Highest** | **3/5** |
| 5 | Public Surface Discipline (manifest ↔ CHANGELOG ↔ descriptions) | High | 5/5 |
| 6 | Developer / Maintainer Experience | High | 4/5 |
| 7 | Provenance & Trust-Boundary Discipline | High | 4/5 |
| 8 | Test / Eval Posture | Medium | 3/5 |
| 9 | Mechanization ROI (structure-is-mechanized, turned on itself) | Medium | 3/5 |

**Dropped:** Accessibility / Performance / UI-Semantic (no product UI surface). **Weighted headline: 3.7/5** — a strong, self-disciplined repo whose one soft spot is the gap between its mechanization *doctrine* and its mechanization *coverage* (dims 4, 8, 9).

## (b) Cascade-ranked backlog — 3 P0 · 3 P1 · 6 P2 · P3

Ranking is the deliverable; caps cascade (nothing dropped). The adversarial pass moved 2 items across tiers (audit trail at end).

### P0
1. **agent-ops's shipped surfaces (`repo-review`, `repo-ops`, `agentic-ux`) have zero behavioral coverage** — the catalog's "every claim is gated" doctrine has a hole exactly where this audit lives. Only the two blueprint fixtures exist; `repo-review`/`repo-ops`/`agentic-ux` appear in no fixture/checker/gate. *Dims 4·8·9 · major · M.* **Before/after:** add `fixtures/seeded-smell-repo/` + `check-repo-review.py` (assert the produced backlog cites each planted smell, catch-rate shape like the other three plugins), wired into CI beside the blueprint baselines. *(Held P0 through adversarial — anchors the headline doctrine; the audited skill is itself the gap.)*
2. **`gen-index.py` — the generator that caused the 5-day R-1 outage — has `--check` but no selftest** (`gen-index.py:262-266`; sibling `check-ci-paths.py` ships one, born from the same postmortem). The repo's own rule (PLAN.md:83 "new gates prove themselves") is violated by its highest-stakes generator. *Dims 4·6·8 · major · S–M.* **Before/after:** `gen-index.py selftest` — a fixture marketplace asserting (a) a stale committed `index.html` is rejected and (b) an untracked file does NOT leak into the render (the exact R-1 mechanism). *(Promoted P1→P0 in adversarial: "the only Sev-1 in repo history, still unguarded, outranks a forward-looking gap.")*
3. **Eval-ceremony ROI is inverted** — 979 LOC of calibration Python across 9 forked `check*.py` + `check-recall.py` (a meta-checker testing the checkers' own regex recall), while three shipped skills (P0-1) have none. Over-investment beside under-investment. The checkers self-describe as non-deterministic ("a catch-rate, not a CI gate") yet all run in CI. *Dims 9·8·6 · major · M (a rebalancing, not a deletion).* **Before/after:** freeze further calibration-depth (defer the PLAN "Next" sub-council shapes), redirect to P0-1, and collapse the 9 forked checkers → one parameterized `score_transcript(PLANTED, text)`. *Recorded baselines stay; the refactor is shape-only.* *(Sharpened in adversarial from a lazy "too much eval" to the defensible "marginal over-investment + meta-harness tax, beside the P0-1 gap.")*

### P1
1. **`check-sourcing.py` forked 246 vs 98 lines** under the zero-cross-plugin-dependency rule — silent drift risk in a *provenance* gate, unlike the corpus-reader which IS sync-gated. *Dims 3·7·6 · major · M.* Fix: extract+sync-gate the shared core, or declare the forks permanently independent with a why-comment. *(Closest P0/P1 call — demoted because the drift is latent, both pass today.)*
2. **The "untrusted DATA" trust-boundary guard is hand-duplicated across 95 files with no presence check.** Correct by design (critics run isolated) but enforced by author discipline; a new critic without the block is a silent security regression. *Dims 7·6·3 · major · M.* Fix: a `check-trust-boundary.py` asserting every `agents/critic-*.md` + evaluator skill carries a sentinel phrase.
3. **CI readability threshold crossed:** a 495-char inline `python3 -c` assertion (`ci.yml:65`, the bake-safety XSS check) in a 155-line, 34-step YAML. Unreviewable in a diff, untestable in isolation — the P0-2 anti-pattern in YAML form, tied to R-1's "unnoticed because unwatched/unreadable" root cause. *Dims 6·4 · major · S–M.* Fix: extract the inline blocks into named, selftested `bin/check-*.py` gates.

### P2
1. **I-8: critic provenance lives only in 4 gitignored `.name-map.md` files (721 lines)** — a documented single-point-of-loss that full-mode `check-sourcing` depends on. Ranked P2 (repo tracks it P3) because losing the working tree destroys the attributions. *S.*
2. **9 forked `check*.py` checkers are ~70% structurally identical** — the clean mechanical-dedup half of P0-3 (one parameterized checker). *M.*
3. SKILL frontmatter block-scalar style inconsistent (`>` vs `>-`) across plugins. *S.*
4. Per-plugin scale asymmetry large + undocumented (product-forge 217 md / 24 agents vs brand-forge 63 / 16) — add an intended-scale line to each ROADMAP. *S.*
5. `check-recall.py` is a standing maintenance tax for one-time value (31 gaps caught once, now gates 9 checkers' recall forever) — bound it by folding into P2-2's single checker. *M.*
6. agent-ops ships a `repo-memory` MCP but no vendored corpus-reader — likely intentional (its retrieval is the MCP), but an undocumented asymmetry; confirm with one CLAUDE.md line. *S.*

### P3 (uncapped quick fixes)
- ~~P3-1 `.DS_Store` committed~~ — **struck (false positive; see verification note — none tracked).**
- P3-2 doc snapshot dates lag a day (`docs/*.md` say 2026-06-10; repo at 06-11). *S.*
- P3-3 PLAN.md "Next" lists corpus-reader items ISSUES.md marks resolved (I-1) — reconcile. *S.*
- P3-4 `agent-ops` umbrella skill pinned `version: 0.1.0` while plugin is 0.1.9 — confirm per-skill versioning intent. *S.*
- P3-5 CLAUDE.md opens with `plugins-forge` then corrects to claude-plugins — lead with the repo name. *S.*

## (c) Tier-1 patterns — the preservation contract

1. **Gated vendoring of the corpus-reader** (`sync-corpus-reader.py:19-40` + `ci.yml:49`) — duplication that *cannot* drift: byte-identical copies, sha256 over behavior-bearing source, per-consumer state excluded. The repo's answer to "zero cross-plugin deps vs. one source of truth," without a build system. The pattern P1-1 should adopt.
2. **Self-documenting gates that cite the red-team finding they exist for** (`validate_plugin.py:1-52` + every `check-*.py` docstring) — turns a gate into a readable threat model; the only record of *why* each check is load-bearing.
3. **"Structure is mechanized; taste is not"** (CLAUDE.md → `bin/brand-lint` SMELLS ↔ `skills/brand-methodology/`) — the central thesis, drawn correctly almost everywhere; P0-3 is its one miscalibration (mechanizing taste's *measurement instruments*).
4. **New gates ship with a failing fixture; postmortems become gates** (PLAN.md:83 → `check-ci-paths.py` + R-1/I-6) — the learning loop that makes "every claim is gated" more than a slogan. P0-2 is its one exception, which is why that exception is a P0.
5. **The duplicated trust-boundary guard in every isolated critic** (95 files) — looks like a DRY violation, is the correct design for isolated parallel critics; the catalog's core safety property (and P1-2 proposes mechanizing its presence).

## Rubric validation (directional → recorded)

**Discriminated cleanly:** **Gate Integrity (4)** was the most discriminating dimension and the one *added* for this repo-type — it separated genuine strength (clean-checkout doctrine, sync-gating, postmortem→gate loop) from genuine weakness (`gen-index.py` unguarded; agent-ops surfaces ungated); both P0-1 and P0-2 fell out of it. On the *default* rubric this disciplined repo scores a flat ~4.5; this dimension found the 3/5 reality — the strongest evidence the repo-type fork worked. **Mechanization ROI (9)** caught the over-investment the brief asked about (P0-3); the default rubric has no "you mechanized too much" lens. **Public Surface Discipline (5)** discriminated *positively* — a confident 5/5 with no findings (told me where NOT to spend the backlog). **Provenance (7)** found edge items (P1-2, P2-1) the default's "Public Surface" lens would miss.

**Non-discriminating / near-inapplicable here:** API Symmetry (1) and Naming (2) scored 4/5 but produced only P2/P3 — the 5-primitive model is so uniform these lenses confirmed health rather than separated strong from weak (useful as negative space). The three dropped UI dimensions were correctly dropped — forcing them would have produced N/A noise; the SKILL's `repo-type-adaptations.md` fork instruction is load-bearing and it worked.

**Honest assessment of the method.** The rubric, applied for real, produced a **defensible ranking**, and the forcing functions did real work: the cascade caps forced a true close call (P0-2 vs P1-1, active-vs-latent risk), and the adversarial pass earned its keep — it **promoted gen-index P1→P0** on an argument a single synthesis pass wouldn't reach, and **sharpened** the eval-ROI finding into something defensible. Both are the findings I'm most confident in, and both came *out of the adversarial wave* — direct evidence for First Principle 4 ("adversarial review beats more authors").

**Gaps the method revealed in itself:**
1. **No native "doctrine-coverage gap" dimension.** The most important finding (P0-1 — a stated doctrine that lapses on one surface) emerged only because I forked in Gate Integrity *and* cross-referenced the README's "every claim is gated" claim. A team using the default rubric verbatim would likely **miss P0-1**. The method should arguably promote "discover the repo's central *claim* and audit the claim↔coverage gap" to a first-class step.
2. **Single-agent collapse understates a risk.** Running Discover→Audit→Synthesize→Adversarial in one context means the adversarial pass shared memory with the synthesis — the skill itself warns "same context = same answer." A faithful high-stakes run needs the consultant dispatched as a *fresh* agent; this proxy simulated the stance but cannot claim true isolation. The method is right to flag this as non-negotiable.
3. **Eval Posture (8) vs Mechanization ROI (9) blurred** — three findings span both; the two dimensions may want merging into one "Verification Economy" lens for repos like this.

**Net:** the directional rubric, forked per its own instructions, produced a ranking I'd stand behind in front of the engineer — and the two moves I'm proudest of came from the parts of the method (the repo-type fork + the adversarial pass) that are *most* tempting to skip. The ceremony that looked optional is exactly where the value was — the strongest possible validation of the method.
