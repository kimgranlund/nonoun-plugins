# SDLC Lite maintenance

Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction. Improvements serve [the four pillars](../../docs/specs/sdlc-lite/pillars.md): performance, cost, quality, resilience.

Read [repository guidance](../../AGENTS.md) first. Paths below are relative to this plugin unless a command starts with `plugins/`; those commands run from the repository root.

## Contracts and routing

- Ticket level L1 and L2 plugin work goes to `solo` by default; `/fix` only when the user asks for it or the lane script prints `fix`, and the lean lane when the lane script says so. Run the full chain only with a stated reason (an L4 or L5 step, a merge step, cross-cutting scope, a security-sensitive change) and record that reason in the ticket. See [the SDLC Lite design](../../docs/specs/sdlc-lite/design.md).
- Shared roles live in `agents/`; workflows and output contracts live in `skills/`. Keep callers and producers consistent when changing handoffs or verdicts.
- A skill is self-contained: what it needs to run (schemas, templates, rubrics, fixtures) ships in its own folder, and it names no repo-relative path outside it. Scripts and any file shared with another skill (the Codex adapter, `handoff-format/run-operations.md`, an agent file) are reached through `${CLAUDE_PLUGIN_ROOT}/...`, never `../` or `plugins/...`, and the consumer's own files (`.sdlc/`) are found by the script, not assumed by the skill text. `scripts/check.py` item 42 enforces it: a link that leaves its skill folder, a `plugins/` prose path, or a dangling plugin-root path fails.
- `agents/` also holds three session agents that are not `run.sh` roles, the `conductor`, the `messenger`, and `solo`. `scripts/check.py` excludes all three from the run.sh agreement check and checks the messenger's and solo's files and Codex mappings.
- Pipeline role execution goes through `scripts/run.sh` so required output sections, result files, and `runs.jsonl` remain authoritative. Direct native delegation alone does not advance pipeline state.
- `scripts/results.py` owns each role's result schema (key section, allowed first values, header, declared section order). `run.sh` and `steps.py` call it, `scripts/check.py` checks agent bodies against it, and no other file copies it.
- Claude dispatches roles as sub-agents (`scripts/dispatch.py`; design in [sub-agent mode](../../docs/planning/sdlc-lite/subagent-mode.md)); sub-agent mode is the Claude mode, and `run.sh` is the Codex runner. Its Claude branch is legacy for bench and CI: it exits 2 pointing to `dispatch.py prepare` unless `SDLC_CLAUDE_EXEC=1`. Codex supports standalone exec and native subagent exchange; read [Codex execution](../../docs/references/codex-role-execution.md) before changing that adapter.
- Claude models and efforts live in `adapters/claude/levels.json` (the `scripts/run.sh` `case` rows mirror it for the legacy Claude branch), with the consumer explanation in `skills/level-rubric/SKILL.md`. `scripts/check.py` checks the three against each other. Codex defaults live in `adapters/codex/models.json`. A change to either table needs a new eval in `.sdlc/evals/` and `scripts/evals.py lock`, else `scripts/check.py` fails; read [the evals entry file](../../.sdlc/evals/AGENTS.md) first.
- After changing shared role bodies, preloaded skill bodies, Codex mappings, `overlays/<role>.md`, or the Codex prelude, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Preserve managed-agent install ownership checks.
- `agents/<role>-L<n>.md` and `agents/solo-L1|L2|L3.md` are generated, one per `levels.json` row, from the role file and the table: never edit one. After changing a role file, its skills list, `levels.json`, or `overlays/<role>.md`, run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate`; `generate --check` and `check.py` fail on a stale, hand-edited, or orphaned file.
- For runner, ticket, board, step, or fanout internals, read only the relevant entry in [the implementation reference](../../docs/references/sdlc-internals.md).
- For Claude hook registration, permissions, and background execution rules, read [hook maintenance](../../docs/references/claude-hooks.md). Do not apply Claude flags or permission bypasses to Codex.

## Behavioral invariants

- `scripts/order.py` owns newest-result ordering; never use file modification time.
- `scripts/steps.py` owns next-action decisions. Missing verdicts, inherited failures, plan defects, and implementation failures are distinct outcomes. Preserve the one-criterion verifier swap rules and recurring-finding replan route.
- Keep the merge-step template consistent across planner and handoff-format and with the builder's commit boundary. `scripts/check.py` validates these contracts.
- Checks must be able to fail. Preserve independent verification and the recorded build baseline (`SDLC_BASE_SHA`); scope criteria must account for relevant untracked work.
- Ticket changes must preserve cross-worktree ID uniqueness, reference-safe closure, and explicit follow-up selection. Read the ticket/file skills and associated tests before editing these behaviors.
- Preserve in-scope loose-end handling and the one-ticket follow-up cap; a new task is for work that is out of scope, large, or needs user input.
- Runner-created temporary worktrees use `SDLC_TMP_WORKTREES`; preserve owned cleanup and stray-worktree reporting. Fanout worktrees (`.worktrees/`, and `.claude/worktrees/` for sub-agent lanes) require project watcher/test exclusions as well as Git ignores.
- `scripts/supervisor.py` never claims, moves, or reads a message body; a wake it starts follows unattended-run rules (`SDLC_HEADLESS=1`, never push or publish).

## Lanes

Interim directive until the plugin ships its own sweep.

- Where: fanout lanes are `<repo>/.worktrees/fanout/<lane>`, sub-agent lanes `.claude/worktrees/`, role temp trees under `$SDLC_TMP_WORKTREES`. All are gitignored and excluded from watchers.
- Open: `fanout.py run` or `prep` opens a lane; the ticket is claimed with `claimed_by:`.
- Close: after `fanout.py land` and `tickets.py close`, remove the lane worktree and branch once their content is on the default branch (ancestor, a MERGED PR whose head sha equals the tip, or every changed file equal).
- Before removal keep the branch reachable as `refs/archive/<date>/<branch>` and archive its untracked records.
- Never delete unmerged work. A locked worktree (`git worktree lock`) is a running lane: skip it.
- Names for new work: `lane/<ticket>-<slug>`, `wave/<N>`, `release/<X.Y.Z>`, annotated tags `vX.Y.Z`. Existing branches keep their names.
- Until the sweep ships, the maintainer's tool `~/.claude/lane/sweep.py` does the removal; it is a dry run by default.

## Verification

Use the root validation matrix. Useful focused checks, run from the repository root:

- Role/skill contracts: `python3 plugins/sdlc-lite/scripts/check.py`.
- Generated agents: `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` (and `claude_roles.py selftest`).
- Sub-agent dispatch (`prepare`, the pre-launch half of `run.sh`, and `record`, the validate-and-record half): `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`; a gate or `runs.jsonl` change in `run.sh` needs the same change in `dispatch.py`, which the parity cases compare.
- Codex adapter: `python3 plugins/sdlc-lite/scripts/codex-selftest.py`.
- Tickets, board, steps, ordering, fanout: the affected `plugins/sdlc-lite/scripts/<name>.py selftest`.
- Evals and the model-table lock: `python3 plugins/sdlc-lite/scripts/evals.py check` (and `selftest`).
- Proposals mined from runs: `python3 plugins/sdlc-lite/scripts/proposals.py selftest`; read [the proposals entry file](../../.sdlc/proposals/AGENTS.md) before scan, accept, reject, or promote.
- Prompt references in agents, skills, and overlays: `python3 plugins/sdlc-lite/scripts/prompt_lint.py` (and `selftest`).
- Docs-only verifier skip: `python3 plugins/sdlc-lite/scripts/verify_scope.py selftest` (and the `(docs-only)` cases of `tickets.py selftest`).
- Runner: `bash plugins/sdlc-lite/scripts/run-selftest.sh`.
- Hooks: commands in the hook maintenance reference.
- Full regression suite: `bash plugins/sdlc-lite/scripts/check.sh`.

A role behavior change needs a focused live run on a throwaway project. Benchmark fixtures must expose all names and constraints pinned by hidden checks and demonstrate both failure and success. If a verifier passes while a hidden check fails, resolve the discrepancy before tuning models.
Raw transcripts and benchmark logs are ignored; retain appropriate result reports and run records. Keep dated validation evidence separate from current instructions.

Readiness and run ownership live in `scripts/readiness.py` and `scripts/run_lifecycle.py`. Preserve failure evidence and handoff-directory exclusion for both backends. Run `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` after changes to routing records, cancellation, or recovery; it includes negative readiness and duplicate-launch controls. Runtime `completed` status means a valid report was delivered, not that a task or verification passed.
