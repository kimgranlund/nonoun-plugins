# SDLC Lite maintenance

Read [repository guidance](../../AGENTS.md) first. Paths below are relative to this plugin unless a command starts with `plugins/`; those commands run from the repository root.

## Contracts and routing

- Shared roles live in `agents/`; workflows and output contracts live in `skills/`. Keep callers and producers consistent when changing handoffs or verdicts.
- `agents/` also holds two session agents that are not `run.sh` roles, the `conductor` and the `messenger`. `scripts/check.py` excludes both from the run.sh agreement check and checks the messenger's file and Codex mapping.
- Pipeline role execution goes through `scripts/run.sh` so required output sections, result files, and `runs.jsonl` remain authoritative. Direct native delegation alone does not advance pipeline state.
- `scripts/results.py` owns each role's result schema (key section, allowed first values, header, declared section order). `run.sh` and `steps.py` call it, `scripts/check.py` checks agent bodies against it, and no other file copies it.
- Claude uses headless role processes. Codex supports standalone exec and native subagent exchange; read [Codex execution](../../docs/codex-role-execution.md) before changing that adapter.
- Claude models and efforts live in `scripts/run.sh`, with the consumer explanation in `skills/level-rubric/SKILL.md`. `scripts/check.py` checks their agreement. Codex defaults live in `adapters/codex/models.json`. A change to either table needs a new eval in `.sdlc/evals/` and `scripts/evals.py lock`, else `scripts/check.py` fails; read [the evals entry file](../../.sdlc/evals/AGENTS.md) first.
- After changing shared role bodies, preloaded skill bodies, Codex mappings, or the Codex prelude, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Preserve managed-agent install ownership checks.
- For runner, ticket, board, step, or fanout internals, read only the relevant entry in [the implementation reference](../../docs/maintenance/sdlc-internals.md).
- For Claude hook registration, permissions, and background execution rules, read [hook maintenance](../../docs/maintenance/claude-hooks.md). Do not apply Claude flags or permission bypasses to Codex.

## Behavioral invariants

- `scripts/order.py` owns newest-result ordering; never use file modification time.
- `scripts/steps.py` owns next-action decisions. Missing verdicts, inherited failures, plan defects, and implementation failures are distinct outcomes. Preserve the one-criterion verifier swap rules and recurring-finding replan route.
- Keep the merge-step template consistent across planner and handoff-format and with the builder's commit boundary. `scripts/check.py` validates these contracts.
- Checks must be able to fail. Preserve independent verification and the recorded build baseline (`SDLC_BASE_SHA`); scope criteria must account for relevant untracked work.
- Ticket changes must preserve cross-worktree ID uniqueness, reference-safe closure, and explicit follow-up selection. Read the ticket/file skills and associated tests before editing these behaviors.
- Preserve in-scope loose-end handling and the one-ticket follow-up cap; a new task is for work that is out of scope, large, or needs user input.
- Runner-created temporary worktrees use `SDLC_TMP_WORKTREES`; preserve owned cleanup and stray-worktree reporting. Fanout worktrees require project watcher/test exclusions as well as Git ignores.

## Verification

Use the root validation matrix. Useful focused checks, run from the repository root:

- Role/skill contracts: `python3 plugins/sdlc-lite/scripts/check.py`.
- Generated agents: `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`.
- Codex adapter: `python3 plugins/sdlc-lite/scripts/codex-selftest.py`.
- Tickets, board, steps, ordering, fanout: the affected `plugins/sdlc-lite/scripts/<name>.py selftest`.
- Evals and the model-table lock: `python3 plugins/sdlc-lite/scripts/evals.py check` (and `selftest`).
- Runner: `bash plugins/sdlc-lite/scripts/run-selftest.sh`.
- Hooks: commands in the hook maintenance reference.
- Full regression suite: `bash plugins/sdlc-lite/scripts/check.sh`.

A role behavior change needs a focused live run on a throwaway project. Benchmark fixtures must expose all names and constraints pinned by hidden checks and demonstrate both failure and success. If a verifier passes while a hidden check fails, resolve the discrepancy before tuning models.
Raw transcripts and benchmark logs are ignored; retain appropriate result reports and run records. Keep dated validation evidence separate from current instructions.

Readiness and run ownership live in `scripts/readiness.py` and `scripts/run_lifecycle.py`. Preserve failure evidence and handoff-directory exclusion for both backends. Run `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` after changes to routing records, cancellation, or recovery; it includes negative readiness and duplicate-launch controls. Runtime `completed` status means a valid report was delivered, not that a task or verification passed.
