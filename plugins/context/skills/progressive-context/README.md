# Progressive Context

Start with [SKILL.md](SKILL.md) for task-led review, design and refactoring routes.
The detailed T0-T11 architecture is a reference, not a mandatory implementation.

- [Contracts](references/contracts.md): optional local JSON descriptors and registry.
- [Evaluation](references/evaluation.md): static, authored replay and live evidence boundaries.
- [Worked corpus](examples/worked-corpus/README.md): a short route that fails until required governing context is loaded.

From this directory, run `python3 -B -m unittest discover -s tests`.
The scripts use Python 3.9+ standard library only, never execute corpus code, and
make no network calls. Non-file storage needs its own adapter.
