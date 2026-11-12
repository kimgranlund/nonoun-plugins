# Concept or relation record

Use the project's format when one exists. This is a checklist for missing meaning,
not a mandatory serialization or a new global registry.

## Concept

- **ID and identity scope:** Namespace and version resolution.
- **Label and definition:** What does it denote?
- **Aliases:** Source/language/context where each label has this meaning.
- **Examples and counterexamples:** Distinguish nearby concepts.
- **Kind and classification:** Concept, class, instance, collection or other local kind.
- **Evidence and lifecycle:** Governing source, owner and replacement/deprecation if any.

## Relation

- **Predicate and definition:** Meaning and direction.
- **Endpoints:** Supported subject/object kinds.
- **Context:** Configuration/time/scope that affects the assertion.
- **Permitted inference:** Inverse, transitivity, cardinality or type implications
  only where explicitly defined.
- **Positive and misleading examples:** Show what consumers may and may not conclude.
- **Executable checks:** Existing validator/query/policy and its limits, if applicable.
