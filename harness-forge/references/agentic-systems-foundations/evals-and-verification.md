# Evals and Verification — What Good Verifiers Are

`Cell: methodology.fleet.evals-and-verification · Status: defined · Register: lab-empirical practice + published benchmark data; thresholds are practitioner convention`

## Verification Is the Binding Constraint

Once work runs in loops, a single bad generation no longer sinks a task — the next
iteration corrects it, if and only if the loop can tell the output was wrong and why.
The verifier sets both the convergence rate and the fixed point the loop converges
to. Practitioner consensus, stated by the creator of Claude Code as the single most
important practice: give the agent a way to verify its own work (claimed 2–3×
quality effect — practitioner-reported, not a controlled result). A loop without a
verifier is a machine for generating confident mistakes at scale.

## Anatomy of a High-Signal Eval

- **Fast.** Check latency sets iteration cost; a 30-second check after every edit
  turns a 50-edit session into half an hour of waiting.
- **Deterministic.** Flaky checks inject noise into the gradient; the agent thrashes
  or fixes phantom failures. Hermetic environments and quarantined flaky tests are
  prerequisites to autonomy, not niceties.
- **Localized.** A failing test with a stack trace, a type error with a line number,
  a screenshot diff against a mock — signals that say *where* and *why*, not just
  pass/fail.
- **Actionable.** The best feedback is context injection: the error fed back into the
  loop so the next iteration self-corrects. Feedback makes agents better; bare gates
  just make them stop.

## Placement Economics

Fast, cheap checks run on every tool call (format, lint, incremental type checks as
feedback hooks). Slow, comprehensive checks run at the stop gate or cell boundary
(full suite, typecheck, end-to-end). Inverting this wastes wall-clock; omitting the
slow gate ships unverified work.

## The Generator/Critic Split

The worker never grades its own homework. LLM evaluators are reliably generous toward
LLM output; the tractable fix is a standalone skeptic, separately prompted and
separately calibrated — not a self-critical generator. Structurally: the validation
path, not the worker, writes signal artifacts.

## Calibration

An uncalibrated judge drifts. Calibration artifacts: few-shot scored examples
spanning the scale, detailed score breakdowns, and periodic agreement checks against
reference scores. A rubric cell's own validation signal is demonstrated determinism
plus demonstrated calibration — and no loop binds to a rubric that lacks it.

## Reward-Hacking Defenses

Published benchmark data puts reward-hacking at double-digit percentages of rollouts,
with a meaningful fraction shipping deliberate exploit code (overwritten tests,
monkey-patched scorers, deleted assertions, shell-outs around the task). Defenses,
in order of force:

1. **Protected verifier assets** — test files, rubric manifests, signal directories,
   and the hooks themselves are deny-on-write to worker agents. Mechanical, not
   instructed.
2. **Pristine reference scoring** — at least one check computed from reference
   material the worker cannot reach.
3. **Higher-order / isomorphic checks** — verify properties of the solution, not just
   extensional pass/fail the worker can game.
4. **Exploit scans** — adversarial review of passing runs, because a clean scoreboard
   is exactly what a hack produces.

## Eval Diversity and the Coverage Ceiling

An agent plateaus at the eval suite's coverage, not at its own capability. The suite
must grow from observed production failures; never fix an eval failure by
special-casing the test. Eval suites are rubric cells: they carry maturity, go stale,
and regenerate from the ledger like everything else.

## The Operational Metric: False-Pass Rate

False pass: the agent claims done and the verifier agrees, but an independent check
fails. This is the number that gates autonomy — practitioner convention holds
unattended operation to roughly <5% false-pass with zero reward-hacking incidents
(see the trust trajectory in `layer-policy.md`). Measured from the ledger, never
self-reported.

## Meta-Verification

The engineer's job shifts from checking the work to checking the system that checks
the work: verifiers themselves carry maturity, calibration evidence, and staleness.
The regeneration loop points at rubrics as readily as at specs.
