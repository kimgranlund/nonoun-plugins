---
date: 2026-06-12
status: draft
version: "0.2.0"
---

# Rubric — Looping Agentic Harness

Scores a looping, latticed agentic harness against the model in `agentic-systems-foundations/`. Seven dimensions, each `[gate]` (mechanically checkable, can cap the score) or `[review]` (calibrated judgment). The disqualifying tell across the whole rubric: **structure without earned signal** — an elegant lattice whose loops cannot evidence a verifier track record from the ledger has not earned what it claims. Two `[gate]` dimensions are hard caps: a reward-hackable verifier surface (H3) and an autonomy tier claimed beyond its measured precondition (H6).

Read each score with evidence cited from the artifacts (`.harness/lattice.json`, the ledger, `signals/`, the gate scripts) and the `bin/` tools as the mechanical checks.

---

## H1 — Lattice integrity `[gate]`

Is the lattice a sound dependency graph — partial order respected, provenance early, nothing stale-but-trusted?

| Score | Evidence |
| --- | --- |
| **5** | `bin/lattice.py validity` is clean across all cells: no rubric advanced before its spec validates, no cell bound to an unvalidated verifier. The ledger schema was present in the first slice. No `stale` cell is trusted as fresh; no cell has frozen while its environment moved. |
| **3** | Mostly sound, but one rubric/spec ordering is implicit (not enforced) or the ledger schema arrived after the first slice. |
| **1** | Rubrics scored against absent specs; provenance retrofitted (or absent); stale cells consumed as if fresh. The lattice is a grid of `defined` claims, not validated assets. |

**Check**: `lattice.py validity` over cells + scan for `stale`. **Cap**: a rubric-before-validated-spec or a verified-against-nothing cell caps H1 ≤ 2.

---

## H2 — Verifier maturity `[gate]`

Does every loop bind to a `validated` rubric that has demonstrated determinism and calibration?

| Score | Evidence |
| --- | --- |
| **5** | Every advancing cell's verifier is a `validated` rubric: no flakiness across repeated runs on fixed input, and agreement with reference scores on a few-shot calibration set. Gates on the fast path, reviews at boundaries. |
| **3** | Verifiers exist and mostly validate, but at least one is uncalibrated (drifts generous) or one loop binds to a `defined` rubric. |
| **1** | Loops run against flaky or uncalibrated verifiers — noise in the gradient; the agent thrashes or fixes phantom failures. A loop without a real verifier is generating confident mistakes at scale. |

**Check**: rubric cells' validation signals; "a cell advances only against a validated rubric." **Cap**: a loop bound to an unvalidated verifier caps H2 ≤ 2.

---

## H3 — Anti-reward-hacking `[gate]` (caps the rubric)

Are verifier assets mechanically protected, and is at least one check beyond the worker's reach?

| Score | Evidence |
| --- | --- |
| **5** | Signal directories, rubric files, eval suites, schemas, and the hooks themselves are **deny-on-write to workers** (`bin/gate-signal`, demonstrated by a blocked probe). Signals are written only by the validation path. ≥1 check is computed from pristine reference the worker cannot reach. Passing runs are exploit-scanned. |
| **3** | Protections declared (frontmatter, prose) but not all mechanically enforced; reference scoring present but the worker can technically reach it. |
| **1** | The worker can write its own signals/rubrics/tests. Reward hacking (overwritten tests, monkey-patched scorers, deleted assertions) is unprevented — and a clean scoreboard is exactly what a hack produces. |

**Check**: `bin/wire.py check` exits 0 — the gate is **wired** as a PreToolUse deny in the project's loop config, not merely present in `bin/` (a gate present-but-unwired is a false pass, the exact surface this dimension exists to catch); the signal was minted by `validate.py` from an external command's exit status, not hand-asserted by the worker; the worker carries no `Bash` (which routes around a path glob); reference-scoring present. **Cap**: a worker-writable or unwired verifier path caps the whole rubric ≤ 2.

---

## H4 — Naming discipline `[gate]`

Does every named artifact parse the typed grammar — no plural, casing, or vocab drift?

| Score | Evidence |
| --- | --- |
| **5** | Every created path passes `bin/naming.py`: layer dirs mirror the enum byte-for-byte (`spec/`, never `specs/`), agents are `{object}-{actor}.md`, hooks are `{gateverb}-{invariant}`, cell IDs are `{layer}.{scope}.{slug}` with state excluded from identity. The naming schema ships in `.harness/`. |
| **3** | Mostly conformant; a few names drift (a plural dir, an off-vocab actor) and are caught only by review, not the gate. |
| **1** | Ad-hoc names; directories and enums diverged; identity carries state (renamed on transition — a drift generator). |

**Check**: `naming.py check` over created artifacts; the write-time gate present.

---

## H5 — Budgets & stop conditions `[review]`

Does every loop carry caps, a no-progress detector, and a *separate* done-judge?

| Score | Evidence |
| --- | --- |
| **5** | Each loop has an iteration cap, a token/dollar budget, a wall-clock limit, and a no-progress detector (same failure signature N times → halt and surface). The worker does **not** declare its own completion — a separate done-judge does. Exhaustion flips `blocked` and surfaces to the compass. |
| **3** | Budgets present but one primitive missing (no wall-clock, or the worker self-declares done). |
| **1** | Uncapped loops — the canonical overnight token-burn liability; the worker grades its own completion. |

**Check**: cell `budget` fields; `ledger.py no-progress` is consulted (the detector is code — a loop that ignores it is self-policing); the done-judge is a distinct path from the worker. **Note the wiring honesty**: the detector exists, but the *automatic* halt Stop-hook is ROADMAP — a harness claiming "budgets enforced mechanically" without a wired stop-gate is overclaiming exactly as an unwired `gate-signal` would.

---

## H6 — Autonomy tier `[review]` `[hypothesis]` (caps if unearned)

Does the operating/claimed autonomy tier match the measured precondition from the ledger?

| Score | Evidence |
| --- | --- |
| **5** | The tier is earned: `bin/ledger.py false-pass` shows < ~5% with zero reward-hacking incidents for any unattended family; a hermetic sandbox and tamper-evident audit trail for scheduled runs. Demotion is automatic on an incident. Autonomy is granted by measurement, not declaration. |
| **3** | The tier is plausible but the false-pass evidence is thin (small N) or the demotion mechanism is manual. |
| **1** | Unattended autonomy claimed with no measured false-pass rate, or a known reward-hacking incident un-demoted. The claim is enthusiasm, not evidence. |

**Check**: `ledger.py false-pass` vs. the trust trajectory in `layer-policy.md`. **Cap**: a tier claimed beyond its measured precondition caps H6 ≤ 2.

---

## H7 — Regeneration `[review]`

Does the loop close — operating cells emit ledger entries, entries distill into patterns, revisions are ledgered not silent?

| Score | Evidence |
| --- | --- |
| **5** | Operating cells emit ledger entries with rationale; distilled windows become patterns (with provenance) and upstream-revision proposals; every revision is a deliberate, ledgered `regenerating` transition. Staleness propagates as a graph computation. The ledger is read, not just stored. |
| **3** | The loop runs but the ledger feeds back only partially (telemetry collected, never routed into selection/trust/regeneration). |
| **1** | A frozen lattice: cells never regenerate, the ledger is write-only storage, patterns are authored-not-distilled hypotheses. Drift wearing the costume of documentation. |

**Check**: ledger coverage; pattern provenance; `regenerating` transitions are ledgered.

---

## Output contract

A per-dimension scorecard (`H{n} [gate|review] {name} · 1–5 · evidence · finding`), a summary table, the **weakest dimension** named, the **earned autonomy tier** with its measured precondition stated, and the top remediations by severity. `[gate]` caps (H3 reward-hacking, H6 unearned autonomy) are called out explicitly when they fire — a harness can be a 5 on structure and still be unfit for unattended operation.
