# todo — a tiny dependency-free CLI task manager

Build a small, well-tested command-line todo manager in a single language with no third-party dependencies
(Python stdlib, or Node with zero deps). A second brief to show the factory handles "almost any idea", not just
the worked solitaire example.

## What a good version does

- `add <text>`, `ls` (list with ids + done/open state), `done <id>`, `rm <id>`, and `clear --done`.
- Persists to a plain JSON file in the user's home (or `$TODO_FILE`); survives across invocations.
- Stable, human-readable ids; `ls` shows open first, then done; a `--json` flag emits machine-readable output.
- A real test suite (the language's stdlib test runner) covering add/done/rm/persistence/empty-state.

## Non-goals

- No due dates, priorities, tags, or sync in this first cut.
- No third-party packages; no network.

## Acceptance signal

`add` then `ls` shows the item open; `done` flips it; `rm` removes it; the JSON file round-trips across a fresh
process; the test suite passes clean.
