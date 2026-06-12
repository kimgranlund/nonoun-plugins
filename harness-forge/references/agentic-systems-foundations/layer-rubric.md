# Rubric Layer — How Well Does It Score

`Cell: ontology.fleet.layer-rubric · Status: defined · Register: established (measurement, eval practice); maturity-precondition rule is synthesis`

## Rubric Layer Definition

A rubric is evaluative knowledge: criteria, scales, and weights for scoring a unit of
work against its specification. The rubric is the verifier's knowledge component —
the loop's sensor. In closed-loop terms, the rubric determines both the convergence
rate of a loop and the fixed point it converges to. Feedback-signal quality, not
prompt quality, is the binding constraint of agentic work; the rubric layer is where
that constraint is engineered.

## Gate Checks vs Review Checks

Every rubric dimension is one of two kinds:

- **`[gate]`** — mechanically checkable: tests pass, types check, links resolve,
  schema validates, screenshot diff under threshold. Deterministic, fast, scriptable.
- **`[review]`** — requires calibrated judgment: design quality, prose clarity,
  appropriateness. Performed by a separate evaluator (model or human) armed with
  few-shot scored exemplars.

A rubric composed only of `[review]` dimensions is too slow and too soft to drive an
autonomous loop. A rubric composed only of `[gate]` dimensions ceilings quality at
what is mechanizable. Production rubrics carry both, with `[gate]` checks placed on
the fast path and `[review]` at cell boundaries.

## Rubric Calibration

An evaluator without calibration drifts generous — LLM judges reliably over-rate
LLM-generated output. Calibration artifacts: few-shot scored examples spanning the
scale, detailed score breakdowns, and at least one higher-order or isomorphic check
computed from pristine reference material the worker cannot touch. The
generator/critic split is the lever: a standalone skeptic is tractable to tune; a
self-critical generator is not.

## Rubric Maturity Precondition

A rubric cell must itself be `validated` before any loop binds to it. The signal for
a rubric is demonstrated determinism (no flakiness across repeated runs on fixed
input) and demonstrated calibration (agreement with reference scores on the few-shot
set). Rule: **a cell advances only against a validated rubric.** A flaky verifier
poisons the loop's gradient; under this rule, flakiness is a maturity violation the
gate catches before the loop runs.

## Rubric vs Spec Boundary

The spec defines done; the rubric measures how well. The rubric binds to the spec and
is meaningless without it.

## Rubric vs Policy Boundary

A rubric scores (graded, advisory within its band); a policy gates (binary, enforced).
Conflating them yields rubrics with unaudited veto power or policies that get
"weighed" instead of obeyed.

## Rubric Artifact Forms

Rubric manifests (JSON: dimensions, kinds, weights, thresholds, calibration refs);
test suites and eval harnesses; screenshot-diff configurations; LLM-judge prompts with
scored exemplars; weighted scorecards.

## Rubric Failure Modes

Evaluator drift and generosity bias (uncalibrated judges). Flaky checks (noise in the
feedback signal; agents thrash or fix phantom failures). Coverage ceiling (the agent
plateaus at the eval suite's coverage, not its own capability — rubrics must
regenerate from observed production failures). Reward-hackable rubrics (scoring from
files the worker can edit). Score inflation across iterations (no pristine reference).
Vibes scoring (no spec upstream).
