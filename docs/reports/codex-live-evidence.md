---
date: 2026-10-12
---

# Codex live evidence: headless chain and solo run

Recorded: 2026-10-12 (T-0316). One small ticket ran through planner, builder and verifier on Codex via `run.sh`, and a second ticket ran through the solo wrapper, in a throwaway repo under `/tmp`. This is the first recorded `run.sh` chain on Codex; the earlier live runs ([native smoke](native-codex-smoke.json), [conductor solo run](codex-conductor-solo-live-run.md)) used native subagent exchange or a conductor.

## What ran

- Plugin 0.22.4 at repository commit `4694d0cd` (agent files generated, `codex_roles.py generate --check` passes); `codex-cli 0.162.0`, `Logged in using ChatGPT`. No model or effort value was changed.
- Throwaway project `/tmp/codex-live-0316` (git, one commit, 28 agents from `codex_roles.py install`, `readiness.py --backend codex --transport exec` ready). Package `kit` with `greet()` returning `"hello"` and a test expecting `"Hello, Ada!"`; the task folder `.sdlc/greet/` has a handoff with no ticket id, so the lane gate does not apply and the full chain runs. Second ticket `.sdlc/0001-shout/` (T-0001, size L1, `steps.py lane` prints `solo`): add `kit/shout.py` and a test. The captured files are in [codex-live-evidence/](codex-live-evidence/).
- Transport: `exec` for every run (`codex exec` with the predefined agent), launched from a Claude Code session with `SDLC_BACKEND=codex`, not from inside Codex.

Commands, run from `/tmp/codex-live-0316` (`$P` is `plugins/sdlc-lite`):

```sh
SDLC_BACKEND=codex SDLC_ROUTING_REASON="T-0316 live evidence run" bash $P/scripts/run.sh planner L1 .sdlc/greet/handoff.md
SDLC_BACKEND=codex SDLC_ROUTING_REASON="T-0316 live evidence run" bash $P/scripts/run.sh builder L1 .sdlc/greet/step-1/handoff.md
SDLC_BACKEND=codex SDLC_ROUTING_REASON="T-0316 live evidence run" bash $P/scripts/run.sh verifier L1 .sdlc/greet/step-1/handoff.md      # fail, see below
SDLC_BACKEND=codex SDLC_ROUTING_REASON="T-0316 rerun after launcher files left in repo root" bash $P/scripts/run.sh verifier L1 .sdlc/greet/step-1/handoff.md   # pass
SDLC_BACKEND=codex python3 $P/scripts/solo_run.py run --backend codex --task-dir .sdlc/0001-shout --tier L1 --no-worktree --brief "Deliver the ticket at .sdlc/0001-shout/handoff.md. Run its done check and report."
```

The step handoff `step-1/handoff.md` is the planner's Step 1 copied by hand into a step folder (the conductor's job).

## Result

| Run | Model, effort | run.sh duration | Tokens in / out | Exit |
|---|---|---|---|---|
| planner L1 | `gpt-6.1-sol` medium | 96.2 s | 228,980 / 1,951 | 0 |
| builder L1 | `gpt-6-luna` low | 37.6 s | 261,905 / 1,803 | 0 |
| verifier L1 (first) | `gpt-6.1-sol` low | 80.3 s | 168,138 / 1,760 | 0, verdict fail |
| verifier L1 (rerun, `-2`) | `gpt-6.1-sol` low | 38.4 s | 119,280 / 692 | 0, verdict pass |
| solo L1 | `gpt-6.1-sol` low | 81.8 s | 123,709 / 453 | 0 |

Sources: [chain-planner-runs.jsonl](codex-live-evidence/chain-planner-runs.jsonl), [chain-step-1-runs.jsonl](codex-live-evidence/chain-step-1-runs.jsonl), [solo-runs.jsonl](codex-live-evidence/solo-runs.jsonl). Cost is null in every row: Codex reports none (`cost_reason: codex reports no cost` on the solo row).

- Chain: the planner wrote one L1 step with two `(red)` criteria ([planner-L1.md](codex-live-evidence/planner-L1.md)). The builder changed `kit/greet.py` to `f"Hello, {name}!"` and reported `## Status done` ([builder-L1.md](codex-live-evidence/builder-L1.md)). The verifier ran on `gpt-6.1-sol`, not the builder's `gpt-6-luna`: the Luna builder and Luna verifier default pair shares a model, so the configured alternate applied and `shared_with_builder` is false in the rows.
- The first verifier returned `fail`, and the cause was mine, not the code's. I had redirected `run.sh` stdout and stderr to `builder.out`, `builder.err` and so on in the repo root, and criterion 4 ("no new files outside `.sdlc/greet/`") caught those files. Its own "For the next attempt" names a plan defect (the criterion contradicted the Do's launcher-artifact exemption) and says the implementation needs no change. Criteria 1 to 3 passed with in-memory negative controls against the base implementation (`'hello' != 'Hello, Ada!'`). I moved the capture files out of the repo and reran; the rerun rechecked criterion 4 only and passed. Both results are kept: [verifier-L1.md](codex-live-evidence/verifier-L1.md) (log of the failed attempt: [verifier-L1.failed-attempt.log.txt](codex-live-evidence/verifier-L1.failed-attempt.log.txt), original path `/tmp/codex-live-0316/.sdlc/greet/step-1/verifier-L1.log`) and [verifier-L1-2.md](codex-live-evidence/verifier-L1-2.md).
- Solo: `sdlc-solo-l1` (`gpt-6.1-sol` low, from the tier table through `codex_exec.py solo L1`) created `kit/shout.py` and `tests/test_shout.py` ([shout.py.txt](codex-live-evidence/shout.py.txt), [test_shout.py.txt](codex-live-evidence/test_shout.py.txt)); the final tree runs `python3 -m unittest discover -s tests`: 3 tests, OK. Report: [solo-report.md](codex-live-evidence/solo-report.md). The wrapper recorded the run row and wrote the lane and skip entries to `skips.md`.
- Validation: `results.py validate` exits 0 on the planner, builder, first verifier and rerun verifier results, and exits 1 on two negative controls (a builder result with its Status value removed; a verifier result checked as a builder). See [validation.txt](codex-live-evidence/validation.txt). `codex_roles.py generate --check` printed `Codex agent definitions verified`.

## What did not work, or is unclear

- Solo has no result file to validate. Its `runs.jsonl` row has `"file": ""` and `results.py validate --role` has no solo role, so the solo run is evidenced by its report, the delivered diff and a rerun of its done check, not by a validated result file. The brief's "validated result files" holds for the chain only.
- The builder's own `results.py validate` call failed ("requires a role/level/model/effort header") because `run.sh` writes the header after the agent finishes; the builder retained the report. The final file validates.
- `redck: process deviation: red-checkpoint: retrospective`: both `(red)` controls were recorded at 15:00:32 as phase `retrospective` with exit 1 (red), not before the first edit; [process-deviations.md](codex-live-evidence/process-deviations.md). The builder says it ran `redck.py record` before the edit but the checkpoint judged it retrospective; the cause was not traced. The verifier noted the deviation.
- Every run printed `run.sh: loaded context not recorded: rollout absent`; `loaded_context.status` is `rollout absent` in each row. The `profile:` first line of each report is present, so the loaded revision is visible in the report but not cross-checked against a Codex rollout.
- Verifier L1's first fail shows that a Codex verifier reads criteria literally and will fail a step on a conflict inside the plan. The planner wrote that conflict; nothing was filed against it because the second pass passed.

## Unverified

- The native subagent transport (`SDLC_CODEX_TRANSPORT=subagent`) was not exercised: this ran from Claude Code, so it used `exec`. The planner, builder and verifier steps have `transport: codex` in their rows and the solo row says `transport: exec`; the native exchange stays as documented in [codex-role-execution.md](../references/codex-role-execution.md) and the earlier live runs.
- The chain ran at planner L1, builder L1, verifier L1 only, on a one-line change. Higher levels, multiple steps, an L4 or L5 plan-reviewer step, `fanout.py` and the conductor were not run.
- One machine, one ChatGPT account, one run each; the fail-then-pass verifier pair is a single sample, not a rate.
- Spend is unknown (Codex reports no cost); token usage is in the table.
- Two copied results ([builder-L1.md](codex-live-evidence/builder-L1.md), [verifier-L1-2.md](codex-live-evidence/verifier-L1-2.md)) had their em dashes replaced with hyphens to meet the repository's no-em-dash rule; nothing else was edited beyond trailing whitespace, and they still validate.
- The throwaway repo and its raw logs live under `/tmp/codex-live-0316`; only the copied files in `codex-live-evidence/` are kept in this repository.
- Failures are filed as tickets: (1) [T-0485](../../.sdlc/0485-solo-result-file/handoff.md) `solo` has no validatable result file; (2) [T-0486](../../.sdlc/0486-redck-retrospective-checkpoint/handoff.md) the retrospective red-checkpoint on a builder that did record before editing; (3) [T-0487](../../.sdlc/0487-codex-exec-rollout-absent/handoff.md) `rollout absent` for loaded context on `codex exec` runs. The failed first verifier attempt was a plan defect in the throwaway ticket, with its log kept at `codex-live-evidence/verifier-L1.failed-attempt.log.txt`.
