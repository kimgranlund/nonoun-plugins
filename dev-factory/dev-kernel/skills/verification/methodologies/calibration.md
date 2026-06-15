# Calibration — making a rubric a verifier instead of a vibe

`Cell: methodology.system.calibration · Status: defined · Register: established lineage (LLM-as-judge calibration, inter-rater agreement / Cohen's κ, metamorphic & property-based testing, frontier-lab reward-model evaluation); the rubric-maturity-precondition framing is house`

## Why this cell exists

A rubric is just JSON until it is calibrated. The factory's whole legitimacy rests on the validation path minting an honest signal — and a signal is only as honest as the rubric the critic ran. An uncalibrated judge does not fail loudly; it drifts *generous*, especially toward model-authored work that pattern-matches its own training. That is the quiet failure: a rubric that passes everything looks like a working verifier and is actually a rubber stamp. Calibration is how a rubric earns the right to reach `validated` and gate other cells.

## The maturity precondition

A rubric cell cannot gate anything until it is itself `validated`. "Validated" for a rubric means two demonstrated properties, not asserted ones:

1. **Deterministic on fixed input** — gate dimensions score identically across repeated runs; review dimensions score within a tight band. Shown by *running it repeatedly*, never by claiming it.
2. **Calibrated against an exemplar set** — its review thresholds reproduce reference scores on a held set within an agreement threshold.

Until both hold, no spec, pattern, or slice may bind to it. The verifier of verifiers is verified (`rubric/rubric-quality.rubric.json`).

## Building the exemplar set

The exemplar set is the calibration ground truth: a small corpus of artifacts of the kind this rubric grades, each carrying a **reference score** assigned by a trusted source (a human, a panel, or a higher-tier critic) and supplied **read-only** — a pristine reference the authoring agent cannot reach or edit.

Construct it to **span the scale and include the adversarial near-misses**, not just clear passes and clear fails:

- A **clear pass** — exercises every dimension at strength.
- A **clear fail** — violates a gate outright.
- **Boundary cases** straddling each review threshold — where calibration is actually tested.
- **Adversarial near-misses** — artifacts engineered to *pass the extensional check while violating intent*: the reachable-reference exploit, the green-tests-wrong-property case, the prose-criterion-dressed-as-checkable case. A rubric that scores these as passes is reward-hackable, and the near-miss is where you find that out before production does.

The near-miss exemplars double as the seed for `policy/exploit-scan.policy.json` — each is a known way to produce a clean board without doing the work.

## The generator/critic split (and its model dimension)

Calibration only means something under the split that the safety model already requires: **the thing being graded and the thing grading it are not the same agent, and ideally not the same model.**

- **The split is structural.** The generator (the worker, or here the rubric-architect) produces the artifact; the critic scores it; the validation path writes the signal. The generator never writes its own signal — `gate-signal` makes that mechanical, not a matter of discipline.
- **The critic's model is an INDEPENDENT choice** (`execution-strategy.md`). This is the dimension teams forget: the split has a *model* axis, not just a prompt axis. The critic is separately selected — often a different tier from the generator — and separately calibrated. A model grading its own output shares its own blind spots; "the model said it's good" is not a signal when the same model wrote it. Record which critic model a rubric was calibrated with, and **re-calibrate when either the generator or the critic model changes** — a model swap silently invalidates the agreement measurement.

## The calibration loop (auto-research hill-climb)

```
  score exemplars ──▶ measure agreement vs. reference ──▶ improve weakest-agreeing dim ──▶ re-score
        ▲                                                                                     │
        └──────────────────── until agreement clears threshold AND scoring is deterministic ──┘
```

1. **Score** every exemplar with the candidate rubric, run by the chosen critic model.
2. **Measure agreement** between the rubric's scores and the held reference scores (per-dimension; an inter-rater agreement statistic for the review dims, exact-match for the gates). Agreement against a pristine reference the author cannot edit — not the author's own re-read.
3. **Improve the weakest-agreeing dimension** — the one whose scores diverge most from reference. Sharpen its check language, split an overloaded dimension, or add a pristine/higher-order component. Raise quality-per-iteration (clearer rubric language, a stronger critic model) before adding iterations.
4. **Re-score and repeat** until agreement clears threshold on every dimension *and* the rubric scores deterministically on fixed input. Stop condition: both met, within budget. On no-progress (the same dimension stays divergent across N passes), that is `ledger.py no-progress` territory — block and escalate, do not burn the budget hill-climbing a rubric whose problem is structural.

## Where computation routes to code

Calibration is judgment around code, never code replaced by judgment:

- **Determinism** is *demonstrated* by repeated runs, not asserted.
- **Agreement** is *measured* against the pristine reference, not eyeballed.
- **Production trustworthiness** is `ledger.py false_pass_rate`, which returns **`unmeasured`** until an independent refuter has actually disagreed with the critic at least once — a 0.0% with no refuter is a lie that would auto-promote a never-checked verifier. A calibrated-but-unrefuted rubric is honestly `unmeasured`, never "proven safe."
- **No-progress** in the calibration loop is `ledger.py no-progress`, the in-code failure-loop detector — not the agent's count of how many times it tried.

## Calibration failure modes

Calibrating against the author's own re-read instead of a pristine reference (the generous drift, unmeasured). A single critic model grading work the same model produced (the split collapsed). An exemplar set of only clear passes and clear fails (the boundary and the near-miss, where calibration is actually tested, are missing). Asserting determinism instead of running the rubric repeatedly. Treating a calibrated-but-unrefuted rubric as proven safe (it is `unmeasured`). Failing to re-calibrate after a model swap (the agreement measurement silently went stale).
