# Decision models

Load this when you write or review an adapter for a runtime, or decide which runtime answers a question set. The contract is in [model.md](model.md); request and response fields belong to the vendor's own skill.

## What counts as a decision model

A model that returns typed answers with probabilities rather than prose:

- a purpose-built decision model (TypeSafe's Jev is the worked example below);
- a general LLM read through log probabilities over a closed set of answer tokens;
- a local classifier with calibrated scores.

Prose answers parsed afterwards are not a decision model: they carry no probabilities, so bands, margins and calibration cannot be measured.

## Writing an adapter

1. Implement `ask(state, questions) → {answers, model_version}` for the runtime, and the target face (one case input on stdin, one answer on stdout) so `evaluation-system` can run it. Copy the structure of `adapters/fixture.py`; replace replay with the runtime call.
2. Map each Question to the runtime's request: instructions, then option or level descriptions in the given order, with `excludes` statements next to their option. Send state as data, never as instructions.
3. Map the response to Answers: `value`, `probabilities` over every option, level or yes and no, `confidence` for choices and scores, and the `model_version` the runtime reports.
4. Refuse when the reported version differs from the set's `model`. Key any cache by request hash plus model version.
5. Record real answers for a sample of states and replay them with the fixture adapter in tests, so CI never calls the runtime.

## Worked example: Jev

Jev answers several typed questions about one state in one request: Choices with option descriptions, Scores with level descriptions, and Propositions returning a probability of truth. That maps onto the spine directly: one request per state with the set's questions, one Answer per question.

- Request and response fields, SDK usage, limits and pricing: hand off to TypeSafe's `typesafe-ai` skill. This skill never restates them.
- Questions in one request are answered in isolation; the evidence base found no benefit from asking related facets together, and joint labels still need an `assemble` validator.
- Pin the exact version string Jev reports (`jev-1.14.0` in the evidence base), never an alias.

## Worked example: an LLM through log probabilities

Present the options with single-token keys, ask for one key, and read the log probabilities of the keys. Normalize over the keys to get `probabilities`; the top key's share is `confidence`. For a proposition, read the yes and no tokens. Option order and key choice move these numbers, which is why every choice suite carries invariance cases. Version pinning matters more here, because hosted aliases move silently.

## Worked example: a local classifier

A classifier with one output per option is a Choice with fixed options. The adapter maps outputs to option keys; `confidence` is the top output after calibration. Its option set is fixed at training time, so a KOS change means retraining, out of this skill's scope.
