# Jev / System One design notes

Primary-source review: 2026-10-08. This note informs synthetic interaction examples; it is not an integration guide or a performance endorsement. Recheck the current documentation before implementing a real model call, confidence calculation or gating policy.

## Verified model boundary

TypeSafe describes Jev as a decision model that evaluates supplied state against typed questions. Its outputs include Choice, Score and Noul; it does not generate the prose of plans or summaries. [Official introduction](https://docs.typesafe.ai/introduction).

A Choice selects from predefined options and exposes their probabilities. [Choice](https://docs.typesafe.ai/primitives/choice). A Score evaluates ordered rubric levels and can occupy a fractional position between them. [Score](https://docs.typesafe.ai/primitives/score). Noul returns a yes-probability rather than an additional confidence field. [Noul](https://docs.typesafe.ai/primitives/noul).

For Choice and Score, the reported confidence is calculated from the answer distribution. Its interpretation is different from an individual option probability or an empirical task-success rate. Thresholds require evaluation for the intended decision and consequences. [Confidence](https://docs.typesafe.ai/confidence).

## Design inference, not a vendor requirement

Use a bounded judgment where an agent workflow needs to route, score or detect something. Keep the input snapshot, question, model result, application policy, human authority and executed action distinguishable. Plans, source retrieval, summaries and tool execution need surrounding components; these demos do not attribute them to Jev alone.

The user can inspect an exception or change policy without approving every routine classification. A high-confidence answer still cannot grant spending, publication or access rights. An ambiguous answer can lead to gathering evidence, a different model, a revised question or human judgment. Choose the route based on the task, not a universal confidence threshold.

A “reasoning log” can expose the question, source references, observed steps, assumptions and concise decision rationale. It should not imply that a non-generative model returned a hidden prose explanation.

## What the synthetic examples add

| Scenario | Decision primitive | Human-facing consequence |
| --- | --- | --- |
| Observatory | Choice among the next evidence-review routes | Inspect the split distribution and decide whether targeted research is worth doing |
| Switchyard | Noul on whether a draft implies guaranteed arrival | Hold an unsupported promise for revision; approval and fresh evidence remain required |
| Atelier | Score for how explicitly a concept supports comparison | Inspect an ordered rubric while keeping taste, accessibility and factual support separate |

All distributions and input states are invented. The examples use the published confidence calculations for transparent illustration, not live API responses. Choice uses probabilities 0.52 / 0.33 / 0.15 and shows confidence 0.28. Score uses 0.05 / 0.25 / 0.70 across levels 0 / 1 / 2, producing score 1.65 and confidence 0.48 after rounding. Noul shows a yes-probability of 0.94 with no separate confidence. No calibration, accuracy, cost or latency has been measured.

Operational readiness counts and evidence-support rubrics remain separate indicators. Neither is relabeled as model confidence. Illustrative routing thresholds are proposed policy, not deployment recommendations.
