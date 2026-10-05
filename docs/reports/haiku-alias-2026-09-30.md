# Haiku alias probe, 2026-09-30

Claude Code 2.1.285, Max login.

| Probe | Reported model |
|---|---|
| `claude -p --model haiku` | modelUsage `claude-sonnet-5-5` |
| `claude -p --model claude-haiku-4-5` | modelUsage `claude-haiku-4-5` |
| `claude -p --model claude-haiku-5-5` | failed with `unrecognized_model` |

The alias `haiku` ran Sonnet 5.5, so the run.sh scout now pins `claude-haiku-4-5`.

Limit: one machine, one login; other plans may resolve the alias differently.

## Live check after the pin

Same day, same machine and login, a throwaway Git project with a two-line `app.py`: `run.sh scout L1` on the pinned runner exited 0. The result header read `model=claude-haiku-4-5 effort=low`, `runs.jsonl` recorded `"model":"claude-haiku-4-5"`, the only key in the transcript's `modelUsage` was `claude-haiku-4-5`, and the map named `app.py:1`, which is correct. One run; it shows which model answered, not scout quality.
