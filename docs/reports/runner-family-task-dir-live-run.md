# Runner family task dir live run

Recorded: 2026-10-04

For T-0195, a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in `step-1/`, where the pre-fix run.sh kept Sonnet. Evidence files sit in [runner-family-task-dir-live-run/](runner-family-task-dir-live-run/) and are copied verbatim.

## Environment

- Claude Code 2.1.286 at the live run; Claude Code 2.1.286 when the dry runs were rerun.
- Live runs at commit aa59ebc, with steps 1 and 2 committed in d87cc4b and aa59ebc (not uncommitted).
- Fixed run.sh blob `e5308edf87a23bd02eb179eab631250a1bf24819`, used by the live runs and the fixed dry run.
- Pre-fix commit `171e13b72a516ccad2472d866f072add289079cf` (`T-0195 plan split`), run.sh blob `dc34865ecd542cb3e55516cc4803a7071f3b7364`, used by the base dry run.
- Dry runs rerun at HEAD e0f7d2e.
- macOS, Darwin 25.6.0. Live project `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.PDQbvWuqBm/claude`; rebuilt dry-run project `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.LZYtMse5bW/claude` (removed after the run).
- Log init model ids from the live project: builder `claude-sonnet-5-5`, verifier `claude-opus-5-5`.

## Method

Every command ran through a wrapper `W` that calls `env -u CLAUDECODE`, adds one `-u` for each set `CLAUDE_CODE_*` and `SDLC_*` variable, then sets `SDLC_BACKEND=claude`, so a nested run inherits no attempt name, base sha, or role.

The live project is a fresh git repository with the task `fam` and one step. From it:

```
W bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/fam/step-1/handoff.md
W bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md
```

The dry-run project is a rebuilt git repository holding only `fam/handoff.md` and `fam/step-1/{handoff.md,builder-L1.md,runs.jsonl}` from the evidence folder, which is the state the live verifier started from. The pre-fix plugin was extracted with `git archive 171e13b plugins/sdlc-lite` into `$X`. From the project, with no model call:

```
W SDLC_DRY_RUN=1 bash "$X/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/fam/handoff.md > <repo>/docs/reports/runner-family-task-dir-live-run/dry-run-base.txt
W SDLC_DRY_RUN=1 bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md > <repo>/docs/reports/runner-family-task-dir-live-run/dry-run-fixed.txt
```

The first negative control used the step-2 checkpoint aa59ebc, which already held the fix, so this one replaced it.

## Results

| Arm | Result | Evidence |
|---|---|---|
| Builder header | `model=sonnet effort=low` | `fam/step-1/builder-L1.md` |
| Verifier header and runs line | `model=opus effort=medium`, backend claude | `fam/verifier-L1.md`, `fam/runs.jsonl` |
| Log model ids | builder `claude-sonnet-5-5`, verifier `claude-opus-5-5` | init events of the live logs |
| Base dry run (pre-fix run.sh) | `--model sonnet --effort medium` | `dry-run-base.txt` |
| Fixed dry run | `--model opus --effort medium` | `dry-run-fixed.txt` |

Result: pass

## Limits

- One trial, on Claude only.
- Codex is covered by `codex-selftest.py` and a dry run, not a live run.
- The live run has one step, so the choice across steps by number is exercised only by the selftests.
- The dry runs ran in a rebuilt project at a later commit than the live runs, with the same run.sh blob as the live runs.
