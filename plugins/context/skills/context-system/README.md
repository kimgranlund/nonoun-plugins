# Context system skill: maintenance

For using the skill, start at [SKILL.md](SKILL.md). This file is for people changing it.

Contents: [Layout](#layout) · [Tests](#tests) · [History](#history)

## Layout

| Path | Holds |
|---|---|
| `SKILL.md` | Entry: route table, layers, invariants, tools |
| `references/<layer>/guide.md` | One guide per layer (vocabulary, modeling, routing, review, statements); the layer's modules sit beside it |
| `references/manifests.md`, `references/routing/entry-files.md` | Manifests, registries, modes; entry-file structure |
| `scripts/`, `tests/`, `fixtures/` | Validators and linters, their tests and fixtures |
| `templates/`, `examples/`, `schemas/` | Starting points, worked examples, the optional routing JSON schemas |
| `evals/trigger-activation.suite.yaml` | Trigger cases in evaluation-system format |

## Tests

From this directory: `python3 -B -m unittest discover -s tests`. `validate_kos.py` and `lint_cnl.py` need PyYAML; the routing and registry tools use the standard library only and never execute corpus code or use the network.

## History

Merged on 2026-11-12 from five skills: progressive-context (routing), context-routing-review (review), knowledge-modeling (modeling), knowledge-organization-system (vocabulary) and controlled-natural-language (statements), with the manifests and entry-files references added. Their history is in git under their old paths.
