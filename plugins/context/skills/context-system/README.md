# Context system skill: maintenance

For using the skill, start at [SKILL.md](SKILL.md). This file is for people changing it.

Contents: [Layout](#layout) · [Tests](#tests) · [The skill checked by itself](#the-skill-checked-by-itself) · [Packaging](#packaging) · [History](#history)

## Layout

| Path | Holds |
|---|---|
| `SKILL.md` | Entry: route table, layers, invariants, tools |
| `references/<layer>/guide.md` | One guide per layer (vocabulary, modeling, routing, review, statements); the layer's modules sit beside it |
| `references/manifests.md`, `references/routing/entry-files.md` | Manifests, registries, modes; entry-file structure |
| `scripts/`, `tests/`, `fixtures/` | Validators and linters, their tests and fixtures |
| `templates/`, `examples/`, `schemas/` | Starting points, worked examples, the optional routing JSON schemas |
| `agents/openai.yaml` | Display name, short description and default prompt for a host that reads agent metadata; no file here names it, by design |
| `evals/trigger-activation.suite.yaml` | Trigger cases in evaluation-system format |

## Tests

From this directory: `python3 -B -m unittest discover -s tests`. Every tool uses the standard library only and never executes corpus code or uses the network. Vocabulary and rules files are JSON, read by `scripts/datafile.py`; a `.yaml` file from before the switch is still read on a machine that has PyYAML.

Trigger cases: `evals/trigger-activation.suite.yaml`, in evaluation-system's suite format. Rerun it when the description or a layer's scope changes.

## The skill checked by itself

The skill keeps the three artifacts it asks a corpus for, at its root: `vocabulary.json` (the words it uses with one meaning), `profile.json` (its entry, layer guides and the references they lead to) and `suite.json` (one route trial per intent in SKILL.md's route table). `python3 scripts/check.py --root . --strict` runs them all, with the link check, and the tests run that command.

After editing SKILL.md or a reference the profile indexes, record the new bytes: `cd scripts && python3 refresh_profile.py --root .. --profile ../profile.json`. A stale hash fails the routing check on purpose.

## Packaging

A consumer's copy carries what a consumer reads or runs. `python3 scripts/package.py --out DIR` writes that copy and checks it: it leaves out `tests/`, `fixtures/`, `evals/`, this file, `scripts/package.py`, the skill's own `vocabulary.json`, `profile.json` and `suite.json`, and the performance contract in `references/routing/earlier/`, then runs the link check on the result, so a consumer file that still points at an author-only path fails the packaging.

## History

Merged on 2026-11-12 from five skills: progressive-context (routing), context-routing-review (review), knowledge-modeling (modeling), knowledge-organization-system (vocabulary) and controlled-natural-language (statements), with the manifests and entry-files references added. Their history is in git under their old paths.
