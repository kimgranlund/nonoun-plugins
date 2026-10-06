# Evals

This folder holds dated records of model and effort experiments. A change to a model or effort row in `plugins/sdlc-lite/adapters/claude/levels.json` (the `scripts/run.sh` `case "$role:$level"` rows mirror it until run.sh is retired, and `claude_roles.py generate` regenerates the agent definitions) or to `plugins/sdlc-lite/adapters/codex/models.json` lands only with a new eval and `evals.py lock`, else `python3 plugins/sdlc-lite/scripts/check.py` fails. Model and effort defaults stay user decisions; an eval records evidence and never changes one. Run every command below from the repository root.

## File format

An eval is a file named `NNNN-<slug>.md` directly in this folder, matching `\d{4}-[a-z0-9][a-z0-9-]*\.md`. `AGENTS.md`, `CLAUDE.md`, and non-`.md` files here are not evals. `evals.py add` picks the next free number.

The file starts with a `---` line, then one `key: value` line per field in the order below, then a `---` line, then the body. Values are bare: no quoting, no comments. Only `evidence` may hold a one-line `[a, b, c]` list.

| Field | Rule |
|---|---|
| `role` | `[a-z][a-z-]*` (syntactic, so a renamed role never invalidates an old record) |
| `level` | `L1` to `L5`, or `all` |
| `model` | `[A-Za-z0-9][A-Za-z0-9._-]*`, any model id, in the table or not, or `all` |
| `effort` | `[a-z]+`, no fixed list |
| `host` | `claude`, `codex`, or `all` |
| `task_set` | any non-empty one-line text, never checked for existence |
| `pass_rate` | `<passed>/<total>`, non-negative integers, passed not above total (`0/0` is allowed) |
| `cost_usd` | a non-negative number (`\d+(\.\d+)?`) or `unknown` |
| `date` | `YYYY-MM-DD` |
| `evidence` | one item or a `[a, b, ...]` list |

`all` in `role`, `level`, `model`, `effort`, or `host` marks a record that covers the whole table.

Each `evidence` item is either an `http(s)` URL (checked for form only, never fetched) or a path relative to the repository root, with no `..` segment, that exists.

The body holds a `## Method` line and a later `## Result` line. Each is followed by at least one non-blank line before the next `## ` line.

Example eval, `.sdlc/evals/0001-scout-sonnet.md`:

```
---
role: scout
level: L1
model: claude-sonnet-5-5
effort: low
host: claude
task_set: bench scout set
pass_rate: 9/10
cost_usd: 1.25
date: 2026-10-05
evidence: [docs/reports/scout-sonnet-2026-10-05.md, https://example.com/run/42]
---
## Method

Ran the scout set twice per model on a throwaway worktree.

## Result

Sonnet matched Haiku on 9 of 10 tasks at a higher cost.
```

## Table lock

`table-lock.json` holds exactly three keys:

- `eval`: the cited eval, a repository-relative path such as `.sdlc/evals/0000-baseline.md`.
- `previous_eval`: the eval it replaced, or `null`.
- `table_sha256`: the hash of the model table the cited eval covers.

The canonical text behind `table_sha256`: every `role:level model effort` row from `run.sh` that matches the regex `^\s*([\w-]+):(L\d)\)\s*model=([\w-]+);\s*effort=(\w+)`, formatted as `<role>:<level> <model> <effort>`, sorted, one per line; then `models.json` as `json.dumps(..., sort_keys=True, separators=(',', ':'))` and a newline. The sha256 hex of that UTF-8 text is the hash. Whitespace edits leave it alone; any value change moves it.

`evals.py check`, and `check.py` through it, enforce these rules:

- Every eval file has a valid name and passes the field and body rules above.
- No eval number is used twice.
- `table-lock.json` exists and holds exactly the three keys.
- The current table hash equals `table_sha256`; otherwise the model table changed without a new lock.
- `eval` names a valid eval in this folder.
- When `previous_eval` is set, it names a valid eval, and `eval` is dated later than it.

## Procedures

Add an eval (refuses an invalid record and writes nothing):

```
python3 plugins/sdlc-lite/scripts/evals.py add <slug> --role R --level L --model M --effort E --host H --task-set S --pass-rate P/T --cost-usd C --date YYYY-MM-DD --evidence X [--evidence Y ...] --method TEXT --result TEXT
```

List the evals, one tab-separated line each: `python3 plugins/sdlc-lite/scripts/evals.py list`.

Check every eval and the lock: `python3 plugins/sdlc-lite/scripts/evals.py check`.

Print the current table hash: `python3 plugins/sdlc-lite/scripts/evals.py hash`.

Change the model table:

1. Run the experiment.
2. Record it with `evals.py add`.
3. Change the row in `run.sh` or `models.json` (a user decision).
4. Run `python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/<file>`.
5. Run `python3 plugins/sdlc-lite/scripts/check.py`.

Never edit `table-lock.json` by hand; only `evals.py lock` writes it.

## Limits

- URLs in `evidence` are checked for form only.
- A hand edit of `table_sha256` alone is not detected, so review the lock in the diff.
- The date rule allows one table change per day per lock chain.
- Eval numbers are not unique across parallel worktrees; `check` reports a duplicate after a merge.
