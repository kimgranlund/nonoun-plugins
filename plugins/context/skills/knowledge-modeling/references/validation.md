# Validation, inference and representations

Use to audit an existing model or make an operational contract from one. Name the
claim each check establishes and exercise the consumer that relies on it.

## Separate the checks

| Check | Can establish | Does not establish by itself |
| --- | --- | --- |
| Syntax/shape | Data conforms to the implemented format constraints | Correct interpretation, complete evidence or accepted mappings |
| Reference integrity | IDs, revisions and links resolve within the declared scope | Truth or authority of the referenced content |
| Semantic constraints | Specified cross-record/context rules hold | Adequacy of the rules for all real-world cases |
| Logical reasoning | Conclusions follow under the selected formal semantics | Completeness of supplied data or runtime authorization |
| Competency/consumer cases | The bounded decisions work for the tested evidence | General accuracy or independent human validation |
| Runtime enforcement | The tested integration mediates particular actions | Universal isolation from descriptive metadata alone |

Choose existing validation tools supported by the project. Do not build a general
JSON Schema interpreter or reasoner to validate a small local profile. A custom
check should state its supported input, assumptions, failure behavior and limits.

## Manifest versus schema

A manifest is usually an instance of a schema. A `$schema` URI declaring a JSON
Schema dialect does not make arbitrary metadata keys into assertion keywords.
Nested parameter schemas under an application-specific `actions` field must be
selected and applied by the application; they are not automatically traversed by
a standard schema validator.

When authoring a validating schema, use the actual schema vocabulary, declare its
dialect, and test valid plus malformed instances. When consuming a manifest, check
both the manifest shape and an actual action's parameters. Treat unknown-keyword
warnings or strict compilation errors as evidence of a contract mismatch, not a
reason to disable checking until everything passes. Some implementations allow
unknown keywords as annotations; that does not enforce their alleged rules.

## Inference and completeness

OWL uses an open-world interpretation; a missing assertion can remain unknown.
SHACL validates a chosen data graph against shapes. State the entailment regime
or preprocessing, if any, since inferred facts can change validation outcomes.
Do not infer missingness, closed-world negation or an enforcement decision from an
ontology axiom without a specified consumer semantics.

## Projections and generated code

Keep the conceptual model, serialization and generated views distinguishable.
Identify the authored authority and declared generator inputs. When exporting to
another format, test preservation of required meaning and report unsupported
constructs. A successful conversion is not proof of a lossless semantic round trip.

LinkML may fit multi-format generation; JSON Schema, SQL or ordinary documents may
already meet the task. Choose tooling from requirements and existing conventions.
Do not introduce a mandatory stack into every knowledge-modeling task.

## Audit output

For each finding give the affected decision, governing source, concrete counterexample,
observed behavior or clearly marked untested hypothesis, and the earliest useful
repair. Include a valid neighbor so blanket rejection cannot count as a fix.
State whether a finding comes from source inspection or an observed consumer result.
Read [evaluation](evaluation.md) only when designing a benchmark, fresh-agent trial
or comparative evaluation, not to complete an ordinary audit.

## Basis

[JSON Schema Core 2020-12](https://json-schema.org/draft/2020-12/json-schema-core),
[OWL 2 Primer](https://www.w3.org/TR/owl2-primer/),
[SHACL](https://www.w3.org/TR/shacl/), and
[LinkML overview](https://linkml.io/linkml/intro/overview.html) describe different
contracts. [OPA](https://www.openpolicyagent.org/docs) explicitly separates policy
decision-making from enforcement. Consult the supported version before implementing
a tool-specific integration; these references are not dependency pins.
